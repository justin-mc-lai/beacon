"""Beacon implement command - execution adapter for implementation stage."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.artifact_paths import (
    change_docs_file,
    change_file_output,
    execution_file_candidates,
    execution_file_output,
    human_execution_file,
    machine_trace_file,
    qa_matrix_candidates,
)
from beacon.utils.branch_governance import evaluate_branch_governance
from beacon.utils.archive_governance import load_feature_archive_boundary
from beacon.utils.circuit_breaker import CircuitBreaker
from beacon.utils.artifact_update_obligations import write_artifact_update_obligations
from beacon.utils.change_surface import build_change_command
from beacon.utils.delivery_baseline import load_implementation_delivery_host
from beacon.utils.delivery_kernel import build_delivery_contract
from beacon.utils.execution_branch_contract import load_execution_branch_contract
from beacon.utils.git_alignment import (
    build_implement_branch_guard_payload,
    ensure_expected_worktree_lane,
    switch_to_expected_branch,
)
from beacon.utils.governance import evaluate_takeover_baseline_gate
from beacon.utils.implementation_plan import (
    build_task_ledger_alignment_payload,
    build_implementation_plan_gate_payload,
    compile_implementation_plan,
    ensure_implementation_git_workflow_contract,
    load_or_seed_implementation_git_workflow_contract,
    implementation_git_workflow_json_path,
    implementation_git_workflow_markdown_path,
    implementation_plan_json_path,
    implementation_plan_markdown_path,
    implementation_plan_progress_path,
    implementation_plan_supported,
    load_implementation_plan_progress,
    mark_implementation_plan_failed,
    mark_implementation_plan_started,
)
from beacon.utils.implementation_evidence import implementation_evidence_gate
from beacon.utils.global_boundaries import global_boundary_principle_summaries
from beacon.utils.implement_native import run_native_implementation
from beacon.utils.implement_adapters import (
    build_default_task_prompt,
    detect_adapter,
    discover_skill_adapters,
    format_template,
    load_beacon_config,
    resolve_adapter,
    resolve_default_runner,
)
from beacon.utils.learning_loop import write_requirement_rewrite_input
from beacon.utils.legacy_cutover import build_legacy_cutover_preflight
from beacon.utils.host_prompt_trace import record_host_prompt_trace
from beacon.utils.implement_prompt_boundary import evaluate_implement_prompt_boundary
from beacon.utils.material_audit import build_requirement_package_gate
from beacon.utils.prd_bootstrap import inspect_requirement_closure
from beacon.utils.feature_package import validate_feature_package
from beacon.utils.revision_delta import load_revision_delta
from beacon.utils.semantic_runtime import load_or_build_semantic_layer
from beacon.utils.skill_admission import admit_runtime_skill
from beacon.utils.project_metadata import resolve_project_metadata_view
from beacon.utils.prototype_support import (
    build_ui_ux_dev_route,
    design_result_adapter_status,
    feature_requires_design_result_binding,
    feature_requires_prototype,
    prototype_adapter_only_supported,
)
from beacon.utils.prototype_utils import prototype_files
from beacon.utils.program_admission import evaluate_program_next_action_admission
from beacon.utils.requirement_deepening import load_requirement_completeness, requirement_paths
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.ralph_runtime import (
    append_ralph_round,
    finalize_ralph_state,
    initialize_ralph_state,
    load_ralph_state,
    mark_ralph_handoff_required,
    save_ralph_state,
)
from beacon.utils.runtime import generate_run_id, now_iso, read_json, write_json
from beacon.utils.story_state import load_story_state
from beacon.utils.workspace_admission import (
    build_workspace_admission_branch_preflight,
    gate_workspace_admission_or_block,
    load_admission_contract,
    run_workspace_admit,
)
from beacon.utils.skill_decision_surface import attach_skill_decision_surface
from beacon.utils.subagent_readiness import (
    delegation_readiness_precheck,
    detect_host_runtime,
    runtime_context_not_required_precheck,
    runtime_context_precheck_required,
    runtime_readiness_precheck,
)
from beacon.utils.team_surface import write_implement_to_qa_handoff
from beacon.utils.truth_map import (
    evaluate_implement_version_governance_preflight,
    feature_package_authoritative,
    resolve_truth_read_refs,
    truth_map_supported,
)
from beacon.utils.v115_delivery import refresh_evidence_manifest
from beacon.utils.versioning import normalize_version, release_line_key, resolve_runtime_version, resolve_target_version
from beacon.utils.workflow_memory import (
    append_lifecycle_event,
    load_lifecycle_events,
    record_stage_writeback,
    resolve_workflow_run_id,
    write_stage_context,
)
from beacon.utils.writeback import record_implementation_writeback

app = typer.Typer(name="implement", help="Run implementation via configured skill adapters")


def _uses_compact_skill_names(version: str) -> bool:
    text = str(version or "").strip().lower().lstrip("v")
    parts: list[int] = []
    for raw in text.split(".")[:3]:
        digits = "".join(ch for ch in raw if ch.isdigit())
        parts.append(int(digits or "0"))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3]) >= (1, 6, 0)


def _with_implement_surface(
    payload: dict[str, Any],
    *,
    reason_code: str = "",
    recommended_command: str = "",
    blocked: bool | None = None,
) -> dict[str, Any]:
    blocked_value = bool(payload.get("status") == "blocked") if blocked is None else blocked
    return attach_skill_decision_surface(
        payload,
        stage="implement",
        reason_code=reason_code or str(payload.get("reason_code", "") or ""),
        recommended_command=recommended_command or str(payload.get("recommended_command", "") or ""),
        blocked=blocked_value,
        dual_read_required=True,
    )


def _with_task_alignment(payload: dict[str, Any], *, project_root: Path, version: str, feature: str) -> dict[str, Any]:
    if "task_alignment" in payload:
        return payload
    payload = dict(payload)
    payload["task_alignment"] = build_task_ledger_alignment_payload(project_root, version=version, feature=feature)
    return payload


def _implement_version_governance_preflight(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    if not truth_map_supported(version):
        return {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": version,
            "status": "not_applicable",
            "blocked": False,
            "reason_code": "",
        }
    git_workflow = load_or_seed_implementation_git_workflow_contract(project_root, version=version, feature=feature)
    return evaluate_implement_version_governance_preflight(
        project_root,
        version=version,
        feature=feature,
        git_workflow=git_workflow,
    )


def _blocked_implement_version_governance_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    preflight: dict[str, Any],
) -> dict[str, Any]:
    reason_code = str(preflight.get("reason_code") or "implement_metadata_contract_blocked")
    recommended_command = str(preflight.get("recommended_command") or "")
    return _with_implement_surface(
        {
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": reason_code,
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": version,
            "implement_version_governance_preflight": preflight,
            "recommended_command": recommended_command,
            "repair_commands": list(preflight.get("repair_commands") or []),
            "project_root": str(project_root),
        },
        reason_code=reason_code,
        recommended_command=recommended_command,
        blocked=True,
    )


def _blocked_legacy_cutover_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    preflight: dict[str, Any],
) -> dict[str, Any]:
    next_route = preflight.get("next_route") if isinstance(preflight.get("next_route"), dict) else {}
    return _with_implement_surface(
        {
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "legacy_cutover_required",
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": version,
            "legacy_cutover_preflight": preflight,
            "legacy_cutover": preflight.get("legacy_cutover", {}),
            "next_route": next_route,
            "recommended_command": str(next_route.get("command") or ""),
            "project_root": str(project_root),
        },
        reason_code="legacy_cutover_required",
        recommended_command=str(next_route.get("command") or ""),
        blocked=True,
    )


def _slug(text: str) -> str:
    return "-".join(str(text or "").strip().lower().split())


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _impl_root(project_root: Path, run_id: str) -> Path:
    return project_root / ".beacon" / "implement" / run_id


def _artifacts(project_root: Path, version: str, feature: str) -> dict[str, str]:
    slug = _slug(feature)
    base = project_root / "docs" / "beacon" / version
    if feature_package_authoritative(version):
        refs = resolve_truth_read_refs(
            project_root,
            version=version,
            feature=slug,
            consumer="implement",
        )["requirement_refs"]
        return {
            "source_of_truth_root": refs["source_of_truth_root"],
            "user_story": refs["user_story"],
            "prd": refs["prd"],
            "test_case": refs["test_case"],
            "truth": refs["truth"],
            "tests": refs["tests"],
            "tasks": refs["tasks"],
            "evidence": refs["evidence"],
            "ac_matrix": str(qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")[0].relative_to(project_root)),
            "prototype_dir": str((base / "prototype" / slug).relative_to(project_root)),
            "execution_dir": str((base / "execution").relative_to(project_root)),
        }
    return {
        "source_of_truth_root": f"docs/beacon/{version}",
        "user_story": str((base / "user-story" / f"{slug}.md").relative_to(project_root)),
        "prd": str((base / "prd" / f"{slug}.md").relative_to(project_root)),
        "test_case": str((base / "qa" / "test-cases" / f"{slug}.md").relative_to(project_root)),
        "ac_matrix": str(qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")[0].relative_to(project_root)),
        "prototype_dir": str((base / "prototype" / slug).relative_to(project_root)),
        "execution_dir": str((base / "execution").relative_to(project_root)),
    }


def _summary_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    return {
        "json": execution_file_output(project_root, version, f"implementation-summary-{slug}.json"),
        "md": human_execution_file(project_root, version, f"implementation-brief-{slug}.md"),
    }


def _trace_artifacts_from_payload(payload: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for key in (
        "plan_path",
        "plan_markdown_path",
        "progress_path",
        "git_workflow_ref",
        "git_workflow_markdown_ref",
        "branch_preflight_path",
        "plan_preflight_path",
        "request_path",
        "result_path",
        "stdout_path",
        "stderr_path",
        "implementation_plan",
        "implementation_marker",
        "implement_to_qa_handoff",
        "host_prompt_trace_ref",
    ):
        text = str(payload.get(key, "") or "").strip()
        if text and text not in refs:
            refs.append(text)
    for key in ("technical_archive", "change_document", "review_spec", "review_quality"):
        item = payload.get(key)
        if not isinstance(item, dict):
            continue
        for value in item.values():
            text = str(value or "").strip()
            if text and text not in refs:
                refs.append(text)
    return refs


def _sync_direct_implement_lifecycle_completion(
    project_root: Path,
    *,
    version: str,
    feature: str,
    evidence_ref: list[str],
) -> dict[str, Any]:
    workflow_run_id = str(os.environ.get("BEACON_WORKFLOW_RUN_ID", "") or "").strip()
    if workflow_run_id:
        return {"synced": False, "reason": "workflow_driver_owns_stage_events", "run_id": workflow_run_id}

    resolved_run_id = resolve_workflow_run_id(project_root, version=version, feature=feature) or ""
    if not resolved_run_id:
        return {"synced": False, "reason": "workflow_run_missing", "run_id": ""}

    stage = "implement"
    stage_events = load_lifecycle_events(project_root, run_id=resolved_run_id, stage=stage)
    event_names = {str(item.get("event", "") or "") for item in stage_events if isinstance(item, dict)}
    created_events: list[str] = []

    if "stage_started" not in event_names:
        append_lifecycle_event(
            project_root,
            run_id=resolved_run_id,
            stage=stage,
            event="stage_started",
            source="implement.run.sync",
            evidence_ref=evidence_ref,
            details={"feature": feature, "version": version, "sync_source": "implement.run"},
        )
        created_events.append("stage_started")

    if "stage_context_injected" not in event_names:
        write_stage_context(
            project_root,
            run_id=resolved_run_id,
            stage=stage,
            feature=feature,
        )
        created_events.append("stage_context_injected")

    append_lifecycle_event(
        project_root,
        run_id=resolved_run_id,
        stage=stage,
        event="stage_finished",
        source="implement.run.sync",
        evidence_ref=evidence_ref,
        details={"feature": feature, "version": version, "status": "completed", "sync_source": "implement.run"},
    )
    record_stage_writeback(
        project_root,
        run_id=resolved_run_id,
        stage=stage,
        feature=feature,
        evidence_ref=evidence_ref,
        status="completed",
    )
    created_events.extend(["stage_finished", "memory_writeback"])
    return {"synced": True, "reason": "workflow_run_backfilled", "run_id": resolved_run_id, "events": created_events}


def _capture_host_prompt_trace(
    *,
    project_root: Path,
    version: str,
    feature: str,
    host_prompt: str,
    surface: str,
    mapped_command: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    trace = record_host_prompt_trace(
        project_root,
        version=version,
        feature=feature,
        original_host_prompt=host_prompt,
        surface=surface,
        mapped_command=mapped_command,
        produced_artifacts=_trace_artifacts_from_payload(payload),
        route_status=str(payload.get("status", "") or "unknown"),
        run_id=str(payload.get("run_id", "") or ""),
        freeze_status="pass" if str(payload.get("version", "") or "").strip() and str(payload.get("status", "") or "") else "",
        team_phase=str(payload.get("status", "") or "") if str(payload.get("team_surface", "") or "") == "implement-team" else "",
        ralph_phase=str(payload.get("phase", "") or ""),
        stop_state=str(payload.get("stop_state", "") or ""),
        next_action=str(payload.get("next_action", "") or ""),
        reason_code=str(payload.get("reason_code", "") or ""),
        execution_sequence=[
            "freeze-pass",
            "implement-team-plan",
            "implement-team-run",
            "implement-ralph",
            "qa",
            "release",
        ],
    )
    if not trace:
        return {}
    run_id = str(payload.get("run_id", "") or "").strip()
    if run_id:
        state_path = project_root / ".beacon" / "implement" / run_id / "state.json"
        state_payload = read_json(state_path, {})
        if isinstance(state_payload, dict) and state_payload:
            state_payload["host_prompt_trace_ref"] = str(trace.get("json_ref", "") or "")
            state_payload["host_prompt_trace_markdown_ref"] = str(trace.get("markdown_ref", "") or "")
            write_json(state_path, state_payload)
    payload["host_prompt_trace"] = trace
    payload["host_prompt_trace_ref"] = str(trace.get("json_ref", "") or "")
    payload["host_prompt_trace_markdown_ref"] = str(trace.get("markdown_ref", "") or "")
    return trace


def _resolve_host_prompt_boundary(
    *,
    project_root: Path,
    version: str,
    feature: str,
    host_prompt: str,
) -> dict[str, Any]:
    prompt = str(host_prompt or "").strip()
    if not prompt:
        return {}
    payload = evaluate_implement_prompt_boundary(
        project_root,
        version=version,
        feature=feature,
        host_prompt=prompt,
    )
    return payload if isinstance(payload, dict) else {}


def _resolve_task_template_boundary(
    *,
    project_root: Path,
    version: str,
    feature: str,
    task_template: str,
) -> dict[str, Any]:
    template = str(task_template or "").strip()
    if not template:
        return {}
    boundary_input = re.sub(r"\{[^{}]+\}", " ", template)
    payload = _resolve_host_prompt_boundary(
        project_root=project_root,
        version=version,
        feature=feature,
        host_prompt=boundary_input,
    )
    if payload:
        payload["surface"] = "task_template"
        payload["prompt"] = template
    return payload


def _build_import_evidence_prompt_boundary(
    *,
    project_root: Path,
    version: str,
    feature: str,
    source_refs: list[str],
    changed_files: list[str],
    service_dirs: list[str],
    summary_ref: str,
) -> dict[str, Any]:
    refs = ", ".join([*source_refs, summary_ref])
    touched = ", ".join([*changed_files, *service_dirs])
    prompt = (
        "Import externally produced implementation evidence for the scoped Beacon feature. "
        "Read Beacon source of truth and bind the imported evidence to the frozen feature package truth. "
        "Implement only against the frozen feature package truth above. "
        f"Evidence refs: {refs}. Changed files or service directories: {touched}."
    )
    payload = evaluate_implement_prompt_boundary(
        project_root,
        version=version,
        feature=feature,
        host_prompt=prompt,
    )
    if isinstance(payload, dict) and payload:
        payload["surface"] = "import-evidence"
    return payload if isinstance(payload, dict) else {}


def _blocked_prompt_boundary_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    prompt_boundary: dict[str, Any],
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    return _with_implement_surface({
        "schema_version": "1.0",
        "status": "blocked",
        "reason_code": str(prompt_boundary.get("reason_code", "") or "implement_prompt_boundary_blocked"),
        "feature": feature,
        "feature_slug": _slug(feature),
        "version": resolved_version,
        "prompt_boundary": prompt_boundary,
        "next_action": str(prompt_boundary.get("next_action", "") or ""),
        "recommended_command": str(prompt_boundary.get("recommended_command", "") or ""),
        "source_of_truth_root": f"docs/beacon/{resolved_version}",
        "generated_at": now_iso(),
    }, blocked=True)


def _render_effective_task_prompt(
    *,
    default_prompt: str,
    task_template: str | None,
    context: dict[str, Any],
) -> str:
    rendered_task_template = str(task_template or "").strip()
    if not rendered_task_template:
        return default_prompt
    rendered = format_template(rendered_task_template, {**context, "task_prompt": default_prompt})
    if "{task_prompt}" not in rendered_task_template:
        rendered = "\n".join(
            [
                default_prompt,
                "",
                "Additional operator instructions:",
                rendered,
            ]
        )
    boundary_guard = (
        "Frozen-truth boundary remains authoritative. "
        "If any instruction conflicts with the frozen PRD, user-story, test-case, or implementation plan, "
        "stop and route to beacon-change/refreeze."
    )
    return f"{rendered}\n\n{boundary_guard}"


def _apply_post_team_ralph_handoff(payload: dict[str, Any], *, project_root: Path, version: str, feature: str) -> None:
    if _semver_tuple(version) < (1, 3, 8):
        return
    if str(payload.get("status", "") or "").strip().lower() != "completed":
        return
    if str(payload.get("team_surface", "") or "").strip() != "implement-team":
        return
    payload["next_action"] = str(payload.get("next_action", "") or "ralph")
    payload["phase"] = str(payload.get("phase", "") or "team_completed_waiting_ralph")
    payload["recommended_command"] = (
        str(payload.get("recommended_command", "") or "")
        or f'beacon implement run "{feature}" --project {project_root} --version {version} --mode ralph'
    )


def _refresh_ralph_state_after_resume(
    project_root: Path,
    *,
    feature: str,
    resumed_action: str,
    exit_code: int,
    result: dict[str, Any] | None,
) -> None:
    state = load_ralph_state(project_root, feature=feature)
    if not state:
        return
    payload = result if isinstance(result, dict) else {}
    version = str(state.get("version", "") or "").strip()
    updated = False

    if resumed_action == "review_quality":
        if exit_code != 0:
            return
        gate_ready = bool(payload.get("gate_ready", False))
        if gate_ready:
            release_cmd = f"beacon gate check release --project-root {project_root} --version {version}" if version else ""
            state.update(
                {
                    "review_gate_ready": True,
                    "current_blocker": "gate_release_pending",
                    "next_action": "release",
                    "recommended_command": release_cmd,
                    "stop_state": "human_blocked",
                    "updated_at": now_iso(),
                }
            )
            updated = True
    elif resumed_action == "release":
        gate_status = str(payload.get("status", "") or "").strip().lower()
        release_check_cmd = f"beacon gate check release --project-root {project_root} --version {version}" if version else ""
        requirement_gate = payload.get("requirement_completeness") if isinstance(payload.get("requirement_completeness"), dict) else {}
        if not requirement_gate and isinstance(payload.get("requirement_completeness_gate"), dict):
            requirement_gate = payload.get("requirement_completeness_gate")
        if gate_status == "pass":
            state.update(
                {
                    "gate_release_status": "pass",
                    "stop_state": "release_ready",
                    "current_blocker": "",
                    "next_action": "release",
                    "recommended_command": f"beacon release check {version} --project {project_root}" if version else "",
                    "updated_at": now_iso(),
                }
            )
            updated = True
        elif gate_status:
            requirement_blocked = (
                isinstance(requirement_gate, dict)
                and (
                    bool(requirement_gate.get("blocked"))
                    or str(requirement_gate.get("status") or "").strip().lower() == "blocked"
                )
            )
            requirement_handoff = requirement_gate.get("human_loop_handoff") if isinstance(requirement_gate.get("human_loop_handoff"), dict) else {}
            state.update(
                {
                    "gate_release_status": gate_status,
                    "stop_state": "human_blocked",
                    "current_blocker": str(requirement_gate.get("reason_code") or "gate_release_blocked") if requirement_blocked else "gate_release_blocked",
                    "next_action": "human_review" if requirement_blocked else "release",
                    "recommended_command": (
                        str(requirement_handoff.get("recommended_command") or requirement_gate.get("recommended_command") or "")
                        if requirement_blocked
                        else release_check_cmd
                    ),
                    "updated_at": now_iso(),
                }
            )
            updated = True

    if updated:
        save_ralph_state(project_root, feature=feature, payload=state)


def _reconcile_ralph_state_with_release_truth(project_root: Path, *, feature: str, state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(state, dict) or not state:
        return state
    version = str(state.get("version", "") or "").strip()
    if not version:
        return state
    stop_state = str(state.get("stop_state", "") or "").strip()
    current_blocker = str(state.get("current_blocker", "") or "").strip()
    if stop_state != "human_blocked" or current_blocker not in {"gate_release_blocked", "deep_loop_unclosed"}:
        return state

    release_scorecard = build_release_scorecard(project_root, version=version)
    release_ready = bool(release_scorecard.get("release_ready", False))
    gate = release_scorecard.get("gate") if isinstance(release_scorecard.get("gate"), dict) else {}
    gate_status = str(gate.get("status") or "").strip().lower()
    if release_ready:
        state.update(
            {
                "stop_state": "release_ready",
                "current_blocker": "",
                "next_action": "release",
                "recommended_command": f"beacon release check {version} --project {project_root}",
                "gate_release_status": "pass",
                "updated_at": now_iso(),
            }
        )
        save_ralph_state(project_root, feature=feature, payload=state)
        return state

    if gate_status == "pass":
        reason_codes = list(gate.get("reason_codes") or [])
        deep_release_supplement = (
            release_scorecard.get("deep_release_supplement")
            if isinstance(release_scorecard.get("deep_release_supplement"), dict)
            else {}
        )
        if bool(deep_release_supplement.get("blocked", False)):
            state.update(
                {
                    "current_blocker": str(deep_release_supplement.get("reason_code") or "deep_loop_unclosed"),
                    "next_action": "release",
                    "recommended_command": str(deep_release_supplement.get("recommended_command") or f'beacon deep run "{feature}" --project-root {project_root} --version {version} --json'),
                    "gate_release_status": "pass",
                    "updated_at": now_iso(),
                }
            )
            save_ralph_state(project_root, feature=feature, payload=state)
            return state
        if reason_codes:
            state.update(
                {
                    "current_blocker": str(reason_codes[0] or "release_not_ready"),
                    "gate_release_status": "pass",
                    "updated_at": now_iso(),
                }
            )
            save_ralph_state(project_root, feature=feature, payload=state)
    return state


def _technical_archive_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    return {
        "md": machine_trace_file(project_root, version, f"technical-implementation-{slug}.md", "implementation", slug),
        "json": execution_file_output(project_root, version, f"technical-implementation-{slug}.json"),
    }


def _change_document_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    return {
        "md": change_docs_file(project_root, version, f"{slug}.md"),
        "json": change_file_output(project_root, version, f"{slug}.json"),
    }


def _ralph_summary_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    return {
        "json": machine_trace_file(project_root, version, f"ralph-summary-{slug}.json", "ralph", slug),
        "md": machine_trace_file(project_root, version, f"ralph-summary-{slug}.md", "ralph", slug),
    }


def _ralph_round_paths(project_root: Path, version: str, feature: str, round_index: int) -> dict[str, Path]:
    slug = _slug(feature)
    round_name = f"round-{int(round_index):03d}"
    return {
        "json": machine_trace_file(project_root, version, f"ralph-round-{slug}-{round_name}.json", "ralph", slug),
        "md": machine_trace_file(project_root, version, f"ralph-round-{slug}-{round_name}.md", "ralph", slug),
    }


def _branch_preflight_path(run_id: str) -> Path:
    return Path(f".beacon/implement/{run_id}/branch-preflight.json")


def _git_commit(project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    text = str(release_line_key(version) or normalize_version(version) or version or "").strip().lstrip("v")
    try:
        major, minor, patch = text.split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _default_runner_for_version(project_root: Path, version: str) -> str:
    if _semver_tuple(version) >= (1, 3, 0):
        return "codex-subagents"
    configured = resolve_default_runner(project_root)
    if configured:
        return configured
    return "native-single"


def _normalize_mode(value: str | None) -> str:
    text = str(value or "").strip().lower()
    return text if text in {"single", "team", "ralph"} else ""


def _resolve_mode_runner(*, mode: str, requested_runner: str | None, project_root: Path, version: str) -> str | None:
    if requested_runner:
        return requested_runner
    if mode == "single":
        return "native-single"
    if mode in {"team", "ralph"}:
        return "codex-subagents"
    return _default_runner_for_version(project_root, version)


def _resolve_host_runtime_for_adapter(*, adapter_id: str, adapter: dict[str, Any], explicit_host_runtime: str | None) -> str:
    explicit = str(explicit_host_runtime or "").strip().lower()
    if explicit in {"codex", "claude"}:
        return explicit
    runtime_family = str(adapter.get("runtime_family", "") or "").strip().lower()
    if adapter_id == "codex-subagents" or runtime_family == "codex-native":
        return "codex"
    if runtime_family == "claude-code" or adapter_id == "gstack":
        return "claude"
    return detect_host_runtime(explicit_host_runtime)


def _requires_host_native_prechecks(*, adapter_id: str, adapter: dict[str, Any], mode: str) -> bool:
    adapter_type = str(adapter.get("adapter_type", "") or "").strip().lower()
    runtime_family = str(adapter.get("runtime_family", "") or "").strip().lower()
    if adapter_type == "handoff":
        return False
    return bool(mode in {"team", "ralph"} or adapter_id == "codex-subagents" or runtime_family == "claude-code")


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and str(value).strip():
        return [str(value).strip()]
    return []


def _requirement_closure_preflight(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    if _semver_tuple(resolved_version) < (1, 4, 0):
        return {
            "enabled": False,
            "status": "pass",
            "reason_code": "",
            "feature": feature,
            "version": resolved_version,
        }
    if feature_package_authoritative(resolved_version):
        validation = validate_feature_package(project_root, version=resolved_version, feature=feature)
        blocked = str(validation.get("status") or "").strip().lower() != "pass"
        refs = resolve_truth_read_refs(
            project_root,
            version=resolved_version,
            feature=feature,
            consumer="implement-plan",
        )["requirement_refs"]
        return {
            "enabled": True,
            "status": "blocked" if blocked else "pass",
            "blocked": blocked,
            "reason_code": "feature_package_validation_failed" if blocked else "",
            "recommended_command": (
                build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="feature-package-validation-failed",
                )
                if blocked
                else ""
            ),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "authority_state": "feature_package_authoritative",
            "truth_authority": "markdown_feature_package",
            "requirement_refs": refs,
            "validation": validation,
        }

    inspection = inspect_requirement_closure(
        project_root,
        feature=feature,
        version=resolved_version,
    )
    verdict = str(inspection.get("closure_verdict") or "").strip().lower()
    readiness = str(inspection.get("readiness_verdict") or "").strip().lower()
    blocked = verdict in {"supplement_required", "drift_repair_required"} or readiness != "implementation_pending"
    reason_code = ""
    recommended_command = ""
    if verdict == "drift_repair_required":
        reason_code = "requirement_closure_drift_repair_required"
        recommended_command = build_change_command(
            feature=feature,
            project_root=project_root,
            version=resolved_version,
            reason="drift-repair-required",
        )
    elif blocked:
        reason_code = "requirement_closure_supplement_required"
        recommended_command = (
            f'beacon prd-bootstrap run "{feature}" --desc "补齐 requirement closure" '
            f'--project-root {project_root} --version {resolved_version} --dry-run'
        )

    return {
        "enabled": True,
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": reason_code,
        "recommended_command": recommended_command,
        **inspection,
    }


def _automation_runtime_preflight(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    return {
        "enabled": True,
        "status": "retired",
        "blocked": False,
        "reason_code": "",
        "recommended_command": "beacon-loop goal",
        "feature": feature,
        "version": resolved_version,
        "runtime_path": "",
        "retired": True,
    }


def _run_auto_qa(project_root: Path, *, feature: str, version: str, extra_args: list[str]) -> tuple[int, dict[str, Any] | None]:
    cmd = [
        sys.executable,
        "-m",
        "beacon.main",
        "qa",
        "run",
        feature,
        "--project",
        str(project_root),
        "--version",
        version,
        "--json",
        *extra_args,
    ]
    result = subprocess.run(cmd, cwd=_repo_root(), capture_output=True, text=True)
    payload = None
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except Exception:  # noqa: BLE001
            payload = None
    return result.returncode, payload


def _run_beacon_json_command(project_root: Path, command: str) -> tuple[int, dict[str, Any] | None]:
    rendered = str(command or "").strip()
    if not rendered:
        return 2, None
    if "--json" not in rendered:
        rendered = f"{rendered} --json"
    result = subprocess.run(rendered, cwd=_repo_root(), shell=True, capture_output=True, text=True)
    payload = None
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except Exception:  # noqa: BLE001
            payload = None
    return result.returncode, payload


def _run_auto_qa_sequence(
    project_root: Path,
    *,
    feature: str,
    version: str,
    extra_args: list[str],
    follow_handoff: bool,
    max_rounds: int,
) -> tuple[int, dict[str, Any]]:
    history: list[dict[str, Any]] = []
    qa_exit, qa_payload = _run_auto_qa(project_root, feature=feature, version=version, extra_args=extra_args)
    history.append(
        {
            "step": "qa-run",
            "round": 1,
            "exit_code": qa_exit,
            "payload": qa_payload,
        }
    )
    final_exit = qa_exit
    final_payload = qa_payload
    previous_signature = ""
    rounds_completed = 1

    while follow_handoff and rounds_completed < max(1, int(max_rounds or 1)):
        feature_scorecard = final_payload.get("feature_scorecard") if isinstance(final_payload, dict) else {}
        if not isinstance(feature_scorecard, dict) or not feature_scorecard:
            break
        continue_decision = str(feature_scorecard.get("continue_decision") or "").strip()
        if continue_decision == "ready_for_release":
            break
        repair_handoff = feature_scorecard.get("repair_handoff") if isinstance(feature_scorecard.get("repair_handoff"), dict) else {}
        action = str(repair_handoff.get("action") or "").strip()
        command = str(repair_handoff.get("command") or "").strip()
        signature = json.dumps(
            {
                "continue_decision": continue_decision,
                "action": action,
                "command": command,
                "stop_reasons": feature_scorecard.get("stop_reasons", []),
                "missing_test_case_ids": (feature_scorecard.get("coverage_gap") or {}).get("missing_test_case_ids", []),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if not action or not command or signature == previous_signature:
            break
        previous_signature = signature
        if action not in {"test-case-create", "verify-run", "qa-run"}:
            break
        handoff_exit, handoff_payload = _run_beacon_json_command(project_root, command)
        history.append(
            {
                "step": action,
                "round": rounds_completed,
                "exit_code": handoff_exit,
                "payload": handoff_payload,
                "command": command,
            }
        )
        if handoff_exit != 0:
            final_exit = handoff_exit
            break
        if action == "qa-run":
            final_exit = handoff_exit
            final_payload = handoff_payload
            break
        rounds_completed += 1
        qa_exit, qa_payload = _run_auto_qa(project_root, feature=feature, version=version, extra_args=extra_args)
        history.append(
            {
                "step": "qa-run",
                "round": rounds_completed,
                "exit_code": qa_exit,
                "payload": qa_payload,
            }
        )
        final_exit = qa_exit
        final_payload = qa_payload

    return final_exit, {
        "enabled": True,
        "triggered": True,
        "args": extra_args,
        "follow_handoff": bool(follow_handoff),
        "max_rounds": int(max_rounds or 1),
        "exit_code": final_exit,
        "payload": final_payload,
        "history": history,
    }


def _render_ralph_round_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Beacon Ralph Round",
        "",
        f"- round: `{payload.get('round', '')}`",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- executor: `{payload.get('executor', '')}`",
        f"- implement_run_id: `{payload.get('run_id', '')}`",
        f"- continue_decision: `{payload.get('continue_decision', '')}`",
        f"- next_action: `{payload.get('next_action', '')}`",
        f"- stop_state: `{payload.get('stop_state', '')}`",
        f"- current_blocker: `{payload.get('current_blocker', '')}`",
        f"- recorded_at: `{payload.get('recorded_at', '')}`",
        "",
        "## Refs",
        f"- implementation_summary: `{payload.get('implementation_summary_ref', '')}`",
        f"- review_quality: `{payload.get('review_quality_ref', '')}`",
        f"- qa_scorecard: `{payload.get('qa_scorecard_ref', '')}`",
        f"- gate_release: `{payload.get('gate_release_ref', '')}`",
        f"- repair_handoff_command: `{payload.get('repair_handoff_command', '')}`",
    ]
    return "\n".join(lines) + "\n"


def _build_ralph_summary(auto_qa_payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = auto_qa_payload if isinstance(auto_qa_payload, dict) else {}
    qa_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
    feature_scorecard = qa_payload.get("feature_scorecard") if isinstance(qa_payload.get("feature_scorecard"), dict) else {}
    continue_decision = str(feature_scorecard.get("continue_decision", "") or "").strip()
    stop_state = "human_blocked"
    if continue_decision == "ready_for_release":
        stop_state = "release_ready"
    elif int(payload.get("max_rounds", 1) or 1) > 0 and len([item for item in payload.get("history", []) if isinstance(item, dict) and str(item.get("step", "")) == "qa-run"]) >= int(payload.get("max_rounds", 1) or 1):
        stop_state = "budget_exhausted"
    repair_handoff = feature_scorecard.get("repair_handoff") if isinstance(feature_scorecard.get("repair_handoff"), dict) else {}
    return {
        "enabled": True,
        "round_count": len([item for item in payload.get("history", []) if isinstance(item, dict) and str(item.get("step", "")) == "qa-run"]),
        "stop_state": stop_state,
        "continue_decision": continue_decision or "",
        "next_action": str((repair_handoff or {}).get("action", "") or ""),
        "recommended_command": str((repair_handoff or {}).get("command", "") or ""),
        "repair_handoff": repair_handoff,
        "history": payload.get("history", []),
    }


def _run_ralph_controller(  # noqa: PLR0913
    *,
    feature: str,
    project_root: Path,
    version: str,
    runner: str | None,
    skill: str | None,
    task_template: str | None,
    prompt_boundary: dict[str, Any] | None,
    timeout_sec: int | None,
    auto_switch_branch: bool | None,
    team_runtime: str | None,
    host_runtime: str | None,
    max_rounds: int,
) -> tuple[int, dict[str, Any]]:
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    requested_runner = None if str(runner or "").strip().lower() == "auto" else runner
    executor_mode = "single" if str(requested_runner or "").strip() == "native-single" else "team"
    controller_run_id = generate_run_id(project_root)
    detected_host_runtime = detect_host_runtime(host_runtime)
    initialize_ralph_state(
        project_root,
        feature=feature,
        version=resolved_version,
        run_id=controller_run_id,
        host_runtime=detected_host_runtime,
        runner=str(requested_runner or _resolve_mode_runner(mode=executor_mode, requested_runner=None, project_root=project_root, version=resolved_version) or ""),
    )

    # Ralph completion is determined only by structured review/QA/gate
    # artifacts. The circuit breaker remains as a safety guard for stuck loops.
    circuit_breaker = CircuitBreaker(
        no_progress_threshold=3,
        same_error_threshold=3,
        output_decline_threshold=3,
    )

    last_payload: dict[str, Any] = {}
    last_exit_code = 0
    controller_state: dict[str, Any] = load_ralph_state(project_root, feature=feature)

    for round_index in range(1, max(1, int(max_rounds or 1)) + 1):
        child_run_id = generate_run_id(project_root)
        child_runner = _resolve_mode_runner(
            mode=executor_mode,
            requested_runner=requested_runner,
            project_root=project_root,
            version=resolved_version,
        )
        exit_code, round_payload = run_implement_stage(
            feature=feature,
            project_root=project_root,
            version=resolved_version,
            mode=executor_mode,
            host_runtime=detected_host_runtime,
            run_id_override=child_run_id,
            runner=child_runner,
            skill=skill,
            task_template=task_template,
            prompt_boundary=prompt_boundary,
            dry_run=False,
            timeout_sec=timeout_sec,
            auto_review_spec=True,
            auto_review_quality=True,
            auto_qa=True,
            auto_qa_args=[],
            auto_qa_follow_handoff=False,
            auto_qa_max_rounds=1,
            auto_switch_branch=auto_switch_branch,
            team_runtime=team_runtime,
        )
        last_exit_code = exit_code
        last_payload = round_payload if isinstance(round_payload, dict) else {}

        # Check circuit breaker first (safety check)
        result_for_breaker = {
            "output": str(last_payload.get("summary", "") or last_payload.get("status", "") or ""),
            "error": str(last_payload.get("error", "") or ""),
        }
        is_stuck, stuck_reason = circuit_breaker.detect_stuck(round_index, result_for_breaker)
        if is_stuck:
            controller_state = mark_ralph_handoff_required(
                project_root,
                feature=feature,
                run_id=str(last_payload.get("run_id", "") or child_run_id),
                request_markdown=f"Circuit breaker triggered: {stuck_reason}\n\nPlease review the implementation and resolve the issue.",
            )
            append_ralph_round(
                project_root,
                feature=feature,
                round_payload={
                    "round": round_index,
                    "run_id": str(last_payload.get("run_id", "") or child_run_id),
                    "status": "circuit_breaker_triggered",
                    "circuit_breaker_reason": stuck_reason,
                    "recorded_at": now_iso(),
                },
            )
            break

        if str(last_payload.get("status", "") or "") == "handoff_required":
            controller_state = mark_ralph_handoff_required(
                project_root,
                feature=feature,
                run_id=str(last_payload.get("run_id", "") or child_run_id),
                request_markdown=str(last_payload.get("request_markdown", "") or ""),
            )
            append_ralph_round(
                project_root,
                feature=feature,
                round_payload={
                    "round": round_index,
                    "run_id": str(last_payload.get("run_id", "") or child_run_id),
                    "status": "handoff_required",
                    "recorded_at": now_iso(),
                },
            )
            break

        gate_release_info: dict[str, Any] | None = None
        auto_qa_payload = last_payload.get("auto_qa") if isinstance(last_payload.get("auto_qa"), dict) else {}
        auto_qa_feature_scorecard = (
            (auto_qa_payload.get("payload") or {}).get("feature_scorecard", {})
            if isinstance(auto_qa_payload.get("payload"), dict)
            else {}
        )
        review_quality_info = last_payload.get("review_quality") if isinstance(last_payload.get("review_quality"), dict) else {}
        if bool((review_quality_info.get("payload") or {}).get("gate_ready")) and str(auto_qa_feature_scorecard.get("continue_decision", "") or "") == "ready_for_release":
            gate_rc, gate_payload = _run_gate_release_command(project_root, resolved_version)
            gate_release_info = {"exit_code": gate_rc, "payload": gate_payload}

        evaluator_auto_qa_payload = dict(auto_qa_payload)
        # Ralph owns the outer loop budget. The QA payload is a single-round input
        # to the closure evaluator, so its inner max_rounds must not force
        # budget_exhausted after every QA run.
        evaluator_auto_qa_payload["max_rounds"] = 0
        controller_state = finalize_ralph_state(
            project_root,
            feature=feature,
            run_id=str(last_payload.get("run_id", "") or child_run_id),
            review_quality=review_quality_info,
            auto_qa=evaluator_auto_qa_payload,
            gate_release=gate_release_info or {},
        )
        auto_qa_feature_scorecard = (
            (auto_qa_payload.get("payload") or {}).get("feature_scorecard", {})
            if isinstance(auto_qa_payload.get("payload"), dict)
            else {}
        )
        round_paths = _ralph_round_paths(project_root, resolved_version, feature, round_index)
        round_ref_json = str(round_paths["json"].relative_to(project_root))
        round_payload_ref = {
            "round": round_index,
            "feature": feature,
            "version": resolved_version,
            "executor": executor_mode,
            "run_id": str(last_payload.get("run_id", "") or child_run_id),
            "implementation_summary_ref": str(
                ((last_payload.get("summary_paths") or {}).get("json") or "")
            ),
            "review_quality_ref": str(((review_quality_info.get("paths") or {}).get("json") or "")),
            "qa_scorecard_ref": str(((auto_qa_payload.get("payload") or {}).get("feature_scorecard_path") or "")),
            "gate_release_ref": str(((gate_release_info or {}).get("payload") or {}).get("release_scorecard_path", "")) if isinstance((gate_release_info or {}).get("payload"), dict) else "",
            "continue_decision": str(auto_qa_feature_scorecard.get("continue_decision", "") or ""),
            "next_action": str(controller_state.get("next_action", "") or ""),
            "stop_state": str(controller_state.get("stop_state", "") or ""),
            "current_blocker": str(controller_state.get("current_blocker", "") or ""),
            "repair_handoff_command": str((auto_qa_feature_scorecard.get("repair_handoff") or {}).get("command", "")) if isinstance(auto_qa_feature_scorecard.get("repair_handoff"), dict) else "",
            "recorded_at": now_iso(),
            "round_ref": round_ref_json,
            "review_quality": review_quality_info,
            "auto_qa": auto_qa_payload,
            "gate_release": gate_release_info or {},
        }
        write_json(round_paths["json"], round_payload_ref)
        _write_text(round_paths["md"], _render_ralph_round_markdown(round_payload_ref))
        controller_state = append_ralph_round(
            project_root,
            feature=feature,
            round_payload=round_payload_ref,
        )
        if str(controller_state.get("stop_state", "") or "") in {"release_ready", "budget_exhausted"}:
            break
        if str(controller_state.get("next_action", "") or "") != "implement":
            break

    ralph_paths = _ralph_summary_paths(project_root, resolved_version, feature)
    write_json(ralph_paths["json"], controller_state)
    _write_text(ralph_paths["md"], _render_ralph_summary_markdown(controller_state))
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(ralph_paths["json"].relative_to(project_root)),
            str(ralph_paths["md"].relative_to(project_root)),
        ],
        version=resolved_version,
    )

    payload = {
        "schema_version": "1.0",
        "run_id": controller_run_id,
        "feature": feature,
        "feature_slug": _slug(feature),
        "version": resolved_version,
        "mode": "ralph",
        "host_runtime": detected_host_runtime,
        "status": str(controller_state.get("status", "") or "completed"),
        "ralph": controller_state,
        "ralph_artifacts": {
            "json": str(ralph_paths["json"].relative_to(project_root)),
            "md": str(ralph_paths["md"].relative_to(project_root)),
        },
        "last_round": last_payload,
    }
    if isinstance(prompt_boundary, dict) and prompt_boundary:
        payload["prompt_boundary"] = prompt_boundary
    write_json(project_root / _branch_preflight_path(controller_run_id).with_name("state.json"), payload)
    return last_exit_code if str(controller_state.get("stop_state", "") or "") != "release_ready" else 0, payload


def _render_summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Beacon Implementation Summary",
        "",
        f"- feature: `{payload.get('feature')}`",
        f"- version: `{payload.get('version')}`",
        f"- run_id: `{payload.get('run_id')}`",
        f"- status: `{payload.get('status')}`",
        f"- runner: `{payload.get('runner')}`",
        f"- adapter_type: `{payload.get('adapter_type')}`",
    ]
    mode = str(payload.get("mode", "") or "").strip()
    if mode:
        lines.append(f"- mode: `{mode}`")
    host_runtime = str(payload.get("host_runtime", "") or "").strip()
    if host_runtime:
        lines.append(f"- host_runtime: `{host_runtime}`")
    skill = str(payload.get("skill", "") or "").strip()
    if skill:
        lines.append(f"- skill: `{skill}`")
    ralph = payload.get("ralph") if isinstance(payload.get("ralph"), dict) else {}
    if ralph:
        lines.append(f"- ralph_stop_state: `{ralph.get('stop_state', '')}`")
        lines.append(f"- ralph_round_count: `{ralph.get('round_count', 0)}`")
    change_document = payload.get("change_document") if isinstance(payload.get("change_document"), dict) else {}
    if change_document:
        lines.append(f"- change_document_md: `{change_document.get('md', '')}`")
        lines.append(f"- change_document_json: `{change_document.get('json', '')}`")
    lines.extend(["", "## Changed Files"])
    changed = payload.get("changed_files") if isinstance(payload.get("changed_files"), list) else []
    if changed:
        for item in changed:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    verification = payload.get("verification") if isinstance(payload.get("verification"), list) else []
    lines.extend(["", "## Verification"])
    if verification:
        for item in verification:
            if isinstance(item, dict):
                lines.append(f"- `{item.get('status', 'unknown')}`: {item.get('command', '')}")
    else:
        lines.append("- none")
    updates = payload.get("artifact_updates") if isinstance(payload.get("artifact_updates"), dict) else {}
    lines.extend(["", "## Artifact Updates"])
    if updates:
        for key, value in updates.items():
            if isinstance(value, dict):
                lines.append(f"- `{key}`: required={value.get('required')} reason={value.get('reason', '')}")
            else:
                lines.append(f"- `{key}`: {value}")
    else:
        lines.append("- none")
    requirement_traceability = payload.get("requirement_traceability") if isinstance(payload.get("requirement_traceability"), dict) else {}
    lines.extend(["", "## Requirement Traceability"])
    if requirement_traceability:
        for key in ("source_of_truth_root", "prd", "user_story", "test_case", "ac_matrix", "revision_id"):
            lines.append(f"- {key}: `{requirement_traceability.get(key, '')}`")
        lines.append(f"- implemented_item_ids: `{', '.join(_normalize_list(requirement_traceability.get('implemented_item_ids')))}`")
        lines.append(f"- implemented_task_ids: `{', '.join(_normalize_list(requirement_traceability.get('implemented_task_ids')))}`")
        lines.append(f"- verified_task_ids: `{', '.join(_normalize_list(requirement_traceability.get('verified_task_ids')))}`")
    else:
        lines.append("- none")
    delivery_surfaces = payload.get("delivery_surfaces") if isinstance(payload.get("delivery_surfaces"), dict) else {}
    lines.extend(["", "## Delivery Surfaces"])
    if delivery_surfaces:
        lines.append(f"- runtime_mode: `{delivery_surfaces.get('runtime_mode', '')}`")
        lines.append(f"- shipped_surfaces: `{', '.join(_normalize_list(delivery_surfaces.get('shipped_surfaces')))}`")
        lines.append(f"- partial_surfaces: `{', '.join(_normalize_list(delivery_surfaces.get('partial_surfaces')))}`")
        lines.append(f"- deferred_surfaces: `{', '.join(_normalize_list(delivery_surfaces.get('deferred_surfaces')))}`")
        lines.append(f"- downgrade_rationale: `{delivery_surfaces.get('downgrade_rationale', '')}`")
    else:
        lines.append("- none")
    revision_cleanup = payload.get("revision_cleanup") if isinstance(payload.get("revision_cleanup"), dict) else {}
    lines.extend(["", "## Revision Cleanup"])
    if revision_cleanup:
        lines.append(f"- cleanup_required: `{bool(revision_cleanup.get('cleanup_required', False))}`")
        lines.append(f"- cleanup_review_completed: `{bool(revision_cleanup.get('cleanup_review_completed', False))}`")
        lines.append(f"- source_revision_id: `{revision_cleanup.get('source_revision_id', '')}`")
        lines.append(f"- revision_delta_ref: `{revision_cleanup.get('revision_delta_ref', '')}`")
        lines.append(f"- removed_surfaces: `{', '.join(_normalize_list(revision_cleanup.get('removed_surfaces')))}`")
        lines.append(f"- retained_legacy_surfaces: `{', '.join(_normalize_list(revision_cleanup.get('retained_legacy_surfaces')))}`")
        lines.append(f"- cleanup_rationale: `{revision_cleanup.get('cleanup_rationale', '')}`")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def _render_ralph_summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Beacon Ralph Summary",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- run_id: `{payload.get('run_id', '')}`",
        f"- stop_state: `{payload.get('stop_state', '')}`",
        f"- round_count: `{payload.get('round_count', 0)}`",
        f"- failure_streak: `{payload.get('failure_streak', 0)}`",
        f"- no_delta_streak: `{payload.get('no_delta_streak', 0)}`",
        f"- next_action: `{payload.get('next_action', '')}`",
        f"- recommended_command: `{payload.get('recommended_command', '')}`",
        "",
        "## Rounds",
    ]
    rounds = payload.get("rounds") if isinstance(payload.get("rounds"), list) else []
    if not rounds:
        lines.append("- none")
    else:
        for item in rounds:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- round=`{item.get('round', '')}` run_id=`{item.get('run_id', '')}` "
                f"continue_decision=`{item.get('continue_decision', '')}` next_action=`{item.get('next_action', '')}` "
                f"round_ref=`{item.get('round_ref', '')}`"
            )
    implementation_order = payload.get("implementation_order") if isinstance(payload.get("implementation_order"), dict) else {}
    waves = implementation_order.get("waves") if isinstance(implementation_order.get("waves"), list) else []
    lines.extend(["", "## Implementation Order"])
    if not waves:
        lines.append("- none")
    else:
        for wave in waves:
            if not isinstance(wave, dict):
                continue
            lines.append(f"- wave `{wave.get('wave', '')}`")
            for item in wave.get("features", []):
                if not isinstance(item, dict):
                    continue
                slug = str(item.get("feature_slug", "") or "").strip()
                deps = ", ".join(str(dep) for dep in item.get("depends_on_features", []) if str(dep).strip())
                suffix = f" (depends_on={deps})" if deps else ""
                lines.append(f"  - `{slug}`{suffix}")
    return "\n".join(lines) + "\n"


def _v140_implementation_order(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    host = load_implementation_delivery_host(project_root, version=resolved_version)
    feature_order = [
        "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor",
        "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure",
        "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
    ]
    host_features = host.get("features") if isinstance(host.get("features"), list) else []
    ordered: list[dict[str, Any]] = []
    for slug in feature_order:
        row = next(
            (
                item
                for item in host_features
                if isinstance(item, dict) and str(item.get("feature_slug") or "") == slug
            ),
            None,
        )
        if not isinstance(row, dict):
            continue
        ordered.append(
            {
                "feature": str(row.get("feature") or ""),
                "feature_slug": slug,
                "depends_on_features": [str(dep) for dep in row.get("depends_on_features", []) if str(dep).strip()],
            }
        )
    if not ordered:
        return {"status": "missing", "feature_count": 0, "ordered_feature_slugs": [], "waves": []}
    waves = [
        {
            "wave": index + 1,
            "parallelizable": False,
            "features": [row],
        }
        for index, row in enumerate(ordered)
    ]
    return {
        "status": "analyzed",
        "feature_count": len(ordered),
        "ordered_feature_slugs": [row["feature_slug"] for row in ordered],
        "waves": waves,
    }


def _normalize_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _story_item_ids(story: dict[str, Any], *, kinds: set[str]) -> list[str]:
    out: list[str] = []
    for item in story.get("items", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("kind", "") or "") not in kinds:
            continue
        if not bool(item.get("required", True)):
            continue
        item_id = str(item.get("id", "") or "").strip().upper()
        if item_id:
            out.append(item_id)
    return out


def _modules_from_changed_files(changed_files: list[str]) -> list[str]:
    modules: set[str] = set()
    for item in changed_files:
        text = str(item).strip()
        if not text:
            continue
        parts = text.split("/")
        if len(parts) >= 2:
            modules.add("/".join(parts[:2]))
        elif parts:
            modules.add(parts[0])
    return sorted(modules)


def _dedupe_strings(values: list[Any]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _relative_ref(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _read_json_dict(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _implementation_design_truth(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    runtime_version = resolve_runtime_version(project_root, "auto")
    if prototype_adapter_only_supported(version, runtime_version=runtime_version):
        adapter_status = design_result_adapter_status(project_root, version, feature)
        required = feature_requires_design_result_binding(
            project_root,
            version,
            feature,
            runtime_version=runtime_version,
        )
        status_text = str(adapter_status.get("status") or "").strip().lower()
        paths = adapter_status.get("paths") if isinstance(adapter_status.get("paths"), dict) else {}
        if required or status_text == "ready":
            refs = {
                key: str(value)
                for key, value in paths.items()
                if key in {"binding_json", "binding_md"} and str(value).strip()
            }
            missing_refs = [] if status_text == "ready" else ["adapter_binding"]
            return {
                "schema_version": "1.0",
                "status": "ready" if status_text == "ready" else "missing",
                "feature": feature,
                "feature_slug": _slug(feature),
                "version": version,
                "docs_version": version,
                "runtime_version": runtime_version,
                "source_surface": "prototype-adapter",
                "consumption_surface": "implement",
                "mode": "design-result-adapter",
                "required": required,
                "allowed_inputs": [value for value in refs.values() if value],
                "blocked_human_inputs": ["Beacon-native wireframe generation"] if missing_refs else [],
                "refs": refs,
                "missing_refs": missing_refs,
                "reason_code": "" if status_text == "ready" else "design_result_adapter_binding_missing",
                "recommended_route": adapter_status.get("recommended_route")
                or build_ui_ux_dev_route(feature=feature, version=version, project_root=project_root, intent="review"),
                "recommended_command": str(adapter_status.get("recommended_command") or ""),
                "adapter_binding": adapter_status,
                "design_preset": "",
                "canonical_design_preset": "",
                "preset_source": "ui-ux-dev",
                "preset_family": "",
                "template_catalog_count": 0,
                "anti_ai_ui_contract": {},
                "template_layout_rules": [],
                "interaction_discipline_rules": [],
            }
        return {
            "schema_version": "1.0",
            "status": "not_applicable",
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": version,
            "docs_version": version,
            "runtime_version": runtime_version,
            "source_surface": "prototype-adapter",
            "consumption_surface": "implement",
            "mode": "design-result-adapter",
            "required": False,
            "allowed_inputs": [],
            "blocked_human_inputs": [],
            "refs": {},
            "missing_refs": [],
            "design_preset": "",
            "canonical_design_preset": "",
            "preset_source": "",
            "preset_family": "",
            "template_catalog_count": 0,
            "anti_ai_ui_contract": {},
            "template_layout_rules": [],
            "interaction_discipline_rules": [],
        }
    if not feature_requires_prototype(project_root, version, feature):
        return {
            "schema_version": "1.0",
            "status": "not_applicable",
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": version,
            "source_surface": "prototype",
            "consumption_surface": "implement",
            "mode": "",
            "allowed_inputs": [],
            "blocked_human_inputs": [],
            "refs": {},
            "missing_refs": [],
            "design_preset": "",
            "canonical_design_preset": "",
            "preset_source": "",
            "preset_family": "",
            "template_catalog_count": 0,
            "anti_ai_ui_contract": {},
            "template_layout_rules": [],
            "interaction_discipline_rules": [],
        }
    files = prototype_files(project_root, version, feature)
    implementation_index = _read_json_dict(files["implementation_index"])
    implementation_map = _read_json_dict(files["implementation_map"])
    style_path = files["design_artifacts_dir"] / "style-preset.json"
    lint_path = files["design_artifacts_dir"] / "design-lint-rules.json"
    style_preset = _read_json_dict(style_path)
    lint_rules = _read_json_dict(lint_path)
    style_payload = style_preset.get("payload") if isinstance(style_preset.get("payload"), dict) else {}
    lint_payload = lint_rules.get("payload") if isinstance(lint_rules.get("payload"), dict) else {}
    default_consumption_entry = (
        implementation_map.get("default_consumption_entry", {})
        if isinstance(implementation_map.get("default_consumption_entry"), dict)
        else {}
    )
    anti_ai_contract = style_payload.get("anti_ai_ui_contract") if isinstance(style_payload.get("anti_ai_ui_contract"), dict) else {}
    if not anti_ai_contract and isinstance(lint_payload.get("anti_ai_ui_contract"), dict):
        anti_ai_contract = lint_payload.get("anti_ai_ui_contract", {})
    allowed_inputs = [str(item).strip() for item in implementation_index.get("allowed_inputs", []) if str(item).strip()] if isinstance(implementation_index.get("allowed_inputs"), list) else []
    required_refs = {
        "implementation_index": files["implementation_index"],
        "implementation_map": files["implementation_map"],
        "style_preset": style_path,
        "design_lint_rules": lint_path,
    }
    refs = {
        key: _relative_ref(project_root, path)
        for key, path in required_refs.items()
        if path.exists()
    }
    missing_refs = [
        key
        for key, path in required_refs.items()
        if not path.exists()
    ]
    return {
        "schema_version": "1.0",
        "status": "ready" if not missing_refs else "missing",
        "feature": feature,
        "feature_slug": _slug(feature),
        "version": version,
        "source_surface": "prototype",
        "consumption_surface": "implement",
        "mode": str(implementation_index.get("mode", "") or default_consumption_entry.get("mode", "") or ""),
        "allowed_inputs": allowed_inputs,
        "blocked_human_inputs": [str(item).strip() for item in implementation_index.get("blocked_human_inputs", []) if str(item).strip()] if isinstance(implementation_index.get("blocked_human_inputs"), list) else [],
        "refs": refs,
        "missing_refs": missing_refs,
        "design_preset": str(style_payload.get("design_preset") or ""),
        "canonical_design_preset": str(style_payload.get("canonical_design_preset") or lint_payload.get("canonical_design_preset") or ""),
        "preset_source": str(style_payload.get("preset_source") or lint_payload.get("preset_source") or ""),
        "preset_family": str(style_payload.get("preset_family") or ""),
        "template_catalog_count": int(style_payload.get("template_catalog_count") or lint_payload.get("template_catalog_count") or 0),
        "anti_ai_ui_contract": anti_ai_contract,
        "template_layout_rules": [
            str(item).strip()
            for item in (style_payload.get("template_layout_rules") or lint_payload.get("template_layout_rules") or [])
            if str(item).strip()
        ],
        "interaction_discipline_rules": [
            str(item).strip()
            for item in (
                style_payload.get("interaction_discipline_rules")
                or anti_ai_contract.get("interaction_quality_rules")
                or lint_payload.get("interaction_quality_rules")
                or []
            )
            if str(item).strip()
        ],
    }


def _revision_cleanup_payload(*, result_payload: dict[str, Any], revision_delta: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(revision_delta, dict) or not revision_delta:
        return {}
    removed_requirement_surfaces = [
        {
            "id": str(item.get("id", "") or "").strip(),
            "text": str(item.get("text", "") or "").strip(),
            "label": f"{str(item.get('id', '') or '').strip()}: {str(item.get('text', '') or '').strip()}".strip(": "),
            "signature": str(item.get("signature", "") or "").strip(),
        }
        for item in _normalize_list(revision_delta.get("removed_requirement_surfaces"))
        if isinstance(item, dict)
    ]
    removed_surfaces = _dedupe_strings(
        _normalize_list(result_payload.get("removed_surfaces"))
        or _normalize_list(result_payload.get("deletions"))
    )
    retained_legacy_surfaces = _dedupe_strings(_normalize_list(result_payload.get("retained_legacy_surfaces")))
    cleanup_rationale = str(result_payload.get("cleanup_rationale", "") or "").strip()
    cleanup_required = bool(revision_delta.get("cleanup_required", False))
    cleanup_review_completed = bool(result_payload.get("cleanup_review_completed", False)) or not cleanup_required
    return {
        "schema_version": "1.0",
        "revision_id": str(revision_delta.get("revision_id", "") or ""),
        "source_revision_id": str(revision_delta.get("source_revision_id", "") or ""),
        "revision_delta_ref": str(revision_delta.get("json_ref", "") or ""),
        "revision_delta_markdown_ref": str(revision_delta.get("markdown_ref", "") or ""),
        "cleanup_required": cleanup_required,
        "cleanup_review_completed": cleanup_review_completed,
        "removed_requirement_surfaces": removed_requirement_surfaces,
        "removed_surfaces": removed_surfaces,
        "retained_legacy_surfaces": retained_legacy_surfaces,
        "cleanup_rationale": cleanup_rationale,
    }


def _feature_change_payload(
    *,
    feature: str,
    version: str,
    run_id: str,
    summary_ref: str,
    technical_ref: str,
    technical_payload: dict[str, Any],
) -> dict[str, Any]:
    added = _dedupe_strings(_normalize_list(technical_payload.get("additions")))
    revision_cleanup = technical_payload.get("revision_cleanup") if isinstance(technical_payload.get("revision_cleanup"), dict) else {}
    removed = _dedupe_strings(
        _normalize_list(technical_payload.get("deletions"))
        + _normalize_list(revision_cleanup.get("removed_surfaces"))
        + [
            str(item.get("label", "") or item.get("text", "") or item.get("id", "") or "").strip()
            for item in _normalize_list(revision_cleanup.get("removed_requirement_surfaces"))
            if isinstance(item, dict)
        ]
    )
    fixed = _dedupe_strings(
        _normalize_list(technical_payload.get("modifications"))
        + _normalize_list(technical_payload.get("refactors"))
    )
    changed_files = _dedupe_strings(_normalize_list(technical_payload.get("changed_files")))
    if not added and not removed and not fixed and changed_files:
        fixed = [f"Updated `{path}`" for path in changed_files]

    implementation_impact = _dedupe_strings(
        [f"Changed file: `{path}`" for path in changed_files]
        + [f"Module touched: `{path}`" for path in _normalize_list(technical_payload.get("modules_touched"))]
        + [f"Service touched: `{path}`" for path in _normalize_list(technical_payload.get("services"))]
        + (
            ["Database-related changes present"]
            if isinstance(technical_payload.get("db_changes"), dict) and not bool(technical_payload.get("db_changes", {}).get("none", True))
            else []
        )
        + (
            ["API-related changes present"]
            if isinstance(technical_payload.get("api_changes"), dict) and not bool(technical_payload.get("api_changes", {}).get("none", True))
            else []
        )
    )

    verification = []
    for item in _normalize_list(technical_payload.get("verification")):
        if isinstance(item, dict):
            status = str(item.get("status", "unknown") or "unknown").strip()
            command = str(item.get("command", "") or "").strip()
            verification.append(f"{status}: {command}".strip(": "))
        else:
            text = str(item or "").strip()
            if text:
                verification.append(text)

    traceability_refs = _dedupe_strings(
        [
            summary_ref,
            technical_ref,
            str((technical_payload.get("traceability") or {}).get("request_path", "") or ""),
            str((technical_payload.get("traceability") or {}).get("result_path", "") or ""),
            str((technical_payload.get("traceability") or {}).get("stdout_path", "") or ""),
            str((technical_payload.get("traceability") or {}).get("stderr_path", "") or ""),
        ]
    )

    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": str(technical_payload.get("feature_slug", "") or _slug(feature)),
        "version": version,
        "run_id": run_id,
        "status": "completed",
        "summary": str(technical_payload.get("implementation_scope_summary", "") or ""),
        "added": added,
        "removed": removed,
        "fixed": fixed,
        "implementation_impact": implementation_impact,
        "verification_status": verification,
        "traceability_refs": traceability_refs,
        "generated_at": now_iso(),
    }


def _render_feature_change_markdown(payload: dict[str, Any]) -> str:
    def _section(title: str, items: list[str]) -> list[str]:
        lines = ["", f"## {title}"]
        if not items:
            lines.append("- none")
            return lines
        for item in items:
            lines.append(f"- {item}")
        return lines

    lines = [
        "# Beacon Feature Change Document",
        "",
        f"- feature: `{payload.get('feature')}`",
        f"- feature_slug: `{payload.get('feature_slug')}`",
        f"- version: `{payload.get('version')}`",
        f"- run_id: `{payload.get('run_id')}`",
        f"- status: `{payload.get('status')}`",
        "",
        "## Scope",
        f"- {payload.get('summary') or 'No summary provided'}",
    ]
    lines.extend(_section("Added", [str(x) for x in _normalize_list(payload.get("added"))]))
    lines.extend(_section("Removed / Reduced", [str(x) for x in _normalize_list(payload.get("removed"))]))
    lines.extend(_section("Fixed", [str(x) for x in _normalize_list(payload.get("fixed"))]))
    lines.extend(_section("Implementation Impact", [str(x) for x in _normalize_list(payload.get("implementation_impact"))]))
    lines.extend(_section("Verification Status", [str(x) for x in _normalize_list(payload.get("verification_status"))]))
    lines.extend(_section("Traceability Refs", [f"`{x}`" for x in _normalize_list(payload.get("traceability_refs"))]))
    return "\n".join(lines) + "\n"


def _technical_archive_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    run_id: str,
    runner: str,
    skill: str,
    request_path: str,
    result_path: str,
    stdout_path: str,
    stderr_path: str,
    result_payload: dict[str, Any],
    revision_cleanup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    slug = _slug(feature)
    changed_files = [str(x) for x in _normalize_list(result_payload.get("changed_files")) if str(x).strip()]
    additions = [str(x) for x in _normalize_list(result_payload.get("additions")) if str(x).strip()]
    modifications = [str(x) for x in _normalize_list(result_payload.get("modifications")) if str(x).strip()]
    deletions = [str(x) for x in _normalize_list(result_payload.get("deletions")) if str(x).strip()]
    refactors = [str(x) for x in _normalize_list(result_payload.get("refactors")) if str(x).strip()]
    services = _normalize_list(result_payload.get("services"))
    assumptions = _normalize_list(result_payload.get("assumptions"))
    simplicity_notes = _normalize_list(result_payload.get("simplicity_notes"))
    scope_guard = result_payload.get("scope_guard") if isinstance(result_payload.get("scope_guard"), dict) else {}
    verification = _normalize_list(result_payload.get("verification"))
    revision_cleanup_payload = revision_cleanup if isinstance(revision_cleanup, dict) else {}
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "revision_id": "",
        "run_id": run_id,
        "implemented_at": now_iso(),
        "runner": runner,
        "skill": skill,
        "profile_id": str(result_payload.get("profile_id", "") or ""),
        "git_commit": _git_commit(project_root),
        "services": services,
        "boundary_principles": global_boundary_principle_summaries(),
        "implementation_scope_summary": str(result_payload.get("summary", "") or ""),
        "business_goal_summary": str(result_payload.get("business_goal_summary", "") or str(result_payload.get("summary", "") or "")),
        "acceptance_scope": _normalize_list(result_payload.get("acceptance_scope")),
        "assumptions": assumptions,
        "simplicity_notes": simplicity_notes,
        "scope_guard": {
            "in_scope": bool(scope_guard.get("in_scope", True)),
            "summary": str(scope_guard.get("summary", "") or ""),
            "allowed_paths": _normalize_list(scope_guard.get("allowed_paths")),
        },
        "changed_files": changed_files,
        "modules_touched": _modules_from_changed_files(changed_files),
        "additions": additions,
        "modifications": modifications,
        "deletions": deletions,
        "refactors": refactors,
        "data_operations": _normalize_list(result_payload.get("data_operations")),
        "db_changes": result_payload.get("db_changes") if isinstance(result_payload.get("db_changes"), dict) else {"none": True, "new_tables": [], "altered_tables": [], "indexes": [], "migrations": []},
        "cache_changes": _normalize_list(result_payload.get("cache_changes")),
        "event_contract_changes": _normalize_list(result_payload.get("event_contract_changes")),
        "api_changes": result_payload.get("api_changes") if isinstance(result_payload.get("api_changes"), dict) else {"none": True, "new_endpoints": [], "changed_endpoints": [], "removed_endpoints": []},
        "external_integrations": _normalize_list(result_payload.get("external_integrations")),
        "queue_or_job_changes": _normalize_list(result_payload.get("queue_or_job_changes")),
        "cron_changes": _normalize_list(result_payload.get("cron_changes")),
        "config_changes": _normalize_list(result_payload.get("config_changes")),
        "env_changes": _normalize_list(result_payload.get("env_changes")),
        "feature_flags": _normalize_list(result_payload.get("feature_flags")),
        "deployment_notes": _normalize_list(result_payload.get("deployment_notes")),
        "verification": verification,
        "verification_signals": {
            "count": len(verification),
            "has_acceptance_scope": bool(_normalize_list(result_payload.get("acceptance_scope"))),
            "has_assumptions": bool(assumptions),
        },
        "known_risks": _normalize_list(result_payload.get("known_risks")),
        "rollback_notes": _normalize_list(result_payload.get("rollback_notes")),
        "compatibility_notes": _normalize_list(result_payload.get("compatibility_notes")),
        "artifact_updates": result_payload.get("artifact_updates") if isinstance(result_payload.get("artifact_updates"), dict) else {},
        "revision_cleanup": revision_cleanup_payload,
        "traceability": {
            "request_path": request_path,
            "result_path": result_path,
            "stdout_path": stdout_path,
            "stderr_path": stderr_path,
        },
    }
    return payload


def _render_technical_archive_markdown(payload: dict[str, Any]) -> str:
    def _render_section(title: str, items: list[Any]) -> list[str]:
        lines = ["", f"## {title}"]
        if not items:
            lines.append("- none")
            return lines
        for item in items:
            lines.append(f"- {item}")
        return lines

    lines = [
        "# Beacon Technical Implementation Archive",
        "",
        f"- feature: `{payload.get('feature')}`",
        f"- feature_slug: `{payload.get('feature_slug')}`",
        f"- version: `{payload.get('version')}`",
        f"- run_id: `{payload.get('run_id')}`",
        f"- runner: `{payload.get('runner')}`",
        f"- profile_id: `{payload.get('profile_id')}`",
        f"- git_commit: `{payload.get('git_commit')}`",
        "",
        "## Traceability",
        f"- request_path: `{payload.get('traceability', {}).get('request_path', '')}`",
        f"- result_path: `{payload.get('traceability', {}).get('result_path', '')}`",
        f"- stdout_path: `{payload.get('traceability', {}).get('stdout_path', '')}`",
        f"- stderr_path: `{payload.get('traceability', {}).get('stderr_path', '')}`",
    ]
    lines.extend(_render_section("Services", [str(x) for x in payload.get("services", [])]))
    lines.extend(_render_section("Boundary Principles", [f"`{item.get('id', '')}`: {item.get('heading', '')}" for item in payload.get("boundary_principles", []) if isinstance(item, dict)]))
    lines.extend(_render_section("Assumptions", payload.get("assumptions", [])))
    lines.extend(_render_section("Simplicity Notes", payload.get("simplicity_notes", [])))
    lines.extend(_render_section("Changed Files", [f"`{x}`" for x in payload.get("changed_files", [])]))
    lines.extend(_render_section("Modules Touched", [f"`{x}`" for x in payload.get("modules_touched", [])]))
    lines.extend(_render_section("Additions", payload.get("additions", [])))
    lines.extend(_render_section("Modifications", payload.get("modifications", [])))
    lines.extend(_render_section("Deletions", payload.get("deletions", [])))
    lines.extend(_render_section("Refactors", payload.get("refactors", [])))
    lines.extend(_render_section("Data Operations", payload.get("data_operations", [])))
    lines.extend(_render_section("Config Changes", payload.get("config_changes", [])))
    lines.extend(_render_section("Env Changes", payload.get("env_changes", [])))
    lines.extend(_render_section("Feature Flags", payload.get("feature_flags", [])))
    lines.extend(_render_section("Queue / Job Changes", payload.get("queue_or_job_changes", [])))
    lines.extend(_render_section("Known Risks", payload.get("known_risks", [])))
    lines.extend(_render_section("Rollback Notes", payload.get("rollback_notes", [])))
    lines.extend(_render_section("Verification", [str(item) for item in payload.get("verification", [])]))
    revision_cleanup = payload.get("revision_cleanup") if isinstance(payload.get("revision_cleanup"), dict) else {}
    if revision_cleanup:
        lines.extend(
            [
                "",
                "## Revision Cleanup",
                f"- cleanup_required: `{bool(revision_cleanup.get('cleanup_required', False))}`",
                f"- cleanup_review_completed: `{bool(revision_cleanup.get('cleanup_review_completed', False))}`",
                f"- source_revision_id: `{revision_cleanup.get('source_revision_id', '')}`",
                f"- revision_delta_ref: `{revision_cleanup.get('revision_delta_ref', '')}`",
                f"- removed_surfaces: `{', '.join(_normalize_list(revision_cleanup.get('removed_surfaces')))}`",
                f"- retained_legacy_surfaces: `{', '.join(_normalize_list(revision_cleanup.get('retained_legacy_surfaces')))}`",
                f"- cleanup_rationale: `{revision_cleanup.get('cleanup_rationale', '')}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Scope Guard",
            f"- in_scope: `{payload.get('scope_guard', {}).get('in_scope', True)}`",
            f"- summary: `{payload.get('scope_guard', {}).get('summary', '')}`",
            f"- allowed_paths: `{', '.join(payload.get('scope_guard', {}).get('allowed_paths', []))}`",
            "",
            "## Verification Signals",
            json.dumps(payload.get("verification_signals", {}), ensure_ascii=False, indent=2),
        ]
    )
    lines.extend(["", "## DB Changes", json.dumps(payload.get("db_changes", {}), ensure_ascii=False, indent=2)])
    lines.extend(["", "## API Changes", json.dumps(payload.get("api_changes", {}), ensure_ascii=False, indent=2)])
    return "\n".join(lines) + "\n"


def _validate_result(payload: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not isinstance(payload, dict):
        return ["result payload is not an object"]
    for key in ("status", "summary"):
        if not str(payload.get(key, "")).strip():
            problems.append(f"{key} missing")
    changed = payload.get("changed_files")
    if changed is not None and not isinstance(changed, list):
        problems.append("changed_files must be a list")
    verification = payload.get("verification")
    if verification is not None and not isinstance(verification, list):
        problems.append("verification must be a list")
    assumptions = payload.get("assumptions")
    if assumptions is not None and not isinstance(assumptions, list):
        problems.append("assumptions must be a list")
    simplicity_notes = payload.get("simplicity_notes")
    if simplicity_notes is not None and not isinstance(simplicity_notes, list):
        problems.append("simplicity_notes must be a list")
    scope_guard = payload.get("scope_guard")
    if scope_guard is not None and not isinstance(scope_guard, dict):
        problems.append("scope_guard must be an object")
    updates = payload.get("artifact_updates")
    if updates is not None and not isinstance(updates, dict):
        problems.append("artifact_updates must be an object")
    cleanup_review_completed = payload.get("cleanup_review_completed")
    if cleanup_review_completed is not None and not isinstance(cleanup_review_completed, bool):
        problems.append("cleanup_review_completed must be a boolean")
    for key in ("removed_surfaces", "retained_legacy_surfaces"):
        value = payload.get(key)
        if value is not None and not isinstance(value, list):
            problems.append(f"{key} must be a list")
    for key in ("implemented_task_ids", "verified_task_ids", "blocked_task_ids", "failed_task_ids"):
        value = payload.get(key)
        if value is not None and not isinstance(value, list):
            problems.append(f"{key} must be a list")
    return problems


def _run_review_command(project_root: Path, version: str, feature: str, mode: str) -> tuple[int, dict[str, Any] | None]:
    cmd = [
        sys.executable,
        "-m",
        "beacon.main",
        "review",
        mode,
        feature,
        "--project",
        str(project_root),
        "--version",
        version,
        "--json",
    ]
    result = subprocess.run(cmd, cwd=_repo_root(), capture_output=True, text=True)
    payload = None
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except Exception:  # noqa: BLE001
            payload = None
    return result.returncode, payload


def _run_gate_release_command(project_root: Path, version: str) -> tuple[int, dict[str, Any] | None]:
    cmd = [
        sys.executable,
        "-m",
        "beacon.main",
        "gate",
        "check",
        "release",
        "--project-root",
        str(project_root),
        "--version",
        version,
        "--json",
    ]
    result = subprocess.run(cmd, cwd=_repo_root(), capture_output=True, text=True)
    payload = None
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except Exception:  # noqa: BLE001
            payload = None
    return result.returncode, payload


def _run_branch_preflight(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    auto_switch_branch: bool,
    require_clean_worktree_for_switch: bool,
    expected_branch: str = "",
    branch_prefix: str = "beacon/",
    base_branch: str = "main",
    git_roots: list[str] | None = None,
    direct_delivery_services: list[str] | None = None,
    branch_governance: dict[str, Any] | None = None,
    service_branch_map: dict[str, str] | None = None,
    service_worktree_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    feature_slug = _slug(feature)
    admission_branch_preflight = build_workspace_admission_branch_preflight(
        project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        cwd=Path.cwd(),
    )
    if admission_branch_preflight is not None:
        return admission_branch_preflight
    branch_preflight = build_implement_branch_guard_payload(
        project_root,
        version,
        require_clean_worktree_for_switch=require_clean_worktree_for_switch,
        expected_branch=expected_branch,
        branch_prefix=branch_prefix,
        base_branch=base_branch,
        git_roots=git_roots,
        direct_delivery_services=direct_delivery_services,
        service_branch_map=service_branch_map,
        service_worktree_map=service_worktree_map,
    )
    branch_preflight.update(
        {
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "generated_at": now_iso(),
        }
    )
    if isinstance(branch_governance, dict) and branch_governance:
        governance_payload = evaluate_branch_governance(
            {
                **branch_governance,
                "current_branch": str(branch_preflight.get("current_branch", "") or branch_governance.get("current_branch", "")),
                "target_branch": str(branch_preflight.get("expected_branch", "") or branch_governance.get("target_branch", "")),
                "current_worktree_path": str(branch_governance.get("current_worktree_path", "") or project_root),
            }
        )
        branch_preflight["branch_governance"] = governance_payload
        if governance_payload.get("blocked"):
            branch_preflight["blocked"] = True
            branch_preflight["status"] = "blocked"
            branch_preflight["summary"] = str(governance_payload.get("blocked_reason") or branch_preflight.get("summary") or "")
            branch_preflight["reason_codes"] = list(
                dict.fromkeys([*list(branch_preflight.get("reason_codes", [])), *list(governance_payload.get("reason_codes", []))])
            )
            if governance_payload.get("recommended_action"):
                branch_preflight["recommended_command"] = str(governance_payload.get("recommended_action") or "")
    if branch_preflight.get("blocked") and auto_switch_branch:
        dirty_worktree = bool(branch_preflight.get("dirty_worktree"))
        governance_payload = branch_preflight.get("branch_governance") if isinstance(branch_preflight.get("branch_governance"), dict) else {}
        if "branch_governance_worktree_required" in branch_preflight.get("reason_codes", []) and governance_payload.get("worktree_path"):
            worktree_attempt = ensure_expected_worktree_lane(
                project_root,
                str(branch_preflight.get("expected_branch", "") or ""),
                worktree_path=str(governance_payload.get("worktree_path", "") or ""),
                base_branch=base_branch,
            )
            branch_preflight["worktree_attempt"] = worktree_attempt
            if worktree_attempt.get("status") in {"created", "switched"}:
                branch_preflight["recommended_command"] = f"cd {worktree_attempt.get('worktree_path', '')} && beacon implement run \"{feature}\" --project {worktree_attempt.get('worktree_path', '')} --version {version}"
        elif not (dirty_worktree and require_clean_worktree_for_switch):
            switch_payload = switch_to_expected_branch(
                project_root,
                str(branch_preflight.get("expected_branch", "") or ""),
                create_if_missing=True,
                git_roots=git_roots,
            )
            branch_preflight["switch_attempt"] = switch_payload
            refreshed = build_implement_branch_guard_payload(
                project_root,
                version,
                require_clean_worktree_for_switch=require_clean_worktree_for_switch,
                expected_branch=expected_branch,
                branch_prefix=branch_prefix,
                base_branch=base_branch,
                git_roots=git_roots,
                direct_delivery_services=direct_delivery_services,
                service_branch_map=service_branch_map,
                service_worktree_map=service_worktree_map,
            )
            refreshed.update(
                {
                    "run_id": run_id,
                    "feature": feature,
                    "feature_slug": feature_slug,
                    "generated_at": now_iso(),
                    "switch_attempt": switch_payload,
                    "auto_switch_branch": True,
                }
            )
            if isinstance(branch_governance, dict) and branch_governance:
                refreshed_governance = evaluate_branch_governance(
                    {
                        **branch_governance,
                        "current_branch": str(refreshed.get("current_branch", "") or branch_governance.get("current_branch", "")),
                        "target_branch": str(refreshed.get("expected_branch", "") or branch_governance.get("target_branch", "")),
                        "current_worktree_path": str(branch_governance.get("current_worktree_path", "") or project_root),
                    }
                )
                refreshed["branch_governance"] = refreshed_governance
                if refreshed_governance.get("blocked"):
                    refreshed["blocked"] = True
                    refreshed["status"] = "blocked"
                    refreshed["summary"] = str(refreshed_governance.get("blocked_reason") or refreshed.get("summary") or "")
                    refreshed["reason_codes"] = list(
                        dict.fromkeys([*list(refreshed.get("reason_codes", [])), *list(refreshed_governance.get("reason_codes", []))])
                    )
                    if refreshed_governance.get("recommended_action"):
                        refreshed["recommended_command"] = str(refreshed_governance.get("recommended_action") or "")
            if switch_payload.get("status") == "failed" and refreshed.get("blocked"):
                refreshed["reason_codes"] = list(
                    dict.fromkeys([*list(refreshed.get("reason_codes", [])), "implement_branch_switch_failed"])
                )
            branch_preflight = refreshed
    return branch_preflight


def _branch_guard_inputs(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    from beacon.utils.project_governance import governance_md_authoritative

    config = load_beacon_config(project_root)
    implementation_cfg = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    branch_guard_cfg = implementation_cfg.get("branch_guard") if isinstance(implementation_cfg.get("branch_guard"), dict) else {}
    contract = load_or_seed_implementation_git_workflow_contract(project_root, version=version, feature=feature)
    execution_contract = load_execution_branch_contract(project_root, version=version, feature=feature)
    governance_md_active = governance_md_authoritative(project_root)
    execution_branch_override_keys = {
        "expected_branch",
        "branch_prefix",
        "base_branch",
        "require_clean_worktree_for_switch",
        "service_directories",
        "direct_delivery_services",
        "git_roots",
        "worktree_root",
        "service_branch_map",
        "service_worktree_map",
    }
    if isinstance(execution_contract, dict) and execution_contract.get("material_paths"):
        if governance_md_active:
            contract = {
                **contract,
                "execution_branch_contract": {
                    **execution_contract,
                    "branch_authority": "markdown_project_governance",
                    "execution_branch_override_blocked": True,
                },
            }
        else:
            contract = {
                **contract,
                **{
                    key: value
                    for key, value in execution_contract.items()
                    if key in execution_branch_override_keys and value not in ("", None, [], {})
                },
                "execution_branch_contract": execution_contract,
            }
    service_directories = _normalize_string_list(contract.get("service_directories") or contract.get("git_roots"))
    direct_delivery_services = _normalize_string_list(contract.get("direct_delivery_services") or service_directories)
    expected_branch = str(contract.get("expected_branch", "") or str(branch_guard_cfg.get("expected_branch", "") or "")).strip()
    branch_prefix = str(contract.get("branch_prefix", "") or str(branch_guard_cfg.get("branch_prefix", "beacon/") or "beacon/")).strip() or "beacon/"
    base_branch = str(contract.get("base_branch", "") or str(branch_guard_cfg.get("base_branch", "main") or "main")).strip() or "main"
    require_clean = bool(
        contract.get("require_clean_worktree_for_switch", branch_guard_cfg.get("require_clean_worktree_for_switch", True))
    )
    payload = {
        "git_workflow": contract,
        "execution_branch_contract": contract.get("execution_branch_contract", {}),
        "branch_governance": contract.get("branch_governance", {}),
        "expected_branch": expected_branch,
        "branch_prefix": branch_prefix,
        "base_branch": base_branch,
        "git_roots": service_directories,
        "direct_delivery_services": direct_delivery_services,
        "require_clean_worktree_for_switch": require_clean,
    }
    service_branch_map = contract.get("service_branch_map") if isinstance(contract.get("service_branch_map"), dict) else {}
    service_worktree_map = contract.get("service_worktree_map") if isinstance(contract.get("service_worktree_map"), dict) else {}
    if service_branch_map:
        payload["service_branch_map"] = {str(key): str(value) for key, value in service_branch_map.items() if str(key).strip() and str(value).strip()}
    if service_worktree_map:
        payload["service_worktree_map"] = {str(key): str(value) for key, value in service_worktree_map.items() if str(key).strip() and str(value).strip()}
    metadata_view = resolve_project_metadata_view(project_root, version=version)
    version_contract = metadata_view.get("version_contract") if isinstance(metadata_view.get("version_contract"), dict) else {}
    selected_service = str(metadata_view.get("selected_service") or "").strip()
    service_binding = metadata_view.get("selected_service_binding") if isinstance(metadata_view.get("selected_service_binding"), dict) else {}
    if governance_md_active and version_contract and selected_service and service_binding:
        per_service = version_contract.get("per_service_canonical_branch") if isinstance(version_contract.get("per_service_canonical_branch"), dict) else {}
        participating = version_contract.get("participating_services") if isinstance(version_contract.get("participating_services"), list) else []
        payload["expected_branch"] = str(per_service.get(selected_service) or metadata_view.get("selected_branch") or "").strip()
        if "/" in payload["expected_branch"]:
            payload["branch_prefix"] = payload["expected_branch"].split("/", 1)[0] + "/"
        git_roots = [
            str(item.get("repo_root") or "")
            for item in metadata_view.get("service_bindings", [])
            if isinstance(item, dict) and str(item.get("service_key") or "") in participating and str(item.get("repo_root") or "").strip()
        ]
        if git_roots:
            payload["git_roots"] = git_roots
        if participating:
            payload["direct_delivery_services"] = [str(item) for item in participating]
            if str(metadata_view.get("topology_kind") or "").strip() == "single_repo":
                repo_aliases = [Path(item).name for item in git_roots if str(item).strip()]
                payload["direct_delivery_services"] = list(dict.fromkeys(repo_aliases or payload["direct_delivery_services"]))
        if per_service:
            payload["service_branch_map"] = {str(key): str(value) for key, value in per_service.items() if str(key).strip() and str(value).strip()}
        if isinstance(metadata_view.get("branch_governance"), dict):
            payload["branch_governance"] = metadata_view.get("branch_governance", {})
        payload["metadata_contract"] = {
            "project_root": metadata_view.get("project_root", ""),
            "topology_kind": metadata_view.get("topology_kind", ""),
            "selected_service": selected_service,
            "governance_md_path": metadata_view.get("paths", {}).get("governance_md", ""),
            "authority": metadata_view.get("authority", "markdown_project_governance"),
        }
        return payload
    if version_contract and selected_service and service_binding:
        per_service = version_contract.get("per_service_canonical_branch") if isinstance(version_contract.get("per_service_canonical_branch"), dict) else {}
        selected_branch = str(per_service.get(selected_service) or "").strip()
        participating = version_contract.get("participating_services") if isinstance(version_contract.get("participating_services"), list) else []
        if selected_branch:
            payload["expected_branch"] = selected_branch
            if "/" in selected_branch:
                payload["branch_prefix"] = selected_branch.split("/", 1)[0] + "/"
        git_roots = [
            str(item.get("repo_root") or "")
            for item in metadata_view.get("service_bindings", [])
            if isinstance(item, dict) and str(item.get("service_key") or "") in participating and str(item.get("repo_root") or "").strip()
        ]
        if git_roots:
            payload["git_roots"] = git_roots
        if participating:
            payload["direct_delivery_services"] = [str(item) for item in participating]
            if str(metadata_view.get("topology_kind") or "").strip() == "single_repo":
                repo_aliases = [Path(item).name for item in git_roots if str(item).strip()]
                payload["direct_delivery_services"] = list(dict.fromkeys(repo_aliases or payload["direct_delivery_services"]))
        if isinstance(metadata_view.get("branch_governance"), dict):
            payload["branch_governance"] = metadata_view.get("branch_governance", {})
        payload["metadata_contract"] = {
            "project_root": metadata_view.get("project_root", ""),
            "topology_kind": metadata_view.get("topology_kind", ""),
            "selected_service": selected_service,
            "machine_path": metadata_view.get("paths", {}).get("machine", ""),
        }
    return payload


def run_implement_stage(  # noqa: PLR0913
    *,
    feature: str,
    project_root: Path,
    version: str,
    mode: str | None = None,
    host_runtime: str | None = None,
    run_id_override: str | None = None,
    runner: str | None = None,
    skill: str | None = None,
    task_template: str | None = None,
    prompt_boundary: dict[str, Any] | None = None,
    dry_run: bool = False,
    timeout_sec: int | None = None,
    auto_review_spec: bool | None = None,
    auto_review_quality: bool | None = None,
    auto_qa: bool | None = None,
    auto_qa_args: list[str] | None = None,
    auto_qa_follow_handoff: bool | None = None,
    auto_qa_max_rounds: int | None = None,
    auto_switch_branch: bool | None = None,
    team_runtime: str | None = None,
) -> tuple[int, dict[str, Any]]:
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    prompt_boundary_payload = prompt_boundary if isinstance(prompt_boundary, dict) else {}
    archive_boundary = load_feature_archive_boundary(project_root, version=resolved_version, feature=feature)
    if bool(archive_boundary.get("archived", False)):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "feature_archived_from_current_delivery",
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "archive_boundary": archive_boundary,
            "recommended_command": (
                f'beacon archive status --project-root {project_root} --version {resolved_version} --feature "{feature}" --json'
            ),
        }, blocked=True)
        return 2, payload
    cutover_preflight = build_legacy_cutover_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
        resume_intent="implement",
    )
    if bool(cutover_preflight.get("blocked")):
        return 2, _blocked_legacy_cutover_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            preflight=cutover_preflight,
        )
    requirement_package_gate = build_requirement_package_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        strict=True,
    )
    if str(requirement_package_gate.get("status") or "").lower() == "blocked":
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(requirement_package_gate.get("reason_code") or "requirement_package_contract_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "requirement_package_gate": requirement_package_gate,
            "recommended_command": str(
                requirement_package_gate.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-package-contract-blocked",
                )
            ),
        }, blocked=True)
        return 2, payload
    closure_preflight = _requirement_closure_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(closure_preflight.get("blocked")):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(closure_preflight.get("reason_code") or "requirement_closure_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "requirement_package_gate": requirement_package_gate,
            "closure_preflight": closure_preflight,
            "recommended_command": str(
                closure_preflight.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-closure-blocked",
                )
            ),
        }, blocked=True)
        return 2, payload
    automation_runtime_preflight = _automation_runtime_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(automation_runtime_preflight.get("blocked")):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(automation_runtime_preflight.get("reason_code") or "automation_runtime_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "requirement_package_gate": requirement_package_gate,
            "closure_preflight": closure_preflight,
            "automation_runtime_preflight": automation_runtime_preflight,
            "recommended_command": str(
                automation_runtime_preflight.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="automation-runtime-blocked",
                )
            ),
        }, blocked=True)
        return 2, payload
    workspace_admission_block = gate_workspace_admission_or_block(
        project_root,
        version=resolved_version,
        feature=feature,
        cwd=project_root,
    )
    if workspace_admission_block:
        payload = _with_implement_surface({
            **workspace_admission_block,
            "feature": feature,
            "feature_slug": _slug(feature),
            "requirement_package_gate": requirement_package_gate,
            "closure_preflight": closure_preflight,
        }, blocked=True)
        return 2, payload
    program_admission = evaluate_program_next_action_admission(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(program_admission.get("blocked")):
        run_id = str(run_id_override or "").strip() or generate_run_id(project_root)
        feature_slug = _slug(feature)
        impl_dir = _impl_root(project_root, run_id)
        impl_dir.mkdir(parents=True, exist_ok=True)
        reason_code = str(program_admission.get("reason_code") or "program_implement_admission_blocked")
        payload = _with_implement_surface(
            {
                "schema_version": "1.0",
                "run_id": run_id,
                "feature": feature,
                "feature_slug": feature_slug,
                "version": resolved_version,
                "status": "blocked",
                "reason_code": reason_code,
                "reason_codes": list(program_admission.get("reason_codes") or [reason_code]),
                "program_next_action_admission": program_admission,
                "requirement_package_gate": requirement_package_gate,
                "closure_preflight": closure_preflight,
                "recommended_command": str(program_admission.get("recommended_command") or ""),
                "diagnostic_only": True,
                "generated_at": now_iso(),
            },
            reason_code=reason_code,
            recommended_command=str(program_admission.get("recommended_command") or ""),
            blocked=True,
        )
        write_json(impl_dir / "state.json", payload)
        return 2, payload
    resolved_mode = _normalize_mode(mode)
    if resolved_mode == "ralph" and not dry_run and not str(run_id_override or "").strip():
        return _run_ralph_controller(
            feature=feature,
            project_root=project_root,
            version=resolved_version,
            runner=runner,
            skill=skill,
            task_template=task_template,
            prompt_boundary=prompt_boundary_payload,
            timeout_sec=timeout_sec,
            auto_switch_branch=auto_switch_branch,
            team_runtime=team_runtime,
            host_runtime=host_runtime,
            max_rounds=max(2, int(auto_qa_max_rounds or 2)),
        )
    config = load_beacon_config(project_root)
    implementation_cfg = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    branch_guard_cfg = implementation_cfg.get("branch_guard") if isinstance(implementation_cfg.get("branch_guard"), dict) else {}
    auto_review_spec = bool(implementation_cfg.get("auto_review_spec", True)) if auto_review_spec is None else auto_review_spec
    auto_review_quality = bool(implementation_cfg.get("auto_review_quality", False)) if auto_review_quality is None else auto_review_quality
    auto_qa = bool(implementation_cfg.get("auto_qa", False)) if auto_qa is None else auto_qa
    auto_qa_follow_handoff = (
        bool(implementation_cfg.get("auto_qa_follow_handoff", False))
        if auto_qa_follow_handoff is None
        else auto_qa_follow_handoff
    )
    auto_qa_max_rounds = int(implementation_cfg.get("auto_qa_max_rounds", 2) or 2) if auto_qa_max_rounds is None else int(auto_qa_max_rounds or 1)
    resolved_auto_qa_args = (
        _normalize_string_list(implementation_cfg.get("auto_qa_args"))
        if auto_qa_args is None
        else [str(item) for item in auto_qa_args if str(item).strip()]
    )
    auto_switch_branch = (
        bool(branch_guard_cfg.get("auto_switch", False))
        if auto_switch_branch is None
        else auto_switch_branch
    )
    if resolved_mode == "ralph":
        auto_qa = True
        auto_qa_follow_handoff = True
        auto_qa_max_rounds = max(int(auto_qa_max_rounds or 0), 3)
        auto_review_quality = True
    branch_guard_inputs = _branch_guard_inputs(project_root, version=resolved_version, feature=feature)
    require_clean_worktree_for_switch = bool(branch_guard_inputs.get("require_clean_worktree_for_switch", True))
    expected_branch_override = str(branch_guard_inputs.get("expected_branch", "") or "").strip()
    branch_prefix_override = str(branch_guard_inputs.get("branch_prefix", "beacon/") or "beacon/").strip() or "beacon/"
    base_branch_override = str(branch_guard_inputs.get("base_branch", "main") or "main").strip() or "main"
    workspace_git_roots = [str(item) for item in _normalize_string_list(branch_guard_inputs.get("git_roots"))]
    direct_delivery_services = [str(item) for item in _normalize_string_list(branch_guard_inputs.get("direct_delivery_services"))]
    git_workflow_contract = branch_guard_inputs.get("git_workflow", {}) if isinstance(branch_guard_inputs.get("git_workflow"), dict) else {}

    run_id = str(run_id_override or "").strip() or generate_run_id(project_root)
    feature_slug = _slug(feature)
    impl_dir = _impl_root(project_root, run_id)
    impl_dir.mkdir(parents=True, exist_ok=True)
    state_path = impl_dir / "state.json"
    if resolved_mode == "ralph":
        initialize_ralph_state(
            project_root,
            feature=feature,
            version=resolved_version,
            run_id=run_id,
            host_runtime=str(host_runtime or ""),
            runner=str(runner or ""),
        )
    takeover_gate = evaluate_takeover_baseline_gate(project_root, version=resolved_version)
    if str(takeover_gate.get("status", "") or "") == "blocked":
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": "takeover_baseline_required",
            "takeover_gate": takeover_gate,
            "git_workflow": git_workflow_contract,
            "generated_at": now_iso(),
        }, blocked=True)
        write_json(state_path, payload)
        return 2, payload
    branch_preflight_path = _branch_preflight_path(run_id)
    branch_preflight = _run_branch_preflight(
        project_root=project_root,
        version=resolved_version,
        run_id=run_id,
        feature=feature,
        auto_switch_branch=bool(auto_switch_branch),
        require_clean_worktree_for_switch=require_clean_worktree_for_switch,
        expected_branch=expected_branch_override,
        branch_prefix=branch_prefix_override,
        base_branch=base_branch_override,
        git_roots=workspace_git_roots,
        direct_delivery_services=direct_delivery_services,
        branch_governance=branch_guard_inputs.get("branch_governance", {}),
        service_branch_map=branch_guard_inputs.get("service_branch_map", {}),
        service_worktree_map=branch_guard_inputs.get("service_worktree_map", {}),
    )
    branch_preflight["git_workflow"] = git_workflow_contract
    branch_preflight["branch_preflight_path"] = str(branch_preflight_path)
    write_json(project_root / branch_preflight_path, branch_preflight)
    if branch_preflight.get("blocked"):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": "implement_branch_guard_blocked",
            "branch_preflight_path": str(branch_preflight_path),
            "branch_preflight": branch_preflight,
            "expected_branch": branch_preflight.get("expected_branch", ""),
            "current_branch": branch_preflight.get("current_branch", ""),
            "recommended_command": branch_preflight.get("recommended_command", ""),
            "git_workflow": git_workflow_contract,
            "generated_at": now_iso(),
        }, blocked=True)
        write_json(state_path, payload)
        return 2, payload

    plan_preflight_path = Path(f".beacon/implement/{run_id}/plan-preflight.json")
    implementation_plan_gate: dict[str, Any] = {}
    if implementation_plan_supported(resolved_version):
        implementation_plan_gate = build_implementation_plan_gate_payload(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
        )
        write_json(project_root / plan_preflight_path, implementation_plan_gate)
        if implementation_plan_gate.get("blocked"):
            payload = _with_implement_surface({
                "schema_version": "1.0",
                "run_id": run_id,
                "feature": feature,
                "feature_slug": feature_slug,
                "version": resolved_version,
                "status": "blocked",
                "reason_code": str(implementation_plan_gate.get("reason_code", "implementation_plan_missing") or "implementation_plan_missing"),
                "plan_preflight_path": str(plan_preflight_path),
                "plan_preflight": implementation_plan_gate,
                "branch_preflight_path": str(branch_preflight_path),
                "branch_preflight": branch_preflight,
                "recommended_command": str(implementation_plan_gate.get("recommended_command", "") or ""),
                "git_workflow": git_workflow_contract,
                "generated_at": now_iso(),
            }, blocked=True)
            write_json(state_path, payload)
            return 2, payload

    requested_runner = None if str(runner or "").strip().lower() == "auto" else runner
    requested_runner = _resolve_mode_runner(
        mode=resolved_mode,
        requested_runner=requested_runner,
        project_root=project_root,
        version=resolved_version,
    )
    adapter_id, adapter = resolve_adapter(project_root, requested_runner)
    if not adapter_id or not adapter:
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "runner_not_configured",
            "feature": feature,
            "version": resolved_version,
            "run_id": run_id,
            "feature_slug": feature_slug,
            "branch_preflight_path": str(branch_preflight_path),
            "branch_preflight": branch_preflight,
        }, blocked=True)
        write_json(state_path, payload)
        return 2, payload

    resolved_host_runtime = _resolve_host_runtime_for_adapter(
        adapter_id=adapter_id,
        adapter=adapter,
        explicit_host_runtime=host_runtime,
    )
    adapter_type = str(adapter.get("adapter_type", "")).strip()
    skill_admission: dict[str, Any] = {}
    if str(skill or "").strip():
        skill_admission = admit_runtime_skill(
            project_root,
            version=resolved_version,
            feature=feature,
            skill=str(skill or "").strip(),
            host_runtime=resolved_host_runtime,
            stage="implement",
            adapter_id=adapter_id,
            adapter_type=adapter_type,
        )
        if str(skill_admission.get("status", "")).strip().lower() != "pass":
            payload = _with_implement_surface({
                "schema_version": "1.0",
                "status": "blocked",
                "reason_code": str(skill_admission.get("reason_code", "skill_admission_blocked") or "skill_admission_blocked"),
                "feature": feature,
                "version": resolved_version,
                "run_id": run_id,
                "feature_slug": feature_slug,
                "host_runtime": resolved_host_runtime,
                "mode": resolved_mode or "",
                "runner": adapter_id,
                "adapter_type": adapter_type,
                "skill_admission": skill_admission,
                "recommended_command": str(skill_admission.get("recommended_command", "") or ""),
            }, blocked=True)
            write_json(state_path, payload)
            return 2, payload
    subagent_prechecks: dict[str, Any] = {
        "required": False,
        "host_runtime": resolved_host_runtime,
        "runtime_readiness": {},
        "delegation_readiness": {},
    }
    if _requires_host_native_prechecks(adapter_id=adapter_id, adapter=adapter, mode=resolved_mode):
        adapter_type_text = str(adapter.get("adapter_type", "") or "")
        runtime_family_text = str(adapter.get("runtime_family", "") or "")
        if runtime_context_precheck_required(
            version=resolved_version,
            adapter_id=adapter_id,
            adapter_type=adapter_type_text,
            runtime_family=runtime_family_text,
            mode=resolved_mode,
            runtime=team_runtime,
        ):
            runtime_precheck = runtime_readiness_precheck(project_root, host_runtime=resolved_host_runtime)
        else:
            runtime_precheck = runtime_context_not_required_precheck(
                host_runtime=resolved_host_runtime,
                detail=(
                    "Local native team runtime for this Beacon surface is driven by Beacon-managed execution artifacts; "
                    "project AGENTS/CLAUDE context files are not required to proceed."
                ),
            )
        delegation_precheck = delegation_readiness_precheck(
            project_root,
            feature=feature,
            version=resolved_version,
        )
        subagent_prechecks = {
            "required": True,
            "host_runtime": resolved_host_runtime,
            "runtime_readiness": runtime_precheck,
            "delegation_readiness": delegation_precheck,
        }
        if str(runtime_precheck.get("status", "")).strip().lower() != "pass":
            payload = _with_implement_surface({
                "schema_version": "1.0",
                "status": "blocked",
                "reason_code": str(runtime_precheck.get("reason_code", "runtime_not_ready") or "runtime_not_ready"),
                "feature": feature,
                "version": resolved_version,
                "run_id": run_id,
                "feature_slug": feature_slug,
                "host_runtime": resolved_host_runtime,
                "mode": resolved_mode or "",
                "subagent_prechecks": subagent_prechecks,
                "recommended_command": str(runtime_precheck.get("recommended_command", "") or ""),
            }, blocked=True)
            write_json(state_path, payload)
            return 2, payload
        if str(delegation_precheck.get("status", "")).strip().lower() != "pass":
            payload = _with_implement_surface({
                "schema_version": "1.0",
                "status": "blocked",
                "reason_code": str(delegation_precheck.get("reason_code", "delegation_not_ready") or "delegation_not_ready"),
                "feature": feature,
                "version": resolved_version,
                "run_id": run_id,
                "feature_slug": feature_slug,
                "host_runtime": resolved_host_runtime,
                "mode": resolved_mode or "",
                "subagent_prechecks": subagent_prechecks,
                "recommended_command": str(delegation_precheck.get("recommended_command", "") or ""),
            }, blocked=True)
            write_json(state_path, payload)
            return 2, payload

    artifacts = _artifacts(project_root, resolved_version, feature)
    semantic_layer = load_or_build_semantic_layer(
        project_root,
        version=resolved_version,
        feature=feature,
        stage="implement",
        run_id=run_id,
        persist=not dry_run,
    )
    semantic_artifacts = {
        key: str(value)
        for key, value in (semantic_layer.get("artifacts", {}) if isinstance(semantic_layer.get("artifacts"), dict) else {}).items()
        if str(value).strip()
    }
    if semantic_artifacts:
        artifacts = {**artifacts, **semantic_artifacts}
    default_design_bridge = (
        semantic_layer.get("default_design_bridge", {})
        if isinstance(semantic_layer.get("default_design_bridge"), dict)
        else {}
    )
    design_truth = _implementation_design_truth(project_root, version=resolved_version, feature=feature)
    design_truth_refs = design_truth.get("refs") if isinstance(design_truth.get("refs"), dict) else {}
    if bool(design_truth.get("required")) and str(design_truth.get("status") or "").strip().lower() != "ready":
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(design_truth.get("reason_code") or "design_truth_missing"),
            "design_truth": design_truth,
            "missing_refs": design_truth.get("missing_refs", []),
            "recommended_command": str(
                design_truth.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="design-truth-missing",
                )
            ),
            "branch_preflight_path": str(branch_preflight_path),
            "branch_preflight": branch_preflight,
            "plan_preflight_path": str(plan_preflight_path),
            "plan_preflight": implementation_plan_gate,
            "git_workflow": git_workflow_contract,
            "generated_at": now_iso(),
        }, blocked=True)
        write_json(state_path, payload)
        return 2, payload
    if design_truth_refs:
        artifacts = {**artifacts, **{f"design_truth_{key}": str(value) for key, value in design_truth_refs.items() if str(value).strip()}}
    request_path = Path(f".beacon/implement/{run_id}/request.json")
    request_md_path = Path(
        format_template(
            str(adapter.get("request_file") or f".beacon/implement/{run_id}/request.md"),
            {"run_id": run_id},
        )
    ) if str(adapter.get("adapter_type", "")).strip() in {"handoff", "claude-skill"} else None
    result_path = Path(
        format_template(
            str(adapter.get("result_file") or f".beacon/implement/{run_id}/result.json"),
            {"run_id": run_id},
        )
    )
    stdout_path = Path(
        format_template(str(adapter.get("stdout_file") or f".beacon/implement/{run_id}/stdout.log"), {"run_id": run_id})
    )
    stderr_path = Path(
        format_template(str(adapter.get("stderr_file") or f".beacon/implement/{run_id}/stderr.log"), {"run_id": run_id})
    )
    command_path = Path(
        format_template(str(adapter.get("command_file") or f".beacon/implement/{run_id}/command.txt"), {"run_id": run_id})
    )

    context = {
        "project_root": str(project_root),
        "workspace_root": str(project_root.parent),
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "run_id": run_id,
        "request_file": str(request_path),
        "result_file": str(result_path),
        "source_of_truth_root": artifacts["source_of_truth_root"],
        "semantic_contract": str(semantic_artifacts.get("semantic_contract", "")),
        "semantic_dictionary": str(semantic_artifacts.get("semantic_dictionary", "")),
        "semantic_usage_guidelines": str(semantic_artifacts.get("semantic_usage_guidelines", "")),
        "semantic_review": str(semantic_artifacts.get("semantic_review", "")),
        "default_design_bridge_skill": str(default_design_bridge.get("skill_id", "")),
        "design_preset": str(design_truth.get("design_preset", "")),
        "canonical_design_preset": str(design_truth.get("canonical_design_preset", "")),
        "design_style_preset": str(design_truth_refs.get("style_preset", "")),
        "design_lint_rules": str(design_truth_refs.get("design_lint_rules", "")),
    }
    implementation_plan_file = (
        str(implementation_plan_json_path(project_root, resolved_version, feature).relative_to(project_root))
        if implementation_plan_supported(resolved_version)
        else ""
    )
    revision_delta = load_revision_delta(project_root, version=resolved_version, feature=feature)
    if revision_delta:
        revision_delta["json_ref"] = str(revision_delta.get("json_ref", "") or f"docs/beacon/{resolved_version}/.machine/execution/revision-delta-{feature_slug}.json")
        revision_delta["markdown_ref"] = str(revision_delta.get("markdown_ref", "") or f"docs/beacon/{resolved_version}/execution/revision-delta-{feature_slug}.md")
    rendered_skill = str(skill or adapter.get("skill_prefix", "") or "").strip()
    default_prompt = build_default_task_prompt(
        feature=feature,
        version=resolved_version,
        project_root=project_root,
        source_of_truth_root=artifacts["source_of_truth_root"],
        feature_slug=feature_slug,
        result_file=str(result_path),
        implementation_plan_file=implementation_plan_file,
        semantic_artifact_refs=semantic_artifacts,
        default_design_bridge=default_design_bridge,
        design_truth=design_truth,
        revision_cleanup=revision_delta,
        operator_prompt=str(prompt_boundary_payload.get("prompt", "") or ""),
        prompt_boundary=prompt_boundary_payload,
    )
    task_prompt = _render_effective_task_prompt(
        default_prompt=default_prompt,
        task_template=task_template or adapter.get("task_template") or None,
        context=context,
    )
    if rendered_skill:
        task_prompt = f"{rendered_skill}\n{task_prompt}"
    context["task_prompt"] = task_prompt
    if not prompt_boundary_payload:
        prompt_boundary_payload = evaluate_implement_prompt_boundary(
            project_root,
            version=resolved_version,
            feature=feature,
            host_prompt=task_prompt,
        )
        if prompt_boundary_payload:
            prompt_boundary_payload["surface"] = "task_prompt"

    request_delivery_contract = build_delivery_contract(
        feature=feature,
        version=resolved_version,
        requested_mode=resolved_mode or "",
        effective_mode=resolved_mode or "",
        execution_mode=resolved_mode or "",
        runner_mode=adapter_id,
        host_runtime=resolved_host_runtime,
        subagent_prechecks=subagent_prechecks,
        requirement_binding={
            "source_of_truth_root": artifacts["source_of_truth_root"],
            "prd": artifacts["prd"],
            "user_story": artifacts["user_story"],
            "test_case": artifacts["test_case"],
            "ac_matrix": artifacts["ac_matrix"],
        },
        traceability_refs=[
            artifacts["prd"],
            artifacts["user_story"],
            artifacts["test_case"],
            artifacts["ac_matrix"],
            str(revision_delta.get("json_ref", "") or ""),
            *[value for value in semantic_artifacts.values() if value],
            *[value for value in design_truth_refs.values() if value],
            str((skill_admission.get("artifacts") or {}).get("machine_path", "") or ""),
            str(request_path),
            str(result_path),
        ],
        runner=adapter_id,
        adapter_type=adapter_type,
        execution_surface="implement-team" if resolved_mode == "team" else adapter_id,
        team_mode=resolved_mode == "team",
        capability_snapshot={
            "skill_admission_status": str(skill_admission.get("status", "") or ""),
            "skill_admission_mode": str(skill_admission.get("admission_mode", "") or ""),
            "skill_id": str(skill_admission.get("skill_id", "") or ""),
            "skill_surface_kind": str(((skill_admission.get("contract") or {}).get("surface_kind", "") if isinstance(skill_admission.get("contract"), dict) else "") or ""),
            "skill_non_code_supported": bool(
                str((((skill_admission.get("contract") or {}).get("surface_kind", "")) if isinstance(skill_admission.get("contract"), dict) else "") or "").strip().lower()
                not in {"", "code-only"}
            ),
        },
        risk_flags=[
            str(skill_admission.get("reason_code", "") or "")
        ] if str(skill_admission.get("reason_code", "") or "").strip() else [],
    )

    request_payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "source_of_truth_root": artifacts["source_of_truth_root"],
        "artifacts": artifacts,
        "runner": {
            "id": adapter_id,
            "adapter_type": str(adapter.get("adapter_type", "")),
            "runtime_family": str(adapter.get("runtime_family", "")),
            "skill": rendered_skill,
        },
        "mode": resolved_mode or "",
        "host_runtime": resolved_host_runtime,
        "subagent_prechecks": subagent_prechecks,
        "branch_preflight_path": str(branch_preflight_path),
        "branch_preflight": branch_preflight,
        "program_next_action_admission": program_admission,
        "task_prompt": task_prompt,
        "result_file": str(result_path),
        "implementation_plan": implementation_plan_file,
        "revision_delta": revision_delta,
        "git_workflow": git_workflow_contract,
        "generated_at": now_iso(),
        "semantic_layer": {
            "artifacts": semantic_artifacts,
            "default_design_bridge": default_design_bridge,
        },
        "design_truth": design_truth,
        "skill_admission": skill_admission,
        "delivery_contract": request_delivery_contract,
        "host_native_delivery": request_delivery_contract,
    }
    if prompt_boundary_payload:
        request_payload["prompt_boundary"] = prompt_boundary_payload
    write_json(project_root / request_path, request_payload)

    state_path = impl_dir / "state.json"
    base_state = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "mode": resolved_mode or "",
        "host_runtime": resolved_host_runtime,
        "runner": adapter_id,
        "adapter_type": str(adapter.get("adapter_type", "")),
        "request_path": str(request_path),
        "result_path": str(result_path),
        "branch_preflight_path": str(branch_preflight_path),
        "plan_preflight_path": str(plan_preflight_path),
        "program_next_action_admission": program_admission,
        "revision_delta": revision_delta,
        "git_workflow": git_workflow_contract,
        "generated_at": now_iso(),
        "status": "planned",
        "subagent_prechecks": subagent_prechecks,
        "semantic_layer": {
            "artifacts": semantic_artifacts,
            "default_design_bridge": default_design_bridge,
        },
        "design_truth": design_truth,
        "skill_admission": skill_admission,
        "delivery_contract": request_delivery_contract,
        "host_native_delivery": request_delivery_contract,
    }
    if prompt_boundary_payload:
        base_state["prompt_boundary"] = prompt_boundary_payload
    if dry_run and adapter_type in {"native", "handoff", "claude-skill"}:
        payload = {
            **base_state,
            "status": "dry_run",
            "command": [],
            "command_path": str(command_path),
            "task_prompt": task_prompt,
            "plan_preflight_path": str(plan_preflight_path),
            "plan_preflight": implementation_plan_gate,
            "implementation_plan": implementation_plan_file,
        }
        if request_md_path is not None:
            payload["request_markdown"] = (
                str(request_md_path.relative_to(project_root))
                if request_md_path.is_absolute()
                else str(request_md_path)
            )
        write_json(state_path, payload)
        return 0, payload
    if adapter_type == "native" and str(skill or "").strip():
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="native_skill_execution_unsupported",
        )
        payload = {
            **base_state,
            "status": "blocked",
            "reason_code": "native_skill_execution_unsupported",
            "recommended_command": (
                f'beacon implement run "{feature}" --project {project_root} '
                f"--version {resolved_version} --runner {adapter_id} --skill {str(skill or '').strip()} --dry-run"
            ),
            "detail": (
                "Beacon native runners currently validate skill admission and delivery context, "
                "but do not execute external/project skill work as a real host-native implementation bridge."
            ),
            "supported_execution_adapters": ["command-skill", "claude-skill"],
        }
        payload = _with_implement_surface(payload, blocked=True)
        write_json(state_path, payload)
        return 2, payload
    if adapter_type == "native":
        mark_implementation_plan_started(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
        )
        native_mode = str(adapter.get("mode", "single") or "single")
        result_payload = run_native_implementation(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            mode=native_mode,
            runtime=str(team_runtime or "file"),
        )
        if str(result_payload.get("status", "")).strip().lower() != "completed":
            mark_implementation_plan_failed(
                project_root,
                version=resolved_version,
                feature=feature,
                run_id=run_id,
                reason_code=str(result_payload.get("reason_code", "native_runner_failed") or "native_runner_failed"),
            )
            payload = {
                **base_state,
                "status": "failed",
                "reason_code": str(result_payload.get("reason_code", "native_runner_failed") or "native_runner_failed"),
                "result": result_payload,
            }
            payload = _with_implement_surface(payload, blocked=True)
            write_json(state_path, payload)
            return 2, payload
        evidence_gate = implementation_evidence_gate(result_payload)
        if bool(evidence_gate.get("blocked")):
            mark_implementation_plan_failed(
                project_root,
                version=resolved_version,
                feature=feature,
                run_id=run_id,
                reason_code=str(evidence_gate.get("reason_code") or "implementation_evidence_blocked"),
            )
            reason_code = str(evidence_gate.get("reason_code") or "implementation_evidence_blocked")
            payload = {
                **base_state,
                "status": "blocked",
                "reason_code": reason_code,
                "implementation_evidence_gate": evidence_gate,
                "result": result_payload,
                "diagnostic_only": True,
            }
            payload = _with_implement_surface(payload, reason_code=reason_code, blocked=True)
            write_json(state_path, payload)
            return 2, payload
        summary_paths = _summary_paths(project_root, resolved_version, feature)
        archive_paths = _technical_archive_paths(project_root, resolved_version, feature)
        story_state = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True) or {}
        requirement_completeness = load_requirement_completeness(project_root, resolved_version, feature)
        marker = project_root / ".beacon" / "state" / f"implementation-{feature_slug}.json"
        write_json(marker, {
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "runner": adapter_id,
            "skill": rendered_skill,
            "status": "completed",
            "generated_at": now_iso(),
        })
        implemented_item_ids = [str(item) for item in _normalize_string_list(result_payload.get("implemented_items"))]
        if not implemented_item_ids:
            implemented_item_ids = _story_item_ids(story_state, kinds={"ac", "task"})
        implemented_task_ids = [str(item) for item in _normalize_string_list(result_payload.get("implemented_task_ids"))]
        revision_cleanup_summary = _revision_cleanup_payload(result_payload=result_payload, revision_delta=revision_delta)
        requirement_traceability = {
            "source_of_truth_root": artifacts["source_of_truth_root"],
            "prd": artifacts["prd"],
            "user_story": artifacts["user_story"],
            "test_case": artifacts["test_case"],
            "ac_matrix": artifacts["ac_matrix"],
            "requirement_completeness_ref": str(
                requirement_paths(project_root, resolved_version, feature)["completeness"].relative_to(project_root)
            ) if requirement_completeness else "",
            "requirement_completeness_verdict": str(requirement_completeness.get("completeness_verdict") or ""),
            "revision_id": str(story_state.get("revision_id", "") or story_state.get("current_revision_id", "") or ""),
            "implemented_item_ids": implemented_item_ids,
            "implemented_task_ids": implemented_task_ids,
            "verified_task_ids": result_payload.get("verified_task_ids", []),
        }
        delivery_surfaces = {
            "runtime_mode": resolved_mode or native_mode or "single",
            "shipped_surfaces": _normalize_string_list(result_payload.get("shipped_surfaces")),
            "partial_surfaces": _normalize_string_list(result_payload.get("partial_surfaces")),
            "deferred_surfaces": _normalize_string_list(result_payload.get("deferred_surfaces")),
            "downgrade_rationale": str(result_payload.get("downgrade_rationale", "") or ""),
        }
        summary_traceability_refs = _dedupe_strings(
            [
                artifacts["prd"],
                artifacts["user_story"],
                artifacts["test_case"],
                artifacts["ac_matrix"],
                str(revision_cleanup_summary.get("revision_delta_ref", "") or ""),
                str((skill_admission.get("artifacts") or {}).get("machine_path", "") or ""),
                *[value for value in design_truth_refs.values() if value],
                str(request_path),
                str(result_path),
            ]
        )
        summary_payload = {
            **base_state,
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "runner": adapter_id,
            "adapter_type": adapter_type,
            "skill": rendered_skill,
            "status": "completed",
            "summary": str(result_payload.get("summary", "")),
            "changed_files": result_payload.get("changed_files", []),
            "verification": result_payload.get("verification", []),
            "implemented_task_ids": implemented_task_ids,
            "verified_task_ids": result_payload.get("verified_task_ids", []),
            "blocked_task_ids": result_payload.get("blocked_task_ids", []),
            "failed_task_ids": result_payload.get("failed_task_ids", []),
            "artifact_updates": result_payload.get("artifact_updates", {}),
            "branch_preflight": branch_preflight,
            "plan_preflight_path": str(plan_preflight_path),
            "plan_preflight": implementation_plan_gate,
            "program_next_action_admission": program_admission,
            "implementation_marker": str(marker.relative_to(project_root)),
            "technical_archive": {
                "json": str(archive_paths["json"].relative_to(project_root)),
                "md": str(archive_paths["md"].relative_to(project_root)),
            },
            "implementation_plan": implementation_plan_file,
            "implementation_plan_progress": load_implementation_plan_progress(project_root, version=resolved_version, feature=feature),
            "implementation_order": _v140_implementation_order(project_root, version=resolved_version) if resolved_version == "v1.4.0" else {},
            "requirement_traceability": requirement_traceability,
            "delivery_surfaces": delivery_surfaces,
            "revision_cleanup": revision_cleanup_summary,
            "skill_admission": skill_admission,
            "design_truth": design_truth,
            "traceability_refs": summary_traceability_refs,
            "generated_at": now_iso(),
        }
        if prompt_boundary_payload:
            summary_payload["prompt_boundary"] = prompt_boundary_payload
        summary_delivery_contract = build_delivery_contract(
            feature=feature,
            version=resolved_version,
            requested_mode=resolved_mode or native_mode or "single",
            effective_mode=resolved_mode or native_mode or "single",
            execution_mode=resolved_mode or native_mode or "single",
            runner_mode=adapter_id,
            host_runtime=resolved_host_runtime,
            subagent_prechecks=subagent_prechecks,
            requirement_binding=requirement_traceability,
            traceability_refs=summary_traceability_refs,
            runner=adapter_id,
            adapter_type=adapter_type,
            execution_surface="implement-team" if resolved_mode == "team" else adapter_id,
            team_mode=resolved_mode == "team",
            capability_snapshot={
                "skill_admission_status": str(skill_admission.get("status", "") or ""),
                "skill_admission_mode": str(skill_admission.get("admission_mode", "") or ""),
                "skill_id": str(skill_admission.get("skill_id", "") or ""),
                "skill_surface_kind": str(((skill_admission.get("contract") or {}).get("surface_kind", "") if isinstance(skill_admission.get("contract"), dict) else "") or ""),
                "skill_non_code_supported": bool(
                    str((((skill_admission.get("contract") or {}).get("surface_kind", "")) if isinstance(skill_admission.get("contract"), dict) else "") or "").strip().lower()
                    not in {"", "code-only"}
                ),
            },
            risk_flags=[
                str(skill_admission.get("reason_code", "") or "")
            ] if str(skill_admission.get("reason_code", "") or "").strip() else [],
        )
        summary_payload["delivery_contract"] = summary_delivery_contract
        summary_payload["host_native_delivery"] = summary_delivery_contract
        for key, value in result_payload.items():
            if key in summary_payload:
                continue
            summary_payload[key] = value
        technical_payload = _technical_archive_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            runner=adapter_id,
            skill=rendered_skill,
            request_path=str(request_path),
            result_path=str(result_path),
            stdout_path="",
            stderr_path="",
            result_payload=result_payload,
            revision_cleanup=revision_cleanup_summary,
        )
        current_revision_id = str(story_state.get("current_revision_id", "") or "")
        technical_payload["revision_id"] = current_revision_id
        write_json(archive_paths["json"], technical_payload)
        _write_text(archive_paths["md"], _render_technical_archive_markdown(technical_payload))
        refresh_evidence_manifest(
            project_root,
            refs=[
                str(archive_paths["json"].relative_to(project_root)),
                str(archive_paths["md"].relative_to(project_root)),
            ],
            version=resolved_version,
        )
        learning_payload = write_requirement_rewrite_input(
            project_root,
            version=resolved_version,
            feature=feature,
            archive_payload=technical_payload,
            archive_path=str(archive_paths["json"].relative_to(project_root)),
        )
        obligations = write_artifact_update_obligations(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            updates=result_payload.get("artifact_updates") if isinstance(result_payload.get("artifact_updates"), dict) else {},
            technical_archive_path=str(archive_paths["json"].relative_to(project_root)),
        )
        summary_payload["artifact_writeback_obligations"] = str(
            (
                project_root
                / ".beacon"
                / "state"
                / "artifact-update-obligations"
                / f"{feature_slug}.json"
            ).relative_to(project_root)
        )
        summary_payload["artifact_writeback_open_count"] = int(obligations.get("open_count", 0) or 0)
        summary_payload["requirement_rewrite_input"] = str(learning_payload.get("path", "") or "")
        handoff_path = write_implement_to_qa_handoff(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            summary_ref=str(summary_paths["json"].relative_to(project_root)),
            technical_archive_ref=str(archive_paths["json"].relative_to(project_root)),
            evidence_refs=[str(summary_paths["json"].relative_to(project_root)), str(archive_paths["json"].relative_to(project_root))],
            changed_files=result_payload.get("changed_files", []),
            implementation_plan_ref=implementation_plan_file,
            design_truth=design_truth,
        )
        summary_payload["implement_to_qa_handoff"] = str(handoff_path.relative_to(project_root))
        summary_payload["auto_qa"] = {
            "enabled": bool(auto_qa),
            "triggered": False,
            "args": resolved_auto_qa_args,
            "follow_handoff": bool(auto_qa_follow_handoff),
            "max_rounds": int(auto_qa_max_rounds or 1),
        }
        auto_qa_exit = 0
        gate_release_info: dict[str, Any] | None = None
        if auto_qa:
            auto_qa_exit, auto_qa_payload = _run_auto_qa_sequence(
                project_root,
                feature=feature,
                version=resolved_version,
                extra_args=resolved_auto_qa_args,
                follow_handoff=bool(auto_qa_follow_handoff),
                max_rounds=int(auto_qa_max_rounds or 1),
            )
            summary_payload["auto_qa"] = auto_qa_payload
        auto_qa_feature_scorecard = (
            ((summary_payload.get("auto_qa") or {}).get("payload") or {}).get("feature_scorecard", {})
            if isinstance((summary_payload.get("auto_qa") or {}).get("payload"), dict)
            else {}
        )
        if resolved_mode == "ralph" and bool((review_quality_info or {}).get("payload", {}).get("gate_ready")) and str(auto_qa_feature_scorecard.get("continue_decision", "") or "") == "ready_for_release":
            gate_rc, gate_payload = _run_gate_release_command(project_root, resolved_version)
            gate_release_info = {"exit_code": gate_rc, "payload": gate_payload}
            summary_payload["gate_release"] = gate_release_info
        if resolved_mode == "ralph":
            append_ralph_round(
                project_root,
                feature=feature,
                round_payload={
                    "run_id": run_id,
                    "review_quality": {},
                    "auto_qa": summary_payload.get("auto_qa", {}),
                    "gate_release": gate_release_info or {},
                    "recorded_at": now_iso(),
                },
            )
            summary_payload["ralph"] = finalize_ralph_state(
                project_root,
                feature=feature,
                run_id=run_id,
                review_quality=review_quality_info or {},
                auto_qa=summary_payload.get("auto_qa", {}),
                gate_release=gate_release_info or {},
            )
            ralph_paths = _ralph_summary_paths(project_root, resolved_version, feature)
            write_json(ralph_paths["json"], summary_payload["ralph"])
            _write_text(ralph_paths["md"], _render_ralph_summary_markdown(summary_payload["ralph"]))
            summary_payload["ralph_artifacts"] = {
                "json": str(ralph_paths["json"].relative_to(project_root)),
                "md": str(ralph_paths["md"].relative_to(project_root)),
            }
            refresh_evidence_manifest(
                project_root,
                refs=[
                    str(ralph_paths["json"].relative_to(project_root)),
                    str(ralph_paths["md"].relative_to(project_root)),
                ],
                version=resolved_version,
            )
        write_json(summary_paths["json"], summary_payload)
        _write_text(summary_paths["md"], _render_summary_markdown(summary_payload))
        refresh_evidence_manifest(
            project_root,
            refs=[
                str(summary_paths["json"].relative_to(project_root)),
                str(summary_paths["md"].relative_to(project_root)),
            ],
            version=resolved_version,
        )
        summary_payload["workflow_lifecycle_sync"] = _sync_direct_implement_lifecycle_completion(
            project_root,
            version=resolved_version,
            feature=feature,
            evidence_ref=[
                str(summary_paths["json"].relative_to(project_root)),
                str(summary_paths["md"].relative_to(project_root)),
                str(marker.relative_to(project_root)),
            ],
        )
        write_json(state_path, summary_payload)
        return auto_qa_exit, summary_payload
    if adapter_type in {"handoff", "claude-skill"}:
        request_md = project_root / (request_md_path or Path(f".beacon/implement/{run_id}/request.md"))
        _write_text(request_md, task_prompt + "\n")
        payload = {
            **base_state,
            "status": "handoff_required",
            "request_path": str(request_path),
            "request_markdown": str(request_md.relative_to(project_root)),
            "recommended_flows": adapter.get("recommended_flows", []),
            "plan_preflight_path": str(plan_preflight_path),
            "plan_preflight": implementation_plan_gate,
            "implementation_plan": implementation_plan_file,
        }
        if resolved_mode == "ralph":
            payload["ralph"] = mark_ralph_handoff_required(
                project_root,
                feature=feature,
                run_id=run_id,
                request_markdown=str(request_md.relative_to(project_root)),
            )
            ralph_paths = _ralph_summary_paths(project_root, resolved_version, feature)
            write_json(ralph_paths["json"], payload["ralph"])
            _write_text(ralph_paths["md"], _render_ralph_summary_markdown(payload["ralph"]))
            payload["ralph_artifacts"] = {
                "json": str(ralph_paths["json"].relative_to(project_root)),
                "md": str(ralph_paths["md"].relative_to(project_root)),
            }
            refresh_evidence_manifest(
                project_root,
                refs=[
                    str(ralph_paths["json"].relative_to(project_root)),
                    str(ralph_paths["md"].relative_to(project_root)),
                ],
                version=resolved_version,
            )
        write_json(state_path, payload)
        return 0, payload

    rendered_args = [format_template(str(arg), context) for arg in adapter.get("args", [])]
    command = [str(adapter.get("command", "")).strip(), *rendered_args]
    _write_text(project_root / command_path, " ".join(command) + "\n")

    if dry_run:
        payload = {
            **base_state,
            "status": "dry_run",
            "command": command,
            "command_path": str(command_path),
            "task_prompt": task_prompt,
            "plan_preflight_path": str(plan_preflight_path),
            "plan_preflight": implementation_plan_gate,
            "implementation_plan": implementation_plan_file,
        }
        write_json(state_path, payload)
        return 0, payload

    env = {}
    for key in adapter.get("env_passthrough", []) if isinstance(adapter.get("env_passthrough"), list) else []:
        if key in os.environ:
            env[key] = os.environ[key]
    if isinstance(adapter.get("env_overrides"), dict):
        env.update({str(k): str(v) for k, v in adapter.get("env_overrides", {}).items()})

    timeout = int(timeout_sec or adapter.get("timeout_sec") or 3600)
    mark_implementation_plan_started(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
    )
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, **env},
        )
    except subprocess.TimeoutExpired:
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_execution_timeout",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_execution_timeout",
            "command": command,
            "timeout_sec": timeout,
        }
        payload = _with_implement_surface(payload, blocked=True)
        write_json(state_path, payload)
        return 2, payload
    except FileNotFoundError:
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_command_not_found",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_command_not_found",
            "command": command,
        }
        payload = _with_implement_surface(payload, blocked=True)
        write_json(state_path, payload)
        return 2, payload
    _write_text(project_root / stdout_path, result.stdout or "")
    _write_text(project_root / stderr_path, result.stderr or "")

    if result.returncode != 0:
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_execution_failed",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_execution_failed",
            "command": command,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "exit_code": result.returncode,
        }
        payload = _with_implement_surface(payload, blocked=True)
        write_json(state_path, payload)
        return 2, payload

    full_result_path = project_root / result_path
    if not full_result_path.exists():
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_result_missing",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_result_missing",
            "command": command,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        }
        payload = _with_implement_surface(payload, blocked=True)
        write_json(state_path, payload)
        return 2, payload

    try:
        result_payload = json.loads(full_result_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_result_invalid",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_result_invalid",
            "problems": [f"result json parse failed: {exc}"],
        }
        payload = _with_implement_surface(payload, blocked=True)
        write_json(state_path, payload)
        return 2, payload
    problems = _validate_result(result_payload)
    if problems:
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_result_invalid",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_result_invalid",
            "problems": problems,
        }
        payload = _with_implement_surface(payload, blocked=True)
        write_json(state_path, payload)
        return 2, payload

    if str(result_payload.get("status", "")).strip().lower() != "completed":
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="implement_execution_failed",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "implement_execution_failed",
            "result": result_payload,
        }
        payload = _with_implement_surface(payload, blocked=True)
        write_json(state_path, payload)
        return 2, payload
    evidence_gate = implementation_evidence_gate(result_payload)
    if bool(evidence_gate.get("blocked")):
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code=str(evidence_gate.get("reason_code") or "implementation_evidence_blocked"),
        )
        reason_code = str(evidence_gate.get("reason_code") or "implementation_evidence_blocked")
        payload = {
            **base_state,
            "status": "blocked",
            "reason_code": reason_code,
            "implementation_evidence_gate": evidence_gate,
            "result": result_payload,
            "diagnostic_only": True,
        }
        payload = _with_implement_surface(payload, reason_code=reason_code, blocked=True)
        write_json(state_path, payload)
        return 2, payload

    marker = project_root / ".beacon" / "state" / f"implementation-{feature_slug}.json"
    write_json(
        marker,
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "runner": adapter_id,
            "skill": rendered_skill,
            "status": "completed",
            "generated_at": now_iso(),
        },
    )

    review_spec_info: dict[str, Any] | None = None
    review_quality_info: dict[str, Any] | None = None

    summary_paths = _summary_paths(project_root, resolved_version, feature)
    archive_paths = _technical_archive_paths(project_root, resolved_version, feature)
    change_paths = _change_document_paths(project_root, resolved_version, feature)
    story_state = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True) or {}
    requirement_completeness = load_requirement_completeness(project_root, resolved_version, feature)
    implemented_item_ids = [str(item) for item in _normalize_string_list(result_payload.get("implemented_items"))]
    if not implemented_item_ids:
        implemented_item_ids = _story_item_ids(story_state, kinds={"ac", "task"})
    implemented_task_ids = [str(item) for item in _normalize_string_list(result_payload.get("implemented_task_ids"))]
    writeback_payload = record_implementation_writeback(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        implemented_item_ids=implemented_item_ids,
        task_ids=implemented_task_ids,
        changed_files=result_payload.get("changed_files", []),
    )
    revision_cleanup_summary = _revision_cleanup_payload(result_payload=result_payload, revision_delta=revision_delta)
    requirement_traceability = {
        "source_of_truth_root": artifacts["source_of_truth_root"],
        "prd": artifacts["prd"],
        "user_story": artifacts["user_story"],
        "test_case": artifacts["test_case"],
        "ac_matrix": artifacts["ac_matrix"],
        "requirement_completeness_ref": str(
            requirement_paths(project_root, resolved_version, feature)["completeness"].relative_to(project_root)
        ) if requirement_completeness else "",
        "requirement_completeness_verdict": str(requirement_completeness.get("completeness_verdict") or ""),
        "revision_id": str(story_state.get("revision_id", "") or story_state.get("current_revision_id", "") or ""),
        "implemented_item_ids": implemented_item_ids,
        "implemented_task_ids": implemented_task_ids,
        "verified_task_ids": result_payload.get("verified_task_ids", []),
    }
    delivery_surfaces = {
        "runtime_mode": resolved_mode or "single",
        "shipped_surfaces": _normalize_string_list(result_payload.get("shipped_surfaces")),
        "partial_surfaces": _normalize_string_list(result_payload.get("partial_surfaces")),
        "deferred_surfaces": _normalize_string_list(result_payload.get("deferred_surfaces")),
        "downgrade_rationale": str(result_payload.get("downgrade_rationale", "") or ""),
    }
    summary_traceability_refs = _dedupe_strings(
        [
            artifacts["prd"],
            artifacts["user_story"],
            artifacts["test_case"],
            artifacts["ac_matrix"],
            str(revision_cleanup_summary.get("revision_delta_ref", "") or ""),
            str((skill_admission.get("artifacts") or {}).get("machine_path", "") or ""),
            *[value for value in design_truth_refs.values() if value],
            str(request_path),
            str(result_path),
            str(stdout_path),
            str(stderr_path),
        ]
    )
    summary_payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "runner": adapter_id,
        "adapter_type": adapter_type,
        "skill": rendered_skill,
        "status": "completed",
        "summary": str(result_payload.get("summary", "")),
        "changed_files": result_payload.get("changed_files", []),
        "verification": result_payload.get("verification", []),
        "implemented_task_ids": implemented_task_ids,
        "verified_task_ids": result_payload.get("verified_task_ids", []),
        "blocked_task_ids": result_payload.get("blocked_task_ids", []),
        "failed_task_ids": result_payload.get("failed_task_ids", []),
        "artifact_updates": result_payload.get("artifact_updates", {}),
        "request_path": str(request_path),
        "result_path": str(result_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "branch_preflight_path": str(branch_preflight_path),
        "branch_preflight": branch_preflight,
        "plan_preflight_path": str(plan_preflight_path),
        "plan_preflight": implementation_plan_gate,
        "implementation_plan": implementation_plan_file,
        "implementation_plan_progress": load_implementation_plan_progress(project_root, version=resolved_version, feature=feature),
        "requirement_traceability": requirement_traceability,
        "delivery_surfaces": delivery_surfaces,
        "revision_cleanup": revision_cleanup_summary,
        "skill_admission": skill_admission,
        "design_truth": design_truth,
        "traceability_refs": summary_traceability_refs,
        "implementation_marker": str(marker.relative_to(project_root)),
        "technical_archive": {
            "json": str(archive_paths["json"].relative_to(project_root)),
            "md": str(archive_paths["md"].relative_to(project_root)),
        },
        "change_document": {
            "json": str(change_paths["json"].relative_to(project_root)),
            "md": str(change_paths["md"].relative_to(project_root)),
        },
        "review_spec": review_spec_info,
        "review_quality": review_quality_info,
        "generated_at": now_iso(),
        "writeback": writeback_payload,
    }
    if prompt_boundary_payload:
        summary_payload["prompt_boundary"] = prompt_boundary_payload
    summary_delivery_contract = build_delivery_contract(
        feature=feature,
        version=resolved_version,
        requested_mode=resolved_mode or "",
        effective_mode=resolved_mode or "",
        execution_mode=resolved_mode or "",
        runner_mode=adapter_id,
        host_runtime=resolved_host_runtime,
        subagent_prechecks=subagent_prechecks,
        requirement_binding=requirement_traceability,
        traceability_refs=summary_traceability_refs,
        runner=adapter_id,
        adapter_type=adapter_type,
        execution_surface="implement-team" if resolved_mode == "team" else adapter_id,
        team_mode=resolved_mode == "team",
        capability_snapshot={
            "skill_admission_status": str(skill_admission.get("status", "") or ""),
            "skill_admission_mode": str(skill_admission.get("admission_mode", "") or ""),
            "skill_id": str(skill_admission.get("skill_id", "") or ""),
            "skill_surface_kind": str(((skill_admission.get("contract") or {}).get("surface_kind", "") if isinstance(skill_admission.get("contract"), dict) else "") or ""),
            "skill_non_code_supported": bool(
                str((((skill_admission.get("contract") or {}).get("surface_kind", "")) if isinstance(skill_admission.get("contract"), dict) else "") or "").strip().lower()
                not in {"", "code-only"}
            ),
        },
        risk_flags=[
            str(skill_admission.get("reason_code", "") or "")
        ] if str(skill_admission.get("reason_code", "") or "").strip() else [],
    )
    summary_payload["delivery_contract"] = summary_delivery_contract
    summary_payload["host_native_delivery"] = summary_delivery_contract
    technical_payload = _technical_archive_payload(
        project_root=project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        runner=adapter_id,
        skill=rendered_skill,
        request_path=str(request_path),
        result_path=str(result_path),
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        result_payload=result_payload,
        revision_cleanup=revision_cleanup_summary,
    )
    technical_payload["revision_id"] = str(story_state.get("current_revision_id", "") or "")
    write_json(archive_paths["json"], technical_payload)
    _write_text(archive_paths["md"], _render_technical_archive_markdown(technical_payload))
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(archive_paths["json"].relative_to(project_root)),
            str(archive_paths["md"].relative_to(project_root)),
        ],
        version=resolved_version,
    )
    change_payload = _feature_change_payload(
        feature=feature,
        version=resolved_version,
        run_id=run_id,
        summary_ref=str(summary_paths["json"].relative_to(project_root)),
        technical_ref=str(archive_paths["json"].relative_to(project_root)),
        technical_payload=technical_payload,
    )
    learning_payload = write_requirement_rewrite_input(
        project_root,
        version=resolved_version,
        feature=feature,
        archive_payload=technical_payload,
        archive_path=str(archive_paths["json"].relative_to(project_root)),
    )
    obligations = write_artifact_update_obligations(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        updates=result_payload.get("artifact_updates") if isinstance(result_payload.get("artifact_updates"), dict) else {},
        technical_archive_path=str(archive_paths["json"].relative_to(project_root)),
    )
    summary_payload["artifact_writeback_obligations"] = str(
        (
            project_root
            / ".beacon"
            / "state"
            / "artifact-update-obligations"
            / f"{feature_slug}.json"
        ).relative_to(project_root)
    )
    summary_payload["artifact_writeback_open_count"] = int(obligations.get("open_count", 0) or 0)
    summary_payload["requirement_rewrite_input"] = str(learning_payload.get("path", "") or "")
    handoff_path = write_implement_to_qa_handoff(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        summary_ref=str(summary_paths["json"].relative_to(project_root)),
        technical_archive_ref=str(archive_paths["json"].relative_to(project_root)),
        evidence_refs=[str(summary_paths["json"].relative_to(project_root)), str(archive_paths["json"].relative_to(project_root))],
        changed_files=result_payload.get("changed_files", []),
        implementation_plan_ref=implementation_plan_file,
        design_truth=design_truth,
    )
    summary_payload["implement_to_qa_handoff"] = str(handoff_path.relative_to(project_root))
    write_json(change_paths["json"], change_payload)
    _write_text(change_paths["md"], _render_feature_change_markdown(change_payload))
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(change_paths["json"].relative_to(project_root)),
            str(change_paths["md"].relative_to(project_root)),
        ],
        version=resolved_version,
    )
    write_json(summary_paths["json"], summary_payload)
    _write_text(summary_paths["md"], _render_summary_markdown(summary_payload))
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(summary_paths["json"].relative_to(project_root)),
            str(summary_paths["md"].relative_to(project_root)),
        ],
        version=resolved_version,
    )

    if auto_review_spec:
        rc, payload = _run_review_command(project_root, resolved_version, feature, "spec")
        review_spec_info = {"exit_code": rc, "payload": payload}
        summary_payload["review_spec"] = review_spec_info
    if auto_review_quality:
        rc, payload = _run_review_command(project_root, resolved_version, feature, "quality")
        review_quality_info = {"exit_code": rc, "payload": payload}
        summary_payload["review_quality"] = review_quality_info

    summary_payload["auto_qa"] = {
        "enabled": bool(auto_qa),
        "triggered": False,
        "args": resolved_auto_qa_args,
        "follow_handoff": bool(auto_qa_follow_handoff),
        "max_rounds": int(auto_qa_max_rounds or 1),
    }
    auto_qa_exit = 0
    gate_release_info: dict[str, Any] | None = None
    if auto_qa:
        auto_qa_exit, auto_qa_payload = _run_auto_qa_sequence(
            project_root,
            feature=feature,
            version=resolved_version,
            extra_args=resolved_auto_qa_args,
            follow_handoff=bool(auto_qa_follow_handoff),
            max_rounds=int(auto_qa_max_rounds or 1),
        )
        summary_payload["auto_qa"] = auto_qa_payload
    auto_qa_feature_scorecard = (
        ((summary_payload.get("auto_qa") or {}).get("payload") or {}).get("feature_scorecard", {})
        if isinstance((summary_payload.get("auto_qa") or {}).get("payload"), dict)
        else {}
    )
    if resolved_mode == "ralph" and bool((review_quality_info or {}).get("payload", {}).get("gate_ready")) and str(auto_qa_feature_scorecard.get("continue_decision", "") or "") == "ready_for_release":
        gate_rc, gate_payload = _run_gate_release_command(project_root, resolved_version)
        gate_release_info = {"exit_code": gate_rc, "payload": gate_payload}
        summary_payload["gate_release"] = gate_release_info
    if resolved_mode == "ralph":
        append_ralph_round(
            project_root,
            feature=feature,
            round_payload={
                "run_id": run_id,
                "review_quality": review_quality_info or {},
                "auto_qa": summary_payload.get("auto_qa", {}),
                "gate_release": gate_release_info or {},
                "recorded_at": now_iso(),
            },
        )
        summary_payload["ralph"] = finalize_ralph_state(
            project_root,
            feature=feature,
            run_id=run_id,
            review_quality=review_quality_info or {},
            auto_qa=summary_payload.get("auto_qa", {}),
            gate_release=gate_release_info or {},
        )
        summary_payload["ralph"]["implementation_order"] = summary_payload.get("implementation_order", {})
        ralph_paths = _ralph_summary_paths(project_root, resolved_version, feature)
        write_json(ralph_paths["json"], summary_payload["ralph"])
        _write_text(ralph_paths["md"], _render_ralph_summary_markdown(summary_payload["ralph"]))
        summary_payload["ralph_artifacts"] = {
            "json": str(ralph_paths["json"].relative_to(project_root)),
            "md": str(ralph_paths["md"].relative_to(project_root)),
        }
        refresh_evidence_manifest(
            project_root,
            refs=[
                str(ralph_paths["json"].relative_to(project_root)),
                str(ralph_paths["md"].relative_to(project_root)),
            ],
            version=resolved_version,
        )
    write_json(summary_paths["json"], summary_payload)
    _write_text(summary_paths["md"], _render_summary_markdown(summary_payload))
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(summary_paths["json"].relative_to(project_root)),
            str(summary_paths["md"].relative_to(project_root)),
        ],
        version=resolved_version,
    )

    summary_payload["workflow_lifecycle_sync"] = _sync_direct_implement_lifecycle_completion(
        project_root,
        version=resolved_version,
        feature=feature,
        evidence_ref=[
            str(summary_paths["json"].relative_to(project_root)),
            str(summary_paths["md"].relative_to(project_root)),
            str(marker.relative_to(project_root)),
        ],
    )
    payload = {**base_state, **summary_payload}
    write_json(state_path, payload)
    return auto_qa_exit, payload


@app.command("list-runners")
def list_runners(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """List implementation runners available to Beacon."""
    root = Path(project_root) if project_root else Path.cwd()
    adapters = discover_skill_adapters(root)
    preferred = resolve_default_runner(root) or _default_runner_for_version(root, "v1.3.0")
    rows = []
    for adapter_id, adapter in sorted(adapters.items()):
        detected, evidence = detect_adapter(adapter_id, root)
        rows.append(
            {
                "id": adapter_id,
                "adapter_type": str(adapter.get("adapter_type", "")),
                "runtime_family": str(adapter.get("runtime_family", "")),
                "preferred": adapter_id == preferred,
                "detected": detected,
                "evidence": evidence,
            }
        )
    if json_output:
        typer.echo(json.dumps({"preferred": preferred or "", "runners": rows}, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Implement Runners")
    typer.echo("=" * 25)
    for row in rows:
        marker = "*" if row["preferred"] else "-"
        typer.echo(f"{marker} {row['id']} ({row['adapter_type']}) detected={row['detected']}")


@app.command("import-evidence")
def import_evidence(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    run_id: str = typer.Option("", "--run-id", help="Existing implementation/import run id"),
    source_ref: Optional[list[str]] = typer.Option(None, "--source-ref", help="Evidence source ref, repeatable"),
    changed_file: Optional[list[str]] = typer.Option(None, "--changed-file", help="Changed file ref, repeatable"),
    service_dir: Optional[list[str]] = typer.Option(None, "--service-dir", help="Changed service directory, repeatable"),
    summary_ref: str = typer.Option("", "--summary-ref", help="Implementation summary document or artifact ref"),
    approved_by: str = typer.Option("", "--approved-by", help="Human/operator approving the import"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Import externally produced implementation evidence into Beacon's QA-readable marker."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    slug = _slug(feature)
    source_refs = [str(item).strip() for item in (source_ref or []) if str(item).strip()]
    changed_files = [str(item).strip() for item in (changed_file or []) if str(item).strip()]
    service_dirs = [str(item).strip() for item in (service_dir or []) if str(item).strip()]
    summary = str(summary_ref or "").strip()
    approver = str(approved_by or "").strip()

    problems: list[str] = []
    if not source_refs:
        problems.append("source_ref_required")
    if not changed_files and not service_dirs:
        problems.append("changed_file_or_service_dir_required")
    if not summary:
        problems.append("summary_ref_required")
    if not approver:
        problems.append("approved_by_required")
    if problems:
        payload = _with_implement_surface(
            {
                "schema_version": "1.0",
                "feature": feature,
                "feature_slug": slug,
                "version": resolved_version,
                "status": "blocked",
                "reason_code": "implementation_evidence_import_incomplete",
                "problems": problems,
                "recommended_command": (
                    f'beacon implement import-evidence "{feature}" --project {project_root} '
                    f"--version {resolved_version} --source-ref <ref> --changed-file <path> "
                    "--summary-ref <ref> --approved-by <operator>"
                ),
            },
            blocked=True,
        )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon implement import-evidence blocked: missing required evidence fields", err=True)
        raise typer.Exit(2)

    import_run_id = str(run_id or "").strip() or generate_run_id(project_root)
    prompt_boundary = _build_import_evidence_prompt_boundary(
        project_root=project_root,
        version=resolved_version,
        feature=feature,
        source_refs=source_refs,
        changed_files=changed_files,
        service_dirs=service_dirs,
        summary_ref=summary,
    )
    if prompt_boundary.get("blocked"):
        payload = _blocked_prompt_boundary_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            prompt_boundary=prompt_boundary,
        )
        payload = _with_task_alignment(payload, project_root=project_root, version=resolved_version, feature=feature)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement import-evidence blocked: {payload.get('reason_code')}", err=True)
        raise typer.Exit(2)
    marker = project_root / ".beacon" / "state" / f"implementation-{slug}.json"
    marker_payload = {
        "schema_version": "1.0",
        "run_id": import_run_id,
        "import_id": import_run_id,
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "runner": "import-evidence",
        "skill": "beacon-gen-implement" if _uses_compact_skill_names(resolved_version) else "beacon-implement",
        "status": "completed",
        "imported": True,
        "source_refs": source_refs,
        "changed_files": changed_files,
        "service_dirs": service_dirs,
        "summary_ref": summary,
        "approved_by": approver,
        "prompt_boundary": prompt_boundary,
        "created_at": now_iso(),
        "generated_at": now_iso(),
    }
    write_json(marker, marker_payload)
    story_state = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True) or {}
    implemented_item_ids = _story_item_ids(story_state, kinds={"ac", "task", "test"})
    writeback_payload = record_implementation_writeback(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=import_run_id,
        implemented_item_ids=implemented_item_ids,
        changed_files=[*changed_files, *service_dirs],
    )
    refresh_evidence_manifest(
        project_root,
        refs=[str(marker.relative_to(project_root)), summary, *source_refs],
        version=resolved_version,
    )
    payload = _with_implement_surface(
        {
            **marker_payload,
            "implementation_marker": str(marker.relative_to(project_root)),
            "writeback": writeback_payload,
            "next_route": {
                "target_surface": "beacon-eval-qa" if _uses_compact_skill_names(resolved_version) else "beacon-qa",
                "command": f'beacon qa run "{feature}" --project {project_root} --version {resolved_version}',
            },
        },
        blocked=False,
    )
    state_payload = {
        **payload,
        "mode": "import-evidence",
        "adapter_type": "external-evidence",
        "request_path": "",
        "result_path": "",
        "implementation_marker": str(marker.relative_to(project_root)),
    }
    write_json(_impl_root(project_root, import_run_id) / "state.json", state_payload)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implementation evidence imported: {marker}")


@app.command("run")
def run(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    mode: str = typer.Option("", "--mode", help="Implementation mode: single|team|ralph"),
    host_runtime: str = typer.Option("", "--host-runtime", help="Host runtime for native subagent checks: codex|claude"),
    runner: str = typer.Option("auto", "--runner", help="Runner id or auto"),
    skill: str = typer.Option("", "--skill", help="Override adapter skill"),
    task_template: str = typer.Option("", "--task-template", help="Override task template"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Write request only"),
    timeout_sec: int = typer.Option(0, "--timeout-sec", help="Override timeout seconds"),
    auto_review_spec: bool = typer.Option(True, "--auto-review-spec/--no-auto-review-spec", help="Auto trigger review spec"),
    auto_review_quality: bool = typer.Option(False, "--auto-review-quality/--no-auto-review-quality", help="Auto trigger review quality"),
    auto_qa: Optional[bool] = typer.Option(None, "--auto-qa/--no-auto-qa", help="Auto trigger qa run after successful implementation"),
    auto_qa_arg: Optional[list[str]] = typer.Option(None, "--auto-qa-arg", help="Extra argument passed to auto-triggered qa run (repeatable)"),
    auto_qa_follow_handoff: Optional[bool] = typer.Option(None, "--auto-qa-follow-handoff/--no-auto-qa-follow-handoff", help="When auto-qa is blocked, follow supported repair handoff actions and retry QA"),
    auto_qa_max_rounds: int = typer.Option(0, "--auto-qa-max-rounds", help="Maximum QA rounds in the auto-qa follow-handoff loop"),
    auto_switch_branch: bool = typer.Option(False, "--auto-switch-branch", help="Explicitly switch/create the expected Beacon version branch before implementation"),
    runtime: str = typer.Option("file", "--runtime", help="Team runtime for native-team/codex-subagents: file/tmux/auto"),
    prompt_trace: str = typer.Option("", "--host-prompt", help="Original host prompt for structured prompt trace"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run implementation using the resolved skill adapter."""
    project_root = (Path(project) if project else Path.cwd()).expanduser().resolve()
    try:
        from beacon.utils.agent_trace import record_lifecycle_stage_trace

        from beacon.utils.agent_trace import lifecycle_trace_fail_closed_enabled

        _trc = record_lifecycle_stage_trace(
            project_root,
            harness="implement",
            stage="implement-run-start",
            feature_slug=feature,
            event_type="decision",
            summary=f"implement run start: {feature}",
            payload={"dry_run": bool(dry_run), "mode": mode or ""},
            fail_closed=lifecycle_trace_fail_closed_enabled(),
        )
        if lifecycle_trace_fail_closed_enabled() and str((_trc or {}).get("status") or "") != "pass":
            # soft-log only at start; do not abort implement admission here
            pass
    except Exception:
        pass
    prompt_boundary = _resolve_host_prompt_boundary(
        project_root=project_root,
        version=version,
        feature=feature,
        host_prompt=prompt_trace,
    )
    if not prompt_boundary:
        prompt_boundary = _resolve_task_template_boundary(
            project_root=project_root,
            version=version,
            feature=feature,
            task_template=task_template,
        )
    if prompt_boundary.get("blocked"):
        resolved_version = resolve_target_version(project_root, version)
        payload = _blocked_prompt_boundary_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            prompt_boundary=prompt_boundary,
        )
        if prompt_trace:
            mapped_command = f'beacon implement run "{feature}" --project {project_root} --version {resolved_version}'
            if mode:
                mapped_command += f" --mode {mode}"
            _capture_host_prompt_trace(
                project_root=project_root,
                version=resolved_version,
                feature=feature,
                host_prompt=prompt_trace,
                surface="implement-run",
                mapped_command=mapped_command,
                payload=payload,
            )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement blocked: {payload.get('reason_code')}")
        raise typer.Exit(code=2)
    code, payload = run_implement_stage(
        feature=feature,
        project_root=project_root,
        version=version,
        mode=mode or None,
        host_runtime=host_runtime or None,
        runner=runner,
        skill=skill or None,
        task_template=task_template or None,
        prompt_boundary=prompt_boundary or None,
        dry_run=dry_run,
        timeout_sec=timeout_sec or None,
        auto_review_spec=auto_review_spec,
        auto_review_quality=auto_review_quality,
        auto_qa=auto_qa,
        auto_qa_args=list(auto_qa_arg or []),
        auto_qa_follow_handoff=auto_qa_follow_handoff,
        auto_qa_max_rounds=auto_qa_max_rounds or None,
        auto_switch_branch=auto_switch_branch,
        team_runtime=runtime,
    )
    resolved_version = resolve_target_version(project_root, version)
    if prompt_boundary:
        payload["prompt_boundary"] = prompt_boundary
    _apply_post_team_ralph_handoff(payload, project_root=project_root, version=resolved_version, feature=feature)
    payload = _with_implement_surface(payload)
    if prompt_trace:
        mapped_command = f'beacon implement run "{feature}" --project {project_root} --version {resolved_version}'
        if mode:
            mapped_command += f" --mode {mode}"
        _capture_host_prompt_trace(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            host_prompt=prompt_trace,
            surface="implement-run",
            mapped_command=mapped_command,
            payload=payload,
        )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement status: {payload.get('status')}")
        typer.echo(f"run_id: {payload.get('run_id', '')}")
        if payload.get("mode"):
            typer.echo(f"mode: {payload.get('mode')}")
        if payload.get("host_runtime"):
            typer.echo(f"host_runtime: {payload.get('host_runtime')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
    raise typer.Exit(code=code)


@app.command("check-branch")
def check_branch(
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: str = typer.Option("implement-branch-preflight", "--feature", help="Feature label for traceability"),
    auto_switch_branch: bool = typer.Option(False, "--auto-switch-branch", help="Explicitly switch/create the expected Beacon version branch"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Check or repair the required Beacon implementation branch before coding."""
    project_root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    resolved_version = resolve_target_version(project_root, version)
    admission_contract = load_admission_contract(project_root, version=resolved_version)
    if admission_contract.get("require_workspace_admission"):
        payload = run_workspace_admit(
            project_root,
            version=resolved_version,
            feature=feature,
        )
        payload["alias_of"] = "beacon workspace admit"
        payload["surface"] = "implement check-branch"
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement check-branch (workspace admit): {payload.get('status')}")
            if payload.get("worktree_path"):
                typer.echo(f"worktree_path: {payload.get('worktree_path')}")
            if payload.get("branch"):
                typer.echo(f"branch: {payload.get('branch')}")
            if payload.get("reason_code"):
                typer.echo(f"reason_code: {payload.get('reason_code')}")
        raise typer.Exit(code=2 if payload.get("status") != "pass" else 0)
    branch_guard_inputs = _branch_guard_inputs(project_root, version=resolved_version, feature=feature)
    expected_branch_override = str(branch_guard_inputs.get("expected_branch", "") or "").strip()
    branch_prefix_override = str(branch_guard_inputs.get("branch_prefix", "beacon/") or "beacon/").strip() or "beacon/"
    base_branch_override = str(branch_guard_inputs.get("base_branch", "main") or "main").strip() or "main"
    workspace_git_roots = [str(item) for item in _normalize_string_list(branch_guard_inputs.get("git_roots"))]
    direct_delivery_services = [str(item) for item in _normalize_string_list(branch_guard_inputs.get("direct_delivery_services"))]
    run_id = generate_run_id(project_root)
    payload = _run_branch_preflight(
        project_root=project_root,
        version=resolved_version,
        run_id=run_id,
        feature=feature,
        auto_switch_branch=auto_switch_branch,
        require_clean_worktree_for_switch=True,
        expected_branch=expected_branch_override,
        branch_prefix=branch_prefix_override,
        base_branch=base_branch_override,
        git_roots=workspace_git_roots,
        direct_delivery_services=direct_delivery_services,
        branch_governance=branch_guard_inputs.get("branch_governance", {}),
        service_branch_map=branch_guard_inputs.get("service_branch_map", {}),
        service_worktree_map=branch_guard_inputs.get("service_worktree_map", {}),
    )
    payload["git_workflow"] = branch_guard_inputs.get("git_workflow", {})
    payload["branch_preflight_path"] = str(_branch_preflight_path(run_id))
    write_json(project_root / _branch_preflight_path(run_id), payload)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement branch check: {payload.get('status')}")
        typer.echo(f"expected_branch: {payload.get('expected_branch', '')}")
        typer.echo(f"current_branch: {payload.get('current_branch', '')}")
        if payload.get("recommended_command"):
            typer.echo(f"recommended_command: {payload.get('recommended_command')}")
    raise typer.Exit(code=2 if payload.get("blocked") else 0)


@app.command("dev-run")
def dev_run(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    runner: str = typer.Option("auto", "--runner", help="Runner id or auto"),
    runtime: str = typer.Option("file", "--runtime", help="Team runtime for native-team/codex-subagents: file/tmux/auto"),
    auto_switch_branch: bool = typer.Option(True, "--auto-switch-branch/--no-auto-switch-branch", help="Auto repair branch/workspace alignment before entering implementation"),
    auto_review_spec: bool = typer.Option(True, "--auto-review-spec/--no-auto-review-spec", help="Auto trigger review spec"),
    auto_review_quality: bool = typer.Option(False, "--auto-review-quality/--no-auto-review-quality", help="Auto trigger review quality"),
    prompt_trace: str = typer.Option("", "--host-prompt", help="Original host prompt for structured prompt trace"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Compile safe pre-implement artifacts/gates, then enter implementation."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    prompt_boundary = _resolve_host_prompt_boundary(
        project_root=project_root,
        version=resolved_version,
        feature=feature,
        host_prompt=prompt_trace,
    )
    if prompt_boundary.get("blocked"):
        payload = _blocked_prompt_boundary_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            prompt_boundary=prompt_boundary,
        )
        if prompt_trace:
            _capture_host_prompt_trace(
                project_root=project_root,
                version=resolved_version,
                feature=feature,
                host_prompt=prompt_trace,
                surface="implement-dev-run",
                mapped_command=f'beacon implement dev-run "{feature}" --project {project_root} --version {resolved_version}',
                payload=payload,
            )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement dev-run blocked: {payload.get('reason_code')}")
        raise typer.Exit(code=2)
    preflight_resolution: dict[str, Any] = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": _slug(feature),
        "version": resolved_version,
        "steps": [],
    }

    takeover_gate = evaluate_takeover_baseline_gate(project_root, version=resolved_version)
    if str(takeover_gate.get("status", "") or "") == "blocked":
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "takeover_baseline_required",
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "takeover_gate": takeover_gate,
            "preflight_resolution": {
                **preflight_resolution,
                "status": "blocked",
                "steps": [
                    {
                        "gate": "takeover_baseline",
                        "status": "blocked",
                        "reason_code": "takeover_baseline_required",
                    }
                ],
            },
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon implement dev-run blocked: takeover baseline required")
        raise typer.Exit(code=2)

    governance_preflight = _implement_version_governance_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    preflight_resolution["steps"].append(
        {
            "gate": "implement_version_governance_preflight",
            "status": "pass" if not governance_preflight.get("blocked") else "blocked",
            "reason_code": str(governance_preflight.get("reason_code") or ""),
        }
    )
    if bool(governance_preflight.get("blocked")):
        payload = _blocked_implement_version_governance_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            preflight=governance_preflight,
        )
        payload["preflight_resolution"] = {
            **preflight_resolution,
            "status": "blocked",
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement dev-run blocked: {payload.get('reason_code')}")
        raise typer.Exit(code=2)

    admission_contract = load_admission_contract(project_root, version=resolved_version)
    if admission_contract.get("require_workspace_admission"):
        admit_payload = run_workspace_admit(
            project_root,
            version=resolved_version,
            feature=feature,
        )
        preflight_resolution["steps"].append(
            {
                "gate": "workspace_admission",
                "status": "pass" if admit_payload.get("status") == "pass" else "blocked",
                "reason_code": str(admit_payload.get("reason_code") or ""),
                "worktree_path": str(admit_payload.get("worktree_path") or ""),
            }
        )
        if admit_payload.get("status") != "pass":
            payload = _with_implement_surface({
                "schema_version": "1.0",
                "status": "blocked",
                "reason_code": str(admit_payload.get("reason_code") or "workspace_admission_required"),
                "feature": feature,
                "feature_slug": _slug(feature),
                "version": resolved_version,
                "workspace_admission": admit_payload,
                "preflight_resolution": {
                    **preflight_resolution,
                    "status": "blocked",
                },
                "recommended_command": (
                    f"beacon workspace admit --project-root {project_root} "
                    f"--version {resolved_version} --feature {_slug(feature)} --json"
                ),
            }, blocked=True)
            if json_output:
                typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                typer.echo(f"Beacon implement dev-run blocked: {payload.get('reason_code')}")
            raise typer.Exit(code=2)

    branch_guard_inputs = _branch_guard_inputs(project_root, version=resolved_version, feature=feature)
    preflight_run_id = generate_run_id(project_root)
    branch_preflight = _run_branch_preflight(
        project_root=project_root,
        version=resolved_version,
        run_id=preflight_run_id,
        feature=feature,
        auto_switch_branch=auto_switch_branch,
        require_clean_worktree_for_switch=bool(branch_guard_inputs.get("require_clean_worktree_for_switch", True)),
        expected_branch=str(branch_guard_inputs.get("expected_branch", "") or "").strip(),
        branch_prefix=str(branch_guard_inputs.get("branch_prefix", "beacon/") or "beacon/").strip() or "beacon/",
        base_branch=str(branch_guard_inputs.get("base_branch", "main") or "main").strip() or "main",
        git_roots=[str(item) for item in _normalize_string_list(branch_guard_inputs.get("git_roots"))],
        direct_delivery_services=[str(item) for item in _normalize_string_list(branch_guard_inputs.get("direct_delivery_services"))],
        branch_governance=branch_guard_inputs.get("branch_governance", {}),
        service_branch_map=branch_guard_inputs.get("service_branch_map", {}),
        service_worktree_map=branch_guard_inputs.get("service_worktree_map", {}),
    )
    preflight_resolution["steps"].append(
        {
            "gate": "branch_preflight",
            "status": "pass" if not branch_preflight.get("blocked") else "blocked",
            "reason_codes": list(branch_preflight.get("reason_codes", [])),
            "expected_branch": str(branch_preflight.get("expected_branch", "") or ""),
        }
    )
    if branch_preflight.get("blocked"):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "implement_branch_guard_blocked",
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "branch_preflight": branch_preflight,
            "preflight_resolution": {
                **preflight_resolution,
                "status": "blocked",
            },
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon implement dev-run blocked: branch preflight blocked")
        raise typer.Exit(code=2)

    git_workflow_contract = ensure_implementation_git_workflow_contract(project_root, version=resolved_version, feature=feature)
    preflight_resolution["steps"].append(
        {
            "gate": "git_workflow_contract",
            "status": "materialized",
            "path": str(implementation_git_workflow_json_path(project_root, resolved_version, feature).relative_to(project_root)),
            "expected_branch": str(git_workflow_contract.get("expected_branch", "") or ""),
        }
    )

    plan_code, plan_payload = compile_implementation_plan(project_root, version=resolved_version, feature=feature)
    preflight_resolution["steps"].append(
        {
            "gate": "implementation_plan",
            "status": "planned" if plan_code == 0 else "blocked",
            "reason_code": str(plan_payload.get("reason_code", "") or ""),
            "plan_path": str(plan_payload.get("plan_path", "") or ""),
            "git_workflow_ref": str(plan_payload.get("git_workflow_ref", "") or ""),
        }
    )
    if plan_code != 0:
        payload = _with_implement_surface({
            **plan_payload,
            "preflight_resolution": {
                **preflight_resolution,
                "status": "blocked",
            },
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement dev-run blocked: {payload.get('reason_code')}")
        raise typer.Exit(code=plan_code)

    code, payload = run_implement_stage(
        feature=feature,
        project_root=project_root,
        version=resolved_version,
        runner=runner,
        prompt_boundary=prompt_boundary or None,
        auto_switch_branch=False,
        auto_review_spec=auto_review_spec,
        auto_review_quality=auto_review_quality,
        team_runtime=runtime,
    )
    payload["preflight_resolution"] = {
        **preflight_resolution,
        "status": "completed" if code == 0 else "blocked",
    }
    if prompt_boundary:
        payload["prompt_boundary"] = prompt_boundary
    _apply_post_team_ralph_handoff(payload, project_root=project_root, version=resolved_version, feature=feature)
    if prompt_trace:
        _capture_host_prompt_trace(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            host_prompt=prompt_trace,
            surface="implement-dev-run",
            mapped_command=f'beacon implement dev-run "{feature}" --project {project_root} --version {resolved_version}',
            payload=payload,
        )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement dev-run status: {payload.get('status')}")
        typer.echo(f"run_id: {payload.get('run_id', '')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
    raise typer.Exit(code=code)


@app.command("sync-git-workflow")
def sync_git_workflow(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    force_from_seed: bool = typer.Option(False, "--force-from-seed", help="Refresh the versioned contract from config/default seed even if one already exists"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Materialize or refresh the versioned git workflow contract for a feature."""
    project_root = (Path(project) if project else Path.cwd()).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    payload = ensure_implementation_git_workflow_contract(
        project_root,
        version=resolved_version,
        feature=feature,
        force_refresh_from_seed=force_from_seed,
    )
    output = {
        "schema_version": "1.0",
        "status": "materialized",
        "feature": feature,
        "feature_slug": _slug(feature),
        "version": resolved_version,
        "git_workflow_ref": str(implementation_git_workflow_json_path(project_root, resolved_version, feature).relative_to(project_root)),
        "git_workflow_markdown_ref": str(implementation_git_workflow_markdown_path(project_root, resolved_version, feature).relative_to(project_root)),
        "git_workflow": payload,
        "source_mode": "seed_refresh" if force_from_seed else str(payload.get("source", "") or "version_material"),
    }
    output = _with_implement_surface(output)
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement git workflow sync: {feature}")
        typer.echo(f"git_workflow_ref: {output['git_workflow_ref']}")
        typer.echo(f"expected_branch: {payload.get('expected_branch', '')}")
    raise typer.Exit(code=0)


def _plan_impl(feature: str, project: Optional[str], version: str, json_output: bool, host_prompt: str = "") -> int:
    project_root = (Path(project) if project else Path.cwd()).expanduser().resolve()
    prompt_boundary = _resolve_host_prompt_boundary(
        project_root=project_root,
        version=version,
        feature=feature,
        host_prompt=host_prompt,
    )
    resolved_version = resolve_target_version(project_root, version)
    if prompt_boundary.get("blocked"):
        payload = _blocked_prompt_boundary_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            prompt_boundary=prompt_boundary,
        )
        payload = _with_task_alignment(payload, project_root=project_root, version=resolved_version, feature=feature)
        if host_prompt:
            _capture_host_prompt_trace(
                project_root=project_root,
                version=resolved_version,
                feature=feature,
                host_prompt=host_prompt,
                surface="implement-plan",
                mapped_command=f'beacon implement plan "{feature}" --project-root {project_root} --version {resolved_version}',
                payload=payload,
            )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implementation plan blocked: {payload.get('reason_code')}")
        return 2
    cutover_preflight = build_legacy_cutover_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
        resume_intent="implement",
    )
    if bool(cutover_preflight.get("blocked")):
        payload = _blocked_legacy_cutover_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            preflight=cutover_preflight,
        )
        payload = _with_task_alignment(payload, project_root=project_root, version=resolved_version, feature=feature)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implementation plan blocked: {payload.get('reason_code')}")
        return 2
    governance_preflight = _implement_version_governance_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(governance_preflight.get("blocked")):
        payload = _blocked_implement_version_governance_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            preflight=governance_preflight,
        )
        payload = _with_task_alignment(payload, project_root=project_root, version=resolved_version, feature=feature)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implementation plan blocked: {payload.get('reason_code')}")
        return 2
    closure_preflight = _requirement_closure_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(closure_preflight.get("blocked")):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(closure_preflight.get("reason_code") or "requirement_closure_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "closure_preflight": closure_preflight,
            "recommended_command": str(
                closure_preflight.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-closure-blocked",
                )
            ),
        }, blocked=True)
        payload = _with_task_alignment(payload, project_root=project_root, version=resolved_version, feature=feature)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implementation plan blocked: {payload.get('reason_code')}")
        return 2
    automation_runtime_preflight = _automation_runtime_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(automation_runtime_preflight.get("blocked")):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(automation_runtime_preflight.get("reason_code") or "automation_runtime_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "automation_runtime_preflight": automation_runtime_preflight,
            "closure_preflight": closure_preflight,
            "recommended_command": str(
                automation_runtime_preflight.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="automation-runtime-blocked",
                )
            ),
        }, blocked=True)
        payload = _with_task_alignment(payload, project_root=project_root, version=resolved_version, feature=feature)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implementation plan blocked: {payload.get('reason_code')}")
        return 2
    requirement_package_gate = build_requirement_package_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        strict=True,
    )
    if str(requirement_package_gate.get("status") or "").lower() == "blocked":
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(requirement_package_gate.get("reason_code") or "requirement_package_contract_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "requirement_package_gate": requirement_package_gate,
            "recommended_command": str(
                requirement_package_gate.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-package-contract-blocked",
                )
            ),
        }, blocked=True)
        payload = _with_task_alignment(payload, project_root=project_root, version=resolved_version, feature=feature)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implementation plan blocked: {payload.get('reason_code')}")
        return 2
    code, payload = compile_implementation_plan(project_root, version=version, feature=feature)
    if prompt_boundary:
        payload["prompt_boundary"] = prompt_boundary
    if host_prompt:
        _capture_host_prompt_trace(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            host_prompt=host_prompt,
            surface="implement-plan",
            mapped_command=f'beacon implement plan "{feature}" --project-root {project_root} --version {resolved_version}',
            payload=payload,
        )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implementation plan status: {payload.get('status')}")
        if payload.get("plan_id"):
            typer.echo(f"plan_id: {payload.get('plan_id')}")
        if payload.get("plan_path"):
            typer.echo(f"plan_path: {payload.get('plan_path')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
    return code


def _team_plan_impl(feature: str, project: Optional[str], version: str, json_output: bool, host_prompt: str = "") -> int:
    project_root = Path(project) if project else Path.cwd()
    prompt_boundary = _resolve_host_prompt_boundary(
        project_root=project_root,
        version=version,
        feature=feature,
        host_prompt=host_prompt,
    )
    resolved_version = resolve_target_version(project_root, version)
    if prompt_boundary.get("blocked"):
        payload = _blocked_prompt_boundary_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            prompt_boundary=prompt_boundary,
        )
        if host_prompt:
            _capture_host_prompt_trace(
                project_root=project_root,
                version=resolved_version,
                feature=feature,
                host_prompt=host_prompt,
                surface="implement-team-plan",
                mapped_command=f'beacon implement team-plan "{feature}" --project-root {project_root} --version {resolved_version}',
                payload=payload,
            )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement team-plan blocked: {payload.get('reason_code')}")
        return 2
    governance_preflight = _implement_version_governance_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(governance_preflight.get("blocked")):
        payload = _blocked_implement_version_governance_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            preflight=governance_preflight,
        )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement team-plan blocked: {payload.get('reason_code')}")
        return 2
    closure_preflight = _requirement_closure_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(closure_preflight.get("blocked")):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(closure_preflight.get("reason_code") or "requirement_closure_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "closure_preflight": closure_preflight,
            "recommended_command": str(
                closure_preflight.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-closure-blocked",
                )
            ),
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement team-plan blocked: {payload.get('reason_code')}")
        return 2
    automation_runtime_preflight = _automation_runtime_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(automation_runtime_preflight.get("blocked")):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(automation_runtime_preflight.get("reason_code") or "automation_runtime_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "automation_runtime_preflight": automation_runtime_preflight,
            "closure_preflight": closure_preflight,
            "recommended_command": str(
                automation_runtime_preflight.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="automation-runtime-blocked",
                )
            ),
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement team-plan blocked: {payload.get('reason_code')}")
        return 2
    requirement_package_gate = build_requirement_package_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        strict=True,
    )
    if str(requirement_package_gate.get("status") or "").lower() == "blocked":
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(requirement_package_gate.get("reason_code") or "requirement_package_contract_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "requirement_package_gate": requirement_package_gate,
            "recommended_command": str(
                requirement_package_gate.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-package-contract-blocked",
                )
            ),
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement team-plan blocked: {payload.get('reason_code')}")
        return 2
    closure_preflight = _requirement_closure_preflight(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    if bool(closure_preflight.get("blocked")):
        payload = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": str(closure_preflight.get("reason_code") or "requirement_closure_blocked"),
            "feature": feature,
            "feature_slug": _slug(feature),
            "version": resolved_version,
            "closure_preflight": closure_preflight,
            "requirement_package_gate": requirement_package_gate,
            "recommended_command": str(
                closure_preflight.get("recommended_command")
                or build_change_command(
                    feature=feature,
                    project_root=project_root,
                    version=resolved_version,
                    reason="requirement-closure-blocked",
                )
            ),
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement team-plan blocked: {payload.get('reason_code')}")
        return 2
    code, payload = compile_implementation_plan(project_root, version=version, feature=feature)
    team_mode = {
        "preferred_surface": "implement-team",
        "preferred_runner": "codex-subagents" if _semver_tuple(resolved_version) >= (1, 3, 0) else "native-team",
        "plan_command": f'beacon implement team-plan "{feature}" --project-root {project_root} --version {resolved_version}',
        "run_command": f'beacon implement team-run "{feature}" --project {project_root} --version {resolved_version}',
        "dev_run_command": f'beacon implement dev-run "{feature}" --project {project_root} --version {resolved_version}',
    }
    payload = {
        **payload,
        "team_surface": "implement-team",
        "team_mode": payload.get("team_mode", {}) or team_mode,
        "recommended_command": str((payload.get("team_mode", {}) or team_mode).get("run_command") or ""),
    }
    payload = _with_implement_surface(payload)
    if prompt_boundary:
        payload["prompt_boundary"] = prompt_boundary
    if host_prompt:
        _capture_host_prompt_trace(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            host_prompt=host_prompt,
            surface="implement-team-plan",
            mapped_command=f'beacon implement team-plan "{feature}" --project-root {project_root} --version {resolved_version}',
            payload=payload,
        )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement team-plan status: {payload.get('status')}")
        typer.echo(f"team_surface: implement-team")
        if payload.get("recommended_command"):
            typer.echo(f"recommended_command: {payload.get('recommended_command')}")
    return code


@app.command("plan")
def plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    host_prompt: str = typer.Option("", "--host-prompt", help="Original host prompt for structured prompt trace"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Compile PRD/user-story/test-case into an implementation plan."""
    raise typer.Exit(code=_plan_impl(feature, project, version, json_output, host_prompt))


@app.command("team-plan")
def team_plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    host_prompt: str = typer.Option("", "--host-prompt", help="Original host prompt for structured prompt trace"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Compile an implementation plan with explicit implement-team guidance."""
    raise typer.Exit(code=_team_plan_impl(feature, project, version, json_output, host_prompt))


@app.command("compile-plan")
def compile_plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    host_prompt: str = typer.Option("", "--host-prompt", help="Original host prompt for structured prompt trace"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Alias of `implement plan`."""
    raise typer.Exit(code=_plan_impl(feature, project, version, json_output, host_prompt))


@app.command("team-run")
def team_run(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    auto_review_spec: bool = typer.Option(True, "--auto-review-spec/--no-auto-review-spec", help="Auto trigger review spec"),
    auto_review_quality: bool = typer.Option(False, "--auto-review-quality/--no-auto-review-quality", help="Auto trigger review quality"),
    runtime: str = typer.Option("file", "--runtime", help="Runtime mode: file/tmux/auto"),
    host_prompt: str = typer.Option("", "--host-prompt", help="Original host prompt for structured prompt trace"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run implementation through the explicit implement-team surface."""
    project_root = Path(project) if project else Path.cwd()
    prompt_boundary = _resolve_host_prompt_boundary(
        project_root=project_root,
        version=version,
        feature=feature,
        host_prompt=host_prompt,
    )
    resolved_version = resolve_target_version(project_root, version)
    if prompt_boundary.get("blocked"):
        payload = _blocked_prompt_boundary_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            prompt_boundary=prompt_boundary,
        )
        if host_prompt:
            _capture_host_prompt_trace(
                project_root=project_root,
                version=resolved_version,
                feature=feature,
                host_prompt=host_prompt,
                surface="implement-team-run",
                mapped_command=f'beacon implement team-run "{feature}" --project {project_root} --version {resolved_version}',
                payload=payload,
            )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon implement team-run blocked: {payload.get('reason_code')}")
        raise typer.Exit(code=2)
    code, payload = run_implement_stage(
        feature=feature,
        project_root=project_root,
        version=version,
        mode="team",
        runner="codex-subagents",
        prompt_boundary=prompt_boundary or None,
        auto_review_spec=auto_review_spec,
        auto_review_quality=auto_review_quality,
        team_runtime=runtime,
    )
    if prompt_boundary:
        payload["prompt_boundary"] = prompt_boundary
    _apply_post_team_ralph_handoff(payload, project_root=project_root, version=resolved_version, feature=feature)
    if host_prompt:
        _capture_host_prompt_trace(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            host_prompt=host_prompt,
            surface="implement-team-run",
            mapped_command=f'beacon implement team-run "{feature}" --project {project_root} --version {resolved_version}',
            payload=payload,
        )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement team-run status: {payload.get('status')}")
        typer.echo(f"team_surface: {payload.get('team_surface', '')}")
        typer.echo(f"run_id: {payload.get('run_id', '')}")
    raise typer.Exit(code=code)


@app.command("status")
def status(
    feature_or_run_id: str = typer.Argument(..., help="Feature name or run id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    run_id: str = typer.Option("", "--run-id", help="Explicit run id"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show implementation run status."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    target_run = run_id.strip()
    feature_slug = _slug(feature_or_run_id)
    implement_root = project_root / ".beacon" / "implement"
    state_payload: dict[str, Any] | None = None
    if target_run:
        state_path = implement_root / target_run / "state.json"
        if state_path.exists():
            state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    else:
        candidate_states = sorted(implement_root.glob("*/state.json")) if implement_root.exists() else []
        fallback_state: dict[str, Any] | None = None
        for state_path in reversed(candidate_states):
            payload = json.loads(state_path.read_text(encoding="utf-8"))
            payload_feature_matches = (
                str(payload.get("feature_slug", "")) == feature_slug
                or str(payload.get("feature", "")) == feature_or_run_id
            )
            if not payload_feature_matches:
                continue
            payload_version = normalize_version(str(payload.get("version", "")).strip())
            if payload_version and payload_version == resolved_version:
                state_payload = payload
                break
            if fallback_state is None:
                fallback_state = payload
        if state_payload is None:
            state_payload = fallback_state
        if state_payload is None and feature_or_run_id.startswith("run-"):
            state_path = implement_root / feature_or_run_id / "state.json"
            if state_path.exists():
                state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    if state_payload is None:
        missing_payload = _with_implement_surface({
            "status": "missing",
            "reason_code": "implementation_run_not_found",
            "message": "Implementation run not found",
            "feature": feature_or_run_id if not feature_or_run_id.startswith("run-") else "",
            "feature_slug": feature_slug if not feature_or_run_id.startswith("run-") else "",
            "run_id": target_run or (feature_or_run_id if feature_or_run_id.startswith("run-") else ""),
            "version": resolved_version,
            "project_root": str(project_root),
            "summary_exists": False,
            "review_spec_exists": False,
            "review_quality_exists": False,
            "implementation_marker_exists": False,
            "implementation_plan_exists": False,
            "implementation_plan_markdown_exists": False,
            "implementation_plan_progress_exists": False,
            "implementation_plan_progress": {},
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(missing_payload, ensure_ascii=False, indent=2))
            return
        typer.echo(json.dumps(missing_payload, ensure_ascii=False, indent=2))
        return

    slug = str(state_payload.get("feature_slug", feature_slug))
    summary = _summary_paths(project_root, resolved_version, slug).get("json")
    review_spec = execution_file_candidates(project_root, resolved_version, f"review-spec-{slug}.json")
    review_quality = execution_file_candidates(project_root, resolved_version, f"review-quality-{slug}.json")
    output = dict(state_payload)
    output["summary_exists"] = bool(summary and summary.exists())
    output["review_spec_exists"] = any(path.exists() for path in review_spec)
    output["review_quality_exists"] = any(path.exists() for path in review_quality)
    output["implementation_marker_exists"] = (project_root / ".beacon" / "state" / f"implementation-{slug}.json").exists()
    output["implementation_plan_exists"] = implementation_plan_json_path(project_root, resolved_version, slug).exists()
    output["implementation_plan_markdown_exists"] = implementation_plan_markdown_path(project_root, resolved_version, slug).exists()
    output["implementation_plan_progress_exists"] = implementation_plan_progress_path(project_root, resolved_version, slug).exists()
    output["implementation_plan_progress"] = load_implementation_plan_progress(project_root, version=resolved_version, feature=slug)
    output["requirement_completeness"] = load_requirement_completeness(project_root, resolved_version, slug)
    output = _with_implement_surface(output)
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(output, ensure_ascii=False, indent=2))


@app.command("ralph-status")
def ralph_status(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show Ralph controller state for one feature."""
    project_root = Path(project) if project else Path.cwd()
    payload = load_ralph_state(project_root, feature=feature)
    if not payload:
        typer.echo("Ralph state not found", err=True)
        raise typer.Exit(2)
    payload = _reconcile_ralph_state_with_release_truth(project_root, feature=feature, state=payload)
    payload = _with_implement_surface(payload)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        raise typer.Exit(0)
    typer.echo("Beacon Ralph Status")
    typer.echo("=" * 20)
    typer.echo(f"feature: {payload.get('feature', '')}")
    typer.echo(f"version: {payload.get('version', '')}")
    typer.echo(f"phase: {payload.get('phase', '')}")
    typer.echo(f"status: {payload.get('status', '')}")
    typer.echo(f"stop_state: {payload.get('stop_state', '') or 'N/A'}")
    typer.echo(f"next_action: {payload.get('next_action', '') or 'N/A'}")
    typer.echo(f"recommended_command: {payload.get('recommended_command', '') or 'N/A'}")
    raise typer.Exit(0)


@app.command("ralph-resume")
def ralph_resume(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Resume the next actionable Ralph step when it is safe to do so."""
    project_root = Path(project) if project else Path.cwd()
    payload = load_ralph_state(project_root, feature=feature)
    if not payload:
        typer.echo("Ralph state not found", err=True)
        raise typer.Exit(2)
    next_action = str(payload.get("next_action", "") or "").strip()
    command = str(payload.get("recommended_command", "") or "").strip()
    if next_action not in {"implement", "qa", "verify", "test-case", "review_quality", "release"} or not command:
        output = _with_implement_surface({
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "ralph_resume_not_actionable",
            "feature": feature,
            "ralph": payload,
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon Ralph resume blocked")
            typer.echo(f"next_action: {next_action or 'N/A'}")
            typer.echo(f"recommended_command: {command or 'N/A'}")
        raise typer.Exit(2)
    exit_code, result = _run_beacon_json_command(project_root, command)
    _refresh_ralph_state_after_resume(
        project_root,
        feature=feature,
        resumed_action=next_action,
        exit_code=exit_code,
        result=result if isinstance(result, dict) else {},
    )
    output = _with_implement_surface({
        "schema_version": "1.0",
        "status": "completed" if exit_code == 0 else "failed",
        "feature": feature,
        "recommended_command": command,
        "exit_code": exit_code,
        "result": result,
    }, blocked=exit_code != 0)
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon Ralph resume status: {output['status']}")
        typer.echo(f"recommended_command: {command}")
    raise typer.Exit(exit_code)
