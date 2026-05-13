"""Beacon report command."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import typer

from beacon.utils.artifact_paths import execution_file_output, human_execution_file
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.control_plane import build_resume_contract
from beacon.utils.implementation_plan import implementation_plan_supported, load_implementation_plan_progress
from beacon.utils.runtime import load_run_state, newest_run_id, now_iso, read_json, write_json
from beacon.utils.acceptance_audit import (
    build_acceptance_audit_payload,
    render_acceptance_audit_markdown,
    run_regression_command,
    write_acceptance_audit,
)
from beacon.utils.versioning import resolve_runtime_version, resolve_target_version
from beacon.utils.material_audit import build_material_audit
from beacon.utils.learning_loop import load_keep_discard_engine
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.acceptance_kit import build_acceptance_kit_projection
from beacon.utils.v110_baseline import load_latest_spec_fingerprint
from beacon.utils.v110_metrics import (
    compute_baseline_drift_metrics,
    compute_memory_governance_metrics,
)
from beacon.utils.v115_delivery import refresh_evidence_manifest
from beacon.utils.versioning import runtime_feature_supported
from beacon.utils.workflow_memory import (
    compute_memory_metrics,
    compute_workflow_progress,
    resolve_workflow_run_id,
)

app = typer.Typer(
    name="report",
    help="Generate run reports",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _human_summary(machine: dict[str, Any]) -> str:
    release_summary = summarize_release_scorecard(machine.get("release_scorecard"))
    lines = [
        "# Beacon Human Summary",
        "",
        f"- Run ID: `{machine.get('run_id', 'latest')}`",
        f"- Workflow: `{machine.get('workflow', 'workflow')}`",
        f"- Mode: `{machine.get('mode', 'normal')}`",
        f"- Status: **{machine.get('status', 'unknown')}**",
        f"- Release Ready: `{release_summary.get('release_ready')}`",
        f"- Release Gate: `{release_summary.get('gate_status')}`",
        f"- QA Status: `{release_summary.get('qa_status')}`",
        f"- QA Mode: `{release_summary.get('qa_execution_mode')}`",
        "",
        "## Release Readiness",
        f"- release_ready: `{release_summary.get('release_ready')}`",
        f"- gate_status: `{release_summary.get('gate_status')}`",
        f"- gate_blocked_count: `{release_summary.get('gate_blocked_count')}`",
        f"- qa_status: `{release_summary.get('qa_status')}`",
        f"- qa_execution_mode: `{release_summary.get('qa_execution_mode')}`",
        f"- qa_evidence_done: `{release_summary.get('qa_evidence_done')}`",
        f"- qa_project_profile_gate: `{release_summary.get('qa_project_profile_gate_status')}`",
        f"- requirement_clarity_status: `{release_summary.get('requirement_clarity_status')}`",
        f"- requirement_clarity_blocked: `{release_summary.get('requirement_clarity_blocked')}`",
        f"- technical_review_status: `{release_summary.get('technical_review_status')}`",
        f"- technical_review_review_status: `{release_summary.get('technical_review_review_status')}`",
        f"- research_projection_present: `{release_summary.get('research_projection_present')}`",
        f"- research_projection_section_count: `{release_summary.get('research_projection_section_count')}`",
        f"- research_projection_sections: `{', '.join(release_summary.get('research_projection_sections') or [])}`",
        f"- change_documents_status: `{release_summary.get('change_documents_status')}`",
        f"- change_documents_feature_count: `{release_summary.get('change_documents_feature_count')}`",
        f"- change_documents_includes_current_feature: `{release_summary.get('change_documents_includes_current_feature')}`",
        f"- prototype_status: `{release_summary.get('prototype_status')}`",
        f"- prototype_review_status: `{release_summary.get('prototype_review_status')}`",
        f"- prototype_gate_ready: `{release_summary.get('prototype_gate_ready')}`",
        f"- prototype_drift_status: `{release_summary.get('prototype_drift_status')}`",
        "- note: `release_ready` reflects current-feature closure readiness; change documents and package closure remain version-line governance surfaces.",
        f"- release_confidence_min: `{release_summary.get('release_confidence_min')}`",
        f"- release_confidence_avg: `{release_summary.get('release_confidence_avg')}`",
        f"- review_required_count: `{release_summary.get('review_required_count')}`",
        f"- needs_replay_count: `{release_summary.get('needs_replay_count')}`",
        f"- continue_decision: `{release_summary.get('continue_decision')}`",
        f"- test_case_backfill_required: `{release_summary.get('test_case_backfill_required')}`",
        f"- main_kpi: `{release_summary.get('main_kpi')}`",
        f"- main_kpi_score: `{release_summary.get('main_kpi_score')}`",
        f"- keep/review/discard: `{release_summary.get('decision_keep')}/{release_summary.get('decision_review')}/{release_summary.get('decision_discard')}`",
        "",
        "## Artifacts",
    ]
    artifacts = machine.get("artifacts", {})
    if isinstance(artifacts, dict) and artifacts:
        for key, value in artifacts.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- (none)")
    memory_metrics = machine.get("memory_metrics")
    coverage = machine.get("coverage_metrics")
    memory_governance = machine.get("memory_governance")
    baseline_drift = machine.get("baseline_drift")
    consistency_snapshot = machine.get("consistency_snapshot")
    control_plane = machine.get("control_plane")
    qa_status = machine.get("qa_status")
    learning_plane = machine.get("learning_plane")
    release_scorecard = machine.get("release_scorecard")
    if isinstance(memory_metrics, dict):
        lines.extend(
            [
                "",
                "## Memory Loop",
                f"- closure_complete: `{memory_metrics.get('closure_complete')}`",
                f"- recall_injections: `{memory_metrics.get('recall_injections')}`",
                f"- writebacks: `{memory_metrics.get('writebacks')}`",
                f"- feedback_assimilations: `{memory_metrics.get('feedback_assimilations')}`",
                f"- next_stage: `{machine.get('workflow_progress', {}).get('next_stage')}`",
            ]
        )
        prototype_state = ((machine.get("workflow_progress", {}) or {}).get("stages", {}) or {}).get("prototype")
        if isinstance(prototype_state, dict):
            lines.append(f"- prototype_status: `{prototype_state.get('status')}`")
    if isinstance(coverage, dict):
        lines.extend(
            [
                "",
                "## Coverage",
                f"- story: `{coverage.get('implemented_story')}/{coverage.get('planned_story')}`",
                f"- ac: `{coverage.get('tested_ac')}/{coverage.get('total_ac')}`",
                f"- tc: `{coverage.get('executed_tc')}/{coverage.get('total_tc')}`",
                f"- full_coverage: `{coverage.get('full_coverage')}`",
            ]
        )
    if isinstance(memory_governance, dict):
        lines.extend(
            [
                "",
                "## Memory Governance",
                f"- raw_debug_events: `{memory_governance.get('raw_debug_events')}`",
                f"- candidate_files: `{memory_governance.get('candidate_files')}`",
                f"- apply_reports: `{memory_governance.get('apply_reports')}`",
                f"- unsynced_candidates: `{memory_governance.get('unsynced_candidates')}`",
                f"- lifecycle_dedupe_keys: `{memory_governance.get('lifecycle_dedupe_keys')}`",
            ]
        )
    if isinstance(baseline_drift, dict):
        lines.extend(
            [
                "",
                "## Baseline Drift",
                f"- has_baseline: `{baseline_drift.get('has_baseline')}`",
                f"- baseline_id: `{baseline_drift.get('baseline_id')}`",
                f"- revision_of: `{baseline_drift.get('revision_of')}`",
                f"- changed_layers: `{baseline_drift.get('changed_layers')}`",
                f"- doc_chain_update_required: `{baseline_drift.get('doc_chain_update_required')}`",
            ]
        )
    if isinstance(consistency_snapshot, dict):
        lines.extend(
            [
                "",
                "## Consistency Snapshot",
                f"- status: `{consistency_snapshot.get('status')}`",
                f"- expected_spec_fingerprint: `{consistency_snapshot.get('expected_spec_fingerprint')}`",
                f"- actual_spec_fingerprint: `{consistency_snapshot.get('actual_spec_fingerprint')}`",
                f"- reason_codes: `{consistency_snapshot.get('reason_codes')}`",
            ]
        )
    if isinstance(control_plane, dict):
        lines.extend(
            [
                "",
                "## Control Plane",
                f"- failure_streak: `{control_plane.get('failure_streak')}`",
                f"- escalation_level: `{control_plane.get('escalation_level')}`",
                f"- required_next_action: `{control_plane.get('required_next_action')}`",
                f"- current_blocker: `{control_plane.get('current_blocker')}`",
            ]
        )
    if isinstance(qa_status, dict) and qa_status:
        lines.extend(
            [
                "",
                "## QA Closure",
                f"- feature: `{qa_status.get('feature')}`",
                f"- status: `{qa_status.get('status')}`",
                f"- evidence_done: `{qa_status.get('evidence_done')}`",
            ]
        )
    if isinstance(learning_plane, dict):
        decision_summary = learning_plane.get("decision_summary", {}) if isinstance(learning_plane.get("decision_summary"), dict) else {}
        if decision_summary:
            lines.extend(
                [
                    "",
                    "## Keep / Discard Engine",
                    f"- keep: `{decision_summary.get('keep')}`",
                    f"- review: `{decision_summary.get('review')}`",
                    f"- discard: `{decision_summary.get('discard')}`",
                ]
            )
    implementation_plan = machine.get("implementation_plan")
    if isinstance(implementation_plan, dict) and implementation_plan:
        lines.extend(
            [
                "",
                "## Implementation Plan",
                f"- plan_id: `{implementation_plan.get('plan_id')}`",
                f"- status: `{implementation_plan.get('status')}`",
                f"- next_task_id: `{implementation_plan.get('next_task_id')}`",
                f"- blocked_task_ids: `{implementation_plan.get('blocked_task_ids')}`",
                f"- counts: `{implementation_plan.get('counts')}`",
            ]
        )
    if release_summary.get("requirement_clarity_status") or release_summary.get("technical_review_status"):
        lines.extend(
            [
                "",
                "## Human-Loop Gates",
                f"- requirement_clarity_status: `{release_summary.get('requirement_clarity_status')}`",
                f"- requirement_clarity_blocked: `{release_summary.get('requirement_clarity_blocked')}`",
                f"- requirement_clarity_finding_count: `{release_summary.get('requirement_clarity_finding_count')}`",
                f"- technical_review_status: `{release_summary.get('technical_review_status')}`",
                f"- technical_review_blocked: `{release_summary.get('technical_review_blocked')}`",
                f"- technical_review_review_status: `{release_summary.get('technical_review_review_status')}`",
                f"- research_projection_present: `{release_summary.get('research_projection_present')}`",
                f"- research_projection_sections: `{', '.join(release_summary.get('research_projection_sections') or [])}`",
            ]
        )
    if isinstance(release_scorecard, dict) and release_scorecard and release_summary.get("exhaustiveness_status"):
        lines.append(
            f"- exhaustiveness: `{release_summary.get('exhaustiveness_status')}` score=`{release_summary.get('exhaustiveness_score')}` threshold=`{release_summary.get('exhaustiveness_threshold')}`"
        )
    return "\n".join(lines) + "\n"


def _compute_consistency_snapshot(project_root: Path, *, version: str) -> dict[str, Any]:
    fingerprint_payload = load_latest_spec_fingerprint(project_root, version=version)
    expected_hash = str(fingerprint_payload.get("fingerprint_hash", "")).strip()
    status_path = project_root / ".beacon" / "auto-test-status.json"
    status_data: dict[str, Any] = {}
    if status_path.exists():
        try:
            loaded = json.loads(status_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                status_data = loaded
        except Exception:  # noqa: BLE001
            status_data = {}

    execution = status_data.get("execution")
    actual_hash = ""
    if isinstance(execution, dict):
        spec_fp = execution.get("spec_fingerprint")
        if isinstance(spec_fp, dict):
            actual_hash = str(spec_fp.get("fingerprint_hash", "")).strip()
    if not actual_hash:
        actual_hash = str(status_data.get("spec_fingerprint_hash", "")).strip()

    reason_codes: list[str] = []
    status = "pass"
    if expected_hash and actual_hash and expected_hash != actual_hash:
        status = "blocked"
        reason_codes.append("spec_impl_drift_detected")
    elif expected_hash and not actual_hash:
        status = "warn"
        reason_codes.append("execution_fingerprint_missing")
    elif not expected_hash:
        status = "warn"
        reason_codes.append("spec_fingerprint_missing")

    return {
        "status": status,
        "expected_spec_fingerprint": expected_hash,
        "actual_spec_fingerprint": actual_hash,
        "reason_codes": reason_codes,
    }


def _latest_implement_state(project_root: Path, *, feature: str | None = None) -> dict[str, Any]:
    implement_root = project_root / ".beacon" / "implement"
    if not implement_root.exists():
        return {}
    candidates = sorted(implement_root.glob("*/state.json"))
    filtered_feature = str(feature or "").strip()
    for state_path in reversed(candidates):
        loaded = read_json(state_path, {})
        if not isinstance(loaded, dict):
            continue
        if filtered_feature and str(loaded.get("feature", "") or "").strip() != filtered_feature:
            continue
        return loaded
    return {}


def _build_machine_payload(
    project_root: Path,
    run_id: str,
    *,
    version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    resolved = run_id
    if not resolved or resolved == "latest":
        resolved = (
            resolve_workflow_run_id(project_root, version=version, feature=feature)
            or newest_run_id(project_root)
            or "latest"
        )

    state = load_run_state(project_root, resolved) if resolved != "latest" else None
    if not state:
        progress = compute_workflow_progress(
            project_root,
            run_id=None if resolved == "latest" else resolved,
            version=version,
            feature=feature,
        )
        coverage_version = (
            (version or "").strip()
            or str(progress.get("version", "")).strip()
            or resolve_target_version(project_root, None)
        )
        consistency_snapshot = _compute_consistency_snapshot(project_root, version=coverage_version)
        implement_state = _latest_implement_state(project_root, feature=feature)
        plan_feature = str(feature or progress.get("feature", "") or implement_state.get("feature", "") or "").strip()
        implementation_plan = (
            load_implementation_plan_progress(project_root, version=coverage_version, feature=plan_feature)
            if plan_feature and implementation_plan_supported(coverage_version)
            else {}
        )
        return {
            "run_id": resolved,
            "workflow": "workflow",
            "mode": "normal",
            "status": str(implement_state.get("status", "unknown") or "unknown"),
            "reason": str(implement_state.get("reason_code", "no-run-state") or "no-run-state"),
            "events": [],
            "llm_prompts": [],
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "tool_calls": [],
            "artifacts": {},
            "deviations": [],
            "confirmations": [],
            "memory_metrics": compute_memory_metrics(
                project_root,
                None if resolved == "latest" else resolved,
                version=version,
                feature=feature,
            ),
            "coverage_metrics": compute_coverage_metrics(
                project_root,
                version=coverage_version,
                feature=feature,
            ),
            "memory_governance": compute_memory_governance_metrics(project_root),
            "baseline_drift": compute_baseline_drift_metrics(project_root, version=coverage_version),
            "consistency_snapshot": consistency_snapshot,
            "control_plane": build_resume_contract(project_root, run_id=None if resolved == "latest" else resolved),
            "qa_status": load_qa_status(project_root),
            "learning_plane": load_keep_discard_engine(project_root),
            "release_scorecard": build_release_scorecard(project_root, version=coverage_version),
            "implementation_plan": implementation_plan,
            "source_of_truth": {
                "root": f"docs/beacon/{coverage_version}",
                "runtime_state_root": ".beacon",
                "formal_package_closure": build_material_audit(project_root, version=coverage_version, strict=False).get("status", "unknown"),
            },
            "workflow_progress": progress,
            "filters": {"version": version or "", "feature": feature or ""},
            "generated_at": now_iso(),
        }

    progress = compute_workflow_progress(
        project_root,
        run_id=resolved,
        version=version,
        feature=feature,
    )
    coverage_version = (
        (version or "").strip()
        or str(progress.get("version", "")).strip()
        or str(state.get("version", "")).strip()
        or resolve_target_version(project_root, None)
    )
    consistency_snapshot = _compute_consistency_snapshot(project_root, version=coverage_version)
    plan_feature = str(feature or state.get("feature", "") or progress.get("feature", "") or "").strip()
    implementation_plan = (
        load_implementation_plan_progress(project_root, version=coverage_version, feature=plan_feature)
        if plan_feature and implementation_plan_supported(coverage_version)
        else {}
    )
    return {
        "run_id": resolved,
        "workflow": state.get("workflow", "workflow"),
        "mode": state.get("mode", "normal"),
        "status": state.get("status", "unknown"),
        "reason": state.get("reason", ""),
        "events": state.get("events", []),
        "llm_prompts": state.get("llm_prompts", []),
        "token_usage": state.get("token_usage", {"prompt_tokens": 0, "completion_tokens": 0}),
        "tool_calls": state.get("tool_calls", []),
        "artifacts": state.get("artifacts", {}),
        "deviations": state.get("deviations", []),
        "confirmations": state.get("confirmations", []),
        "memory_metrics": compute_memory_metrics(
            project_root,
            resolved,
            version=version,
            feature=feature,
        ),
        "coverage_metrics": compute_coverage_metrics(
            project_root,
            version=coverage_version,
            feature=feature,
        ),
        "memory_governance": compute_memory_governance_metrics(project_root),
        "baseline_drift": compute_baseline_drift_metrics(project_root, version=coverage_version),
        "consistency_snapshot": consistency_snapshot,
        "control_plane": build_resume_contract(project_root, run_id=resolved),
        "qa_status": load_qa_status(project_root),
        "learning_plane": load_keep_discard_engine(project_root),
        "release_scorecard": build_release_scorecard(project_root, version=coverage_version),
        "implementation_plan": implementation_plan,
        "source_of_truth": {
            "root": f"docs/beacon/{coverage_version}",
            "runtime_state_root": ".beacon",
            "formal_package_closure": build_material_audit(project_root, version=coverage_version, strict=False).get("status", "unknown"),
        },
        "workflow_progress": progress,
        "filters": {"version": version or "", "feature": feature or ""},
        "generated_at": now_iso(),
    }


def _report_impl(
    project_root: str,
    run_id: str,
    human: bool,
    machine: bool,
    version: str,
    feature: str,
    write_summary: bool,
) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    version_filter = (
        resolve_target_version(root, version)
        if version and version.strip()
        else resolve_target_version(root, None)
    )
    feature_filter = feature.strip() if feature and feature.strip() else None
    payload = _build_machine_payload(root, run_id, version=version_filter, feature=feature_filter)
    report_version = (
        version_filter
        or str(payload.get("workflow_progress", {}).get("version", "")).strip()
        or str(payload.get("filters", {}).get("version", "")).strip()
        or resolve_target_version(root, None)
    )
    if write_summary:
        summary_json = execution_file_output(root, report_version, "summary.json")
        summary_md = human_execution_file(root, report_version, "summary.md")
        write_json(summary_json, payload)
        summary_md.parent.mkdir(parents=True, exist_ok=True)
        summary_md.write_text(_human_summary(payload), encoding="utf-8")
        refresh_evidence_manifest(
            root,
            refs=[
                str(summary_json.relative_to(root)),
                str(summary_md.relative_to(root)),
            ],
            version=report_version,
        )

    emit_human = human or not machine
    if emit_human:
        typer.echo(_human_summary(payload), nl=False)
    else:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _git_status_lines(project_root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "status", "--short"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return []
    if result.returncode != 0:
        return []
    return [line for line in (result.stdout or "").splitlines() if line.strip()]


def _run_real_project_validation_command(project_root: Path, args: list[str]) -> dict[str, Any]:
    package_root = Path(__file__).resolve().parents[2]
    env = dict(os.environ)
    existing_pythonpath = str(env.get("PYTHONPATH") or "").strip()
    env["PYTHONPATH"] = (
        str(package_root)
        if not existing_pythonpath
        else f"{package_root}{os.pathsep}{existing_pythonpath}"
    )
    env["BEACON_ALLOW_CONTEXT_VERSION_DRIFT"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "beacon.main", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    stdout = str(result.stdout or "")
    stderr = str(result.stderr or "")
    parsed: dict[str, Any] | None = None
    for candidate in (stdout.strip(), stderr.strip()):
        if not candidate:
            continue
        try:
            loaded = json.loads(candidate)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(loaded, dict):
            parsed = loaded
            break
    return {
        "command": " ".join(args),
        "args": list(args),
        "exit_code": int(result.returncode),
        "stdout": stdout,
        "stderr": stderr,
        "json": parsed or {},
    }


def _classify_validation_surface(result: dict[str, Any]) -> str:
    exit_code = int(result.get("exit_code") or 0)
    payload = result.get("json") if isinstance(result.get("json"), dict) else {}
    stdout = str(result.get("stdout") or "").strip()
    stderr = str(result.get("stderr") or "").strip()
    combined = "\n".join(part for part in (stdout, stderr) if part).lower()
    if exit_code == 0:
        return "operational"
    if "no such option" in combined or "traceback" in combined:
        return "beacon_cli_defect"
    if payload:
        return "project_state_blocker"
    if "✗ fail:" in combined or "\nfail:" in combined or "ac matrix not found" in combined:
        return "project_state_blocker"
    if "blocked" in combined or "not ready" in combined or "release_ready=false" in combined:
        return "project_state_blocker"
    return "beacon_cli_defect"


def _surface_status_record(name: str, result: dict[str, Any]) -> dict[str, Any]:
    payload = result.get("json") if isinstance(result.get("json"), dict) else {}
    result_payload = payload.get("result") if isinstance(payload.get("result"), dict) else {}
    next_step = payload.get("next_step") if isinstance(payload.get("next_step"), dict) else {}
    reason_codes: set[str] = {
        str(item.get("reason_code") or "").strip()
        for item in (
            payload.get("issues")
            if isinstance(payload.get("issues"), list)
            else payload.get("findings")
            if isinstance(payload.get("findings"), list)
            else []
        )
        if isinstance(item, dict) and str(item.get("reason_code") or "").strip()
    }
    if str(payload.get("action") or "") == "verify-materials":
        for item in result_payload.get("checks", []) if isinstance(result_payload.get("checks"), list) else []:
            if not isinstance(item, dict) or str(item.get("status") or "").lower() != "fail":
                continue
            name_code = str(item.get("name") or "").strip()
            if name_code:
                reason_codes.add(name_code)
    return {
        "name": name,
        "command": str(result.get("command") or ""),
        "exit_code": int(result.get("exit_code") or 0),
        "classification": _classify_validation_surface(result),
        "structured": bool(payload),
        "status": str(
            payload.get("status")
            or payload.get("review_status")
            or payload.get("gate_status")
            or payload.get("release_ready")
            or ""
        ),
        "blocked": bool(payload.get("blocked")) if "blocked" in payload else False,
        "reason_codes": sorted(code for code in reason_codes if code),
        "next_step": {
            "action": str(next_step.get("action") or ""),
            "reason": str(next_step.get("reason") or ""),
            "command": str(next_step.get("command") or ""),
        } if next_step else {},
        "stdout_tail": "\n".join(str(result.get("stdout") or "").splitlines()[-8:]),
        "stderr_tail": "\n".join(str(result.get("stderr") or "").splitlines()[-8:]),
    }


def _real_project_command_specs(project_root: Path, version: str, feature: str, *, extended: bool) -> list[tuple[str, list[str]]]:
    runtime_version = resolve_runtime_version(project_root, "auto")
    specs: list[tuple[str, list[str]]] = [
        ("help", ["help", "--project-root", str(project_root), "--version", version, "--feature", feature, "--json"]),
        ("doctor", ["doctor", "--json", "--project-root", str(project_root)]),
        ("doctor_verify_materials", ["doctor", "verify-materials", "--project-root", str(project_root), "--version", version, "--strict", "--json"]),
        ("doctor_metadata_show", ["doctor", "metadata", "show", "--project-root", str(project_root), "--version", version, "--json"]),
        ("doctor_metadata_verify", ["doctor", "metadata", "verify", "--project-root", str(project_root), "--version", version, "--json"]),
        ("status", ["status", "show-status", "--project-root", str(project_root), "--version", version, "--feature", feature, "--board"]),
        ("prd_list", ["prd", "list", "-p", str(project_root), "-v", version]),
        ("user_story_list", ["user-story", "list", "-p", str(project_root), "-v", version]),
        ("test_case_list", ["test-case", "list", "-p", str(project_root), "-v", version]),
        ("test_case_gate", ["test-case", "gate", feature, "-p", str(project_root), "-v", version]),
        ("prototype_list", ["prototype", "list", "-p", str(project_root), "-v", version]),
        ("prototype_status", ["prototype", "status", feature, "-p", str(project_root), "-v", version, "--json"]),
        ("implement_status", ["implement", "status", feature, "-p", str(project_root), "-v", version, "--json"]),
        ("qa_status", ["qa", "status", "-p", str(project_root), "--json"]),
        ("qa_evolve", ["qa", "evolve", feature, "-p", str(project_root), "-v", version, "--no-write-matrix", "--json"]),
        ("release_check", ["release", "check", version, "--project-root", str(project_root), "--json"]),
        ("release_scorecard", ["release", "scorecard", version, "-p", str(project_root), "--json"]),
        ("archive_status", ["archive", "status", "-p", str(project_root), "-v", version, "--feature", feature, "--json"]),
        ("archive_explain", ["archive", "explain", "-p", str(project_root), "-v", version, "--json"]),
        ("archive_plan", ["archive", "plan", "-p", str(project_root), "-v", version, "--feature", feature, "--json"]),
        ("gate_prototype", ["gate", "check", "prototype", "--project-root", str(project_root), "--version", version, "--json"]),
        ("gate_release", ["gate", "check", "release", "--project-root", str(project_root), "--version", version, "--json"]),
    ]
    if extended and runtime_feature_supported("v1.3.0", runtime_version=runtime_version):
        specs.extend(
            [
                ("doctor_verify_subagent_runtime_codex", ["doctor", "verify-subagent-runtime", "--project-root", str(project_root), "--host-runtime", "codex", "--json"]),
                ("doctor_verify_subagent_runtime_claude", ["doctor", "verify-subagent-runtime", "--project-root", str(project_root), "--host-runtime", "claude", "--json"]),
                ("doctor_verify_subagent_delegation", ["doctor", "verify-subagent-delegation", feature, "--project-root", str(project_root), "--version", version, "--json"]),
                ("implement_team_dry_run_codex", ["implement", "run", feature, "--project", str(project_root), "--version", version, "--mode", "team", "--runner", "codex-subagents", "--host-runtime", "codex", "--dry-run", "--json"]),
                ("implement_team_dry_run_claude", ["implement", "run", feature, "--project", str(project_root), "--version", version, "--mode", "team", "--runner", "gstack", "--host-runtime", "claude", "--dry-run", "--json"]),
                ("implement_ralph_dry_run_codex", ["implement", "run", feature, "--project", str(project_root), "--version", version, "--mode", "ralph", "--runner", "codex-subagents", "--host-runtime", "codex", "--dry-run", "--json"]),
                ("implement_ralph_dry_run_claude", ["implement", "run", feature, "--project", str(project_root), "--version", version, "--mode", "ralph", "--runner", "gstack", "--host-runtime", "claude", "--dry-run", "--json"]),
                ("implement_ralph_status", ["implement", "ralph-status", feature, "--project-root", str(project_root), "--json"]),
                ("qa_session_list", ["qa", "session", "list", "-p", str(project_root), "--json"]),
                ("qa_run", ["qa", "run", feature, "-p", str(project_root), "-v", version, "--json"]),
                ("qa_team_run_codex", ["qa", "team-run", feature, "-p", str(project_root), "-v", version, "--host-runtime", "codex", "--json"]),
                ("qa_team_run_claude", ["qa", "team-run", feature, "-p", str(project_root), "-v", version, "--host-runtime", "claude", "--json"]),
            ]
        )
    return specs


def _real_project_overlay(
    *,
    version: str,
    runtime_version: str,
    surface_results: dict[str, dict[str, Any]],
    release_scorecard: dict[str, Any],
    acceptance_kit: dict[str, Any],
) -> dict[str, Any]:
    summary = summarize_release_scorecard(release_scorecard)
    kit_summary = acceptance_kit.get("summary") if isinstance(acceptance_kit.get("summary"), dict) else {}
    materials_verify = surface_results.get("doctor_verify_materials", {})
    materials_verify_payload = materials_verify.get("json") if isinstance(materials_verify.get("json"), dict) else {}
    materials_verify_result = (
        materials_verify_payload.get("result") if isinstance(materials_verify_payload.get("result"), dict) else {}
    )
    metadata_verify = surface_results.get("doctor_metadata_verify", {})
    metadata_verify_payload = metadata_verify.get("json") if isinstance(metadata_verify.get("json"), dict) else {}
    metadata_verify_result = (
        metadata_verify_payload.get("result") if isinstance(metadata_verify_payload.get("result"), dict) else {}
    )
    gate_prototype = surface_results.get("gate_prototype", {})
    gate_prototype_payload = gate_prototype.get("json") if isinstance(gate_prototype.get("json"), dict) else {}
    gate_prototype_issues = gate_prototype_payload.get("issues") if isinstance(gate_prototype_payload.get("issues"), list) else []
    gate_prototype_reason_codes = {
        str(item.get("reason_code") or "").strip()
        for item in gate_prototype_issues
        if isinstance(item, dict) and str(item.get("reason_code") or "").strip()
    }
    checks: list[dict[str, Any]] = []
    if metadata_verify_payload:
        checks.append(
            {
                "id": "project_metadata_governance_contract",
                "status": "pass" if str(metadata_verify_result.get("status") or "").strip().lower() == "pass" else "blocked",
                "source": "doctor_metadata_verify",
            }
        )
    if materials_verify_payload:
        checks.append(
            {
                "id": "requirement_package_truth_contract",
                "status": "pass" if str(materials_verify_result.get("status") or "").strip().lower() == "pass" else "blocked",
                "source": "doctor_verify_materials",
            }
        )
    if runtime_feature_supported("v1.3.8", runtime_version=runtime_version):
        archive_operational = all(
            _classify_validation_surface(surface_results.get(name, {})) == "operational"
            for name in ("archive_status", "archive_explain", "archive_plan")
        )
        checks.extend(
            [
                {
                    "id": "post_freeze_host_prompt_trace",
                    "status": "pass" if str(summary.get("prompt_boundary_status") or "").strip().lower() == "pass" else "blocked",
                    "source": "release_scorecard.prompt_boundary",
                },
                {
                    "id": "prompt_boundary_gate_release_convergence",
                    "status": "pass"
                    if str(summary.get("prompt_boundary_status") or "").strip().lower() == "pass"
                    and str(summary.get("gate_status") or "").strip().lower() == "pass"
                    else "blocked",
                    "source": "release_scorecard+gate_release",
                },
                {
                    "id": "archive_governance_support_surface",
                    "status": "pass" if archive_operational else "blocked",
                    "source": "archive_status+archive_explain+archive_plan",
                },
                {
                    "id": "canonical_delivery_baseline_convergence",
                    "status": "pass" if str(summary.get("host_native_delivery_status") or "").strip().lower() != "blocked" else "blocked",
                    "source": "release_scorecard.host_native_delivery",
                },
                {
                    "id": "prototype_projection_frozen_release_surface",
                    "status": "pass"
                    if str(summary.get("prototype_status") or "").strip().lower() == "frozen"
                    and str(summary.get("prototype_review_status") or "").strip().lower() == "pass"
                    and bool(summary.get("prototype_gate_ready", False))
                    and str(summary.get("prototype_drift_status") or "").strip().lower() == "consistent"
                    else "blocked",
                    "source": "release_scorecard.prototype_projection",
                },
            ]
        )
    if runtime_feature_supported("v1.3.9", runtime_version=runtime_version):
        checks.extend(
            [
                {
                    "id": "acceptance_projection_transaction_dual_write",
                    "status": "pass" if str(release_scorecard.get("qa", {}).get("acceptance_transaction_status") or "").strip().lower() == "pass" else "blocked",
                    "source": "release_scorecard.qa.acceptance_transaction_status",
                },
                {
                    "id": "acceptance_kit_shared_proof_chain",
                    "status": "pass" if bool(kit_summary.get("all_layers_passed", False)) else "blocked",
                    "source": "acceptance_kit.summary",
                },
                {
                    "id": "prototype_auto_template_downgrade_guard",
                    "status": "pass" if "prototype_auto_template_downgrade_blocked" not in gate_prototype_reason_codes else "blocked",
                    "source": "gate_check_prototype",
                },
            ]
        )
    return {
        "version": version,
        "checks": checks,
    }


@app.command("real-project-validation")
def real_project_validation(
    project_root: str = typer.Option("", "--project-root", help="Real project root path."),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version line."),
    feature: str = typer.Option("", "--feature", "-f", help="Primary feature to validate."),
    extended: bool = typer.Option(False, "--extended", help="Also run team/ralph/browser-support validation surfaces."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
):
    """Run current-version real-project release proof on the public Beacon surface."""
    root = Path(project_root) if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    docs_root = root / "docs" / "beacon" / resolved_version
    if not docs_root.exists():
        raise typer.BadParameter(f"docs version not found: {docs_root}")

    release_scorecard = build_release_scorecard(root, version=resolved_version)
    primary_feature = str(feature or ((release_scorecard.get("qa") or {}).get("feature")) or "").strip()
    if not primary_feature:
        raise typer.BadParameter("feature is required for real-project validation")
    acceptance_kit = build_acceptance_kit_projection(root, version=resolved_version, feature=primary_feature) if primary_feature else {}

    worktree_lines = _git_status_lines(root)
    executed: list[dict[str, Any]] = []
    by_name: dict[str, dict[str, Any]] = {}
    for name, args in _real_project_command_specs(root, resolved_version, primary_feature, extended=extended):
        result = _run_real_project_validation_command(root, args)
        record = _surface_status_record(name, result)
        executed.append(record)
        by_name[name] = {"record": record, "json": result.get("json") if isinstance(result.get("json"), dict) else {}}

    operational = [item for item in executed if item["classification"] == "operational"]
    blockers = [item for item in executed if item["classification"] == "project_state_blocker"]
    defects = [item for item in executed if item["classification"] == "beacon_cli_defect"]
    release_summary = summarize_release_scorecard(release_scorecard)
    overlay = _real_project_overlay(
        version=resolved_version,
        runtime_version=resolve_runtime_version(root, "auto"),
        surface_results={key: {"json": value.get("json") or {}, "exit_code": (value.get("record") or {}).get("exit_code", 1)} for key, value in by_name.items()},
        release_scorecard=release_scorecard,
        acceptance_kit=acceptance_kit,
    )
    current_feature_ready = bool(release_scorecard.get("release_ready", False))
    version_line_open = str(release_summary.get("change_documents_status") or "").strip().lower() != "pass"
    if defects:
        recommendation = "blocked until Beacon defect is fixed"
    elif blockers:
        recommendation = "safe for read-only use only"
    else:
        recommendation = "safe to use on this project"

    payload = {
        "schema_version": "1.0",
        "validation_scope": "current-version-release-proof",
        "project_root": str(root),
        "docs_version": resolved_version,
        "primary_feature": primary_feature,
        "touched_real_project_worktree": False,
        "worktree_dirty": bool(worktree_lines),
        "worktree_status": worktree_lines,
        "overlay_sources": [
            "AGENTS.md",
            f"docs/beacon/{resolved_version}/SUMMARY.md",
            f"docs/beacon/{resolved_version}/execution/index.md",
            f"docs/beacon/{resolved_version}/release/{resolved_version}.md",
            "skills/beacon/SKILL.md",
        ],
        "executed_commands": [item["command"] for item in executed],
        "surfaces": {
            "operational": operational,
            "project_state_blockers": blockers,
            "beacon_defects": defects,
        },
        "current_feature_closure_ready": current_feature_ready,
        "version_line_package_change_doc_closure_open": version_line_open,
        "release_scorecard": {
            "release_ready": bool(release_scorecard.get("release_ready", False)),
            "summary": release_summary,
        },
        "latest_feature_overlay": overlay,
        "acceptance_kit": acceptance_kit,
        "covered_paths": {
            "current_version_release_proof": True,
            "specialized_board_acceptance": False,
            "extended_support_surfaces": bool(extended),
        },
        "recommendation": recommendation,
    }

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"validated project root: {payload['project_root']}")
        typer.echo(f"validated docs version: {payload['docs_version']}")
        typer.echo(f"primary feature: {payload['primary_feature']}")
        typer.echo(f"operational surfaces: {len(operational)}")
        typer.echo(f"project-state blockers: {len(blockers)}")
        typer.echo(f"beacon defects: {len(defects)}")
        typer.echo(f"current-feature closure ready: {payload['current_feature_closure_ready']}")
        typer.echo(f"version-line package/change-doc closure open: {payload['version_line_package_change_doc_closure_open']}")
        typer.echo(f"recommendation: {payload['recommendation']}")


@app.callback(invoke_without_command=True)
def report_callback(
    ctx: typer.Context,
    run_id: str = typer.Argument("latest", help="Run ID (default: latest)"),
    human: bool = typer.Option(False, "--human", help="Generate human-friendly report"),
    machine: bool = typer.Option(False, "--machine", help="Generate machine JSON report"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version filter"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature filter"),
    write_summary: bool = typer.Option(
        False,
        "--write-summary",
        help="Write summary.md into docs/beacon/<version>/execution and summary.json into docs/beacon/<version>/.machine/execution (disabled by default).",
    ),
):
    """Generate report directly (PTK flat syntax compatibility)."""
    if ctx.invoked_subcommand is None:
        code = _report_impl(
            project_root=project_root,
            run_id=run_id,
            human=human,
            machine=machine,
            version=version,
            feature=feature,
            write_summary=write_summary,
        )
        raise typer.Exit(code=code)


@app.command("generate")
def generate(
    run_id: str = typer.Argument("latest", help="Run ID"),
    human: bool = typer.Option(True, "--human/--machine", help="Report format"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version filter"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature filter"),
    write_summary: bool = typer.Option(
        False,
        "--write-summary",
        help="Write summary.md into docs/beacon/<version>/execution and summary.json into docs/beacon/<version>/.machine/execution (disabled by default).",
    ),
):
    """Generate run report (nested compatibility)."""
    code = _report_impl(
        project_root=project_root,
        run_id=run_id,
        human=human,
        machine=not human,
        version=version,
        feature=feature,
        write_summary=write_summary,
    )
    raise typer.Exit(code=code)


@app.command("acceptance-audit")
def acceptance_audit(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Version filter"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature name"),
    run_regression: bool = typer.Option(False, "--run-regression", help="Run regression command before building audit."),
    regression_command: str = typer.Option("python3 -m pytest -q", "--regression-command", help="Command used when --run-regression is enabled."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON instead of markdown."),
    write_output: bool = typer.Option(True, "--write/--no-write", help="Write acceptance-regression-audit.md into docs/beacon/<version>/execution and acceptance-regression-audit.json into docs/beacon/<version>/.machine/execution."),
):
    """Generate deterministic acceptance regression audit artifacts."""
    root = Path(project_root) if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    feature_name = feature.strip() if feature and feature.strip() else ""

    regression_payload = None
    if run_regression:
        regression_payload = run_regression_command(root, regression_command)

    payload = build_acceptance_audit_payload(
        root,
        version=resolved_version,
        feature=feature_name,
        regression=regression_payload,
    )
    if write_output:
        written = write_acceptance_audit(root, payload)
        payload["artifacts"] = sorted(written.keys())

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(render_acceptance_audit_markdown(payload), nl=False)

    blocked = bool(run_regression and regression_payload and regression_payload.get("status") != "pass")
    raise typer.Exit(2 if blocked else 0)


if __name__ == "__main__":
    app()
