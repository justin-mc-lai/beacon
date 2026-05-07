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
    support_surface_projection = payload.get("support_surface_projection", {}) if isinstance(payload.get("support_surface_projection"), dict) else {}
    minimal_hud = payload.get("minimal_hud", {}) if isinstance(payload.get("minimal_hud"), dict) else {}
    hud_lines = minimal_hud.get("lines", []) if isinstance(minimal_hud.get("lines"), list) else []
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
        f"archive status  : {execution_surface.get('archive_status', '') or 'N/A'}",
        f"freeze status   : {execution_surface.get('freeze_status', '') or 'N/A'}",
        f"implement mode  : {execution_surface.get('implement_mode', '') or 'N/A'}",
        f"team phase      : {execution_surface.get('team_phase', '') or 'N/A'}",
        f"implement runner: {execution_surface.get('implement_runner', '') or 'N/A'}",
        f"subagent runtime: {execution_surface.get('subagent_runtime_status', '') or 'N/A'}",
        f"subagent deleg. : {execution_surface.get('subagent_delegation_status', '') or 'N/A'}",
        f"host trace ref  : {execution_surface.get('host_prompt_trace_ref', '') or 'N/A'}",
        f"ralph phase     : {execution_surface.get('ralph_phase', '') or 'N/A'}",
        f"ralph status    : {execution_surface.get('ralph_status', '') or 'N/A'}",
        f"ralph stop      : {execution_surface.get('ralph_stop_state', '') or 'N/A'}",
        f"ralph next      : {execution_surface.get('ralph_next_action', '') or 'N/A'}",
        f"ralph rounds    : {execution_surface.get('ralph_round_count', 0) or 0}",
        f"ralph round ref : {execution_surface.get('ralph_last_round_ref', '') or 'N/A'}",
        f"qa mode         : {execution_surface.get('qa_execution_mode', '') or 'N/A'}",
        f"qa session      : {execution_surface.get('qa_current_session_id', '') or 'N/A'}",
        f"qa runner       : {execution_surface.get('qa_runner_type', '') or 'N/A'}",
        f"operator doc    : {support_surface_projection.get('primary_operator_doc_ref', '') or 'N/A'}",
    ]
    if hud_lines:
        lines.extend(["", "minimal hud"])
        for line in hud_lines:
            lines.append(f"- {line}")
    lines.extend([
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
    ])
    change_loop = payload.get("change_loop", {}) if isinstance(payload.get("change_loop"), dict) else {}
    requirement_gap_digest = payload.get("requirement_gap_digest", {}) if isinstance(payload.get("requirement_gap_digest"), dict) else {}
    brainstorm_hint = payload.get("brainstorm_hint", {}) if isinstance(payload.get("brainstorm_hint"), dict) else {}
    requirement_package = payload.get("requirement_package_gate", {}) if isinstance(payload.get("requirement_package_gate"), dict) else {}
    acceptance_kit = payload.get("acceptance_kit", {}) if isinstance(payload.get("acceptance_kit"), dict) else {}
    acceptance_summary = acceptance_kit.get("summary", {}) if isinstance(acceptance_kit.get("summary"), dict) else {}
    if bool(requirement_package.get("enabled")):
        lines.extend(
            [
                "",
                "requirement package",
                f"- status      : {requirement_package.get('status', 'pass')}",
                f"- remediation : {requirement_package.get('remediation_mode', '') or 'none'}",
            ]
        )
        failure_categories = requirement_package.get("failure_categories", []) if isinstance(requirement_package.get("failure_categories"), list) else []
        lines.append(f"- failures    : {', '.join(str(item) for item in failure_categories) if failure_categories else 'none'}")
        if requirement_package.get("recommended_command"):
            lines.append(f"- command     : {requirement_package.get('recommended_command', '')}")
    if acceptance_summary:
        lines.extend(
            [
                "",
                "acceptance kit",
                f"- summary     : {acceptance_summary.get('summary', '')}",
                f"- verdict     : {acceptance_summary.get('verdict', '')}",
            ]
        )
        failed_layers = acceptance_summary.get("failed_layers", [])
        if failed_layers:
            lines.append(f"- failed      : {', '.join(str(item) for item in failed_layers)}")
    if change_loop.get("intent") or bool(change_loop.get("recommended")):
        lines.extend(
            [
                "",
                "change loop",
                f"- intent      : {change_loop.get('intent', '')}",
                f"- recommended : {change_loop.get('recommended', False)}",
                f"- route       : {change_loop.get('route', '')}",
            ]
        )
        ladder = change_loop.get("ladder", []) if isinstance(change_loop.get("ladder"), list) else []
        if ladder:
            lines.append(f"- ladder      : {' -> '.join(str(item) for item in ladder)}")
    if requirement_gap_digest.get("human_followup_needed") or brainstorm_hint.get("recommended_route"):
        lines.extend(
            [
                "",
                "requirement convergence",
                f"- gap_id     : {requirement_gap_digest.get('gap_id', '')}",
                f"- gap_type   : {requirement_gap_digest.get('gap_type', '')}",
                f"- severity   : {requirement_gap_digest.get('gap_severity', '')}",
                f"- route      : {requirement_gap_digest.get('recommended_route', '') or brainstorm_hint.get('recommended_route', '')}",
            ]
        )
        focus_areas = brainstorm_hint.get("focus_areas", []) if isinstance(brainstorm_hint.get("focus_areas"), list) else []
        if focus_areas:
            lines.append(f"- focus      : {', '.join(str(item) for item in focus_areas[:4])}")
        open_questions = brainstorm_hint.get("open_questions", []) if isinstance(brainstorm_hint.get("open_questions"), list) else []
        if open_questions:
            lines.append(f"- questions  : {open_questions[0]}")
        if brainstorm_hint.get("recommended_mode"):
            lines.append(f"- mode       : {brainstorm_hint.get('recommended_mode')}")
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



def _help_impl(project_root: str, version: str, feature: str, run_id: str, change_intent: str, json_output: bool) -> int:
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
    payload = build_help_payload(
        root,
        version=version,
        feature=target_feature,
        run_id=run_id or None,
        change_intent=change_intent or None,
    )
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
    change_intent: str = typer.Option("", "--change-intent", help="Optional user change-intent text for post-freeze routing"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show stage-aware next-step guidance."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(code=_help_impl(project_root, version, feature, run_id, change_intent, json_output))


@app.command("show")
def show(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature name"),
    run_id: str = typer.Option("", "--run-id", help="Run id filter"),
    change_intent: str = typer.Option("", "--change-intent", help="Optional user change-intent text for post-freeze routing"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Alias of main help output."""
    raise typer.Exit(code=_help_impl(project_root, version, feature, run_id, change_intent, json_output))
