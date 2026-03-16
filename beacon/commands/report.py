"""Beacon report command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.runtime import load_run_state, newest_run_id, now_iso, write_json
from beacon.utils.acceptance_audit import (
    build_acceptance_audit_payload,
    render_acceptance_audit_markdown,
    run_regression_command,
    write_acceptance_audit,
)
from beacon.utils.versioning import resolve_target_version
from beacon.utils.v110_baseline import load_latest_spec_fingerprint
from beacon.utils.v110_metrics import (
    compute_baseline_drift_metrics,
    compute_memory_governance_metrics,
)
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
    lines = [
        "# Beacon Human Summary",
        "",
        f"- Run ID: `{machine.get('run_id', 'latest')}`",
        f"- Workflow: `{machine.get('workflow', 'workflow')}`",
        f"- Mode: `{machine.get('mode', 'normal')}`",
        f"- Status: **{machine.get('status', 'unknown')}**",
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
        return {
            "run_id": resolved,
            "workflow": "workflow",
            "mode": "normal",
            "status": "unknown",
            "reason": "no-run-state",
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
    exec_dirs = [root / "docs" / "beacon" / report_version / "execution"]
    if write_summary:
        for exec_dir in exec_dirs:
            exec_dir.mkdir(parents=True, exist_ok=True)
            summary_json = exec_dir / "summary.json"
            summary_md = exec_dir / "summary.md"
            write_json(summary_json, payload)
            summary_md.write_text(_human_summary(payload), encoding="utf-8")

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
        help="Write summary.{json,md} into docs/beacon/<version>/execution (disabled by default).",
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
        help="Write summary.{json,md} into docs/beacon/<version>/execution (disabled by default).",
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
    write_output: bool = typer.Option(True, "--write/--no-write", help="Write acceptance audit into docs/beacon/<version>/execution."),
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
