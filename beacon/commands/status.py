"""Beacon status command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.artifact_paths import machine_root, uses_machine_surface
from beacon.utils.control_plane import build_resume_contract
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.delivery_baseline import load_implementation_delivery_host
from beacon.utils.implementation_plan import load_implementation_plan_progress
from beacon.utils.learning_loop import load_keep_discard_engine
from beacon.utils.material_audit import build_material_audit, build_requirement_package_gate
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload, load_requirement_clarity_state
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.truth_map import resolve_version_governance
from beacon.utils.runtime_projection import build_runtime_projection
from beacon.utils.runtime_projection_store import list_projects, load_project_detail, sync_projection
from beacon.utils.runtime import newest_run_id, read_json
from beacon.utils.semantic_runtime import evaluate_semantic_contract
from beacon.utils.technical_review_contract import build_technical_review_gate_payload, load_technical_review_state
from beacon.utils.versioning import (
    describe_project_version_context,
    project_release_feature_enabled,
    resolve_target_version,
)
from beacon.utils.writeback import acceptance_projection_transaction_contract
from beacon.utils.workflow_memory import compute_memory_metrics, compute_workflow_progress, workflow_memory_transaction_contract
from beacon.utils.help_support import build_help_payload, canonicalize_lifecycle_action, canonicalize_lifecycle_stage
from beacon.utils.support_surface_transactions import load_support_surface_summary

app = typer.Typer(
    name="status",
    help="Show workflow status",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _release_surface_enabled(root: Path, version: str, capability_version: str) -> bool:
    return project_release_feature_enabled(
        root,
        capability_version,
        docs_version=version,
        runtime_version=None,
    )


def _implementation_order_view(root: Path, *, version: str) -> dict[str, object]:
    host = load_implementation_delivery_host(root, version=version)
    feature_order = [
        "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor",
        "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure",
        "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
    ]
    host_features = host.get("features") if isinstance(host.get("features"), list) else []
    ordered: list[dict[str, object]] = []
    for slug in feature_order:
        item = next(
            (
                feature
                for feature in host_features
                if isinstance(feature, dict) and str(feature.get("feature_slug") or "") == slug
            ),
            None,
        )
        if not isinstance(item, dict):
            continue
        ordered.append(
            {
                "feature": str(item.get("feature") or ""),
                "feature_slug": slug,
                "depends_on_features": [
                    str(dep) for dep in item.get("depends_on_features", []) if str(dep).strip()
                ],
            }
        )
    if not ordered and version == "v1.4.0":
        ordered = [
            {
                "feature": "Beacon v1.4.0 lightweight kernel and core surface refactor",
                "feature_slug": "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor",
                "depends_on_features": [],
            },
            {
                "feature": "Beacon v1.4.0 PRD bootstrap safe requirement bootstrap and freeze closure",
                "feature_slug": "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure",
                "depends_on_features": ["beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor"],
            },
            {
                "feature": "Beacon v1.4.0 PRD bootstrap unified requirement closure orchestration",
                "feature_slug": "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
                "depends_on_features": ["beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure"],
            },
        ]
    if not ordered:
        return {"status": "missing", "feature_count": 0, "ordered_feature_slugs": [], "waves": []}
    waves = [
        {"wave": index + 1, "parallelizable": False, "features": [row]}
        for index, row in enumerate(ordered)
    ]
    return {
        "status": "analyzed",
        "feature_count": len(ordered),
        "ordered_feature_slugs": [row["feature_slug"] for row in ordered],
        "waves": waves,
    }


def _status_impl(
    board: bool,
    verbose: bool,
    project_root: str,
    version: str,
    feature: str,
    run_id: str,
    change_intent: str,
) -> int:
    root = (Path(project_root) if project_root else Path.cwd()).expanduser().resolve()
    team_root = root / ".beacon" / "team"
    team_count = len([p for p in team_root.glob("*") if p.is_dir()]) if team_root.exists() else 0
    bridge_root = root / ".beacon" / "bridge"
    bridge_count = len([p for p in bridge_root.glob("*") if p.is_dir()]) if bridge_root.exists() else 0
    progress = read_json(root / ".beacon" / "test-progress.json", {})
    latest = newest_run_id(root)
    version_filter = resolve_target_version(root, version) if version and version.strip() else resolve_target_version(root, None)
    feature_filter = feature.strip() if feature and feature.strip() else None
    explicit_run_filter = run_id.strip() if run_id and run_id.strip() else None
    run_filter = explicit_run_filter
    memory_metrics = compute_memory_metrics(
        root,
        run_filter,
        version=version_filter,
        feature=feature_filter,
    )
    workflow_progress = compute_workflow_progress(
        root,
        run_id=run_filter,
        version=version_filter,
        feature=feature_filter,
    )
    resolved_run_id = str(workflow_progress.get("run_id", "") or "")
    selected_state = (
        read_json(root / ".beacon" / "runs" / resolved_run_id / "state.json", {})
        if resolved_run_id
        else {}
    )
    memory_transaction = workflow_memory_transaction_contract(
        root,
        run_id=resolved_run_id or None,
        version=version_filter,
        feature=feature_filter,
    )
    terminal_status = str(selected_state.get("status", "unknown")) if isinstance(selected_state, dict) else "unknown"
    coverage_version = (
        version_filter
        or str(workflow_progress.get("version", "") or "").strip()
        or resolve_target_version(root, None)
    )
    truth_map_governance = resolve_version_governance(root, version=coverage_version)
    coverage_metrics = compute_coverage_metrics(
        root,
        version=coverage_version,
        feature=feature_filter,
    )
    material_audit = build_material_audit(root, version=coverage_version, strict=False)
    requirement_package_gate = build_requirement_package_gate(
        root,
        version=coverage_version,
        feature=feature_filter or "",
        strict=True,
    )
    version_context = describe_project_version_context(root, docs_version=coverage_version or None)
    source_of_truth = {
        "root": f"docs/beacon/{coverage_version}",
        "human_root": f"docs/beacon/{coverage_version}",
        "machine_root": (
            str(machine_root(root, coverage_version).relative_to(root))
            if uses_machine_surface(coverage_version)
            else ""
        ),
        "runtime_state_root": ".beacon",
        "truth_map_governance_resolver": truth_map_governance.get("resolver_mode", ""),
        "truth_map_governance_status": truth_map_governance.get("status", ""),
        "manifest_authority": bool(truth_map_governance.get("manifest_authority", True)),
        "json_authority": bool(truth_map_governance.get("json_authority", True)),
        "formal_package_closure": material_audit.get("status", "unknown"),
        "requirement_package_gate": requirement_package_gate.get("status", "pass"),
        "requirement_package_failure_categories": requirement_package_gate.get("failure_categories", []),
        "requirement_package_recommended_action": requirement_package_gate.get("recommended_action", ""),
        "requirement_package_recommended_command": requirement_package_gate.get("recommended_command", ""),
    }

    target_feature = feature_filter or str(workflow_progress.get("feature", "") or "")
    help_payload = (
        build_help_payload(
            root,
            version=coverage_version,
            feature=target_feature,
            run_id=resolved_run_id or None,
            change_intent=change_intent or None,
        )
        if target_feature
        else {}
    )
    lifecycle = help_payload.get("lifecycle", {}) if isinstance(help_payload.get("lifecycle"), dict) else {}
    workflow_progress_display = (
        help_payload.get("workflow_progress_display", {})
        if isinstance(help_payload.get("workflow_progress_display"), dict)
        else {}
    )
    implementation_plan_progress = load_implementation_plan_progress(root, version=coverage_version, feature=target_feature) if target_feature else {}
    requirement_clarity_gate = build_requirement_clarity_gate_payload(root, version=coverage_version, feature=target_feature) if target_feature else {}
    requirement_clarity_state = load_requirement_clarity_state(root, feature=target_feature) if target_feature else {}
    technical_review_gate = build_technical_review_gate_payload(root, version=coverage_version, feature=target_feature, revision_id=str(help_payload.get("revision_id", "") or "")) if target_feature else {}
    technical_review_state = load_technical_review_state(root, feature=target_feature) if target_feature else {}
    technical_review_release_enabled = bool(target_feature) and _release_surface_enabled(root, coverage_version, "v1.3.3")
    qa_status = load_qa_status(root)
    resume_contract = build_resume_contract(root, run_id=resolved_run_id or None)
    keep_discard_engine = load_keep_discard_engine(root)
    release_scorecard = build_release_scorecard(root, version=coverage_version)
    release_summary = summarize_release_scorecard(release_scorecard)
    implementation_order = _implementation_order_view(root, version=coverage_version)
    acceptance_feature = (
        target_feature
        or str(((release_scorecard.get("acceptance") or {}).get("feature")) if isinstance(release_scorecard.get("acceptance"), dict) else "")
        or str(qa_status.get("feature") or "")
    )
    acceptance_transaction = (
        acceptance_projection_transaction_contract(
            root,
            version=coverage_version,
            feature=acceptance_feature,
        )
        if acceptance_feature
        else {}
    )
    semantic_release_enabled = bool(target_feature) and _release_surface_enabled(root, coverage_version, "v1.3.6")
    if not technical_review_release_enabled and target_feature:
        technical_review_gate = {
            **(technical_review_gate if isinstance(technical_review_gate, dict) else {}),
            "status": "not_required",
            "blocked": False,
            "reason_code": "",
        }
    semantic_status = (
        evaluate_semantic_contract(root, version=coverage_version, feature=target_feature)
        if semantic_release_enabled
        else {
            "status": "not_required" if target_feature else "not_applicable",
            "reason_code": "",
            "message": "",
            "artifacts": {},
            "details": {},
        }
    )
    runtime_projection = build_runtime_projection(
        root,
        docs_version=coverage_version or None,
        feature=target_feature or None,
    )
    runtime_ledger = sync_projection(runtime_projection) if board else {
        "status": "not_synced",
        "preflight": runtime_projection.get("projection", {}).get("preflight", {}),
        "db_path": "",
        "pocketbase_root": "",
    }
    portfolio_projects = list_projects(limit=12) if board else []
    portfolio_detail = load_project_detail(str(runtime_projection.get("project_key") or "")) if board else {}

    payload = {
        "team": {"known_teams": team_count},
        "gate": {"terminal_status": terminal_status},
        "bridge": {"known_bridges": bridge_count},
        "test": {"has_progress": bool(progress)},
        "run": {
            "latest_run_id": latest or "",
            "selected_run_id": resolved_run_id,
        },
        "memory": memory_metrics,
        "memory_transaction": memory_transaction,
        "coverage": coverage_metrics,
        "scores": help_payload.get("scores", {}),
        "revision": {
            "revision_id": help_payload.get("revision_id", ""),
            "source_revision_id": help_payload.get("source_revision_id", ""),
            "superseded_by": help_payload.get("superseded_by", ""),
            "doc_status": help_payload.get("doc_status", ""),
            "delivery_status": help_payload.get("delivery_status", ""),
            "is_latest_revision": (help_payload.get("revision_lineage", {}) if isinstance(help_payload.get("revision_lineage"), dict) else {}).get("is_latest_revision", False),
            "is_frozen_baseline": (help_payload.get("revision_lineage", {}) if isinstance(help_payload.get("revision_lineage"), dict) else {}).get("is_frozen_baseline", False),
            "release_delivery_type": (release_scorecard.get("delivery", {}) if isinstance(release_scorecard.get("delivery"), dict) else {}).get("type", ""),
            "blocked": help_payload.get("blocked", False),
            "blocking_reasons": help_payload.get("blocking_reasons", []),
            "blocked_reason": help_payload.get("blocked_reason", ""),
        },
        "next_step": help_payload.get("next_step", {}),
        "lifecycle": lifecycle,
        "change_loop": help_payload.get("change_loop", {}),
        "project_metadata_context": help_payload.get("project_metadata_context", {}),
        "project_mode": help_payload.get("project_mode", "greenfield"),
        "execution_surface": help_payload.get("execution_surface", {}),
        "archive": help_payload.get("archive", {}),
        "host_prompt_trace": help_payload.get("host_prompt_trace", {}),
        "delivery_read_model": help_payload.get("delivery_read_model", {}),
        "support_surface_projection": help_payload.get("support_surface_projection", {}),
        "surface_explanation": help_payload.get("surface_explanation", {}),
        "hud": help_payload.get("hud", {}),
        "minimal_hud": help_payload.get("minimal_hud", {}),
        "learning_surface": help_payload.get("learning_surface", {}),
        "implementation_plan": {
            "plan_id": implementation_plan_progress.get("plan_id", ""),
            "status": implementation_plan_progress.get("status", "missing"),
            "counts": implementation_plan_progress.get("counts", {}),
            "next_task_id": implementation_plan_progress.get("next_task_id", ""),
            "next_task_title": implementation_plan_progress.get("next_task_title", ""),
            "blocked_task_ids": implementation_plan_progress.get("blocked_task_ids", []),
            "blocked_task_titles": implementation_plan_progress.get("blocked_task_titles", []),
            "task_ledger_path": implementation_plan_progress.get("task_ledger_path", ""),
        },
        "implementation_order": implementation_order,
        "requirement_clarity": {
            "status": requirement_clarity_gate.get("status", "not_required"),
            "blocked": requirement_clarity_gate.get("blocked", False),
            "reason_code": requirement_clarity_gate.get("reason_code", ""),
            "finding_count": requirement_clarity_state.get("finding_count", 0),
            "state_path": requirement_clarity_state.get("state_path", ""),
        },
        "technical_review": {
            "status": technical_review_gate.get("status", "not_required"),
            "blocked": technical_review_gate.get("blocked", False),
            "reason_code": technical_review_gate.get("reason_code", ""),
            "review_status": technical_review_state.get("review_status", ""),
            "approved_by": technical_review_state.get("approved_by", ""),
            "state_path": technical_review_state.get("state_path", ""),
        },
        "design_review": load_support_surface_summary(root, surface="beacon-design-review") if target_feature else {},
        "learning_governance": load_support_surface_summary(root, surface="beacon-learn") if target_feature else {},
        "requirement_completeness_gate": help_payload.get("requirement_completeness_gate", {}),
        "requirement_completeness": help_payload.get("requirement_completeness", {}),
        "requirement_gap_digest": help_payload.get("requirement_gap_digest", {}),
        "brainstorm_hint": help_payload.get("brainstorm_hint", {}),
        "supplement_task": help_payload.get("supplement_task", {}),
        "re_freeze_transaction": help_payload.get("re_freeze_transaction", {}),
        "semantic": semantic_status,
        "decision_trace": help_payload.get("decision_trace", []),
        "control_plane": resume_contract,
        "qa_status": {
            "feature": qa_status.get("feature"),
            "status": qa_status.get("status"),
            "evidence_done": qa_status.get("evidence_done"),
        },
        "acceptance_transaction": acceptance_transaction if isinstance(acceptance_transaction, dict) else {},
        "learning_plane": {
            "decision_summary": keep_discard_engine.get("decision_summary", {}),
            "decision_engine_path": ".beacon/state/evo/decision-engine.json",
        },
        "release_scorecard": release_scorecard,
        "lifecycle_hook_advisory": help_payload.get("lifecycle_hook_advisory", {}),
        "release_binding": release_scorecard.get("revision_binding", {}) if isinstance(release_scorecard, dict) else {},
        "version_context": {
            **version_context,
            "docs_version": coverage_version,
            "runtime_version": str(version_context.get("runtime_version", "") or help_payload.get("runtime_version", "")),
        },
        "truth_map_governance": truth_map_governance,
        "version_semantics": help_payload.get("version_semantics", {}) or version_context.get("version_semantics", {}),
        "source_of_truth": source_of_truth,
        "workflow_progress": workflow_progress,
        "workflow_progress_display": workflow_progress_display,
        "filters": {
            "version": version_filter or "",
            "feature": feature_filter or "",
            "run_id": explicit_run_filter or "",
        },
        "runtime_projection": runtime_projection,
        "runtime_ledger": {
            **runtime_ledger,
            "portfolio_projects": portfolio_projects,
            "current_project_detail": portfolio_detail,
        },
    }

    if board:
        typer.echo("Beacon Status Board")
        board_summary = runtime_projection.get("board", {}) if isinstance(runtime_projection.get("board"), dict) else {}
        board_current_stage = canonicalize_lifecycle_stage(board_summary.get("current_stage")) or board_summary.get("current_stage") or "unknown"
        board_next_action = canonicalize_lifecycle_action(board_summary.get("next_action")) or board_summary.get("next_action") or "none"
        typer.echo(f"- truth.line: {runtime_projection.get('docs_version') or coverage_version or 'unknown'}")
        typer.echo(f"- board.project: {runtime_projection.get('display_name') or root.name}")
        typer.echo(f"- board.project_kind: {board_summary.get('project_kind') or runtime_projection.get('project_kind') or 'unknown'}")
        typer.echo(f"- board.current_stage: {board_current_stage}")
        typer.echo(f"- board.progress: {board_summary.get('progress_label') or 'unknown'}")
        typer.echo(f"- board.blocker: {board_summary.get('blocker') or 'none'}")
        typer.echo(f"- board.next_action: {board_next_action}")
        typer.echo(f"- board.debug_state: {board_summary.get('debug_state') or 'no_debug_feed'}")
        typer.echo(f"- board.runtime_corroboration: {board_summary.get('runtime_corroboration') or 'missing'}")
        typer.echo(f"- board.health: {board_summary.get('health_status') or 'unknown'}")
        requirement_completeness = payload.get("requirement_completeness", {}) if isinstance(payload.get("requirement_completeness"), dict) else {}
        if requirement_completeness.get("enabled"):
            typer.echo(
                f"- board.requirement_completeness: {requirement_completeness.get('status')} "
                f"target={requirement_completeness.get('target_stage') or 'none'}"
            )
            blocked_subgates = requirement_completeness.get("blocked_subgates", [])
            downgraded_subgates = requirement_completeness.get("downgraded_subgates", [])
            focus_areas = requirement_completeness.get("focus_areas", [])
            if blocked_subgates:
                typer.echo(f"- board.requirement_blocked_subgates: {', '.join(str(item) for item in blocked_subgates)}")
            if downgraded_subgates:
                typer.echo(f"- board.requirement_downgraded_subgates: {', '.join(str(item) for item in downgraded_subgates)}")
            if focus_areas:
                typer.echo(f"- board.requirement_focus: {focus_areas[0]}")
            handoff = requirement_completeness.get("human_loop_handoff", {}) if isinstance(requirement_completeness.get("human_loop_handoff"), dict) else {}
            if handoff.get("recommended_command"):
                typer.echo(f"- board.requirement_next: {handoff.get('recommended_command')}")
        supplement_task = payload.get("supplement_task", {}) if isinstance(payload.get("supplement_task"), dict) else {}
        if supplement_task.get("target_artifact"):
            typer.echo(
                f"- board.supplement_task: target={supplement_task.get('target_artifact') or 'none'} "
                f"route={supplement_task.get('recommended_route') or 'none'}"
            )
            if supplement_task.get("writeback_target"):
                typer.echo(f"- board.supplement_writeback: {supplement_task.get('writeback_target')}")
        re_freeze_transaction = payload.get("re_freeze_transaction", {}) if isinstance(payload.get("re_freeze_transaction"), dict) else {}
        if re_freeze_transaction:
            typer.echo(
                f"- board.re_freeze: refreeze={re_freeze_transaction.get('refreeze_required')} "
                f"revalidate={re_freeze_transaction.get('revalidate_required')}"
            )
        acceptance_kit = (payload.get("runtime_projection", {}) if isinstance(payload.get("runtime_projection"), dict) else {}).get("acceptance_kit", {})
        acceptance_kit = acceptance_kit if isinstance(acceptance_kit, dict) else {}
        acceptance_summary = acceptance_kit.get("summary", {}) if isinstance(acceptance_kit.get("summary"), dict) else {}
        if acceptance_summary:
            typer.echo(
                f"- board.acceptance_kit: {acceptance_summary.get('summary') or 'unknown'} "
                f"verdict={acceptance_summary.get('verdict') or 'unknown'}"
            )
            failed_layers = acceptance_summary.get("failed_layers", [])
            if failed_layers:
                typer.echo(f"- board.acceptance_failed_layers: {', '.join(str(item) for item in failed_layers)}")
            for item in acceptance_kit.get("links", []) if isinstance(acceptance_kit.get("links"), list) else []:
                layer = str(item.get("layer") or "")
                href = str(item.get("evidence_ref") or item.get("source_truth_ref") or "")
                if layer and href:
                    typer.echo(f"- board.acceptance_jump[{layer}]: {href}")
        typer.echo(f"- board.active_runs: {board_summary.get('active_runs') or 0}")
        typer.echo(f"- board.active_agents: {board_summary.get('active_agents') or 0}")
        typer.echo(f"- board.ledger_sync: {runtime_ledger.get('status') or 'unknown'}")
        typer.echo(f"- board.sqlite: {runtime_ledger.get('sqlite_status') or 'unknown'}")
        typer.echo(f"- board.pocketbase: {runtime_ledger.get('pocketbase_status') or 'unknown'}")
        if runtime_ledger.get("transaction_id"):
            typer.echo(f"- board.transaction_id: {runtime_ledger.get('transaction_id')}")
        failed_sinks = runtime_ledger.get("failed_sinks") if isinstance(runtime_ledger.get("failed_sinks"), list) else []
        if failed_sinks:
            typer.echo(f"- board.failed_sinks: {', '.join(str(item) for item in failed_sinks)}")
        control_plane = runtime_ledger.get("control_plane", {}) if isinstance(runtime_ledger.get("control_plane"), dict) else {}
        if control_plane:
            typer.echo(f"- board.pocketbase_binary: {control_plane.get('binary_status') or 'unknown'}")
            if control_plane.get("admin_ui"):
                typer.echo(f"- board.pocketbase_admin_ui: {control_plane.get('admin_ui')}")
        typer.echo(f"- board.portfolio_projects: {len(portfolio_projects)}")
        for index, project in enumerate(portfolio_projects[:6], start=1):
            project_stage = canonicalize_lifecycle_stage(project.get("current_stage")) or project.get("current_stage")
            project_next_action = canonicalize_lifecycle_action(project.get("next_action")) or project.get("next_action")
            typer.echo(
                f"- portfolio.{index}: "
                f"{project.get('display_name') or project.get('project_key')} | kind={project.get('project_kind')} | "
                f"stage={project_stage} | debug={project.get('debug_state')} | "
                f"next={project_next_action}"
            )
        typer.echo(f"- team.known_teams: {team_count}")
        typer.echo(f"- gate.terminal_status: {terminal_status}")
        typer.echo(f"- bridge.known_bridges: {bridge_count}")
        typer.echo(f"- test.has_progress: {bool(progress)}")
        typer.echo(f"- release.ready: {release_summary.get('release_ready')}")
        typer.echo(f"- release.gate: {release_summary.get('gate_status')}")
        typer.echo(
            f"- release.qa: {release_summary.get('qa_status')} ({release_summary.get('qa_execution_mode')}, evidence_done={release_summary.get('qa_evidence_done')})"
        )
        if release_summary.get("qa_project_profile_gate_status") and release_summary.get("qa_project_profile_gate_status") != "not_configured":
            typer.echo(
                f"- release.project_gate: {release_summary.get('qa_project_profile_gate_status')} ({release_summary.get('qa_project_profile_id') or '-'})"
            )
        if release_summary.get("exhaustiveness_status") and _release_surface_enabled(root, coverage_version, "v1.3.3"):
            typer.echo(
                f"- release.exhaustiveness: {release_summary.get('exhaustiveness_status')} ({release_summary.get('exhaustiveness_score')})"
            )
        if release_summary.get("release_confidence_min") is not None:
            typer.echo(
                f"- release.confidence: min={release_summary.get('release_confidence_min')} avg={release_summary.get('release_confidence_avg')} review={release_summary.get('review_required_count')} replay={release_summary.get('needs_replay_count')}"
            )
        if release_summary.get("continue_decision"):
            typer.echo(f"- release.continue_decision: {release_summary.get('continue_decision')}")
        lifecycle_hook_advisory = payload.get("lifecycle_hook_advisory", {}) if isinstance(payload.get("lifecycle_hook_advisory"), dict) else {}
        if lifecycle_hook_advisory.get("hook_count"):
            typer.echo(
                f"- hook_advisory: boundary={lifecycle_hook_advisory.get('hook_code') or 'none'} "
                f"status={lifecycle_hook_advisory.get('status') or 'none'} "
                f"support_evidence_only={lifecycle_hook_advisory.get('support_evidence_only')}"
            )
            if lifecycle_hook_advisory.get("recommended_command"):
                typer.echo(f"- hook_advisory.next: {lifecycle_hook_advisory.get('recommended_command')}")
        if release_summary.get("research_projection_present"):
            typer.echo(
                f"- release.research: present sections={','.join(release_summary.get('research_projection_sections') or [])} count={release_summary.get('research_projection_section_count')}"
            )
        if release_summary.get("change_documents_status"):
            typer.echo(
                f"- release.change_documents: {release_summary.get('change_documents_status')} "
                f"feature_count={release_summary.get('change_documents_feature_count')} "
                f"includes_current={release_summary.get('change_documents_includes_current_feature')}"
            )
        coverage_current = release_summary.get("coverage_current") if isinstance(release_summary.get("coverage_current"), dict) else {}
        if coverage_current:
            typer.echo(
                f"- release.coverage_current: {coverage_current.get('executed_scenarios', 0)}/{coverage_current.get('required_scenarios', 0)} ({coverage_current.get('coverage_rate', 0)})"
            )
        typer.echo(
            f"- release.learning: {release_summary.get('main_kpi')}={release_summary.get('main_kpi_score')} keep/review/discard={release_summary.get('decision_keep')}/{release_summary.get('decision_review')}/{release_summary.get('decision_discard')}"
        )
        typer.echo(f"- memory.closure_complete: {memory_metrics.get('closure_complete')}")
        typer.echo(f"- memory.transaction: {memory_transaction.get('status')}")
        typer.echo(f"- memory.writebacks: {memory_metrics.get('writebacks')}")
        typer.echo(f"- memory.recall_injections: {memory_metrics.get('recall_injections')}")
        typer.echo(f"- memory.next_stage: {lifecycle.get('next_stage') or workflow_progress_display.get('next_stage') or canonicalize_lifecycle_stage(workflow_progress.get('next_stage')) or 'none'}")
        if payload.get("implementation_plan", {}).get("plan_id"):
            typer.echo(
                f"- implementation_plan: {payload.get('implementation_plan', {}).get('status')} "
                f"next={payload.get('implementation_plan', {}).get('next_task_id') or 'none'} "
                f"counts={payload.get('implementation_plan', {}).get('counts', {})}"
            )
        implementation_order = payload.get("implementation_order", {}) if isinstance(payload.get("implementation_order"), dict) else {}
        if implementation_order.get("ordered_feature_slugs"):
            typer.echo(
                f"- implementation_order: {', '.join(str(item) for item in implementation_order.get('ordered_feature_slugs', []) if str(item).strip())}"
            )
            waves = implementation_order.get("waves", []) if isinstance(implementation_order.get("waves"), list) else []
            for wave in waves:
                if not isinstance(wave, dict):
                    continue
                feature_slugs = [
                    str(item.get("feature_slug") or "")
                    for item in wave.get("features", [])
                    if isinstance(item, dict) and str(item.get("feature_slug") or "").strip()
                ]
                if feature_slugs:
                    typer.echo(f"- implementation_wave.{wave.get('wave', '')}: {', '.join(feature_slugs)}")
        if target_feature:
            typer.echo(
                f"- requirement_clarity: {payload.get('requirement_clarity', {}).get('status')} "
                f"findings={payload.get('requirement_clarity', {}).get('finding_count')}"
            )
        gap_digest = payload.get("requirement_gap_digest", {}) if isinstance(payload.get("requirement_gap_digest"), dict) else {}
        brainstorm_hint = payload.get("brainstorm_hint", {}) if isinstance(payload.get("brainstorm_hint"), dict) else {}
        if gap_digest.get("human_followup_needed"):
            typer.echo(
                f"- requirement_gap: {gap_digest.get('gap_id') or 'none'} "
                f"type={gap_digest.get('gap_type') or 'none'} "
                f"route={gap_digest.get('recommended_route') or 'none'}"
            )
        if brainstorm_hint.get("recommended_route"):
            typer.echo(
                f"- brainstorm_hint: {brainstorm_hint.get('recommended_mode') or 'none'} "
                f"route={brainstorm_hint.get('recommended_route') or 'none'}"
            )
        supplement_task = payload.get("supplement_task", {}) if isinstance(payload.get("supplement_task"), dict) else {}
        re_freeze_transaction = payload.get("re_freeze_transaction", {}) if isinstance(payload.get("re_freeze_transaction"), dict) else {}
        if supplement_task.get("target_artifact"):
            typer.echo(
                f"- supplement_task: target={supplement_task.get('target_artifact') or 'none'} "
                f"route={supplement_task.get('recommended_route') or 'none'}"
            )
            if supplement_task.get("writeback_target"):
                typer.echo(f"- supplement.writeback: {supplement_task.get('writeback_target')}")
        if re_freeze_transaction:
            typer.echo(
                f"- re_freeze_transaction: refreeze={re_freeze_transaction.get('refreeze_required')} "
                f"revalidate={re_freeze_transaction.get('revalidate_required')}"
            )
        if target_feature and str(payload.get("technical_review", {}).get("status") or "") not in {"", "not_required", "not_applicable"}:
            typer.echo(
                f"- technical_review: {payload.get('technical_review', {}).get('status')} "
                f"review_status={payload.get('technical_review', {}).get('review_status') or 'none'}"
            )
        if target_feature and payload.get("design_review", {}).get("status"):
            typer.echo(
                f"- design_review: {payload.get('design_review', {}).get('status')} "
                f"next={payload.get('design_review', {}).get('latest_next_route') or 'none'}"
            )
        if target_feature and payload.get("learning_governance", {}).get("status"):
            typer.echo(
                f"- learning_governance: {payload.get('learning_governance', {}).get('status')} "
                f"next={payload.get('learning_governance', {}).get('latest_next_route') or 'none'}"
            )
        if target_feature and str(payload.get("semantic", {}).get("status") or "") not in {"", "not_required", "not_applicable"}:
            typer.echo(
                f"- semantic: {payload.get('semantic', {}).get('status')} "
                f"bridge={((payload.get('semantic', {}).get('details', {}) or {}).get('default_design_bridge', {}) or {}).get('skill_id', 'none')}"
            )
        if target_feature and bool(payload.get("change_loop", {}).get("recommended")):
            typer.echo(
                f"- change_loop: route={payload.get('change_loop', {}).get('route') or 'beacon change'} "
                f"intent={payload.get('change_loop', {}).get('intent') or '-'}"
            )
        if payload.get("release_binding"):
            typer.echo(
                f"- release.binding: {payload.get('release_binding', {}).get('status') or 'unknown'} "
                f"current={payload.get('release_binding', {}).get('gate_bound_to_latest_revision')}"
            )
        acceptance_kit = (payload.get("runtime_projection", {}) if isinstance(payload.get("runtime_projection"), dict) else {}).get("acceptance_kit", {})
        acceptance_kit = acceptance_kit if isinstance(acceptance_kit, dict) else {}
        acceptance_summary = acceptance_kit.get("summary", {}) if isinstance(acceptance_kit.get("summary"), dict) else {}
        if acceptance_summary:
            typer.echo(
                f"- acceptance_kit: {acceptance_summary.get('summary') or 'unknown'} "
                f"verdict={acceptance_summary.get('verdict') or 'unknown'}"
            )
            if acceptance_summary.get("failed_layers"):
                typer.echo(f"- acceptance_failed_layers: {', '.join(str(item) for item in acceptance_summary.get('failed_layers', []))}")
        if payload.get("revision", {}).get("release_delivery_type"):
            typer.echo(f"- revision.delivery_type: {payload.get('revision', {}).get('release_delivery_type')}")
        typer.echo(
            f"- control.failure_streak: {resume_contract.get('failure_streak')}"
        )
        typer.echo(
            f"- control.escalation_level: {resume_contract.get('escalation_level')}"
        )
        decision_summary = keep_discard_engine.get("decision_summary", {}) if isinstance(keep_discard_engine, dict) else {}
        if decision_summary:
            typer.echo(f"- learning.keep: {decision_summary.get('keep')}")
            typer.echo(f"- learning.review: {decision_summary.get('review')}")
            typer.echo(f"- learning.discard: {decision_summary.get('discard')}")
        typer.echo(f"- coverage.story: {coverage_metrics.get('implemented_story')}/{coverage_metrics.get('planned_story')}")
        typer.echo(f"- coverage.ac: {coverage_metrics.get('tested_ac')}/{coverage_metrics.get('total_ac')}")
        typer.echo(f"- coverage.tc: {coverage_metrics.get('executed_tc')}/{coverage_metrics.get('total_tc')}")
        typer.echo(f"- coverage.full: {coverage_metrics.get('full_coverage')}")
        typer.echo(f"- version.docs: {payload.get('version_context', {}).get('docs_version')}")
        typer.echo(f"- version.runtime: {payload.get('version_context', {}).get('runtime_version')}")
        if payload.get("version_context", {}).get("context_docs_version"):
            typer.echo(f"- version.context_docs: {payload.get('version_context', {}).get('context_docs_version')}")
        if payload.get("version_context", {}).get("context_managed_version"):
            typer.echo(f"- version.context_runtime: {payload.get('version_context', {}).get('context_managed_version')}")
        if payload.get("scores"):
            typer.echo(f"- score.test: {payload.get('scores', {}).get('test_score')}")
            typer.echo(f"- score.closure: {payload.get('scores', {}).get('closure_score')}")
            typer.echo(f"- score.readiness: {payload.get('scores', {}).get('readiness_score')}")
            typer.echo(f"- score.quality: {payload.get('scores', {}).get('quality_score')}")
        typer.echo(f"- source_of_truth.root: {source_of_truth.get('root')}")
        if source_of_truth.get("machine_root"):
            typer.echo(f"- source_of_truth.machine_root: {source_of_truth.get('machine_root')}")
        typer.echo(
            f"- source_of_truth.version_line_package_closure: {source_of_truth.get('formal_package_closure')}"
        )
        if requirement_package_gate.get("enabled"):
            typer.echo(
                f"- source_of_truth.requirement_package_gate: {source_of_truth.get('requirement_package_gate')}"
            )
            failure_categories = source_of_truth.get("requirement_package_failure_categories", [])
            if failure_categories:
                typer.echo(
                    f"- source_of_truth.requirement_package_failures: {', '.join(str(item) for item in failure_categories)}"
                )
            if source_of_truth.get("requirement_package_recommended_command"):
                typer.echo(
                    f"- source_of_truth.requirement_package_next: {source_of_truth.get('requirement_package_recommended_command')}"
                )
        execution_surface = payload.get("execution_surface", {}) if isinstance(payload.get("execution_surface"), dict) else {}
        if execution_surface:
            typer.echo(f"- execution.host_runtime: {execution_surface.get('host_runtime') or 'N/A'}")
            typer.echo(f"- execution.subagent_runtime: {execution_surface.get('subagent_runtime_status') or 'N/A'}")
            typer.echo(f"- execution.subagent_delegation: {execution_surface.get('subagent_delegation_status') or 'N/A'}")
            typer.echo(f"- execution.ralph_phase: {execution_surface.get('ralph_phase') or 'N/A'}")
            typer.echo(f"- execution.archive_status: {execution_surface.get('archive_status') or 'N/A'}")
            typer.echo(f"- execution.freeze_status: {execution_surface.get('freeze_status') or 'N/A'}")
            typer.echo(f"- execution.team_phase: {execution_surface.get('team_phase') or 'N/A'}")
            typer.echo(f"- execution.host_prompt_trace_ref: {execution_surface.get('host_prompt_trace_ref') or 'N/A'}")
            typer.echo(f"- execution.ralph_stop_state: {execution_surface.get('ralph_stop_state') or 'N/A'}")
            typer.echo(f"- execution.ralph_next_action: {execution_surface.get('ralph_next_action') or 'N/A'}")
            typer.echo(f"- execution.ralph_round_count: {execution_surface.get('ralph_round_count') or 0}")
            typer.echo(f"- execution.ralph_last_round_ref: {execution_surface.get('ralph_last_round_ref') or 'N/A'}")
            typer.echo(f"- execution.ralph_failure_streak: {execution_surface.get('ralph_failure_streak') or 0}")
            typer.echo(f"- execution.ralph_no_delta_streak: {execution_surface.get('ralph_no_delta_streak') or 0}")
            typer.echo(f"- execution.qa_mode: {execution_surface.get('qa_execution_mode') or 'N/A'}")
            typer.echo(f"- execution.qa_session: {execution_surface.get('qa_current_session_id') or 'N/A'}")
            typer.echo(f"- execution.qa_runner: {execution_surface.get('qa_runner_type') or 'N/A'}")
        implement_mode = payload.get("implement_mode_recommendation", {}) if isinstance(payload.get("implement_mode_recommendation"), dict) else {}
        if implement_mode:
            typer.echo(f"- implement_mode.public_skill: {implement_mode.get('public_skill')}")
            typer.echo(f"- implement_mode.recommended: {implement_mode.get('recommended_mode')}")
            typer.echo(f"- implement_mode.reason: {implement_mode.get('reason')}")
            typer.echo(f"- implement_mode.command: {implement_mode.get('canonical_command')}")
            typer.echo(f"- implement_mode.playbook: {implement_mode.get('playbook_ref')}")
        minimal_hud = payload.get("minimal_hud", {}) if isinstance(payload.get("minimal_hud"), dict) else {}
        hud_lines = minimal_hud.get("lines", []) if isinstance(minimal_hud.get("lines"), list) else []
        if hud_lines:
            typer.echo(f"- hud.scenario: {minimal_hud.get('scenario') or 'N/A'}")
            for index, line in enumerate(hud_lines, start=1):
                typer.echo(f"- hud.line{index}: {line}")
        if qa_status:
            typer.echo(f"- qa.status: {qa_status.get('status')}")
            typer.echo(f"- qa.evidence_done: {qa_status.get('evidence_done')}")
        lifecycle_hook_advisory = payload.get("lifecycle_hook_advisory", {}) if isinstance(payload.get("lifecycle_hook_advisory"), dict) else {}
        if lifecycle_hook_advisory.get("hook_count"):
            typer.echo(
                f"- hook_advisory.boundary: {lifecycle_hook_advisory.get('hook_code') or 'none'} "
                f"status={lifecycle_hook_advisory.get('status') or 'none'}"
            )
            if lifecycle_hook_advisory.get("recommended_command"):
                typer.echo(f"- hook_advisory.command: {lifecycle_hook_advisory.get('recommended_command')}")
        if workflow_progress.get("stages", {}).get("prototype"):
            typer.echo(f"- workflow.prototype: {workflow_progress.get('stages', {}).get('prototype', {}).get('status')}")
        if verbose:
            implementation_plan_view = payload.get("implementation_plan", {}) if isinstance(payload.get("implementation_plan"), dict) else {}
            if implementation_plan_view.get("task_ledger_path"):
                typer.echo(f"- implementation.task_ledger: {implementation_plan_view.get('task_ledger_path')}")
            if implementation_plan_view.get("next_task_title"):
                typer.echo(f"- implementation.next_task_title: {implementation_plan_view.get('next_task_title')}")
            blocked_task_titles = implementation_plan_view.get("blocked_task_titles", [])
            if isinstance(blocked_task_titles, list) and blocked_task_titles:
                typer.echo(f"- implementation.blocked_task_titles: {', '.join(str(item) for item in blocked_task_titles)}")
            typer.echo(f"- run.latest_run_id: {latest or 'none'}")
            typer.echo(f"- run.selected_run_id: {resolved_run_id or 'none'}")
            typer.echo(f"- memory.missing_closure_stages: {memory_metrics.get('missing_closure_stages')}")
            typer.echo(f"- workflow.run_id: {workflow_progress.get('run_id') or 'none'}")
            typer.echo(f"- workflow.version: {workflow_progress.get('version') or 'none'}")
            typer.echo(f"- workflow.feature: {workflow_progress.get('feature') or 'none'}")
            typer.echo(f"- version.docs_source: {payload.get('version_context', {}).get('docs_version_source') or 'none'}")
            typer.echo(f"- version.runtime_source: {payload.get('version_context', {}).get('runtime_version_source') or 'none'}")
            typer.echo(f"- revision.id: {payload.get('revision', {}).get('revision_id') or 'none'}")
            typer.echo(f"- revision.doc_status: {payload.get('revision', {}).get('doc_status') or 'none'}")
            typer.echo(f"- revision.delivery_status: {payload.get('revision', {}).get('delivery_status') or 'none'}")
            typer.echo(f"- next_step.action: {payload.get('next_step', {}).get('action') or 'none'}")
    else:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


@app.callback(invoke_without_command=True)
def status_callback(
    ctx: typer.Context,
    board: bool = typer.Option(False, "--board", "-b", help="Render human board"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version filter"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature filter"),
    run_id: str = typer.Option("", "--run-id", help="Run id filter"),
    change_intent: str = typer.Option("", "--change-intent", help="Optional user change-intent text for post-freeze routing"),
):
    """Show current status (PTK flat syntax compatibility)."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(
            code=_status_impl(
                board=board,
                verbose=verbose,
                project_root=project_root,
                version=version,
                feature=feature,
                run_id=run_id,
                change_intent=change_intent,
            )
        )


@app.command("show-status")
def show_status(
    board: bool = typer.Option(False, "--board", "-b", help="Render human board"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version filter"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature filter"),
    run_id: str = typer.Option("", "--run-id", help="Run id filter"),
    change_intent: str = typer.Option("", "--change-intent", help="Optional user change-intent text for post-freeze routing"),
):
    """Show current workflow status."""
    raise typer.Exit(
        code=_status_impl(
            board=board,
            verbose=verbose,
            project_root=project_root,
            version=version,
            feature=feature,
            run_id=run_id,
            change_intent=change_intent,
        )
    )


@app.command("loop-budget")
def loop_budget(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Version filter"),
    date: str = typer.Option("", "--date", help="UTC date YYYY-MM-DD"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Show loop token budget totals, caps, and pause state."""
    from beacon.utils.loop_budget import build_loop_budget_status

    root = (Path(project_root) if project_root else Path.cwd()).expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    payload = build_loop_budget_status(root, version=resolved_version, date=date or None)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Loop Budget")
        typer.echo(f"status: {payload.get('status')}")
        typer.echo(f"date: {payload.get('date')}")
        typer.echo(f"reason_code: {payload.get('reason_code') or 'none'}")
        typer.echo(f"project_total: {payload.get('totals', {}).get('project_total', 0)}")
    raise typer.Exit(code=0)


@app.command("standard-execution-precheck")
def standard_execution_precheck(
    feature: str = typer.Argument(..., help="Feature name or slug"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target docs version"),
    run_id: str = typer.Option("", "--run-id", help="Loop-goal run id for artifact naming"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    record: bool = typer.Option(
        False,
        "--record",
        help="Also record the CLI bundle into loop-goal state when --run-id is provided",
    ),
):
    """Run CLI-owned Standard Execution Flow verification bundle (AC-025)."""
    from beacon.utils.loop_goal_state import record_standard_execution_precheck
    from beacon.utils.standard_execution_precheck import run_standard_execution_precheck
    from beacon.utils.versioning import resolve_target_version

    root = (Path(project_root) if project_root else Path.cwd()).expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    payload = run_standard_execution_precheck(
        root,
        version=resolved_version,
        feature=feature,
        run_id=run_id or "",
    )
    if record and run_id:
        recorded = record_standard_execution_precheck(
            root,
            run_id=run_id,
            precheck={
                **payload,
                "cli_owned": True,
                "verification_bundle_ref": payload.get("verification_bundle_ref"),
                "workspace_admission_ref": payload.get("workspace_admission_ref"),
                "verification_bundle": payload.get("verification_bundle"),
            },
        )
        payload["loop_goal_record"] = recorded
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Standard Execution Precheck")
        typer.echo(f"status: {payload.get('status')}")
        typer.echo(f"reason_code: {payload.get('reason_code') or 'none'}")
        typer.echo(f"artifact: {payload.get('verification_bundle_ref')}")
        typer.echo(f"baseline: {payload.get('truth_baseline_commit') or 'none'}")
    raise typer.Exit(code=0 if payload.get("status") == "pass" else 2)


@app.command("loop-goal")
def loop_goal(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    run_id: str = typer.Option("", "--run-id", help="Loop-goal run id; omit to list all runs"),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Return actionable current_stage + next_skill for same-session continue (AC-029)",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
):
    """Show loop-goal orchestrator run status (current stage, next skill, outputs)."""
    from beacon.utils.loop_goal_state import build_resume, build_status

    root = (Path(project_root) if project_root else Path.cwd()).expanduser().resolve()
    if resume:
        payload = build_resume(root, run_id=run_id or "")
    else:
        payload = build_status(root, run_id=run_id or "")
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Loop Goal" + (" Resume" if resume else ""))
        typer.echo(f"status: {payload.get('status')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
        if payload.get("run_id"):
            typer.echo(f"run_id: {payload.get('run_id')}")
            if payload.get("feature") is not None:
                typer.echo(f"feature: {payload.get('feature')}")
            if payload.get("current_stage") is not None:
                typer.echo(f"current_stage: {payload.get('current_stage')}")
            typer.echo(f"next_skill: {payload.get('next_skill') or 'none'}")
            if resume:
                typer.echo(f"resume_action: {payload.get('resume_action') or 'none'}")
            if payload.get("repair_loop_count") is not None:
                typer.echo(f"repair_loop_count: {payload.get('repair_loop_count')}")
        elif not resume:
            typer.echo(f"run_count: {payload.get('run_count', 0)}")
            for run in payload.get("runs", []):
                typer.echo(
                    f"  {run.get('run_id')} [{run.get('feature')}] "
                    f"stage={run.get('current_stage')} next={run.get('next_skill') or 'none'}"
                )
    raise typer.Exit(code=0 if (not resume or payload.get("status") == "pass") else 2)


if __name__ == "__main__":
    app()
