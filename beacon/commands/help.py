"""Beacon help command - stage-aware next-step navigator."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.help_support import build_help_payload
from beacon.utils.runtime import load_run_state
from beacon.utils.workflow_memory import resolve_workflow_run_id

app = typer.Typer(
    name="help",
    help="Stage-aware workflow help",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _infer_feature(root: Path, version: str, feature: str, run_id: str) -> str:
    if feature.strip():
        return feature.strip()
    resolved_run = resolve_workflow_run_id(root, run_id=run_id or None, version=version, feature=None)
    if resolved_run:
        state = load_run_state(root, resolved_run) or {}
        inferred = str(state.get("feature", "") or "").strip()
        if inferred:
            return inferred
    raise typer.BadParameter("feature is required when no active workflow feature can be inferred")



def _render_human(payload: dict[str, object]) -> str:
    scores = payload.get("scores", {}) if isinstance(payload.get("scores"), dict) else {}
    next_step = payload.get("next_step", {}) if isinstance(payload.get("next_step"), dict) else {}
    version_context = payload.get("version_context", {}) if isinstance(payload.get("version_context"), dict) else {}
    version_guard = payload.get("context_version_guard", {}) if isinstance(payload.get("context_version_guard"), dict) else {}
    execution_surface = payload.get("execution_surface", {}) if isinstance(payload.get("execution_surface"), dict) else {}
    lines = [
        "Beacon Help / Next Step",
        "=" * 26,
        f"feature         : {payload.get('feature', '')}",
        f"docs version    : {payload.get('docs_version', payload.get('version', ''))}",
        f"runtime version : {payload.get('runtime_version', '')}",
        f"context version : {version_context.get('context_managed_version', '') or 'N/A'}",
        f"context guard   : {version_guard.get('status', '') or 'N/A'}",
        f"active revision : {payload.get('revision_id', '')}",
        f"doc status      : {payload.get('doc_status', '')}",
        f"delivery status : {payload.get('delivery_status', '')}",
        f"current stage   : {payload.get('current_stage', '')}",
        f"host runtime    : {execution_surface.get('host_runtime', '') or 'N/A'}",
        f"subagent runtime: {execution_surface.get('subagent_runtime_status', '') or 'N/A'}",
        f"subagent deleg. : {execution_surface.get('subagent_delegation_status', '') or 'N/A'}",
        f"ralph phase     : {execution_surface.get('ralph_phase', '') or 'N/A'}",
        f"ralph stop      : {execution_surface.get('ralph_stop_state', '') or 'N/A'}",
        f"ralph next      : {execution_surface.get('ralph_next_action', '') or 'N/A'}",
        f"ralph rounds    : {execution_surface.get('ralph_round_count', 0) or 0}",
        f"ralph round ref : {execution_surface.get('ralph_last_round_ref', '') or 'N/A'}",
        f"qa mode         : {execution_surface.get('qa_execution_mode', '') or 'N/A'}",
        f"qa session      : {execution_surface.get('qa_current_session_id', '') or 'N/A'}",
        f"qa runner       : {execution_surface.get('qa_runner_type', '') or 'N/A'}",
        "",
        "scores",
        f"- test_score      : {scores.get('test_score', 0)}",
        f"- closure_score   : {scores.get('closure_score', 0)}",
        f"- readiness_score : {scores.get('readiness_score', 0)}",
        f"- quality_score   : {scores.get('quality_score', 0)}",
        "",
        "next step",
        f"- action  : {next_step.get('action', '')}",
        f"- why     : {next_step.get('reason', '')}",
        f"- command : {next_step.get('command', '')}",
    ]
    discovery = payload.get("skill_discovery_hint", {}) if isinstance(payload.get("skill_discovery_hint"), dict) else {}
    if not discovery:
        discovery = payload.get("skill_discovery", {}) if isinstance(payload.get("skill_discovery"), dict) else {}
    if bool(discovery.get("recommended")):
        lines.extend([
            "",
            "skill discovery",
            f"- reason   : {discovery.get('reason', '')}",
            f"- command  : {discovery.get('command', '')}",
            f"- templates: {', '.join(discovery.get('templates', [])) if isinstance(discovery.get('templates'), list) else ''}",
        ])
    reasons = payload.get("blocking_reasons", []) if isinstance(payload.get("blocking_reasons"), list) else []
    lines.extend(["", "blocking reasons"])
    if reasons:
        for reason in reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"



def _help_impl(project_root: str, version: str, feature: str, run_id: str, json_output: bool) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    target_feature = feature.strip()
    if not target_feature:
        try:
            target_feature = _infer_feature(root, version, feature, run_id)
        except Exception as exc:  # noqa: BLE001
            payload = {"schema_version": "1.0", "status": "blocked", "reason": str(exc)}
            if json_output:
                typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                typer.echo(f"Beacon help blocked: {exc}", err=True)
            return 2
    payload = build_help_payload(root, version=version, feature=target_feature, run_id=run_id or None)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(_render_human(payload))
    return 0


@app.callback(invoke_without_command=True)
def help_entry(
    ctx: typer.Context,
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature name"),
    run_id: str = typer.Option("", "--run-id", help="Run id filter"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show stage-aware next-step guidance."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(code=_help_impl(project_root, version, feature, run_id, json_output))


@app.command("show")
def show(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature name"),
    run_id: str = typer.Option("", "--run-id", help="Run id filter"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Alias of main help output."""
    raise typer.Exit(code=_help_impl(project_root, version, feature, run_id, json_output))
