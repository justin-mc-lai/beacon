"""Beacon workflow command - Full product workflow"""
from __future__ import annotations

import hashlib
import json
import typer
from typing import Any, Optional
from pathlib import Path
import subprocess
import sys
import os
import signal

from beacon import __toolkit_version__
from beacon.utils.artifact_paths import (
    execution_file_output,
    human_execution_dir,
    qa_matrix_candidates,
    uses_machine_surface,
)
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.control_plane import (
    build_resume_contract,
    exhaustion_for_run,
    record_stage_failure,
    record_stage_success,
)
from beacon.utils.debug_feedback import (
    append_debug_event_memory,
    append_debug_feedback_event,
    is_debug_mode_enabled,
    load_debug_mode_state,
)
from beacon.utils.git_alignment import collect_git_alignment
from beacon.utils.llm_loop import build_next_stage_trace, merge_token_usage
from beacon.utils.memory import append_memory_entry
from beacon.utils.implement_adapters import load_beacon_config_file, project_config_path
from beacon.utils.qa9 import normalize_qa_type, parse_qa_types
from beacon.utils.runtime import (
    append_jsonl,
    generate_run_id,
    load_run_state,
    now_iso,
    save_run_state,
    write_json,
)
from beacon.utils.versioning import resolve_operational_docs_version, resolve_target_version
from beacon.utils.v110_baseline import record_baseline_snapshot
from beacon.utils.workflow_memory import (
    append_lifecycle_event,
    compute_workflow_progress,
    normalize_workflow_stage,
    record_stage_writeback,
    resolve_workflow_run_id,
    write_stage_context,
)

app = typer.Typer(name="workflow", help="Full product workflow")

WORKFLOW_STAGES = [
    ("prd", "Generate PRD from requirement truth", "beacon prd create"),
    ("user-story", "Generate user stories from PRD", "beacon user-story create"),
    ("test-case", "Generate executable test matrix", "beacon test-case create"),
    ("prototype", "Generate static UI prototype", "beacon prototype create"),
    ("implement", "Execute implementation against frozen materials", "beacon implement dev-run"),
    ("qa", "Run QA verification and evidence closure", "beacon qa run"),
    ("release", "Run release readiness and closure check", "beacon gate check release"),
]


def _workflow_stages(*, prototype_enabled: bool) -> list[tuple[str, str, str]]:
    if prototype_enabled:
        return list(WORKFLOW_STAGES)
    return [stage for stage in WORKFLOW_STAGES if stage[0] != "prototype"]



def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

INTERACTIVE_ACTIONS: dict[str, str] = {
    "1": "single-step",
    "2": "auto-run",
    "3": "show-blockers",
    "4": "feedback-apply",
    "5": "pause",
    "6": "abort",
}
EXECUTION_ACTIONS = {"single-step", "auto-run", "feedback-apply"}


def _bridge_execution_dir(project_root: Path, run_id: str) -> Path:
    return project_root / ".beacon" / "bridge" / run_id


def _record_debug_feedback(
    *,
    project_root: Path,
    source: str,
    goal: str,
    intent: str,
    confidence: float = 1.0,
    boundary_state: str = "in_scope",
    block_reason: str = "",
    recommended_command: str = "",
    executed: bool = False,
    exit_code: int | None = None,
    note: str = "",
    run_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    if not is_debug_mode_enabled(project_root):
        return
    target_run_id, out_path, payload = append_debug_feedback_event(
        project_root,
        source=source,
        goal=goal,
        intent=intent,
        confidence=confidence,
        boundary_state=boundary_state,
        block_reason=block_reason,
        recommended_command=recommended_command,
        executed=executed,
        exit_code=exit_code,
        note=note,
        run_id=run_id,
        extra=extra,
    )
    append_debug_event_memory(
        project_root,
        run_id=target_run_id,
        event_payload=payload,
        evidence_path=out_path,
        source=source,
    )


def _print_next_step_selector(project_root: Path, version: str, run_id: str, feature: str) -> None:
    """Show selectable next-step prompts after workflow terminal states."""
    typer.echo("\n" + "=" * 50)
    typer.echo("NEXT STEP SELECTOR (choose one)")
    typer.echo("=" * 50)
    typer.echo("1) OMC 路径（编排/评审）")
    typer.echo(
        f'   omc run --project-root "{project_root}" '
        f'--task "继续推进 {feature}（version={version}, run_id={run_id}）"'
    )
    typer.echo("2) OMX 路径（长任务执行）")
    typer.echo(
        f'   omx exec --full-auto --cd "{project_root}" --skip-git-repo-check '
        f'"执行 {feature} 的下一轮迭代（version={version}, run_id={run_id}）"'
    )
    typer.echo("3) Beacon Team 协作模式")
    typer.echo(
        f'   beacon team start "{feature} 交付协作" --project "{project_root}"'
    )
    typer.echo("（如需继续当前主流程）")
    typer.echo(
        f'   beacon workflow continue --project "{project_root}" --version "{version}" --run-id "{run_id}" --auto'
    )


def _record_v110_baseline(
    *,
    project_root: Path,
    run_id: str,
    version: str,
    feature: str,
    workflow_status: str,
) -> None:
    baseline = record_baseline_snapshot(
        project_root,
        run_id=run_id,
        version=version,
        feature=feature,
        workflow_status=workflow_status,
    )
    refs = [
        baseline.get("fingerprint_path", ""),
        baseline.get("baseline_path", ""),
        baseline.get("change_impact_path", ""),
    ]
    refs = [x for x in refs if x]
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage="workflow",
        event="baseline_snapshot_recorded",
        source="workflow.v110.baseline",
        evidence_ref=refs,
        details={
            "baseline_id": str((baseline.get("baseline") or {}).get("baseline_id", "")),
            "changed_layers": ((baseline.get("baseline") or {}).get("delta_summary") or {}).get("changed_layers", []),
        },
    )
    append_memory_entry(
        project_root=project_root,
        mem_type="insight",
        text=f"[workflow.v110.baseline] run={run_id} status={workflow_status}",
        source_session_id=run_id,
        source="workflow.v110.baseline",
        evidence_ref=refs,
        confidence=0.8,
        tags=["v110", "baseline", workflow_status],
    )


def _execute_bridge_actions(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    bridge_targets: str,
    bridge_timeout: int,
) -> dict[str, Any]:
    targets = [x.strip().lower() for x in str(bridge_targets or "").split(",") if x.strip()]
    if not targets:
        targets = ["omc", "omx", "team"]

    actions: list[dict[str, Any]] = []
    for target in targets:
        if target == "omc":
            cmd = [
                "omc",
                "run",
                "--project-root",
                str(project_root),
                "--task",
                f"继续推进 {feature}（version={version}, run_id={run_id}）",
            ]
        elif target == "omx":
            cmd = [
                "omx",
                "run",
                "--project-root",
                str(project_root),
                "--task",
                f"执行 {feature} 的下一轮迭代（version={version}, run_id={run_id}）",
            ]
        elif target == "team":
            cmd = [
                sys.executable,
                "-m",
                "beacon.main",
                "team",
                "start",
                f"{feature} 交付协作",
                "--runtime",
                "file",
                "--project",
                str(project_root),
            ]
        else:
            continue

        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=max(10, int(bridge_timeout)),
            )
            actions.append(
                {
                    "target": target,
                    "command": cmd,
                    "exit_code": int(result.returncode),
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            )
        except FileNotFoundError as exc:
            actions.append(
                {
                    "target": target,
                    "command": cmd,
                    "exit_code": 127,
                    "stdout": "",
                    "stderr": str(exc),
                }
            )
        except Exception as exc:  # noqa: BLE001
            actions.append(
                {
                    "target": target,
                    "command": cmd,
                    "exit_code": 1,
                    "stdout": "",
                    "stderr": f"{type(exc).__name__}: {exc}",
                }
            )

    success_count = len([item for item in actions if int(item.get("exit_code", 1)) == 0])
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "version": version,
        "feature": feature,
        "targets": targets,
        "executed_at": now_iso(),
        "results": actions,
        "summary": {
            "executed": len(actions),
            "success": success_count,
            "failed": len(actions) - success_count,
        },
    }
    out_dir = _bridge_execution_dir(project_root, run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "bridge-execution.json"
    write_json(out_file, payload)
    rel = str(out_file.relative_to(project_root))

    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[workflow.bridge] run={run_id} executed={len(actions)} success={success_count}",
        source_session_id=run_id,
        source="workflow.bridge.execute",
        evidence_ref=[rel],
        confidence=0.76,
        tags=["bridge", "workflow", "omc-omx-team"],
    )
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage="workflow",
        event="bridge_execution_recorded",
        source="workflow.bridge.execute",
        evidence_ref=[rel],
        details=payload["summary"],
    )
    _record_debug_feedback(
        project_root=project_root,
        source="workflow.bridge.execute",
        goal=f"{feature} bridge execute",
        intent="workflow",
        confidence=0.9,
        boundary_state="in_scope",
        recommended_command="bridge execution via workflow",
        executed=True,
        exit_code=0 if success_count == len(actions) else 1,
        note="bridge-executed",
        run_id=run_id,
        extra={"targets": targets, "summary": payload["summary"]},
    )
    return payload


def _append_llm_trace(state: dict[str, Any], trace: dict[str, Any]) -> None:
    prompts = state.get("llm_prompts")
    if not isinstance(prompts, list):
        prompts = []
    prompts.append(trace)
    state["llm_prompts"] = prompts
    state["token_usage"] = merge_token_usage(state.get("token_usage"), trace)


def _raw_command_log_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "raw-command-log.jsonl"


def _log_raw_command(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    command: str,
    exit_code: int,
) -> None:
    append_jsonl(
        _raw_command_log_path(project_root),
        {
            "ts": now_iso(),
            "run_id": run_id,
            "stage": stage,
            "command": command,
            "exit_code": exit_code,
        },
    )


def _update_evidence_manifest(
    project_root: Path,
    evidence_refs: list[str],
    *,
    run_id: str | None = None,
    version: str | None = None,
) -> None:
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    payload = {}
    if manifest_path.exists():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            payload = {}
    if not isinstance(payload, dict):
        payload = {}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        entries = []
    by_path: dict[str, dict[str, Any]] = {
        str(item.get("path")): item
        for item in entries
        if isinstance(item, dict) and str(item.get("path", "")).strip()
    }
    by_path = {
        ref_path: item
        for ref_path, item in by_path.items()
        if (project_root / ref_path).exists() and (project_root / ref_path).is_file()
    }
    for ref in evidence_refs:
        ref_path = str(ref or "").strip()
        if not ref_path:
            continue
        full = project_root / ref_path
        if not full.exists() or not full.is_file():
            continue
        by_path[ref_path] = {
            "path": ref_path,
            "sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
            "updated_at": now_iso(),
        }
    next_run_id = str(run_id or payload.get("run_id") or "").strip()
    next_version = str(version or payload.get("version") or "").strip()
    existing_version = str(payload.get("version") or "").strip()
    if existing_version and next_version and _parse_semver_tuple(existing_version) > _parse_semver_tuple(next_version):
        next_version = existing_version
        next_run_id = str(payload.get("run_id") or "").strip() or next_run_id
    existing_run_id = str(payload.get("run_id") or "").strip()
    if existing_version == next_version and existing_run_id.startswith("run-v") and existing_run_id.endswith("release"):
        next_run_id = existing_run_id
    output_payload: dict[str, Any] = {
        "entries": list(by_path.values()),
        "updated_at": now_iso(),
    }
    if next_run_id:
        output_payload["run_id"] = next_run_id
    if next_version:
        output_payload["version"] = next_version
    write_json(manifest_path, output_payload)


def _execution_roots(project_root: Path, version: str) -> list[Path]:
    return [project_root / "docs" / "beacon" / version / "execution"]


def _git_metadata(project_root: Path, version: str) -> dict[str, Any]:
    return collect_git_alignment(project_root, version, allow_tag=True, require_exact_branch=False)


def _existing_research_docs(project_root: Path, version: str) -> list[str]:
    research_dir = project_root / "docs" / "beacon" / version / "research"
    if not research_dir.exists():
        return []
    return sorted(str(path.relative_to(project_root)) for path in research_dir.glob("*.md") if path.is_file())


def _main_chain_refs(project_root: Path, version: str, feature: str) -> list[str]:
    slug = _slug(feature)
    refs = [
        project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md",
        project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.md",
        qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")[0],
        qa_matrix_candidates(project_root, version, slug, "qa9-matrix")[0],
    ]
    return [str(path.relative_to(project_root)) for path in refs if path.exists()]


def _load_change_impact_state(project_root: Path, run_id: str) -> dict[str, Any]:
    return _load_json_dict(project_root / ".beacon" / "state" / "change-impact" / f"{run_id}.json")


def _build_execution_config_payload(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    workflow_status: str,
) -> dict[str, Any]:
    git_meta = _git_metadata(project_root, version)
    return {
        "schema_version": "1.0",
        "version": version,
        "feature": feature,
        "run_id": run_id,
        "generated_at": now_iso(),
        "status": "completed" if workflow_status == "completed" else "draft",
        "strict_mode": True,
        "source_of_truth_root": f"docs/beacon/{version}",
        "resolved_project": {
            "workspace_root": str(project_root.parent),
            "project_name": project_root.name,
            "project_root": str(project_root),
            "resolved_by": "cli_or_cwd",
            "resolution_order": ["cli", "env", "cwd", "default"],
        },
        "docs": {
            "source_root": f"docs/beacon/{version}",
            "write_mode": "source_only",
        },
        "implementation": {
            "root": str(project_root),
            "include_paths": ["beacon", "tests"],
            "exclude_paths": ["dist", "node_modules", ".beacon"],
        },
        "source_info": {
            "enabled": True,
            "output": str(execution_file_output(project_root, version, "source.json").relative_to(project_root)),
            "include_git": True,
            "fields": [
                "project_name",
                "project_root",
                "workspace_root",
                "repo_url",
                "branch",
                "commit",
                "tag",
                "run_id",
                "version",
                "timestamp",
            ],
        },
        "git": {
            "version_policy": "strict",
            "version_ref": version,
            "allowed_refs": git_meta["allowed_refs"],
            "enforce_branch_prefix": git_meta["enforce_branch_prefix"],
            "base_branch": git_meta["base_branch"],
            "target_branch": git_meta["target_branch"],
            "current_branch": git_meta["current_branch"],
            "current_commit": git_meta["current_commit"],
            "current_tag": git_meta["current_tag"],
        },
        "research": {
            "root": f"docs/beacon/{version}/research",
            "sync_to_compat": False,
            "allowed_types": ["brainstorm", "analysis", "research", "architecture", "compare", "convergence"],
            "convergence_rule": "research -> user-story / prd -> test-case",
        },
        "delivery": {
            "manifest_output": str(execution_file_output(project_root, version, "delivery-manifest.json").relative_to(project_root)),
            "change_impact_output": str(execution_file_output(project_root, version, "change-impact.json").relative_to(project_root)),
            "boundaries_output": f"docs/beacon/{version}/execution/boundaries.md",
            "config_output": str(execution_file_output(project_root, version, "config.json").relative_to(project_root)),
            "source_output": str(execution_file_output(project_root, version, "source.json").relative_to(project_root)),
            "git_alignment_output": str(execution_file_output(project_root, version, "git-alignment.json").relative_to(project_root)),
            "terminal_output": str(execution_file_output(project_root, version, "terminal.json").relative_to(project_root)),
        },
        "notes": [
            "Execution config snapshot generated by workflow.",
            f"Runtime toolkit version: {__toolkit_version__}",
            f"Workflow status snapshot: {workflow_status}",
        ],
    }


def _build_execution_source_payload(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    workflow_status: str,
) -> dict[str, Any]:
    git_meta = _git_metadata(project_root, version)
    return {
        "schema_version": "1.0",
        "version": version,
        "feature": feature,
        "run_id": run_id,
        "generated_at": now_iso(),
        "status": "completed" if workflow_status == "completed" else "draft",
        "source_of_truth": True,
        "source_of_truth_root": f"docs/beacon/{version}",
        "project_name": project_root.name,
        "project_root": str(project_root),
        "workspace_root": str(project_root.parent),
        "repo_url": git_meta["repo_url"],
        "branch": git_meta["current_branch"],
        "commit": git_meta["current_commit"],
        "tag": git_meta["current_tag"],
        "timestamp": now_iso(),
        "runtime": {
            "active_skill_path": str(project_root),
            "toolkit_version": __toolkit_version__,
            "cli_entry": "python -m beacon.main",
        },
        "inputs": {
            "research_docs": _existing_research_docs(project_root, version),
            "main_chain_docs": _main_chain_refs(project_root, version, feature),
        },
        "notes": [
            "Source metadata is intended for execution traceability and delivery audit.",
            "Research artifacts are inputs; user-story/prd/test-case are the workflow main chain.",
        ],
    }


def _build_execution_git_alignment_payload(project_root: Path, version: str, run_id: str, feature: str) -> dict[str, Any]:
    git_meta = _git_metadata(project_root, version)
    return {
        "schema_version": "1.0",
        "version": version,
        "feature": feature,
        "run_id": run_id,
        "generated_at": now_iso(),
        "status": "pass" if not git_meta["blocked"] else "warn",
        "strict_required": True,
        "repo_url": git_meta["repo_url"],
        "version_ref": git_meta["version_ref"],
        "allowed_refs": git_meta["allowed_refs"],
        "enforce_branch_prefix": git_meta["enforce_branch_prefix"],
        "git_refs": {
            "base_branch": git_meta["base_branch"],
            "target_branch": git_meta["target_branch"],
            "current_branch": git_meta["current_branch"],
            "commit": git_meta["current_commit"],
            "tag": git_meta["current_tag"],
            "worktree_path": git_meta["worktree_path"],
        },
        "alignment": {
            "branch_matches_target": git_meta["branch_matches_target"],
            "branch_has_required_prefix": git_meta["branch_has_required_prefix"],
            "tag_matches_version": git_meta["tag_matches_version"],
            "version_ref_satisfied": git_meta["version_ref_satisfied"],
        },
        "reason_codes": git_meta["reason_codes"],
        "blocked": git_meta["blocked"],
        "notes": [
            "Git alignment is validated against target branch or exact version tag.",
            "This artifact is intended for doctor verify-git-alignment and delivery gate checks.",
        ],
    }


def _build_execution_change_impact_payload(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    workflow_status: str,
) -> dict[str, Any]:
    base = _load_change_impact_state(project_root, run_id)
    changed_layers = base.get("changed_layers") if isinstance(base.get("changed_layers"), list) else []
    tasks = base.get("tasks") if isinstance(base.get("tasks"), list) else []
    completion_refs = {
        "regenerate-user_story": project_root / "docs" / "beacon" / version / "user-story" / f"{_slug(feature)}.md",
        "regenerate-prd": project_root / "docs" / "beacon" / version / "prd" / f"{_slug(feature)}.md",
        "regenerate-test_case": project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{_slug(feature)}.md",
    }
    for item in tasks:
        if not isinstance(item, dict):
            continue
        task_name = str(item.get("task", "")).strip()
        evidence_path = completion_refs.get(task_name)
        if not evidence_path or not evidence_path.exists():
            continue
        if str(item.get("status", "pending")).strip().lower() == "completed":
            continue
        item["status"] = "completed"
        item["owner"] = project_root.name
        item["evidence"] = str(evidence_path.relative_to(project_root))
    task_names = {str(item.get("task", "")) for item in tasks if isinstance(item, dict)}
    for task_name, evidence in (
        ("publish-config-draft", str(execution_file_output(project_root, version, "config.json").relative_to(project_root))),
        ("publish-source-draft", str(execution_file_output(project_root, version, "source.json").relative_to(project_root))),
        ("publish-git-alignment-draft", str(execution_file_output(project_root, version, "git-alignment.json").relative_to(project_root))),
    ):
        if task_name not in task_names:
            tasks.append(
                {
                    "task": task_name,
                    "status": "completed",
                    "owner": project_root.name,
                    "evidence": evidence,
                }
            )
    research_converged = bool(_existing_research_docs(project_root, version))
    main_chain_refs = _main_chain_refs(project_root, version, feature)
    main_chain_converged = len(main_chain_refs) >= 5
    pending_tasks = [
        str(item.get("task", ""))
        for item in tasks
        if isinstance(item, dict) and str(item.get("status", "pending")).strip().lower() != "completed"
    ]
    doc_chain_update_required = bool(pending_tasks) if tasks else bool(base.get("doc_chain_update_required", bool(changed_layers)))
    return {
        "schema_version": "1.0",
        "version": version,
        "feature": feature,
        "run_id": run_id,
        "generated_at": now_iso(),
        "baseline_run_id": str(base.get("run_id", "") or run_id),
        "affected_projects": [project_root.name],
        "doc_chain_update_required": doc_chain_update_required,
        "changed_layers": changed_layers or ["research", "user-story", "prd", "test-case", "execution"],
        "tasks": tasks,
        "research_converged": research_converged,
        "main_chain_converged": main_chain_converged,
        "delivery_manifest_ready": True,
        "full_delivery_closed": workflow_status == "completed" and not pending_tasks,
        "pending_blockers": pending_tasks,
        "notes": [
            "Change impact is derived from baseline snapshots and enriched with delivery draft tasks.",
            "Full closure still depends on implementation / verify / gate completion.",
        ],
    }


def _build_execution_delivery_manifest_payload(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    workflow_status: str,
    change_impact: dict[str, Any],
    git_alignment: dict[str, Any],
) -> dict[str, Any]:
    source_docs = _existing_research_docs(project_root, version)
    main_chain_docs = _main_chain_refs(project_root, version, feature)
    deliverables = [
        *({"type": "research", "path": ref, "status": "completed"} for ref in source_docs),
        *(
            {
                "type": "user-story" if "/user-story/" in ref else "prd" if "/prd/" in ref else "test-case" if ref.endswith(".md") else "ac-matrix" if ref.endswith(".ac-test-matrix.json") else "qa9-matrix",
                "path": ref,
                "status": "completed",
            }
            for ref in main_chain_docs
        ),
        {"type": "boundaries", "path": f"docs/beacon/{version}/execution/boundaries.md", "status": "completed"},
        {"type": "delivery-manifest", "path": str(execution_file_output(project_root, version, "delivery-manifest.json").relative_to(project_root)), "status": "completed"},
        {"type": "change-impact", "path": str(execution_file_output(project_root, version, "change-impact.json").relative_to(project_root)), "status": "completed"},
        {"type": "config", "path": str(execution_file_output(project_root, version, "config.json").relative_to(project_root)), "status": "completed"},
        {"type": "source", "path": str(execution_file_output(project_root, version, "source.json").relative_to(project_root)), "status": "completed"},
        {"type": "git-alignment", "path": str(execution_file_output(project_root, version, "git-alignment.json").relative_to(project_root)), "status": "completed"},
    ]
    strict_delivery_ready = workflow_status == "completed" and not bool(git_alignment.get("blocked")) and bool(change_impact.get("full_delivery_closed"))
    reason_codes = list(git_alignment.get("reason_codes", []))
    reason_codes.extend(change_impact.get("pending_blockers", []))
    return {
        "schema_version": "1.0",
        "version": version,
        "feature": feature,
        "run_id": run_id,
        "generated_at": now_iso(),
        "source_of_truth_root": f"docs/beacon/{version}",
        "delivery_status": "completed" if strict_delivery_ready else "draft",
        "strict_delivery_ready": strict_delivery_ready,
        "reason_codes": sorted(set(x for x in reason_codes if x)),
        "affected_projects": [
            {
                "name": project_root.name,
                "project_root": str(project_root),
                "repo_url": git_alignment.get("repo_url", ""),
                "change_scope": "docs_governance" if workflow_status != "completed" else "workflow_delivery",
                "changed_layers": change_impact.get("changed_layers", []),
                "base_branch": (git_alignment.get("git_refs") or {}).get("base_branch", ""),
                "target_branch": (git_alignment.get("git_refs") or {}).get("target_branch", ""),
                "current_branch": (git_alignment.get("git_refs") or {}).get("current_branch", ""),
                "commit": (git_alignment.get("git_refs") or {}).get("commit", ""),
                "tag": (git_alignment.get("git_refs") or {}).get("tag", ""),
                "worktree_path": (git_alignment.get("git_refs") or {}).get("worktree_path", ""),
                "alignment_status": "aligned" if not bool(git_alignment.get("blocked")) else "recorded_pending_alignment",
            }
        ],
        "deliverables": deliverables,
        "notes": [
            "多项目/多仓库交付范围必须通过 affected_projects 显式声明。",
            f"Current workflow status snapshot: {workflow_status}.",
            "execution artifacts are emitted only under docs/beacon.",
        ],
    }


def _write_execution_governance_artifacts(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    workflow_status: str,
) -> None:
    existing_source = _load_json_dict(execution_file_output(project_root, version, "source.json"))
    existing_run_id = str(existing_source.get("run_id", "") or "")
    if (
        project_root.resolve() == _repo_root().resolve()
        and str(version).strip() == str(__toolkit_version__).strip()
        and existing_run_id.startswith("run-v")
        and existing_run_id.endswith("release")
        and existing_run_id != str(run_id).strip()
    ):
        return
    config_payload = _build_execution_config_payload(
        project_root=project_root,
        version=version,
        run_id=run_id,
        feature=feature,
        workflow_status=workflow_status,
    )
    source_payload = _build_execution_source_payload(
        project_root=project_root,
        version=version,
        run_id=run_id,
        feature=feature,
        workflow_status=workflow_status,
    )
    git_alignment_payload = _build_execution_git_alignment_payload(project_root, version, run_id, feature)
    change_impact_payload = _build_execution_change_impact_payload(
        project_root=project_root,
        version=version,
        run_id=run_id,
        feature=feature,
        workflow_status=workflow_status,
    )
    delivery_manifest_payload = _build_execution_delivery_manifest_payload(
        project_root=project_root,
        version=version,
        run_id=run_id,
        feature=feature,
        workflow_status=workflow_status,
        change_impact=change_impact_payload,
        git_alignment=git_alignment_payload,
    )

    exec_root = human_execution_dir(project_root, version)
    exec_root.mkdir(parents=True, exist_ok=True)
    boundaries_path = exec_root / "boundaries.md"
    if not boundaries_path.exists():
        boundaries_path.write_text(
            "\n".join(
                [
                    f"# Workflow Boundaries ({version})",
                    "",
                    f"- run_id: {run_id}",
                    f"- feature: {feature}",
                    f"- workflow_status: {workflow_status}",
                    "- guardrail: workflow/gate consume only main-chain docs; research is input-only.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    if uses_machine_surface(version):
        index_path = exec_root / "index.md"
        if not index_path.exists():
            index_path.write_text(
                "\n".join(
                    [
                        f"# Execution Index ({version})",
                        "",
                        "- Human primary execution docs live here.",
                        f"- Machine execution artifacts live under `docs/beacon/{version}/.machine/execution/`.",
                        "- Start with `boundaries.md` for the human-facing contract.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
    write_json(execution_file_output(project_root, version, "config.json"), config_payload)
    write_json(execution_file_output(project_root, version, "source.json"), source_payload)
    write_json(execution_file_output(project_root, version, "git-alignment.json"), git_alignment_payload)
    write_json(execution_file_output(project_root, version, "change-impact.json"), change_impact_payload)
    write_json(execution_file_output(project_root, version, "delivery-manifest.json"), delivery_manifest_payload)
    evidence_refs = sorted(
        set(
            _existing_research_docs(project_root, version)
            + _main_chain_refs(project_root, version, feature)
            + [
                f"docs/beacon/{version}/execution/boundaries.md",
                str(execution_file_output(project_root, version, "config.json").relative_to(project_root)),
                str(execution_file_output(project_root, version, "source.json").relative_to(project_root)),
                str(execution_file_output(project_root, version, "git-alignment.json").relative_to(project_root)),
                str(execution_file_output(project_root, version, "delivery-manifest.json").relative_to(project_root)),
                str(execution_file_output(project_root, version, "change-impact.json").relative_to(project_root)),
            ]
        )
    )
    _update_evidence_manifest(project_root, evidence_refs, run_id=run_id, version=version)


def _write_workflow_terminal_artifacts(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    workflow_status: str,
    reason: str,
) -> None:
    exec_roots = [human_execution_dir(project_root, version)]
    status_value = "Pass" if workflow_status == "completed" else "Blocked"
    evidence_refs = [
        f".beacon/runs/{run_id}/state.json",
        ".beacon/raw-command-log.jsonl",
        ".beacon/auto-test-status.json",
    ]
    resume_contract = build_resume_contract(project_root, run_id=run_id)
    checkpoint_ref = str(resume_contract.get("checkpoint_ref", "") or "")
    if checkpoint_ref:
        evidence_refs.append(checkpoint_ref)
    exhaustion_ref = ".beacon/state/exhaustion.json"
    if (project_root / exhaustion_ref).exists():
        evidence_refs.append(exhaustion_ref)

    written_refs: list[str] = []
    for root in exec_roots:
        root.mkdir(parents=True, exist_ok=True)
        boundaries = root / "boundaries.md"
        terminal = execution_file_output(project_root, version, "terminal.json")
        if not boundaries.exists():
            boundaries.write_text(
                "\n".join(
                    [
                        f"# Workflow Boundaries ({version})",
                        "",
                        f"- run_id: {run_id}",
                        f"- feature: {feature}",
                        f"- workflow_status: {workflow_status}",
                        f"- reason: {reason}",
                        "- guardrail: implementation stage requires explicit command execution",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
        terminal_payload = {
            "schema_version": "1.0",
            "version": version,
            "run_id": run_id,
            "feature": feature,
            "status": status_value,
            "reason": reason,
            "control_plane": {
                "failure_streak": int(resume_contract.get("failure_streak", 0) or 0),
                "escalation_level": str(resume_contract.get("escalation_level", "E0") or "E0"),
                "required_next_action": str(resume_contract.get("required_next_action", "continue_current_plan") or "continue_current_plan"),
                "checkpoint_ref": checkpoint_ref,
            },
            "traceability": {
                "evidence_refs": evidence_refs,
            },
            "generated_at": now_iso(),
        }
        write_json(terminal, terminal_payload)
        written_refs.extend(
            [
                str(boundaries.relative_to(project_root)),
                str(terminal.relative_to(project_root)),
            ]
        )

    auto_test_run_id = ""
    auto_test_status = project_root / ".beacon" / "auto-test-status.json"
    if auto_test_status.exists():
        try:
            auto_payload = json.loads(auto_test_status.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            auto_payload = {}
        if isinstance(auto_payload, dict):
            auto_test_run_id = str(auto_payload.get("run_id", "") or "").strip()

    gate_status = "Pass" if status_value == "Pass" else "Blocked"
    gate_issues: list[dict[str, Any]] = []
    if gate_status == "Blocked":
        gate_issues.append(
            {
                "reason_code": reason or "workflow_blocked",
                "message": f"Workflow blocked: {reason or 'unknown'}",
                "blocked": True,
            }
        )
    coverage = compute_coverage_metrics(project_root, version=version, feature=feature)
    write_json(
        project_root / ".beacon" / "gate-report.json",
        {
            "stage": "release",
            "mode": "strict",
            "status": gate_status,
            "issues": gate_issues,
            "run_id": auto_test_run_id or run_id,
            "version": version,
            "coverage": {
                "full_coverage": bool(coverage.get("full_coverage")),
                "story_coverage": coverage.get("story_coverage"),
                "ac_coverage": coverage.get("ac_coverage"),
                "tc_coverage": coverage.get("tc_coverage"),
            },
            "updated_at": now_iso(),
        },
    )
    _update_evidence_manifest(
        project_root,
        written_refs + [".beacon/gate-report.json"],
        run_id=auto_test_run_id or run_id,
        version=version,
    )

    release_evidence_refs = sorted(
        set(
            written_refs
            + [
                ".beacon/gate-report.json",
                f".beacon/runs/{run_id}/state.json",
                ".beacon/raw-command-log.jsonl",
                ".beacon/auto-test-status.json",
            ]
        )
    )
    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[workflow.release-profile] run={run_id} status={workflow_status} reason={reason}",
        source_session_id=run_id,
        source="workflow.release-profile",
        evidence_ref=release_evidence_refs,
        confidence=0.82,
        tags=["release", "workflow-loop", workflow_status],
    )
    append_lifecycle_event(
        project_root,
        run_id=f"release:{version}",
        stage="release",
        event="release_decision_recorded",
        source="workflow.release-profile",
        evidence_ref=release_evidence_refs,
        details={
            "workflow_run_id": run_id,
            "feature": feature,
            "version": version,
            "status": workflow_status,
            "reason": reason,
        },
    )


def _sync_terminal_manifest(project_root: Path, *, version: str, run_id: str) -> None:
    auto_test_run_id = ""
    auto_test_status = project_root / ".beacon" / "auto-test-status.json"
    if auto_test_status.exists():
        try:
            auto_payload = json.loads(auto_test_status.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            auto_payload = {}
        if isinstance(auto_payload, dict):
            auto_test_run_id = str(auto_payload.get("run_id", "") or "").strip()

    refs = [
        f".beacon/runs/{run_id}/state.json",
        ".beacon/raw-command-log.jsonl",
        ".beacon/auto-test-status.json",
        ".beacon/gate-report.json",
    ]
    for root in (
        project_root / "docs" / "beacon" / version / "execution",
    ):
        for name in (
            "boundaries.md",
            "terminal.json",
            "summary.json",
            "summary.md",
            "config.json",
            "source.json",
            "git-alignment.json",
            "delivery-manifest.json",
            "change-impact.json",
        ):
            path = root / name
            if path.exists():
                refs.append(str(path.relative_to(project_root)))
    _update_evidence_manifest(
        project_root,
        refs,
        run_id=auto_test_run_id or run_id,
        version=version,
    )


def run_beacon_command(
    args: list,
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    extra_env: Optional[dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    """Run a beacon subcommand.

    The workflow executor runs subcommands from the target project root, which may be
    outside the Beacon repository. Ensure the current repository root is injected into
    PYTHONPATH so `python -m beacon.main` resolves the in-repo package consistently in
    tests and local development.
    """
    cmd = [sys.executable, "-m", "beacon.main"] + args
    env = os.environ.copy()
    env.update(extra_env or {})
    repo_root = str(Path(__file__).resolve().parents[2])
    existing = str(env.get("PYTHONPATH", "")).strip()
    env["PYTHONPATH"] = repo_root if not existing else os.pathsep.join([repo_root, existing])
    result = subprocess.run(
        cmd,
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        env=env,
    )
    _log_raw_command(
        project_root,
        run_id=run_id,
        stage=stage,
        command=" ".join(cmd),
        exit_code=int(result.returncode),
    )
    return result


def ensure_output_dirs(project_root: Path, version: str = "v1.0.0"):
    """Ensure canonical Beacon docs roots exist."""
    base = project_root / "docs" / "beacon" / version
    dirs = [
        base / "user-story",
        base / "prd",
        base / "prototype",
        base / "qa" / "test-cases",
        base / "execution",
        base / "release",
        project_root / ".beacon" / "state",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    summary = base / "SUMMARY.md"
    if not summary.exists():
        summary.write_text(f"# Beacon {version} Summary\n", encoding="utf-8")
    release_stub = base / "release" / f"{version}.md"
    if not release_stub.exists():
        release_stub.write_text(f"# Release: {version}\n", encoding="utf-8")


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _stage_output_candidates(project_root: Path, stage: str, feature: str, version: str) -> list[Path]:
    slug = _slug(feature)
    common = [project_root / ".beacon" / "raw-command-log.jsonl"]
    if stage == "user-story":
        return [
            project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md",
        ] + common
    if stage == "prd":
        return [
            project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md",
        ] + common
    if stage == "prototype":
        return [
            project_root / "docs" / "beacon" / version / "prototype" / slug / "wireframe-summary.md",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "manifest.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "source-map.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "prototype-brief.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "theme.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "navigation-map.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "interaction-map.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "coverage-report.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "wireframe-manifest.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "prototype-review.json",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "prototype-review.md",
            project_root / "docs" / "beacon" / version / "prototype" / slug / "freeze.json",
        ] + common
    if stage == "test-case":
        return [
            project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.md",
            qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")[0],
            qa_matrix_candidates(project_root, version, slug, "qa9-matrix")[0],
        ] + common
    if stage in {"implement", "implementation"}:
        return [
            project_root / ".beacon" / "state" / f"implementation-{slug}.json",
        ] + common
    if stage in {"qa", "verify"}:
        return [
            project_root / ".beacon" / "auto-test-status.json",
        ] + common
    if stage in {"release", "gate"}:
        return [
            project_root / ".beacon" / "gate-report.json",
        ] + common
    return common


def _matrix_path_candidates(project_root: Path, feature: str, version: str) -> list[Path]:
    slug = _slug(feature)
    return qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")


def _qa9_matrix_path_candidates(project_root: Path, feature: str, version: str) -> list[Path]:
    slug = _slug(feature)
    return qa_matrix_candidates(project_root, version, slug, "qa9-matrix")


def _append_run_event(state: dict[str, Any], event: str, **details: Any) -> None:
    events = state.get("events")
    if not isinstance(events, list):
        events = []
    payload = {"event": event, "ts": now_iso()}
    payload.update(details)
    events.append(payload)
    state["events"] = events


def _effective_interactive_mode(interactive: Optional[bool]) -> bool:
    if isinstance(interactive, bool):
        return interactive
    try:
        if sys.stdin is not sys.__stdin__ or sys.stdout is not sys.__stdout__:
            return False
        return bool(sys.stdin.isatty() and sys.stdout.isatty())
    except Exception:  # noqa: BLE001
        return False


def _parse_semver_tuple(value: str) -> tuple[int, int, int]:
    raw = str(value or "").strip().lower()
    if raw.startswith("v"):
        raw = raw[1:]
    parts = raw.split(".")
    numbers: list[int] = []
    for part in parts[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        numbers.append(int(digits) if digits else 0)
    while len(numbers) < 3:
        numbers.append(0)
    return (numbers[0], numbers[1], numbers[2])


def _requires_hud_double_confirmation(version: str) -> bool:
    return _parse_semver_tuple(version) >= (1, 1, 0)


def _resolve_workflow_default_runner(project_root: Path, version: str) -> str:
    """Resolve workflow implementation runner from project-local config only.

    Workflow should remain deterministic per project. Global user config must not
    silently change historical workflow behavior for older release lines.
    """
    config = load_beacon_config_file(project_config_path(project_root))
    skill_section = config.get("skill") if isinstance(config.get("skill"), dict) else {}
    implementation_section = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    preferred = str(skill_section.get("preferred", "")).strip()
    if preferred:
        return preferred
    default_runner = str(implementation_section.get("default_runner", "")).strip()
    if default_runner:
        return default_runner
    if _parse_semver_tuple(version) >= (1, 1, 6):
        return "native-single"
    return ""


def _resolve_hud_enforcement(*, version: str, hud_requested: bool, command_name: str) -> bool:
    if _requires_hud_double_confirmation(version):
        if not hud_requested:
            typer.echo(
                f"ℹ {command_name}: v1.1.0+ enforces HUD display; ignoring --no-hud."
            )
        return True
    return bool(hud_requested)


def _workflow_hud_snapshot_path(project_root: Path, run_id: str) -> Path:
    return project_root / ".beacon" / "state" / "workflow-hud" / f"{run_id}.json"


def _load_json_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return data if isinstance(data, dict) else {}


def _consume_change_impact_task(project_root: Path, *, run_id: str, stage: str) -> None:
    task_map = {
        "user-story": "regenerate-user_story",
        "prd": "regenerate-prd",
        "test-case": "regenerate-test_case",
    }
    target_task = task_map.get(str(stage or "").strip())
    if not target_task:
        return
    impact_path = project_root / ".beacon" / "state" / "change-impact" / f"{run_id}.json"
    payload = _load_json_dict(impact_path)
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        return

    changed = False
    for item in tasks:
        if not isinstance(item, dict):
            continue
        if str(item.get("task", "")).strip() != target_task:
            continue
        if str(item.get("status", "pending")).strip().lower() == "completed":
            continue
        item["status"] = "completed"
        item["completed_at"] = now_iso()
        item["completed_by_stage"] = stage
        changed = True

    if not changed:
        return

    pending = [
        item
        for item in tasks
        if isinstance(item, dict)
        and str(item.get("status", "pending")).strip().lower() != "completed"
    ]
    payload["doc_chain_update_required"] = bool(pending)
    payload["updated_at"] = now_iso()
    write_json(impact_path, payload)


def _read_auto_test_status(project_root: Path) -> str:
    payload = _load_json_dict(project_root / ".beacon" / "auto-test-status.json")
    status = str(payload.get("status", "")).strip().lower()
    return status or "unknown"


def _build_latest_reason_codes(progress: dict[str, Any]) -> list[str]:
    stage_map = progress.get("stages", {})
    if not isinstance(stage_map, dict):
        return []
    out: list[str] = []
    for stage, payload in stage_map.items():
        if not isinstance(payload, dict):
            continue
        if str(payload.get("status", "")) == "failed":
            out.append(f"{stage}_failed")
    return out


def _render_workflow_hud(
    *,
    project_root: Path,
    run_id: str,
    feature: str,
    version: str,
    mode: str,
    progress: dict[str, Any],
    show_text: bool = True,
) -> dict[str, Any]:
    stage_status = progress.get("stages", {}) if isinstance(progress.get("stages"), dict) else {}
    missing = progress.get("missing_closure_stages", [])
    if not isinstance(missing, list):
        missing = []
    think_state = _load_json_dict(project_root / ".beacon" / "state" / "think-progress" / f"{version}.json")
    open_questions = think_state.get("open_questions", [])
    conflicts = think_state.get("conflicts", [])
    memory_metrics = {
        "recall_injections": 0,
        "writebacks": 0,
        "feedback_assimilations": 0,
    }
    try:
        from beacon.utils.workflow_memory import compute_memory_metrics  # local import to avoid cycle in tests

        mm = compute_memory_metrics(project_root, run_id=run_id)
        memory_metrics = {
            "recall_injections": int(mm.get("recall_injections", 0) or 0),
            "writebacks": int(mm.get("writebacks", 0) or 0),
            "feedback_assimilations": int(mm.get("feedback_assimilations", 0) or 0),
        }
    except Exception:  # noqa: BLE001
        pass

    coverage = compute_coverage_metrics(project_root, version=version, feature=feature)
    gate_payload = _load_json_dict(project_root / ".beacon" / "gate-report.json")
    gate_status = str(gate_payload.get("status", "")).strip().lower() if gate_payload else ""
    auto_test_status = _read_auto_test_status(project_root)
    gate_ready = (
        str(progress.get("next_stage") or "none") in {"release", "none"}
        and auto_test_status == "passed"
    )

    debug_state = load_debug_mode_state(project_root)
    debug_payload = {
        "enabled": bool(debug_state.get("enabled", False)),
        "run_id": str(debug_state.get("run_id", "") or ""),
    }
    control_payload = exhaustion_for_run(project_root, run_id=run_id)

    hud_payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "version": version,
        "mode": mode,
        "workflow_progress": {
            "next_stage": str(progress.get("next_stage") or "none"),
            "closure_complete": bool(progress.get("closure_complete")),
            "missing_closure_stages": missing,
        },
        "stage_status": {
            stage: str((stage_status.get(stage) or {}).get("status", "not_started"))
            for stage in list(progress.get("workflow_stages", []) or [name for name, _, _ in WORKFLOW_STAGES])
        },
        "blockers": {
            "blocking_open_questions": len(open_questions) if isinstance(open_questions, list) else 0,
            "critical_conflicts": len(conflicts) if isinstance(conflicts, list) else 0,
            "latest_reason_codes": _build_latest_reason_codes(progress),
        },
        "quality": {
            "gate_ready": gate_ready,
            "gate_status": gate_status or "unknown",
            "auto_test_status": auto_test_status,
            "coverage_full": bool(coverage.get("full_coverage")),
        },
        "memory": memory_metrics,
        "debug": debug_payload,
        "control_plane": {
            "failure_streak": int(control_payload.get("failure_streak", 0) or 0),
            "escalation_level": str(control_payload.get("escalation_level", "E0") or "E0"),
            "required_next_action": str(control_payload.get("required_next_action", "continue_current_plan") or "continue_current_plan"),
            "last_failed_stage": str(control_payload.get("last_failed_stage", "") or ""),
        },
        "generated_at": now_iso(),
    }

    snapshot = _workflow_hud_snapshot_path(project_root, run_id)
    write_json(snapshot, hud_payload)
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage="workflow",
        event="hud_rendered",
        source="workflow.hud",
        evidence_ref=[str(snapshot.relative_to(project_root))],
        details={
            "next_stage": hud_payload["workflow_progress"]["next_stage"],
            "closure_complete": hud_payload["workflow_progress"]["closure_complete"],
        },
    )

    if show_text:
        typer.echo("\n" + "=" * 56)
        typer.echo("WORKFLOW HUD")
        typer.echo("=" * 56)
        typer.echo(f"run_id       : {run_id}")
        typer.echo(f"feature      : {feature}")
        typer.echo(f"version      : {version}")
        typer.echo(f"mode         : {mode}")
        typer.echo(f"next_stage   : {hud_payload['workflow_progress']['next_stage']}")
        typer.echo(f"closure      : {hud_payload['workflow_progress']['closure_complete']}")
        typer.echo(f"missing      : {hud_payload['workflow_progress']['missing_closure_stages']}")
        typer.echo(f"auto_test    : {hud_payload['quality']['auto_test_status']}")
        typer.echo(f"release_gate : {hud_payload['quality']['gate_status']}")
        typer.echo(f"coverage_full: {hud_payload['quality']['coverage_full']}")
        typer.echo(
            f"debug_mode   : {hud_payload['debug']['enabled']} "
            f"(run_id={hud_payload['debug']['run_id'] or '-'})"
        )
        typer.echo(
            f"control      : streak={hud_payload['control_plane']['failure_streak']} "
            f"level={hud_payload['control_plane']['escalation_level']} "
            f"next={hud_payload['control_plane']['required_next_action']}"
        )
    return hud_payload


def _print_interactive_menu() -> None:
    typer.echo("\n[Next Step]")
    typer.echo("1) 执行 next_stage（single-step）")
    typer.echo("2) 自动补齐到 release（auto-run）")
    typer.echo("3) 查看阻塞详情（reason_code/open_questions/conflicts）")
    typer.echo("4) 执行反馈修订（feedback extract+apply）")
    typer.echo("5) 暂停并保存（pause）")
    typer.echo("6) 退出（abort）")


def _write_interaction_memory(
    *,
    project_root: Path,
    run_id: str,
    action: str,
    accepted: bool,
    hud_snapshot_rel: str | None = None,
    reason_codes: list[str] | None = None,
    feature: str = "",
    version: str = "",
) -> None:
    refs = [x for x in [hud_snapshot_rel] if x]
    details = {
        "action": action,
        "accepted": accepted,
        "reason_codes": reason_codes or [],
    }
    event_name = "human_checkpoint_confirmed" if accepted else "human_checkpoint_rejected"
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage="workflow",
        event=event_name,
        source="workflow.interactive",
        evidence_ref=refs,
        details=details,
    )
    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[workflow.interactive] action={action} accepted={accepted}",
        source_session_id=run_id,
        source="workflow.interactive",
        evidence_ref=refs,
        confidence=0.8 if accepted else 0.7,
        tags=["workflow", "interactive", "checkpoint", action],
    )
    _record_debug_feedback(
        project_root=project_root,
        source="workflow.interactive.prompt-op",
        goal=feature or f"workflow-run:{run_id}",
        intent="workflow",
        confidence=0.86 if accepted else 0.45,
        boundary_state="in_scope",
        block_reason="" if accepted else "workflow_confirmation_rejected",
        recommended_command=f"interactive-action:{action}",
        executed=bool(accepted),
        exit_code=0 if accepted else None,
        note=f"action={action};accepted={accepted}",
        run_id=run_id,
        extra={
            "action": action,
            "accepted": bool(accepted),
            "reason_codes": reason_codes or [],
            "version": version,
        },
    )


def _resolve_action_with_timeout(
    *,
    run_id: str,
    project_root: Path,
    confirm_timeout: int,
    on_timeout: str,
) -> str:
    default_action = "pause"
    normalized = str(on_timeout or "pause").strip().lower()
    if normalized not in {"pause", "continue", "abort"}:
        normalized = "pause"
    action_map = {"pause": "pause", "continue": "single-step", "abort": "abort"}

    raw_choice = _input_with_timeout("Select action [1-6]: ", confirm_timeout)
    if raw_choice is None:
        resolved = action_map[normalized]
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage="workflow",
            event="workflow_paused",
            source="workflow.interactive",
            details={"reason": "timeout_or_no_input", "on_timeout": normalized, "resolved_action": resolved},
        )
        return resolved or default_action
    raw_choice = str(raw_choice).strip()
    action = INTERACTIVE_ACTIONS.get(raw_choice)
    if not action:
        typer.echo("Invalid choice. default -> pause")
        return "pause"
    return action


def _input_with_timeout(prompt: str, timeout_sec: int) -> str | None:
    timeout = max(1, int(timeout_sec))
    if os.name == "nt":
        try:
            return input(prompt)
        except EOFError:
            return None

    def _raise_timeout(_signum, _frame):  # type: ignore[no-untyped-def]
        raise TimeoutError

    previous = signal.getsignal(signal.SIGALRM)
    try:
        signal.signal(signal.SIGALRM, _raise_timeout)
        signal.alarm(timeout)
        try:
            value = input(prompt)
        except EOFError:
            return None
        return value
    except TimeoutError:
        return None
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def _confirm_action(action: str, *, confirm_timeout: int) -> bool:
    if action not in EXECUTION_ACTIONS:
        return True
    choice = _input_with_timeout("Confirm? (y/N): ", confirm_timeout)
    if choice is None:
        return False
    choice = str(choice).strip().lower()
    return choice in {"y", "yes"}


def _confirm_second_execution_interactive(*, confirm_timeout: int) -> bool:
    choice = _input_with_timeout("Second confirm (type EXECUTE): ", confirm_timeout)
    if choice is None:
        return False
    normalized = str(choice).strip().upper()
    return normalized in {"EXECUTE", "Y", "YES"}


def _pause_workflow_state(project_root: Path, run_id: str, state: dict[str, Any], reason: str = "manual_pause") -> None:
    paused = dict(state)
    paused["status"] = "paused"
    paused["reason"] = reason
    paused["paused_at"] = now_iso()
    _append_run_event(paused, "workflow_paused", reason=reason)
    save_run_state(project_root, run_id, paused)
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage="workflow",
        event="workflow_paused",
        source="workflow.interactive",
        details={"reason": reason},
    )

def _execute_stage(
    *,
    project_root: Path,
    run_id: str,
    stage: str,
    feature: str,
    version: str,
    implementation_command: Optional[str],
    implementation_runner: Optional[str],
    implementation_skill: Optional[str],
    verify_scope: str,
    verify_config: Optional[str],
    verify_ui_command: Optional[str],
    verify_api_curl_command: Optional[str],
    verify_unit_command: Optional[str],
    verify_smoke_command: Optional[str],
    verify_require_ui_actions: bool,
    verify_qa_profile: str,
    verify_qa_types: Optional[list[str]],
    verify_qa_matrix_path: Optional[str],
    verify_ui_runner: str,
    verify_compat_browsers: Optional[str],
    verify_compat_devices: Optional[str],
    verify_require_fresh_evidence: bool,
) -> int:
    """Execute one workflow stage and write lifecycle events."""
    failure_details: dict[str, Any] = {}
    attempted_strategy = stage
    recommended_resume_command = f'beacon resume continue --run-id {run_id} --project-root "{project_root}"'
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=stage,
        event="stage_started",
        source="workflow.start",
        details={"feature": feature, "version": version},
    )
    context_path = write_stage_context(
        project_root,
        run_id=run_id,
        stage=stage,
        feature=feature,
    )
    stage_env = {
        "BEACON_WORKFLOW_RUN_ID": run_id,
        "BEACON_WORKFLOW_STAGE": stage,
        "BEACON_STAGE_CONTEXT_PATH": str(context_path),
    }

    if stage == "prd":
        result = run_beacon_command(
            ["prd", "create", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
    elif stage == "user-story":
        result = run_beacon_command(
            ["user-story", "create", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
    elif stage == "think":
        result = run_beacon_command(
            ["think", "start", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
    elif stage == "prototype":
        result = run_beacon_command(
            ["prototype", "create", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
        if rc == 0:
            review_result = run_beacon_command(
                ["prototype", "review", feature, "--project", str(project_root), "--version", version],
                project_root,
                run_id=run_id,
                stage=stage,
                extra_env=stage_env,
            )
            rc = int(review_result.returncode)
        if rc == 0:
            freeze_result = run_beacon_command(
                ["prototype", "freeze", feature, "--project", str(project_root), "--version", version],
                project_root,
                run_id=run_id,
                stage=stage,
                extra_env=stage_env,
            )
            rc = int(freeze_result.returncode)
    elif stage == "test-case":
        result = run_beacon_command(
            ["test-case", "create", feature, "--project", str(project_root), "--version", version],
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
    elif stage in {"implement", "implementation"}:
        resolved_implementation_command = str(implementation_command or "").strip()
        command_source = "cli"
        resolved_runner = str(implementation_runner or "").strip()
        attempted_strategy = f"implement:{resolved_runner or 'command'}"
        if resolved_implementation_command:
            env = os.environ.copy()
            env.update(stage_env)
            shell_result = subprocess.run(
                resolved_implementation_command,
                cwd=project_root,
                shell=True,
                text=True,
                env=env,
            )
            rc = shell_result.returncode
            _log_raw_command(
                project_root,
                run_id=run_id,
                stage=stage,
                command=resolved_implementation_command,
                exit_code=rc,
            )
            if rc == 0:
                marker = project_root / ".beacon" / "state" / f"implementation-{_slug(feature)}.json"
                write_json(
                    marker,
                    {
                        "schema_version": "1.0",
                        "run_id": run_id,
                        "stage": "implement",
                        "feature": feature,
                        "version": version,
                        "command": resolved_implementation_command,
                        "command_source": command_source,
                        "status": "completed",
                        "generated_at": now_iso(),
                    },
                )
        else:
            if not resolved_runner:
                resolved_runner = _resolve_workflow_default_runner(project_root, version)
            if resolved_runner:
                from beacon.commands.implement import run_implement_stage

                rc, implement_payload = run_implement_stage(
                    feature=feature,
                    project_root=project_root,
                    version=version,
                    run_id_override=run_id,
                    runner=resolved_runner,
                    skill=implementation_skill,
                    dry_run=False,
                    auto_review_spec=True,
                    auto_review_quality=False,
                )
                if rc != 0 or str(implement_payload.get("status", "")).strip().lower() != "completed":
                    failure_details = {
                        "reason_code": str(implement_payload.get("reason_code", "") or "implement_execution_failed"),
                        "runner": resolved_runner,
                        "payload": implement_payload,
                    }
                    rc = 2
                else:
                    rc = 0
            else:
                env_command = str(os.environ.get("BEACON_IMPLEMENTATION_COMMAND", "")).strip()
                if env_command:
                    resolved_implementation_command = env_command
                    command_source = "env"
                    attempted_strategy = "implement:env-command"
                if not resolved_implementation_command:
                    typer.echo("Blocked: implement stage requires explicit external command execution")
                    _log_raw_command(
                        project_root,
                        run_id=run_id,
                        stage=stage,
                        command="<missing implementation command>",
                        exit_code=2,
                    )
                    rc = 2
                    failure_details = {"reason": "missing_implementation_command"}
                else:
                    env = os.environ.copy()
                    env.update(stage_env)
                    shell_result = subprocess.run(
                        resolved_implementation_command,
                        cwd=project_root,
                        shell=True,
                        text=True,
                        env=env,
                    )
                    rc = shell_result.returncode
                    _log_raw_command(
                        project_root,
                        run_id=run_id,
                        stage=stage,
                        command=resolved_implementation_command,
                        exit_code=rc,
                    )
                    if rc == 0:
                        marker = project_root / ".beacon" / "state" / f"implementation-{_slug(feature)}.json"
                        write_json(
                            marker,
                            {
                                "schema_version": "1.0",
                                "run_id": run_id,
                                "stage": "implement",
                                "feature": feature,
                                "version": version,
                                "command": resolved_implementation_command,
                                "command_source": command_source,
                                "status": "completed",
                                "generated_at": now_iso(),
                            },
                        )
    elif stage in {"qa", "verify"}:
        attempted_strategy = f"qa:{(verify_scope or 'all').strip().lower()}"
        verify_scope_norm = (verify_scope or "all").strip().lower()
        require_ui_actions_effective = verify_require_ui_actions and verify_scope_norm in {
            "ui",
            "all",
            "functional",
            "qa9",
        }
        feature_qa_mode = _parse_semver_tuple(version) == (1, 1, 9)
        verify_args = [
            "qa",
            "run",
            feature,
            "--project",
            str(project_root),
            "--version",
            version,
        ] if feature_qa_mode else [
            "auto-test",
            "create",
            verify_scope,
            "--project",
            str(project_root),
            "--version",
            version,
        ]
        if verify_config:
            verify_args.extend(["--config", verify_config])
        if verify_ui_command:
            verify_args.extend(["--ui-command", verify_ui_command])
        if verify_api_curl_command:
            verify_args.extend(["--api-curl-command", verify_api_curl_command])
        if verify_unit_command:
            verify_args.extend(["--unit-command", verify_unit_command])
        if verify_smoke_command:
            verify_args.extend(["--smoke-command", verify_smoke_command])
        if verify_scope_norm == "qa9":
            verify_args.extend(["--qa-profile", verify_qa_profile])
            if verify_qa_types:
                for item in verify_qa_types:
                    verify_args.extend(["--qa-types", item])
            elif feature_qa_mode:
                for item in parse_qa_types(None, profile=verify_qa_profile):
                    verify_args.extend(["--qa-types", item])
            if verify_ui_runner:
                verify_args.extend(["--ui-runner", verify_ui_runner])
            if verify_compat_browsers:
                verify_args.extend(["--compat-browsers", verify_compat_browsers])
            if verify_compat_devices:
                verify_args.extend(["--compat-devices", verify_compat_devices])
            if verify_require_fresh_evidence:
                verify_args.append("--require-fresh-evidence")
        elif feature_qa_mode:
            verify_args.extend(["--qa-types", normalize_qa_type(verify_scope_norm)])
        if require_ui_actions_effective:
            verify_args.append("--require-ui-actions")
        if verify_qa_matrix_path and verify_scope_norm == "qa9":
            verify_args.extend(["--qa-matrix-path", verify_qa_matrix_path])
        else:
            if verify_scope_norm == "qa9":
                for matrix_path in _qa9_matrix_path_candidates(project_root, feature, version):
                    if matrix_path.exists():
                        verify_args.extend(["--qa-matrix-path", str(matrix_path)])
                        break
            for matrix_path in _matrix_path_candidates(project_root, feature, version):
                if matrix_path.exists():
                    verify_args.extend(["--matrix-path", str(matrix_path)])
                    break
        result = run_beacon_command(
            verify_args,
            project_root,
            run_id=run_id,
            stage=stage,
            extra_env=stage_env,
        )
        rc = int(result.returncode)
        # Verify stage hard condition: auto-test artifact must be passed.
        if rc == 0:
            verify_artifact = project_root / ".beacon" / "auto-test-status.json"
            if not verify_artifact.exists():
                rc = 1
                failure_details = {
                    "exit_code": 1,
                    "verify_status": "missing_artifact",
                    "reason": "verify_status_artifact_missing",
                }
            else:
                try:
                    verify_payload = json.loads(verify_artifact.read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    verify_payload = {}
                verify_status = str(verify_payload.get("status", "")).lower()
                if verify_status != "passed":
                    rc = 1
                    failure_details = {
                        "exit_code": 1,
                        "verify_status": verify_status or "unknown",
                        "reason": "verify_not_passed",
                    }
    elif stage in {"release", "gate"}:
        attempted_strategy = "release:strict"
        verify_payload = _load_json_dict(project_root / ".beacon" / "auto-test-status.json")
        verify_status = str(verify_payload.get("status", "")).strip().lower()
        coverage = compute_coverage_metrics(project_root, version=version, feature=feature)
        gate_status = "Pass" if verify_status == "passed" else "Blocked"
        issues: list[dict[str, Any]] = []
        if verify_status != "passed":
            issues.append(
                {
                    "reason_code": "verify_not_passed",
                    "severity": "critical",
                    "message": f"verify status is {verify_status or 'unknown'}",
                    "blocked": True,
                }
            )
        gate_payload = {
            "stage": "release",
            "mode": "strict",
            "status": gate_status,
            "issues": issues,
            "run_id": run_id,
            "version": version,
            "coverage": {
                "full_coverage": bool(coverage.get("full_coverage")),
                "story_coverage": coverage.get("story_coverage"),
                "ac_coverage": coverage.get("ac_coverage"),
                "tc_coverage": coverage.get("tc_coverage"),
            },
            "updated_at": now_iso(),
        }
        write_json(project_root / ".beacon" / "gate-report.json", gate_payload)
        rc = 0 if gate_status == "Pass" else 1
        if rc != 0:
            failure_details = {
                "exit_code": rc,
                "reason": "gate_blocked",
                "gate_status": gate_status,
            }
    else:
        rc = 1

    if rc == 0:
        record_stage_success(project_root, run_id=run_id, stage=stage)
        _consume_change_impact_task(
            project_root,
            run_id=run_id,
            stage=stage,
        )
        evidence = [
            str(path.relative_to(project_root))
            for path in _stage_output_candidates(project_root, stage, feature, version)
            if path.exists()
        ]
        _update_evidence_manifest(project_root, evidence, run_id=run_id, version=version)
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage=stage,
            event="stage_finished",
            source="workflow.start",
            evidence_ref=evidence,
            details={"exit_code": rc},
        )
        record_stage_writeback(
            project_root,
            run_id=run_id,
            stage=stage,
            feature=feature,
            evidence_ref=evidence,
            status="completed",
        )
    else:
        reason_code = str(
            failure_details.get("reason_code")
            or failure_details.get("reason")
            or f"{stage}_failed"
        ).strip()
        if reason_code == "missing_implementation_command":
            typer.echo("implementation stage requires explicit external command execution")
        checkpoint_payload = record_stage_failure(
            project_root,
            run_id=run_id,
            stage=stage,
            attempted_strategy=attempted_strategy,
            reason_code=reason_code,
            current_blocker=str(failure_details.get("reason") or reason_code or stage),
            evidence_gap=failure_details.get("evidence_gap") if isinstance(failure_details.get("evidence_gap"), list) else None,
            next_hypothesis=str(failure_details.get("next_hypothesis") or ""),
            recommended_command=recommended_resume_command,
            details=failure_details or {"exit_code": rc},
        )
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage=stage,
            event="stage_failed",
            source="workflow.start",
            evidence_ref=[str(checkpoint_payload.get("latest_checkpoint_ref") or checkpoint_payload.get("latest_checkpoint_ref", ""))] if str(checkpoint_payload.get("latest_checkpoint_ref", "")).strip() else [],
            details={**(failure_details or {"exit_code": rc}), "escalation_level": checkpoint_payload.get("escalation_level")},
        )
    return rc


@app.command()
def start(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Auto-run all stages until release"),
    skip: Optional[str] = typer.Option(None, "--skip", "-s", help="Skip stages (e.g., prd,user-story)"),
    interactive: Optional[bool] = typer.Option(
        None,
        "--interactive/--no-interactive",
        help="Interactive mode (default: auto detect TTY)",
    ),
    hud: bool = typer.Option(
        True,
        "--hud/--no-hud",
        help="Render workflow HUD before execution (v1.1.0+ always on).",
    ),
    confirm_execute: bool = typer.Option(
        False,
        "--confirm-execute",
        help="Non-interactive first confirmation for execution (required in v1.1.0+).",
    ),
    confirm_execute_second: bool = typer.Option(
        False,
        "--confirm-execute-second",
        help="Non-interactive second confirmation for execution (required in v1.1.0+).",
    ),
    confirm_timeout: int = typer.Option(
        60,
        "--confirm-timeout",
        min=1,
        help="Interactive confirm timeout in seconds (EOF fallback).",
    ),
    on_timeout: str = typer.Option(
        "pause",
        "--on-timeout",
        help="Timeout behavior: pause|continue|abort",
    ),
    with_prototype: bool = typer.Option(
        False,
        "--with-prototype/--no-with-prototype",
        help="Include optional prototype stage for UI visualization flows.",
    ),
    implementation_command: Optional[str] = typer.Option(
        None,
        "--implementation-command",
        help="Implementation stage command override",
    ),
    implementation_runner: Optional[str] = typer.Option(
        None,
        "--implementation-runner",
        help="Implementation stage runner override",
    ),
    implementation_skill: Optional[str] = typer.Option(
        None,
        "--implementation-skill",
        help="Implementation stage skill override for skill-capable runners",
    ),
    verify_scope: str = typer.Option("all", "--verify-scope", help="QA scope: ui/api-curl/unit/smoke/all/qa9"),
    verify_config: Optional[str] = typer.Option(None, "--verify-config", help="Verify config path"),
    verify_ui_command: Optional[str] = typer.Option(None, "--verify-ui-command", help="Verify UI command"),
    verify_api_curl_command: Optional[str] = typer.Option(None, "--verify-api-curl-command", help="Verify API curl command"),
    verify_unit_command: Optional[str] = typer.Option(None, "--verify-unit-command", help="Verify unit command"),
    verify_smoke_command: Optional[str] = typer.Option(None, "--verify-smoke-command", help="Verify smoke command"),
    verify_require_ui_actions: bool = typer.Option(
        False,
        "--verify-require-ui-actions/--no-verify-require-ui-actions",
        help="Require key UI action evidence in qa stage.",
    ),
    verify_qa_profile: str = typer.Option(
        "web-full",
        "--verify-qa-profile",
        help="Verify QA profile for qa9 scope: web-core/web-full/custom",
    ),
    verify_qa_types: Optional[list[str]] = typer.Option(
        None,
        "--verify-qa-types",
        help="Verify QA types for qa9 scope (comma-separated or repeatable).",
    ),
    verify_qa_matrix_path: Optional[str] = typer.Option(
        None,
        "--verify-qa-matrix-path",
        help="Verify QA9 matrix path (*.qa9-matrix.json).",
    ),
    verify_ui_runner: str = typer.Option(
        "playwright",
        "--verify-ui-runner",
        help="Verify UI runner for qa9: playwright/cypress/browser-use/agent-browser/midscene",
    ),
    verify_compat_browsers: Optional[str] = typer.Option(
        None,
        "--verify-compat-browsers",
        help="Verify compatibility browsers list (comma-separated).",
    ),
    verify_compat_devices: Optional[str] = typer.Option(
        None,
        "--verify-compat-devices",
        help="Verify compatibility devices list (comma-separated).",
    ),
    verify_require_fresh_evidence: bool = typer.Option(
        False,
        "--verify-require-fresh-evidence/--no-verify-require-fresh-evidence",
        help="QA stage requires current run fresh evidence for matrix artifacts.",
    ),
    bridge_execute: bool = typer.Option(
        False,
        "--bridge-execute/--no-bridge-execute",
        help="Execute OMC/OMX/team bridge actions on workflow terminal state.",
    ),
    bridge_targets: str = typer.Option(
        "omc,omx,team",
        "--bridge-targets",
        help="Bridge execution targets: comma-separated subset of omc,omx,team.",
    ),
    bridge_timeout: int = typer.Option(
        120,
        "--bridge-timeout",
        min=10,
        help="Per-bridge command timeout in seconds when --bridge-execute is enabled.",
    ),
):
    """Start full product workflow"""
    project_root = Path(project) if project else Path.cwd()
    try:
        resolved_version = resolve_operational_docs_version(
            project_root,
            version,
            command_name="workflow start",
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    effective_hud = _resolve_hud_enforcement(
        version=resolved_version,
        hud_requested=bool(hud),
        command_name="workflow start",
    )
    force_double_confirmation = _requires_hud_double_confirmation(resolved_version)

    # Ensure directories exist
    ensure_output_dirs(project_root, resolved_version)
    run_id = generate_run_id(project_root)
    started_at = now_iso()
    skip_stages = {
        normalize_workflow_stage(x.strip())
        for x in (skip.split(",") if skip else [])
        if x.strip()
    }
    predicted = build_next_stage_trace(
        feature=feature,
        version=resolved_version,
        run_id=run_id,
        next_stage="prd",
        context="workflow.start",
    )
    base_state: dict[str, Any] = {
        "run_id": run_id,
        "workflow": "workflow.start",
        "mode": "auto" if auto else "manual",
        "feature": feature,
        "version": resolved_version,
        "prototype_enabled": bool(with_prototype),
        "status": "running" if auto else "planned",
        "started_at": started_at,
        "events": [{"event": "workflow_started", "ts": started_at}],
        "llm_prompts": [predicted],
        "token_usage": merge_token_usage({}, predicted),
        "tool_calls": [{"name": "workflow.next_stage.predict", "args": {"next_stage": "prd"}}],
    }
    save_run_state(
        project_root,
        run_id,
        base_state,
    )
    _write_execution_governance_artifacts(
        project_root=project_root,
        version=resolved_version,
        run_id=run_id,
        feature=feature,
        workflow_status="running" if auto else "planned",
    )
    _record_debug_feedback(
        project_root=project_root,
        source="workflow.start",
        goal=feature,
        intent="workflow",
        confidence=0.92,
        boundary_state="in_scope",
        recommended_command="beacon workflow start ...",
        executed=True,
        exit_code=0,
        note=f"auto={auto}",
        run_id=run_id,
        extra={"version": resolved_version, "auto": bool(auto)},
    )

    typer.echo(f"Starting Beacon Workflow: {feature}")
    typer.echo(f"Project: {project_root}")
    typer.echo(f"Version: {resolved_version}")
    typer.echo(f"Run ID: {run_id}")
    typer.echo("\n" + "=" * 50)
    typer.echo("WORKFLOW STAGES")
    typer.echo("=" * 50)
    interactive_mode = _effective_interactive_mode(interactive)
    mode_label = "interactive" if interactive_mode else "non_interactive"
    stage_order = [name for name, _, _ in _workflow_stages(prototype_enabled=bool(with_prototype))]
    pending_stages = [stage for stage in stage_order if stage not in skip_stages]
    hud_snapshot_rel: str | None = None

    if effective_hud:
        hud_payload = _render_workflow_hud(
            project_root=project_root,
            run_id=run_id,
            feature=feature,
            version=resolved_version,
            mode=mode_label,
            progress=compute_workflow_progress(project_root, run_id=run_id),
            show_text=True,
        )
        hud_snapshot_rel = str(_workflow_hud_snapshot_path(project_root, run_id).relative_to(project_root))
    else:
        hud_payload = {}

    run_auto = bool(auto)
    run_single_stage: Optional[str] = None
    if auto and interactive_mode:
        while True:
            _print_interactive_menu()
            append_lifecycle_event(
                project_root,
                run_id=run_id,
                stage="workflow",
                event="next_step_prompted",
                source="workflow.interactive",
                evidence_ref=[x for x in [hud_snapshot_rel] if x],
                details={"timeout_sec": confirm_timeout, "on_timeout": on_timeout},
            )
            action = _resolve_action_with_timeout(
                run_id=run_id,
                project_root=project_root,
                confirm_timeout=confirm_timeout,
                on_timeout=on_timeout,
            )
            if action == "show-blockers":
                blockers = hud_payload.get("blockers", {}) if isinstance(hud_payload, dict) else {}
                typer.echo(
                    f"Blockers => open_questions={blockers.get('blocking_open_questions', 0)}, "
                    f"conflicts={blockers.get('critical_conflicts', 0)}, "
                    f"reason_codes={blockers.get('latest_reason_codes', [])}"
                )
                continue
            if action == "feedback-apply":
                append_lifecycle_event(
                    project_root,
                    run_id=run_id,
                    stage="workflow",
                    event="feedback_apply_triggered",
                    source="workflow.interactive",
                    evidence_ref=[x for x in [hud_snapshot_rel] if x],
                    details={"action": action},
                )
                _write_interaction_memory(
                    project_root=project_root,
                    run_id=run_id,
                    action=action,
                    accepted=True,
                    hud_snapshot_rel=hud_snapshot_rel,
                    reason_codes=(hud_payload.get("blockers", {}) or {}).get("latest_reason_codes", []),
                )
                run_beacon_command(
                    ["feedback", "sync", run_id, "--project-root", str(project_root)],
                    project_root,
                    run_id=run_id,
                    stage="workflow",
                )
                if effective_hud:
                    hud_payload = _render_workflow_hud(
                        project_root=project_root,
                        run_id=run_id,
                        feature=feature,
                        version=resolved_version,
                        mode=mode_label,
                        progress=compute_workflow_progress(project_root, run_id=run_id),
                        show_text=True,
                    )
                continue
            if action == "pause":
                _write_interaction_memory(
                    project_root=project_root,
                    run_id=run_id,
                    action=action,
                    accepted=True,
                    hud_snapshot_rel=hud_snapshot_rel,
                    feature=feature,
                    version=resolved_version,
                )
                _pause_workflow_state(project_root, run_id, base_state, reason="interactive_pause")
                typer.echo("Workflow paused.")
                return
            if action == "abort":
                _write_interaction_memory(
                    project_root=project_root,
                    run_id=run_id,
                    action=action,
                    accepted=True,
                    hud_snapshot_rel=hud_snapshot_rel,
                    feature=feature,
                    version=resolved_version,
                )
                aborted = dict(base_state)
                aborted["status"] = "aborted"
                aborted["reason"] = "interactive_abort"
                aborted["ended_at"] = now_iso()
                _append_run_event(aborted, "workflow_aborted")
                save_run_state(project_root, run_id, aborted)
                typer.echo("Workflow aborted.")
                raise typer.Exit(1)
            accepted = _confirm_action(action, confirm_timeout=confirm_timeout)
            _write_interaction_memory(
                project_root=project_root,
                run_id=run_id,
                action=action,
                accepted=accepted,
                hud_snapshot_rel=hud_snapshot_rel,
                reason_codes=(hud_payload.get("blockers", {}) or {}).get("latest_reason_codes", []),
                feature=feature,
                version=resolved_version,
            )
            if not accepted:
                typer.echo("Action rejected. choose again.")
                continue
            if action == "single-step":
                run_auto = False
                run_single_stage = pending_stages[0] if pending_stages else None
            else:
                run_auto = True
            break

    display_stages = _workflow_stages(prototype_enabled=bool(with_prototype))
    for i, (stage, desc, _) in enumerate(display_stages, 1):
        if stage in skip_stages:
            typer.echo(f"{i}. {stage:12} - {desc} [SKIPPED]")
            append_lifecycle_event(
                project_root,
                run_id=run_id,
                stage=stage,
                event="stage_skipped",
                source="workflow.start",
                details={"feature": feature, "version": resolved_version},
            )
        elif run_auto or run_single_stage == stage:
            typer.echo(f"{i}. {stage:12} - {desc}")
        else:
            typer.echo(f"{i}. {stage:12} - {desc} [PENDING]")

    if not auto and not run_single_stage:
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage="workflow",
            event="workflow_planned",
            source="workflow.start",
            details={"feature": feature, "version": resolved_version, "skip_stages": sorted(skip_stages)},
        )
        planned = dict(base_state)
        planned["status"] = "planned"
        planned["reason"] = "awaiting_continue"
        _append_run_event(planned, "workflow_planned")
        save_run_state(project_root, run_id, planned)
        typer.echo("\nWorkflow planned (manual mode).")
        typer.echo("Run next step:")
        typer.echo(
            f"  beacon workflow continue --project {project_root} --version {resolved_version} --run-id {run_id}"
        )
        _record_v110_baseline(
            project_root=project_root,
            run_id=run_id,
            version=resolved_version,
            feature=feature,
            workflow_status="planned",
        )
        _write_execution_governance_artifacts(
            project_root=project_root,
            version=resolved_version,
            run_id=run_id,
            feature=feature,
            workflow_status="planned",
        )
        _print_next_step_selector(project_root=project_root, version=resolved_version, run_id=run_id, feature=feature)
        return

    if run_single_stage:
        execution_sequence = [run_single_stage]
    elif run_auto:
        execution_sequence = [stage for stage in stage_order if stage not in skip_stages]
    else:
        execution_sequence = []

    if force_double_confirmation and execution_sequence:
        if interactive_mode:
            second_ok = _confirm_second_execution_interactive(confirm_timeout=confirm_timeout)
            _write_interaction_memory(
                project_root=project_root,
                run_id=run_id,
                action="second-confirm",
                accepted=second_ok,
                hud_snapshot_rel=hud_snapshot_rel,
                feature=feature,
                version=resolved_version,
            )
            if not second_ok:
                _pause_workflow_state(project_root, run_id, base_state, reason="second_confirmation_rejected")
                typer.echo("Workflow paused: second confirmation rejected.")
                return
        else:
            first_ok = bool(confirm_execute)
            second_ok = bool(confirm_execute_second)
            _write_interaction_memory(
                project_root=project_root,
                run_id=run_id,
                action="non-interactive-confirm-1",
                accepted=first_ok,
                hud_snapshot_rel=hud_snapshot_rel,
                feature=feature,
                version=resolved_version,
            )
            _write_interaction_memory(
                project_root=project_root,
                run_id=run_id,
                action="non-interactive-confirm-2",
                accepted=second_ok,
                hud_snapshot_rel=hud_snapshot_rel,
                feature=feature,
                version=resolved_version,
            )
            if not (first_ok and second_ok):
                _pause_workflow_state(
                    project_root,
                    run_id,
                    base_state,
                    reason="non_interactive_double_confirmation_required",
                )
                typer.echo(
                    "✗ v1.1.0+ workflow execution requires HUD + double confirmation. "
                    "Use --confirm-execute --confirm-execute-second in non-interactive mode."
                )
                raise typer.Exit(2)

    for stage in execution_sequence:
        typer.echo(f"    → Running: {stage}")
        rc = _execute_stage(
            project_root=project_root,
            run_id=run_id,
            stage=stage,
            feature=feature,
            version=resolved_version,
            implementation_command=implementation_command,
            implementation_runner=implementation_runner,
            implementation_skill=implementation_skill,
            verify_scope=verify_scope,
            verify_config=verify_config,
            verify_ui_command=verify_ui_command,
            verify_api_curl_command=verify_api_curl_command,
            verify_unit_command=verify_unit_command,
            verify_smoke_command=verify_smoke_command,
            verify_require_ui_actions=verify_require_ui_actions,
            verify_qa_profile=verify_qa_profile,
            verify_qa_types=verify_qa_types,
            verify_qa_matrix_path=verify_qa_matrix_path,
            verify_ui_runner=verify_ui_runner,
            verify_compat_browsers=verify_compat_browsers,
            verify_compat_devices=verify_compat_devices,
            verify_require_fresh_evidence=verify_require_fresh_evidence,
        )
        if rc == 0:
            typer.echo(f"    ✓ {stage} completed")
            continue
        typer.echo(f"    ✗ {stage} failed (exit={rc})")
        blocked = load_run_state(project_root, run_id) or dict(base_state)
        blocked["status"] = "blocked"
        blocked["reason"] = f"{stage}_failed"
        blocked["ended_at"] = now_iso()
        _append_run_event(blocked, "workflow_blocked", stage=stage, exit_code=rc)
        save_run_state(project_root, run_id, blocked)
        _write_workflow_terminal_artifacts(
            project_root=project_root,
            version=resolved_version,
            run_id=run_id,
            feature=feature,
            workflow_status="blocked",
            reason=f"{stage}_failed",
        )
        _sync_terminal_manifest(project_root, version=resolved_version, run_id=run_id)
        _record_v110_baseline(
            project_root=project_root,
            run_id=run_id,
            version=resolved_version,
            feature=feature,
            workflow_status="blocked",
        )
        _write_execution_governance_artifacts(
            project_root=project_root,
            version=resolved_version,
            run_id=run_id,
            feature=feature,
            workflow_status="blocked",
        )
        if bridge_execute:
            _execute_bridge_actions(
                project_root=project_root,
                version=resolved_version,
                run_id=run_id,
                feature=feature,
                bridge_targets=bridge_targets,
                bridge_timeout=bridge_timeout,
            )
        _print_next_step_selector(project_root=project_root, version=resolved_version, run_id=run_id, feature=feature)
        raise typer.Exit(rc)

    final_progress = compute_workflow_progress(project_root, run_id=run_id)
    final_state = load_run_state(project_root, run_id) or dict(base_state)
    closure_complete = bool(final_progress.get("closure_complete"))
    gate_pass = bool(final_progress.get("gate_pass"))

    if closure_complete and gate_pass:
        typer.echo("\n" + "=" * 50)
        typer.echo("WORKFLOW COMPLETE")
        typer.echo("=" * 50)
        final_state["status"] = "completed"
        final_state["reason"] = "ok"
        final_state["ended_at"] = now_iso()
        _append_run_event(final_state, "workflow_completed")
        save_run_state(project_root, run_id, final_state)
        _write_workflow_terminal_artifacts(
            project_root=project_root,
            version=resolved_version,
            run_id=run_id,
            feature=feature,
            workflow_status="completed",
            reason="ok",
        )
        _sync_terminal_manifest(project_root, version=resolved_version, run_id=run_id)
        _record_v110_baseline(
            project_root=project_root,
            run_id=run_id,
            version=resolved_version,
            feature=feature,
            workflow_status="completed",
        )
        _write_execution_governance_artifacts(
            project_root=project_root,
            version=resolved_version,
            run_id=run_id,
            feature=feature,
            workflow_status="completed",
        )
        if bridge_execute:
            _execute_bridge_actions(
                project_root=project_root,
                version=resolved_version,
                run_id=run_id,
                feature=feature,
                bridge_targets=bridge_targets,
                bridge_timeout=bridge_timeout,
            )
        _print_next_step_selector(project_root=project_root, version=resolved_version, run_id=run_id, feature=feature)
        return

    final_state["status"] = "running"
    final_state["reason"] = "partial_progress"
    _append_run_event(
        final_state,
        "workflow_partial",
        missing_stages=final_progress.get("missing_closure_stages", []),
        gate_pass=gate_pass,
    )
    save_run_state(project_root, run_id, final_state)
    _record_v110_baseline(
        project_root=project_root,
        run_id=run_id,
        version=resolved_version,
        feature=feature,
        workflow_status="running",
    )
    _write_execution_governance_artifacts(
        project_root=project_root,
        version=resolved_version,
        run_id=run_id,
        feature=feature,
        workflow_status="running",
    )
    typer.echo(
        "○ Workflow partial: "
        f"missing={final_progress.get('missing_closure_stages', [])}, "
        f"gate_pass={gate_pass}"
    )


@app.command("continue")
def continue_workflow(  # noqa: A003
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature filter"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Explicit run id"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Continue until release"),
    interactive: Optional[bool] = typer.Option(
        None,
        "--interactive/--no-interactive",
        help="Interactive mode (default: auto detect TTY)",
    ),
    hud: bool = typer.Option(
        True,
        "--hud/--no-hud",
        help="Render workflow HUD before execution (v1.1.0+ always on).",
    ),
    confirm_execute: bool = typer.Option(
        False,
        "--confirm-execute",
        help="Non-interactive first confirmation for execution (required in v1.1.0+).",
    ),
    confirm_execute_second: bool = typer.Option(
        False,
        "--confirm-execute-second",
        help="Non-interactive second confirmation for execution (required in v1.1.0+).",
    ),
    confirm_timeout: int = typer.Option(
        60,
        "--confirm-timeout",
        min=1,
        help="Interactive confirm timeout in seconds (EOF fallback).",
    ),
    on_timeout: str = typer.Option(
        "pause",
        "--on-timeout",
        help="Timeout behavior: pause|continue|abort",
    ),
    with_prototype: Optional[bool] = typer.Option(
        None,
        "--with-prototype/--no-with-prototype",
        help="Override whether this workflow run includes the optional prototype stage.",
    ),
    implementation_command: Optional[str] = typer.Option(
        None,
        "--implementation-command",
        help="Implementation stage command override",
    ),
    implementation_runner: Optional[str] = typer.Option(
        None,
        "--implementation-runner",
        help="Implementation stage runner override",
    ),
    implementation_skill: Optional[str] = typer.Option(
        None,
        "--implementation-skill",
        help="Implementation stage skill override for skill-capable runners",
    ),
    verify_scope: str = typer.Option("all", "--verify-scope", help="QA scope: ui/api-curl/unit/smoke/all/qa9"),
    verify_config: Optional[str] = typer.Option(None, "--verify-config", help="Verify config path"),
    verify_ui_command: Optional[str] = typer.Option(None, "--verify-ui-command", help="Verify UI command"),
    verify_api_curl_command: Optional[str] = typer.Option(None, "--verify-api-curl-command", help="Verify API curl command"),
    verify_unit_command: Optional[str] = typer.Option(None, "--verify-unit-command", help="Verify unit command"),
    verify_smoke_command: Optional[str] = typer.Option(None, "--verify-smoke-command", help="Verify smoke command"),
    verify_require_ui_actions: bool = typer.Option(
        False,
        "--verify-require-ui-actions/--no-verify-require-ui-actions",
        help="Require key UI action evidence in qa stage.",
    ),
    verify_qa_profile: str = typer.Option(
        "web-full",
        "--verify-qa-profile",
        help="Verify QA profile for qa9 scope: web-core/web-full/custom",
    ),
    verify_qa_types: Optional[list[str]] = typer.Option(
        None,
        "--verify-qa-types",
        help="Verify QA types for qa9 scope (comma-separated or repeatable).",
    ),
    verify_qa_matrix_path: Optional[str] = typer.Option(
        None,
        "--verify-qa-matrix-path",
        help="Verify QA9 matrix path (*.qa9-matrix.json).",
    ),
    verify_ui_runner: str = typer.Option(
        "playwright",
        "--verify-ui-runner",
        help="Verify UI runner for qa9: playwright/cypress/browser-use/agent-browser/midscene",
    ),
    verify_compat_browsers: Optional[str] = typer.Option(
        None,
        "--verify-compat-browsers",
        help="Verify compatibility browsers list (comma-separated).",
    ),
    verify_compat_devices: Optional[str] = typer.Option(
        None,
        "--verify-compat-devices",
        help="Verify compatibility devices list (comma-separated).",
    ),
    verify_require_fresh_evidence: bool = typer.Option(
        False,
        "--verify-require-fresh-evidence/--no-verify-require-fresh-evidence",
        help="QA stage requires current run fresh evidence for matrix artifacts.",
    ),
    bridge_execute: bool = typer.Option(
        False,
        "--bridge-execute/--no-bridge-execute",
        help="Execute OMC/OMX/team bridge actions on workflow terminal state.",
    ),
    bridge_targets: str = typer.Option(
        "omc,omx,team",
        "--bridge-targets",
        help="Bridge execution targets: comma-separated subset of omc,omx,team.",
    ),
    bridge_timeout: int = typer.Option(
        120,
        "--bridge-timeout",
        min=10,
        help="Per-bridge command timeout in seconds when --bridge-execute is enabled.",
    ),
):
    """Continue workflow from memory lifecycle progress and execute next stage(s)."""
    project_root = Path(project) if project else Path.cwd()
    version_raw = (version or "").strip().lower()
    version_filter = None if version_raw in {"", "auto", "latest"} else resolve_target_version(project_root, version)
    resolved_run_id = resolve_workflow_run_id(
        project_root,
        run_id=run_id,
        version=version_filter,
        feature=feature,
    )
    if not resolved_run_id:
        typer.echo("✗ No workflow run found for the given filters")
        raise typer.Exit(2)

    state = load_run_state(project_root, resolved_run_id) or {}
    if isinstance(with_prototype, bool):
        state["prototype_enabled"] = with_prototype
    run_feature = str(state.get("feature", "") or feature or "").strip()
    run_version = str(state.get("version", "") or resolve_target_version(project_root, version)).strip()
    if not run_feature:
        typer.echo("✗ Workflow run is missing feature metadata")
        raise typer.Exit(2)
    effective_hud = _resolve_hud_enforcement(
        version=run_version,
        hud_requested=bool(hud),
        command_name="workflow continue",
    )
    force_double_confirmation = _requires_hud_double_confirmation(run_version)
    _record_debug_feedback(
        project_root=project_root,
        source="workflow.continue",
        goal=run_feature,
        intent="resume",
        confidence=0.9,
        boundary_state="in_scope",
        recommended_command="beacon workflow continue ...",
        executed=True,
        exit_code=0,
        note=f"auto={auto}",
        run_id=resolved_run_id,
        extra={"version": run_version, "auto": bool(auto)},
    )
    resume_contract = build_resume_contract(project_root, run_id=resolved_run_id)
    checkpoint_ref = str(resume_contract.get("checkpoint_ref", "") or "")
    append_lifecycle_event(
        project_root,
        run_id=resolved_run_id,
        stage="workflow",
        event="resume_contract_restored",
        source="workflow.continue",
        evidence_ref=[checkpoint_ref] if checkpoint_ref else [],
        details={
            "failure_streak": resume_contract.get("failure_streak", 0),
            "escalation_level": resume_contract.get("escalation_level", "E0"),
            "required_next_action": resume_contract.get("required_next_action", "continue_current_plan"),
        },
    )

    progress = compute_workflow_progress(project_root, run_id=resolved_run_id)
    if progress.get("closure_complete") and progress.get("gate_pass"):
        typer.echo(f"✓ Workflow already complete: {resolved_run_id}")
        return

    mode_interactive = _effective_interactive_mode(interactive)
    mode_label = "interactive" if mode_interactive else "non_interactive"
    if effective_hud:
        hud_payload = _render_workflow_hud(
            project_root=project_root,
            run_id=resolved_run_id,
            feature=run_feature,
            version=run_version,
            mode=mode_label,
            progress=progress,
            show_text=True,
        )
        hud_snapshot_rel = str(_workflow_hud_snapshot_path(project_root, resolved_run_id).relative_to(project_root))
    else:
        hud_payload = {}
        hud_snapshot_rel = None

    next_stage = str(progress.get("next_stage") or "")
    prototype_enabled = bool(state.get("prototype_enabled"))
    stage_order = [name for name, _, _ in _workflow_stages(prototype_enabled=prototype_enabled)]
    if not next_stage and stage_order:
        next_stage = stage_order[0]

    run_auto = bool(auto)
    run_single_stage: Optional[str] = None

    if mode_interactive:
        while True:
            _print_interactive_menu()
            append_lifecycle_event(
                project_root,
                run_id=resolved_run_id,
                stage="workflow",
                event="next_step_prompted",
                source="workflow.interactive",
                evidence_ref=[x for x in [hud_snapshot_rel] if x],
                details={"timeout_sec": confirm_timeout, "on_timeout": on_timeout},
            )
            action = _resolve_action_with_timeout(
                run_id=resolved_run_id,
                project_root=project_root,
                confirm_timeout=confirm_timeout,
                on_timeout=on_timeout,
            )
            if action == "show-blockers":
                blockers = hud_payload.get("blockers", {}) if isinstance(hud_payload, dict) else {}
                typer.echo(
                    f"Blockers => open_questions={blockers.get('blocking_open_questions', 0)}, "
                    f"conflicts={blockers.get('critical_conflicts', 0)}, "
                    f"reason_codes={blockers.get('latest_reason_codes', [])}"
                )
                continue
            if action == "feedback-apply":
                append_lifecycle_event(
                    project_root,
                    run_id=resolved_run_id,
                    stage="workflow",
                    event="feedback_apply_triggered",
                    source="workflow.interactive",
                    evidence_ref=[x for x in [hud_snapshot_rel] if x],
                    details={"action": action},
                )
                _write_interaction_memory(
                    project_root=project_root,
                    run_id=resolved_run_id,
                    action=action,
                    accepted=True,
                    hud_snapshot_rel=hud_snapshot_rel,
                    reason_codes=(hud_payload.get("blockers", {}) or {}).get("latest_reason_codes", []),
                )
                run_beacon_command(
                    ["feedback", "sync", resolved_run_id, "--project-root", str(project_root)],
                    project_root,
                    run_id=resolved_run_id,
                    stage="workflow",
                )
                if effective_hud:
                    progress = compute_workflow_progress(project_root, run_id=resolved_run_id)
                    hud_payload = _render_workflow_hud(
                        project_root=project_root,
                        run_id=resolved_run_id,
                        feature=run_feature,
                        version=run_version,
                        mode=mode_label,
                        progress=progress,
                        show_text=True,
                    )
                continue
            if action == "pause":
                _write_interaction_memory(
                    project_root=project_root,
                    run_id=resolved_run_id,
                    action=action,
                    accepted=True,
                    hud_snapshot_rel=hud_snapshot_rel,
                    feature=run_feature,
                    version=run_version,
                )
                _pause_workflow_state(project_root, resolved_run_id, state, reason="interactive_pause")
                typer.echo("Workflow paused.")
                return
            if action == "abort":
                _write_interaction_memory(
                    project_root=project_root,
                    run_id=resolved_run_id,
                    action=action,
                    accepted=True,
                    hud_snapshot_rel=hud_snapshot_rel,
                    feature=run_feature,
                    version=run_version,
                )
                aborted = dict(state)
                aborted["status"] = "aborted"
                aborted["reason"] = "interactive_abort"
                aborted["ended_at"] = now_iso()
                _append_run_event(aborted, "workflow_aborted")
                save_run_state(project_root, resolved_run_id, aborted)
                typer.echo("Workflow aborted.")
                raise typer.Exit(1)
            accepted = _confirm_action(action, confirm_timeout=confirm_timeout)
            _write_interaction_memory(
                project_root=project_root,
                run_id=resolved_run_id,
                action=action,
                accepted=accepted,
                hud_snapshot_rel=hud_snapshot_rel,
                reason_codes=(hud_payload.get("blockers", {}) or {}).get("latest_reason_codes", []),
                feature=run_feature,
                version=run_version,
            )
            if not accepted:
                typer.echo("Action rejected. choose again.")
                continue
            if action == "single-step":
                run_auto = False
                run_single_stage = str(progress.get("next_stage") or next_stage or "")
            else:
                run_auto = True
            break

    typer.echo(f"Continuing workflow run: {resolved_run_id}")
    typer.echo(f"Feature: {run_feature}")
    typer.echo(f"Version: {run_version}")
    typer.echo(f"Next stage: {next_stage or 'none'}")
    typer.echo(f"Mode: {'auto' if run_auto else 'single-step'}")
    if int(resume_contract.get("failure_streak", 0) or 0) > 0:
        typer.echo(
            f"Resume contract: streak={resume_contract.get('failure_streak')} "
            f"level={resume_contract.get('escalation_level')} "
            f"next={resume_contract.get('required_next_action')}"
        )
        typer.echo(f"  hypothesis: {resume_contract.get('next_hypothesis') or '-'}")
        typer.echo(f"  blocker   : {resume_contract.get('current_blocker') or '-'}")

    if not next_stage and not run_auto and not run_single_stage:
        typer.echo("✗ Cannot resolve next stage from memory progress")
        raise typer.Exit(2)

    trace = build_next_stage_trace(
        feature=run_feature,
        version=run_version,
        run_id=resolved_run_id,
        next_stage=next_stage or "none",
        context="workflow.continue",
    )

    working_state = dict(state)
    working_state["status"] = "running"
    working_state.setdefault("started_at", now_iso())
    _append_llm_trace(working_state, trace)
    _append_run_event(working_state, "workflow_continue_started", next_stage=next_stage, auto=run_auto)
    save_run_state(project_root, resolved_run_id, working_state)

    if run_single_stage:
        stage_sequence = [run_single_stage]
    else:
        start_idx = stage_order.index(next_stage) if next_stage in stage_order else 0
        stage_sequence = stage_order[start_idx:] if run_auto else [next_stage]

    if force_double_confirmation and stage_sequence:
        if mode_interactive:
            second_ok = _confirm_second_execution_interactive(confirm_timeout=confirm_timeout)
            _write_interaction_memory(
                project_root=project_root,
                run_id=resolved_run_id,
                action="second-confirm",
                accepted=second_ok,
                hud_snapshot_rel=hud_snapshot_rel,
                feature=run_feature,
                version=run_version,
            )
            if not second_ok:
                _pause_workflow_state(
                    project_root,
                    resolved_run_id,
                    working_state,
                    reason="second_confirmation_rejected",
                )
                typer.echo("Workflow paused: second confirmation rejected.")
                return
        else:
            first_ok = bool(confirm_execute)
            second_ok = bool(confirm_execute_second)
            _write_interaction_memory(
                project_root=project_root,
                run_id=resolved_run_id,
                action="non-interactive-confirm-1",
                accepted=first_ok,
                hud_snapshot_rel=hud_snapshot_rel,
                feature=run_feature,
                version=run_version,
            )
            _write_interaction_memory(
                project_root=project_root,
                run_id=resolved_run_id,
                action="non-interactive-confirm-2",
                accepted=second_ok,
                hud_snapshot_rel=hud_snapshot_rel,
                feature=run_feature,
                version=run_version,
            )
            if not (first_ok and second_ok):
                _pause_workflow_state(
                    project_root,
                    resolved_run_id,
                    working_state,
                    reason="non_interactive_double_confirmation_required",
                )
                typer.echo(
                    "✗ v1.1.0+ workflow execution requires HUD + double confirmation. "
                    "Use --confirm-execute --confirm-execute-second in non-interactive mode."
                )
                raise typer.Exit(2)

    for stage in stage_sequence:
        stage_progress = compute_workflow_progress(project_root, run_id=resolved_run_id)
        stage_data = stage_progress.get("stages", {}).get(stage, {})
        if str(stage_data.get("status", "")) == "completed":
            typer.echo(f"    · {stage} already completed, skip")
            continue
        typer.echo(f"    → Running stage: {stage}")
        rc = _execute_stage(
            project_root=project_root,
            run_id=resolved_run_id,
            stage=stage,
            feature=run_feature,
            version=run_version,
            implementation_command=implementation_command,
            implementation_runner=implementation_runner,
            implementation_skill=implementation_skill,
            verify_scope=verify_scope,
            verify_config=verify_config,
            verify_ui_command=verify_ui_command,
            verify_api_curl_command=verify_api_curl_command,
            verify_unit_command=verify_unit_command,
            verify_smoke_command=verify_smoke_command,
            verify_require_ui_actions=verify_require_ui_actions,
            verify_qa_profile=verify_qa_profile,
            verify_qa_types=verify_qa_types,
            verify_qa_matrix_path=verify_qa_matrix_path,
            verify_ui_runner=verify_ui_runner,
            verify_compat_browsers=verify_compat_browsers,
            verify_compat_devices=verify_compat_devices,
            verify_require_fresh_evidence=verify_require_fresh_evidence,
        )
        if rc != 0:
            blocked = load_run_state(project_root, resolved_run_id) or working_state
            blocked["status"] = "blocked"
            blocked["reason"] = f"{stage}_failed"
            blocked["ended_at"] = now_iso()
            _append_run_event(blocked, "workflow_continue_blocked", stage=stage, exit_code=rc)
            save_run_state(project_root, resolved_run_id, blocked)
            _write_workflow_terminal_artifacts(
                project_root=project_root,
                version=run_version,
                run_id=resolved_run_id,
                feature=run_feature,
                workflow_status="blocked",
                reason=f"{stage}_failed",
            )
            _sync_terminal_manifest(project_root, version=run_version, run_id=resolved_run_id)
            _record_v110_baseline(
                project_root=project_root,
                run_id=resolved_run_id,
                version=run_version,
                feature=run_feature,
                workflow_status="blocked",
            )
            _write_execution_governance_artifacts(
                project_root=project_root,
                version=run_version,
                run_id=resolved_run_id,
                feature=run_feature,
                workflow_status="blocked",
            )
            if bridge_execute:
                _execute_bridge_actions(
                    project_root=project_root,
                    version=run_version,
                    run_id=resolved_run_id,
                    feature=run_feature,
                    bridge_targets=bridge_targets,
                    bridge_timeout=bridge_timeout,
                )
            typer.echo(f"    ✗ {stage} failed (exit={rc})")
            _print_next_step_selector(
                project_root=project_root,
                version=run_version,
                run_id=resolved_run_id,
                feature=run_feature,
            )
            raise typer.Exit(rc)
        typer.echo(f"    ✓ {stage} completed")

        refreshed = compute_workflow_progress(project_root, run_id=resolved_run_id)
        if not run_auto:
            missing = refreshed.get("missing_closure_stages", [])
            current = load_run_state(project_root, resolved_run_id) or working_state
            gate_pass = bool(refreshed.get("gate_pass"))
            should_complete = not missing and gate_pass
            current["status"] = "completed" if should_complete else "running"
            current["reason"] = "ok" if should_complete else "partial_progress"
            if should_complete:
                current["ended_at"] = now_iso()
            _append_run_event(current, "workflow_continue_step_done", stage=stage, missing_stages=missing)
            save_run_state(project_root, resolved_run_id, current)
            if should_complete:
                _write_workflow_terminal_artifacts(
                    project_root=project_root,
                    version=run_version,
                    run_id=resolved_run_id,
                    feature=run_feature,
                    workflow_status="completed",
                    reason="ok",
                )
                _sync_terminal_manifest(project_root, version=run_version, run_id=resolved_run_id)
                _record_v110_baseline(
                    project_root=project_root,
                    run_id=resolved_run_id,
                    version=run_version,
                    feature=run_feature,
                    workflow_status="completed",
                )
                _write_execution_governance_artifacts(
                    project_root=project_root,
                    version=run_version,
                    run_id=resolved_run_id,
                    feature=run_feature,
                    workflow_status="completed",
                )
                if bridge_execute:
                    _execute_bridge_actions(
                        project_root=project_root,
                        version=run_version,
                        run_id=resolved_run_id,
                        feature=run_feature,
                        bridge_targets=bridge_targets,
                        bridge_timeout=bridge_timeout,
                    )
            else:
                _record_v110_baseline(
                    project_root=project_root,
                    run_id=resolved_run_id,
                    version=run_version,
                    feature=run_feature,
                    workflow_status="running",
                )
                _write_execution_governance_artifacts(
                    project_root=project_root,
                    version=run_version,
                    run_id=resolved_run_id,
                    feature=run_feature,
                    workflow_status="running",
                )
            return

    final_progress = compute_workflow_progress(project_root, run_id=resolved_run_id)
    final_state = load_run_state(project_root, resolved_run_id) or working_state
    if final_progress.get("closure_complete") and final_progress.get("gate_pass"):
        final_state["status"] = "completed"
        final_state["reason"] = "ok"
        final_state["ended_at"] = now_iso()
        _append_run_event(final_state, "workflow_continue_completed")
        save_run_state(project_root, resolved_run_id, final_state)
        _write_workflow_terminal_artifacts(
            project_root=project_root,
            version=run_version,
            run_id=resolved_run_id,
            feature=run_feature,
            workflow_status="completed",
            reason="ok",
        )
        _sync_terminal_manifest(project_root, version=run_version, run_id=resolved_run_id)
        _record_v110_baseline(
            project_root=project_root,
            run_id=resolved_run_id,
            version=run_version,
            feature=run_feature,
            workflow_status="completed",
        )
        _write_execution_governance_artifacts(
            project_root=project_root,
            version=run_version,
            run_id=resolved_run_id,
            feature=run_feature,
            workflow_status="completed",
        )
        if bridge_execute:
            _execute_bridge_actions(
                project_root=project_root,
                version=run_version,
                run_id=resolved_run_id,
                feature=run_feature,
                bridge_targets=bridge_targets,
                bridge_timeout=bridge_timeout,
            )
        typer.echo("✓ Workflow closure complete")
        _print_next_step_selector(
            project_root=project_root,
            version=run_version,
            run_id=resolved_run_id,
            feature=run_feature,
        )
    else:
        final_state["status"] = "running"
        final_state["reason"] = "partial_progress"
        _append_run_event(
            final_state,
            "workflow_continue_partial",
            missing_stages=final_progress.get("missing_closure_stages", []),
            gate_pass=bool(final_progress.get("gate_pass")),
        )
        typer.echo(
            "○ Workflow partially continued; missing stages: "
            f"{final_progress.get('missing_closure_stages', [])}, "
            f"gate_pass={bool(final_progress.get('gate_pass'))}"
        )
        _record_v110_baseline(
            project_root=project_root,
            run_id=resolved_run_id,
            version=run_version,
            feature=run_feature,
            workflow_status="running",
        )
        _write_execution_governance_artifacts(
            project_root=project_root,
            version=run_version,
            run_id=resolved_run_id,
            feature=run_feature,
            workflow_status="running",
        )
    save_run_state(project_root, resolved_run_id, final_state)


@app.command("hud")
def hud_command(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version filter"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature filter"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Explicit run id"),
    json_output: bool = typer.Option(False, "--json", help="Output HUD as JSON only"),
):
    """Render workflow HUD snapshot without stage execution."""
    project_root = Path(project) if project else Path.cwd()
    version_raw = (version or "").strip().lower()
    version_filter = None if version_raw in {"", "auto", "latest"} else resolve_target_version(project_root, version)
    resolved_run_id = resolve_workflow_run_id(
        project_root,
        run_id=run_id,
        version=version_filter,
        feature=feature,
    )
    if not resolved_run_id:
        typer.echo("✗ No workflow run found for HUD")
        raise typer.Exit(2)

    state = load_run_state(project_root, resolved_run_id) or {}
    run_feature = str(state.get("feature", "") or feature or "").strip()
    run_version = str(state.get("version", "") or resolve_target_version(project_root, version)).strip()
    progress = compute_workflow_progress(project_root, run_id=resolved_run_id)
    payload = _render_workflow_hud(
        project_root=project_root,
        run_id=resolved_run_id,
        feature=run_feature,
        version=run_version,
        mode="non_interactive",
        progress=progress,
        show_text=not json_output,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature filter"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Explicit run id"),
):
    """Show workflow status"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    typer.echo("Beacon Workflow Status")
    typer.echo("=" * 40)

    beacon_dir = project_root / "docs" / "beacon" / resolved_version
    beacon_has_docs = beacon_dir.exists() and any(beacon_dir.rglob("*.md"))
    docs_dir = beacon_dir
    docs_type = "beacon"
    if not beacon_has_docs and not beacon_dir.exists():
        docs_dir = beacon_dir

    typer.echo(f"Using: docs/{docs_type}/{resolved_version}")

    # Check each stage
    stages = [
        ("prd", "prd"),
        ("user-story", "user-story"),
        ("test-case", "qa/test-cases"),
        ("prototype", "prototype"),
        ("implement", ".beacon/state"),
        ("qa", ".beacon/auto-test-status.json"),
        ("release", ".beacon/gate-report.json"),
    ]

    for stage, path in stages:
        stage_path = docs_dir / path
        if stage in {"implement", "qa", "release"}:
            stage_path = project_root / path
        if stage_path.exists():
            if stage_path.is_file():
                typer.echo(f"✓ {stage}: Completed")
            elif stage_path.is_dir():
                files = list(stage_path.glob("*.md")) + list(stage_path.glob("*/state.json"))
                if stage == "implement":
                    files.extend(list(stage_path.glob("implementation-*.json")))
                if files:
                    typer.echo(f"✓ {stage}: Completed ({len(files)} files)")
                else:
                    typer.echo(f"○ {stage}: Started (empty)")
            else:
                typer.echo(f"○ {stage}: Not started")
        else:
            typer.echo(f"○ {stage}: Not started")

    typer.echo("\nMemory Lifecycle Progress")
    typer.echo("-" * 40)
    progress = compute_workflow_progress(
        project_root,
        run_id=run_id,
        version=resolved_version,
        feature=feature,
    )
    resolved = progress.get("run_id")
    typer.echo(f"run_id: {resolved or 'N/A'}")
    if progress.get("feature"):
        typer.echo(f"feature: {progress.get('feature')}")
    if progress.get("version"):
        typer.echo(f"version: {progress.get('version')}")
    for stage in progress.get("workflow_stages", ["prd", "user-story", "test-case", "prototype", "implement", "qa", "release"]):
        item = progress.get("stages", {}).get(stage, {})
        typer.echo(f"{stage:12}: {item.get('status', 'not_started')}")
    typer.echo(f"next_stage   : {progress.get('next_stage') or 'none'}")
    typer.echo(f"closure_complete: {bool(progress.get('closure_complete'))}")
    typer.echo(f"gate_pass    : {bool(progress.get('gate_pass'))}")
    typer.echo(f"missing_stages : {progress.get('missing_closure_stages', [])}")


@app.command()
def gate(
    stage: Optional[str] = typer.Argument(
        None,
        help="Stage to check (prd/user-story/test-case/prototype/implement/qa/release)",
    ),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Run gate checks for stages (delegates to `beacon gate check`)."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    stages = (
        ["prd", "user-story", "test-case", "prototype", "implement", "qa", "release"]
        if not stage
        else [stage]
    )

    typer.echo("Beacon Workflow Gate (delegating to beacon gate check)")
    typer.echo("=" * 50)
    typer.echo(f"Target version: {resolved_version}")

    from .gate import _run_check_command

    highest_exit = 0
    for s in stages:
        typer.echo(f"\n--- {s.upper()} Gate ---")
        code = _run_check_command(
            stage=s,
            project_root=str(project_root),
            version=resolved_version,
        )
        if code != 0:
            highest_exit = max(highest_exit, code)

    typer.echo("\n" + "=" * 50)
    typer.echo("GATE RESULT: PASS" if highest_exit == 0 else "GATE RESULT: FAIL")
    if highest_exit != 0:
        raise typer.Exit(highest_exit)


@app.command()
def run(
    command: str = typer.Argument(..., help="Command to run (prd/user-story/test-case/prototype/implement/qa/release/etc)"),
    feature: Optional[str] = typer.Argument(None, help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    options: Optional[str] = typer.Option(None, "--options", "-o", help="Additional options as JSON string"),
):
    """Run any beacon subcommand from workflow"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    # Map command names to actual commands
    command_map = {
        "think": "think",
        "user-story": "user-story",
        "user_story": "user-story",
        "prd": "prd",
        "test-case": "test-case",
        "test_case": "test-case",
        "implement": "implement",
        "implementation": "implement",
        "qa": "qa",
        "verify": "qa",
        "analyze": "analyze",
        "brainstorm": "brainstorm",
        "design": "design",
        "jtbd": "jtbd",
        "kano": "kano",
        "moscow": "moscow",
        "roadmap": "roadmap",
        "persona": "persona",
        "version": "version",
        "doctor": "doctor",
        "status": "status",
        "help": "help",
        "report": "report",
        "debug": "debug",
        "auto-test": "auto-test",
        "auto_test": "auto-test",
        "release": "release",
        "api-design": "api-design",
        "api_design": "api-design",
        "data-dictionary": "data-dictionary",
        "data_dictionary": "data-dictionary",
        "ui-spec": "ui-spec",
        "prototype": "prototype",
        "ui_spec": "ui-spec",
        "save": "save",
        "recall": "recall",
        "remember": "remember",
        "team": "team",
    }

    cmd = command_map.get(command.lower(), command)

    def _parse_options(raw: Optional[str]) -> list[str]:
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            raise typer.BadParameter(f"--options must be valid JSON: {exc}") from exc

        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]

        if not isinstance(parsed, dict):
            raise typer.BadParameter("--options JSON must be object or array")

        option_args: list[str] = []

        raw_args = parsed.get("args")
        if isinstance(raw_args, list):
            option_args.extend(str(item) for item in raw_args if str(item).strip())
        elif isinstance(raw_args, str) and raw_args.strip():
            option_args.append(raw_args.strip())

        for key, value in parsed.items():
            if key == "args" or value is None:
                continue
            flag = f"--{str(key).strip().replace('_', '-')}"
            if isinstance(value, bool):
                if value:
                    option_args.append(flag)
                continue
            if isinstance(value, list):
                for item in value:
                    option_args.extend([flag, str(item)])
                continue
            option_args.extend([flag, str(value)])
        return option_args

    passthrough_subcommands: dict[str, set[str]] = {
        "think": {"start", "status", "confirm", "question", "conflict", "summarize"},
        "user-story": {"create", "list"},
        "prd": {"create", "list"},
        "test-case": {"create", "list", "show"},
        "implement": {"run", "dev-run", "team-run", "plan", "status", "team-plan"},
        "qa": {"run", "team-run", "team-plan", "status", "evolve"},
        "release": {"check", "create", "scorecard"},
        "help": {"show"},
    }
    default_action_map: dict[str, str] = {
        "think": "start",
        "user-story": "create",
        "prd": "create",
        "test-case": "create",
        "implement": "dev-run",
        "qa": "run",
        "release": "check",
    }

    feature_token = str(feature or "").strip()
    full_cmd = [cmd]
    if feature_token:
        known = passthrough_subcommands.get(cmd, set())
        if feature_token in known:
            full_cmd.append(feature_token)
        elif cmd in default_action_map:
            full_cmd.extend([default_action_map[cmd], feature_token])
        else:
            full_cmd.append(feature_token)

    extra_args = _parse_options(options)
    versioned_commands = {
        "think",
        "user-story",
        "prd",
        "test-case",
        "implement",
        "qa",
        "release",
        "help",
        "workflow",
        "status",
        "report",
    }
    if cmd in versioned_commands:
        full_cmd.extend(["--version", resolved_version])
    if extra_args:
        full_cmd.extend(extra_args)

    typer.echo(f"Running: beacon {' '.join(full_cmd)}")
    typer.echo(f"Project: {project_root}")

    # Run the command
    env = os.environ.copy()
    repo_root = str(_repo_root())
    existing_pythonpath = str(env.get("PYTHONPATH", "")).strip()
    env["PYTHONPATH"] = repo_root if not existing_pythonpath else os.pathsep.join([repo_root, existing_pythonpath])
    result = subprocess.run(
        [sys.executable, "-m", "beacon.main"] + full_cmd,
        cwd=project_root,
        env=env,
    )

    if result.returncode == 0:
        typer.echo(f"\n✓ Command completed successfully")
    else:
        typer.echo(f"\n✗ Command failed with code {result.returncode}")
        raise typer.Exit(result.returncode)


if __name__ == "__main__":
    app()
