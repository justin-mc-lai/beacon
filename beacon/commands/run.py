"""Beacon run command."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.llm_loop import build_next_stage_trace, merge_token_usage
from beacon.utils.memory import append_scope_items
from beacon.utils.runtime import (
    append_jsonl,
    generate_run_id,
    now_iso,
    run_events_path,
    save_run_state,
)
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="run", help="Run Beacon workflow")

WORKFLOW_TYPES = {"workflow", "team", "auto-test", "auto_test", "ralph-bridge", "ralph_bridge"}
MODES = {"normal", "debug", "strict", "dry-run", "replay"}
RISK_HIGH_KEYWORDS = (
    "rewrite",
    "重写",
    "drop schema",
    "删除 schema",
    "跨平台 converter",
    "权限模型",
    "execution engine",
)


def _normalize_workflow_type(raw: str) -> str:
    value = (raw or "").strip() or "workflow"
    return value.replace("_", "-")


def _classify_proposal(proposal: str) -> tuple[str, str]:
    text = (proposal or "").strip().lower()
    if any(k in text for k in RISK_HIGH_KEYWORDS):
        return "out-of-scope", "high"
    return "enhancement-proposal", "low"


def _record_scope_memory(
    root: Path,
    run_id: str,
    proposals: list[str],
    confirm: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    deviations: list[dict[str, Any]] = []
    confirmations: list[dict[str, Any]] = []
    has_pending_high = False

    for idx, proposal in enumerate(proposals, start=1):
        proposal = (proposal or "").strip()
        if not proposal:
            continue
        deviation_type, risk = _classify_proposal(proposal)
        deviation = {
            "id": f"DEV-{run_id}-{idx}",
            "run_id": run_id,
            "proposal": proposal,
            "type": deviation_type,
            "risk": risk,
            "created_at": now_iso(),
        }
        deviations.append(deviation)

        if risk == "high":
            status = "confirmed" if confirm in {"A", "B", "C"} else "pending"
            if status == "pending":
                has_pending_high = True
            confirmations.append(
                {
                    "id": f"CONF-{run_id}-{idx}",
                    "run_id": run_id,
                    "deviation_id": deviation["id"],
                    "status": status,
                    "decision": confirm if status == "confirmed" else None,
                    "options": ["A", "B", "C"],
                    "created_at": now_iso(),
                }
            )

    if deviations or confirmations:
        append_scope_items(project_root=root, deviations=deviations, confirmations=confirmations)
    return deviations, confirmations, has_pending_high


def _run_workflow_impl(
    workflow_type: str,
    mode: str,
    feature: str,
    version: str,
    strict: bool,
    json_output: bool,
    project_root: str,
    proposals: list[str],
    confirm: str | None,
) -> int:
    normalized_type = _normalize_workflow_type(workflow_type)
    if normalized_type not in {t.replace("_", "-") for t in WORKFLOW_TYPES}:
        typer.echo(f"Unsupported workflow type: {workflow_type}", err=True)
        return 2

    if mode not in MODES:
        typer.echo(f"Unsupported mode: {mode}", err=True)
        return 2

    root = Path(project_root) if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    run_id = generate_run_id(root)
    events_file = run_events_path(root, run_id)
    events: list[dict[str, Any]] = []
    deviations: list[dict[str, Any]] = []
    confirmations: list[dict[str, Any]] = []

    started = now_iso()
    events.append(
        {
            "event": "run_started",
            "run_id": run_id,
            "mode": mode,
            "workflow_route": normalized_type,
            "ts": started,
        }
    )
    append_jsonl(events_file, events[-1])
    llm_trace = build_next_stage_trace(
        feature=feature or normalized_type,
        version=resolved_version,
        run_id=run_id,
        next_stage="workflow" if normalized_type == "workflow" else normalized_type,
        context="run.workflow.dispatch",
    )

    # Compatibility behavior:
    # strict mode requires an existing user-story artifact in product/beacon docs.
    if mode == "strict":
        story_candidates = [
            root / "docs" / "product" / resolved_version / "user-story",
            root / "docs" / "beacon" / resolved_version / "user-story",
        ]
        has_story = any(path.exists() and any(path.glob("*.md")) for path in story_candidates)
        if not has_story:
            events.append(
                {
                    "event": "run_blocked",
                    "run_id": run_id,
                    "reason": "missing_user_story_for_strict_mode",
                    "ts": now_iso(),
                }
            )
            append_jsonl(events_file, events[-1])
            state = {
                "run_id": run_id,
                "workflow": normalized_type,
                "workflow_input": normalized_type,
                "mode": mode,
                "status": "blocked",
                "reason": "missing_user_story_for_strict_mode",
                "started_at": started,
                "ended_at": now_iso(),
                "events": events,
                "llm_prompts": [llm_trace],
                "token_usage": merge_token_usage({}, llm_trace),
                "tool_calls": [],
                "artifacts": {"events": str(events_file.relative_to(root))},
                "deviations": deviations,
                "confirmations": confirmations,
            }
            save_run_state(root, run_id, state)
            if json_output:
                typer.echo(f'{{"run_id":"{run_id}","status":"blocked","reason":"missing_user_story_for_strict_mode"}}')
            else:
                typer.echo(f"Running {normalized_type} in {mode} mode")
                typer.echo(f"Feature: {feature}, Version: {resolved_version}")
                typer.echo("Strict mode: enabled")
                typer.echo("Blocked: missing user-story artifact for strict mode")
            return 2

        deviations, confirmations, has_pending_high = _record_scope_memory(
            root=root,
            run_id=run_id,
            proposals=proposals,
            confirm=confirm,
        )
        events.append(
            {
                "event": "scope_guard_checked",
                "run_id": run_id,
                "deviation_count": len(deviations),
                "pending_confirmation_count": len([c for c in confirmations if c.get("status") == "pending"]),
                "ts": now_iso(),
            }
        )
        append_jsonl(events_file, events[-1])
        if has_pending_high:
            events.append(
                {
                    "event": "run_blocked",
                    "run_id": run_id,
                    "reason": "awaiting_human_confirmation",
                    "ts": now_iso(),
                }
            )
            append_jsonl(events_file, events[-1])
            state = {
                "run_id": run_id,
                "workflow": normalized_type,
                "workflow_input": normalized_type,
                "mode": mode,
                "status": "blocked",
                "reason": "awaiting_human_confirmation",
                "started_at": started,
                "ended_at": now_iso(),
                "events": events,
                "llm_prompts": [llm_trace],
                "token_usage": merge_token_usage({}, llm_trace),
                "tool_calls": [{"name": "scope_guard.record", "args": {"deviations": len(deviations)}}],
                "artifacts": {
                    "events": str(events_file.relative_to(root)),
                    "scope_deviations": ".beacon/memory/scope/deviations.json",
                    "scope_confirmations": ".beacon/memory/scope/confirmations.json",
                },
                "deviations": deviations,
                "confirmations": confirmations,
            }
            save_run_state(root, run_id, state)
            if json_output:
                typer.echo(f'{{"run_id":"{run_id}","status":"blocked","reason":"awaiting_human_confirmation"}}')
            else:
                typer.echo(f"Running {normalized_type} in {mode} mode")
                typer.echo(f"Feature: {feature}, Version: {resolved_version}")
                typer.echo("Strict mode: enabled")
                typer.echo("Blocked: high-risk scope proposal needs confirmation (A/B/C)")
            return 2

    final_event = (
        {
            "event": "dry_run_completed" if mode == "dry-run" else "run_completed",
            "run_id": run_id,
            "ts": now_iso(),
        }
        if mode in {"normal", "debug", "strict", "dry-run", "replay"}
        else {"event": "run_failed", "run_id": run_id, "reason": "invalid_mode", "ts": now_iso()}
    )
    events.append(final_event)
    append_jsonl(events_file, final_event)

    state = {
        "run_id": run_id,
        "workflow": normalized_type,
        "workflow_input": normalized_type,
        "mode": mode,
        "status": "completed",
        "reason": "dry-run" if mode == "dry-run" else "ok",
        "started_at": started,
        "ended_at": now_iso(),
        "events": events,
        "llm_prompts": [llm_trace],
        "token_usage": merge_token_usage({}, llm_trace),
        "tool_calls": [{"name": "router.dispatch", "args": {"workflow": normalized_type}}],
        "artifacts": {
            "events": str(events_file.relative_to(root)),
            "scope_deviations": ".beacon/memory/scope/deviations.json" if deviations else None,
            "scope_confirmations": ".beacon/memory/scope/confirmations.json" if confirmations else None,
        },
        "deviations": deviations,
        "confirmations": confirmations,
    }
    save_run_state(root, run_id, state)

    if json_output:
        typer.echo(f'{{"run_id":"{run_id}","status":"completed","reason":"{state["reason"]}"}}')
    else:
        typer.echo(f"Running {normalized_type} in {mode} mode")
        typer.echo(f"Feature: {feature}, Version: {resolved_version}")
        if strict:
            typer.echo("Strict mode: enabled")
    return 0


@app.command()
def workflow(
    workflow_type: str = typer.Argument("workflow", help="Workflow type: workflow/team/auto-test"),
    mode: str = typer.Option("normal", "--mode", "-m", help="Run mode: normal/debug/strict/dry-run/replay"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    proposal: list[str] = typer.Option([], "--proposal", help="Optional scope proposal (repeatable)"),
    confirm: Optional[str] = typer.Option(None, "--confirm", help="Human confirmation choice for high-risk scope (A/B/C)"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Run Beacon workflow."""
    if confirm and confirm not in {"A", "B", "C"}:
        typer.echo("Invalid --confirm, expected A/B/C", err=True)
        raise typer.Exit(code=2)

    code = _run_workflow_impl(
        workflow_type=workflow_type,
        mode=mode,
        feature=feature,
        version=version,
        strict=strict,
        json_output=json_output,
        project_root=project_root,
        proposals=proposal,
        confirm=confirm,
    )
    raise typer.Exit(code=code)


if __name__ == "__main__":
    app()
