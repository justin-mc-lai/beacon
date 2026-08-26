"""Version-level phased-lake orchestrator state for Beacon programs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.program_admission import _implementation_closed, _lake_rows, _qa_closed, _read_json
from beacon.utils.program_graph import feature_graph_path, load_feature_graph
from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


TRUTH_DONE = {"frozen", "accepted", "closed", "complete", "completed", "release_accepted"}


def _truth_frozen(lake: dict[str, Any]) -> bool:
    values = {
        str(lake.get("status") or "").strip().lower(),
        str(lake.get("truth_status") or "").strip().lower(),
    }
    values.discard("")
    return bool(values & TRUTH_DONE)


def _run_state_path(project_root: Path, version: str, program_slug: str) -> Path:
    return project_root / 'docs' / 'beacon' / version / 'programs' / program_slug / 'program-run-state.json'


def build_program_orchestrator_state(project_root: Path | str, *, version: str, program_slug: str) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    graph_path = feature_graph_path(root, resolved_version, program_slug)
    graph, errors = load_feature_graph(graph_path)
    if errors or not isinstance(graph, dict):
        return {
            'schema_version': '1.0',
            'status': 'blocked',
            'blocked': True,
            'reason_code': 'feature_graph_invalid',
            'version': resolved_version,
            'program_slug': program_slug,
            'graph_path': str(graph_path.relative_to(root)) if graph_path.exists() else str(graph_path),
            'errors': errors,
        }

    lakes = _lake_rows(graph)
    if not lakes:
        return {
            'schema_version': '1.0',
            'status': 'blocked',
            'blocked': True,
            'reason_code': 'program_lakes_missing',
            'version': resolved_version,
            'program_slug': program_slug,
            'graph_path': str(graph_path.relative_to(root)),
        }

    rows: list[dict[str, Any]] = []
    passed_lakes: list[str] = []
    blocked_lakes: list[str] = []
    current_lake = ''
    current_stage = 'completed'
    next_lake = ''
    resume_action = 'program_complete'
    reason_code = ''

    # Evidence lookup keys follow feature_slug (canonical), while rows may store
    # either the row slug or its feature_slug; resolve_program_lake_topology
    # dual-registers both, so alias deps back to the canonical evidence key too.
    alias_to_evidence: dict[str, str] = {}
    for row in lakes:
        key = feature_slug(str(row.get('feature_slug') or row.get('slug') or ''))
        for alias in (row.get('slug'), row.get('feature_slug')):
            normalized = feature_slug(str(alias or ''))
            if key and normalized:
                alias_to_evidence[normalized] = key

    for row in lakes:
        slug = feature_slug(str(row.get('slug') or row.get('feature_slug') or ''))
        evidence_key = feature_slug(str(row.get('feature_slug') or row.get('slug') or ''))
        impl = _implementation_closed(root, version=resolved_version, feature=evidence_key)
        qa = _qa_closed(root, version=resolved_version, feature=evidence_key)
        deps: list[str] = []
        unclosed_deps = []
        for item in row.get('depends_on', []):
            text = str(item).strip()
            if not text:
                continue
            dep = alias_to_evidence.get(feature_slug(text), feature_slug(text))
            deps.append(dep)
            dep_impl = _implementation_closed(root, version=resolved_version, feature=dep)
            dep_qa = _qa_closed(root, version=resolved_version, feature=dep)
            if not dep_impl.get('closed') or not dep_qa.get('closed'):
                unclosed_deps.append(dep)

        truth_frozen = _truth_frozen(row)
        if not truth_frozen:
            stage = 'truth'
            complete = False
            lake_reason = 'await_next_lake_truth'
        elif unclosed_deps:
            stage = 'truth'
            complete = False
            lake_reason = 'await_upstream_lake_closure'
        elif not impl.get('closed'):
            stage = 'implement'
            complete = False
            lake_reason = 'await_lake_implementation'
        elif not qa.get('closed'):
            stage = 'qa'
            complete = False
            lake_reason = 'await_lake_qa'
        else:
            stage = 'release'
            complete = True
            lake_reason = ''

        rows.append(
            {
                'lake': slug,
                'feature_slug': slug,
                'depends_on': deps,
                'truth_frozen': truth_frozen,
                'implementation_closed': bool(impl.get('closed')),
                'qa_closed': bool(qa.get('closed')),
                'unclosed_dependencies': unclosed_deps,
                'stage': stage,
                'complete': complete,
                'reason_code': lake_reason,
                'implementation_ref': impl.get('path', ''),
                'qa_ref': qa.get('path', ''),
            }
        )

        if complete:
            passed_lakes.append(slug)
            continue
        blocked_lakes.append(slug)
        if not current_lake:
            current_lake = slug
            current_stage = stage
            next_lake = slug
            reason_code = lake_reason
            if stage == 'truth':
                resume_action = 'prepare_next_lake_truth'
            elif stage == 'implement':
                resume_action = 'run_lake_implementation'
            elif stage == 'qa':
                resume_action = 'run_lake_qa'
            else:
                resume_action = 'await_human_gate'

    if not current_lake:
        current_stage = 'release'
        next_lake = ''
        reason_code = ''
        resume_action = 'await_human_gate'

    downstream_lakes = [row['lake'] for row in rows if row['lake'] not in passed_lakes and row['lake'] != current_lake]
    if not next_lake and downstream_lakes:
        next_lake = downstream_lakes[0]

    sea_completion_status = 'all_lakes_complete' if len(passed_lakes) == len(rows) else 'in_progress'
    next_action = ''
    next_action_target = current_lake
    recommended_command = ''
    if current_lake:
        if current_stage == 'truth':
            next_action = f'beacon-truth:{current_lake}'
            recommended_command = f'beacon truth review {current_lake} --project-root {root} --version {resolved_version} --json'
        elif current_stage == 'implement':
            next_action = f'beacon-gen-implement:{current_lake}'
            recommended_command = f'beacon implement run "{current_lake}" --project {root} --version {resolved_version}'
        elif current_stage == 'qa':
            next_action = f'beacon-eval-qa:{current_lake}'
            recommended_command = f'beacon qa run "{current_lake}" --project {root} --version {resolved_version}'
        else:
            next_action = f'beacon-release:{current_lake}'
            recommended_command = f'beacon release create {resolved_version} --project {root}'

    if reason_code == 'await_upstream_lake_closure':
        upstream = []
        if rows:
            upstream = list(rows[0].get('unclosed_dependencies') or [])
        if upstream:
            recommended_command = f'beacon implement run "{upstream[0]}" --project {root} --version {resolved_version}'

    next_action_source = str(_run_state_path(root, resolved_version, str(graph.get('program_slug') or program_slug)).relative_to(root))
    blocking_reason_codes = {'await_upstream_lake_closure'}
    blocked = reason_code in blocking_reason_codes
    status = 'blocked' if blocked else ('pass' if sea_completion_status == 'all_lakes_complete' else 'in_progress')

    return {
        'schema_version': '1.0',
        'status': status,
        'blocked': blocked,
        'reason_code': reason_code,
        'version': resolved_version,
        'program_slug': str(graph.get('program_slug') or program_slug),
        'graph_path': str(graph_path.relative_to(root)),
        'current_lake': current_lake,
        'current_stage': current_stage,
        'passed_lakes': passed_lakes,
        'blocked_lakes': blocked_lakes,
        'next_lake': next_lake,
        'resume_action': resume_action,
        'sea_completion_status': sea_completion_status,
        'next_action': next_action,
        'next_action_target': next_action_target,
        'next_action_source': next_action_source,
        'recommended_command': recommended_command,
        'passed_lake_count': len(passed_lakes),
        'lake_count': len(rows),
        'lakes': rows,
        'updated_at': now_iso(),
    }


def write_program_orchestrator_state(project_root: Path | str, payload: dict[str, Any]) -> Path:
    root = Path(project_root).expanduser().resolve()
    path = _run_state_path(root, str(payload.get('version') or ''), str(payload.get('program_slug') or ''))
    existing = _read_json(path)
    merged = {
        **existing,
        'schema_version': '1.0',
        'program_slug': payload.get('program_slug', existing.get('program_slug', '')),
        'version': payload.get('version', existing.get('version', '')),
        'current_lake': payload.get('current_lake', ''),
        'current_stage': payload.get('current_stage', ''),
        'passed_lakes': payload.get('passed_lakes', []),
        'blocked_lakes': payload.get('blocked_lakes', []),
        'next_lake': payload.get('next_lake', ''),
        'resume_action': payload.get('resume_action', ''),
        'reason_code': payload.get('reason_code', ''),
        'sea_completion_status': payload.get('sea_completion_status', ''),
        'next_action': payload.get('next_action', existing.get('next_action', '')),
        'updated_at': payload.get('updated_at', now_iso()),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
