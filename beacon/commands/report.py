"""Beacon report command."""

from __future__ import annotations

import json
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
from beacon.utils.versioning import resolve_target_version
from beacon.utils.material_audit import build_material_audit
from beacon.utils.learning_loop import load_keep_discard_engine
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.v110_baseline import load_latest_spec_fingerprint
from beacon.utils.v110_metrics import (
    compute_baseline_drift_metrics,
    compute_memory_governance_metrics,
)
from beacon.utils.v115_delivery import refresh_evidence_manifest
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
