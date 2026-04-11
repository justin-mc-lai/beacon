"""Beacon status command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.artifact_paths import machine_root, uses_machine_surface
from beacon.utils.control_plane import build_resume_contract
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.implementation_plan import load_implementation_plan_progress
from beacon.utils.learning_loop import load_keep_discard_engine
from beacon.utils.material_audit import build_material_audit
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.runtime import newest_run_id, read_json
from beacon.utils.versioning import describe_project_version_context, resolve_target_version
from beacon.utils.workflow_memory import compute_memory_metrics, compute_workflow_progress
from beacon.utils.help_support import build_help_payload

app = typer.Typer(
    name="status",
    help="Show workflow status",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _status_impl(
    board: bool,
    verbose: bool,
    project_root: str,
    version: str,
    feature: str,
    run_id: str,
) -> int:
    root = Path(project_root) if project_root else Path.cwd()
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
    terminal_status = str(selected_state.get("status", "unknown")) if isinstance(selected_state, dict) else "unknown"
    coverage_version = (
        version_filter
        or str(workflow_progress.get("version", "") or "").strip()
        or resolve_target_version(root, None)
    )
    coverage_metrics = compute_coverage_metrics(
        root,
        version=coverage_version,
        feature=feature_filter,
    )
    material_audit = build_material_audit(root, version=coverage_version, strict=False)
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
        "formal_package_closure": material_audit.get("status", "unknown"),
    }

    target_feature = feature_filter or str(workflow_progress.get("feature", "") or "")
    help_payload = build_help_payload(root, version=coverage_version, feature=target_feature, run_id=resolved_run_id or None) if target_feature else {}
    implementation_plan_progress = load_implementation_plan_progress(root, version=coverage_version, feature=target_feature) if target_feature else {}
    qa_status = load_qa_status(root)
    resume_contract = build_resume_contract(root, run_id=resolved_run_id or None)
    keep_discard_engine = load_keep_discard_engine(root)
    release_scorecard = build_release_scorecard(root, version=coverage_version)
    release_summary = summarize_release_scorecard(release_scorecard)

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
        "coverage": coverage_metrics,
        "scores": help_payload.get("scores", {}),
        "revision": {
            "revision_id": help_payload.get("revision_id", ""),
            "doc_status": help_payload.get("doc_status", ""),
            "delivery_status": help_payload.get("delivery_status", ""),
            "blocked": help_payload.get("blocked", False),
            "blocking_reasons": help_payload.get("blocking_reasons", []),
            "blocked_reason": help_payload.get("blocked_reason", ""),
        },
        "next_step": help_payload.get("next_step", {}),
        "project_mode": help_payload.get("project_mode", "greenfield"),
        "execution_surface": help_payload.get("execution_surface", {}),
        "learning_surface": help_payload.get("learning_surface", {}),
        "implementation_plan": {
            "plan_id": implementation_plan_progress.get("plan_id", ""),
            "status": implementation_plan_progress.get("status", "missing"),
            "counts": implementation_plan_progress.get("counts", {}),
            "next_task_id": implementation_plan_progress.get("next_task_id", ""),
            "blocked_task_ids": implementation_plan_progress.get("blocked_task_ids", []),
        },
        "decision_trace": help_payload.get("decision_trace", []),
        "control_plane": resume_contract,
        "qa_status": {
            "feature": qa_status.get("feature"),
            "status": qa_status.get("status"),
            "evidence_done": qa_status.get("evidence_done"),
        },
        "learning_plane": {
            "decision_summary": keep_discard_engine.get("decision_summary", {}),
            "decision_engine_path": ".beacon/state/evo/decision-engine.json",
        },
        "release_scorecard": release_scorecard,
        "version_context": {
            **version_context,
            "docs_version": coverage_version,
            "runtime_version": str(version_context.get("runtime_version", "") or help_payload.get("runtime_version", "")),
        },
        "version_semantics": help_payload.get("version_semantics", {}) or version_context.get("version_semantics", {}),
        "source_of_truth": source_of_truth,
        "workflow_progress": workflow_progress,
        "filters": {
            "version": version_filter or "",
            "feature": feature_filter or "",
            "run_id": explicit_run_filter or "",
        },
    }

    if board:
        typer.echo("Beacon Status Board")
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
        if release_summary.get("exhaustiveness_status"):
            typer.echo(
                f"- release.exhaustiveness: {release_summary.get('exhaustiveness_status')} ({release_summary.get('exhaustiveness_score')})"
            )
        if release_summary.get("release_confidence_min") is not None:
            typer.echo(
                f"- release.confidence: min={release_summary.get('release_confidence_min')} avg={release_summary.get('release_confidence_avg')} review={release_summary.get('review_required_count')} replay={release_summary.get('needs_replay_count')}"
            )
        if release_summary.get("continue_decision"):
            typer.echo(f"- release.continue_decision: {release_summary.get('continue_decision')}")
        coverage_current = release_summary.get("coverage_current") if isinstance(release_summary.get("coverage_current"), dict) else {}
        if coverage_current:
            typer.echo(
                f"- release.coverage_current: {coverage_current.get('executed_scenarios', 0)}/{coverage_current.get('required_scenarios', 0)} ({coverage_current.get('coverage_rate', 0)})"
            )
        typer.echo(
            f"- release.learning: {release_summary.get('main_kpi')}={release_summary.get('main_kpi_score')} keep/review/discard={release_summary.get('decision_keep')}/{release_summary.get('decision_review')}/{release_summary.get('decision_discard')}"
        )
        typer.echo(f"- memory.closure_complete: {memory_metrics.get('closure_complete')}")
        typer.echo(f"- memory.writebacks: {memory_metrics.get('writebacks')}")
        typer.echo(f"- memory.recall_injections: {memory_metrics.get('recall_injections')}")
        typer.echo(f"- memory.next_stage: {workflow_progress.get('next_stage') or 'none'}")
        if payload.get("implementation_plan", {}).get("plan_id"):
            typer.echo(
                f"- implementation_plan: {payload.get('implementation_plan', {}).get('status')} "
                f"next={payload.get('implementation_plan', {}).get('next_task_id') or 'none'} "
                f"counts={payload.get('implementation_plan', {}).get('counts', {})}"
            )
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
        if payload.get("version_context", {}).get("context_managed_version"):
            typer.echo(f"- version.context: {payload.get('version_context', {}).get('context_managed_version')}")
        if payload.get("scores"):
            typer.echo(f"- score.test: {payload.get('scores', {}).get('test_score')}")
            typer.echo(f"- score.closure: {payload.get('scores', {}).get('closure_score')}")
            typer.echo(f"- score.readiness: {payload.get('scores', {}).get('readiness_score')}")
            typer.echo(f"- score.quality: {payload.get('scores', {}).get('quality_score')}")
        typer.echo(f"- source_of_truth.root: {source_of_truth.get('root')}")
        if source_of_truth.get("machine_root"):
            typer.echo(f"- source_of_truth.machine_root: {source_of_truth.get('machine_root')}")
        typer.echo(f"- source_of_truth.formal_package_closure: {source_of_truth.get('formal_package_closure')}")
        if qa_status:
            typer.echo(f"- qa.status: {qa_status.get('status')}")
            typer.echo(f"- qa.evidence_done: {qa_status.get('evidence_done')}")
        if workflow_progress.get("stages", {}).get("prototype"):
            typer.echo(f"- workflow.prototype: {workflow_progress.get('stages', {}).get('prototype', {}).get('status')}")
        if verbose:
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
        )
    )


if __name__ == "__main__":
    app()
