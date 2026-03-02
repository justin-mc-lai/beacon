"""Beacon run command."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.runtime import (
    append_jsonl,
    generate_run_id,
    now_iso,
    run_events_path,
    save_run_state,
)

app = typer.Typer(name="run", help="Run Beacon workflow")

WORKFLOW_TYPES = {"workflow", "team", "auto-test", "auto_test", "ralph-bridge", "ralph_bridge"}
MODES = {"normal", "debug", "strict", "dry-run", "replay"}


def _normalize_workflow_type(raw: str) -> str:
    value = (raw or "").strip() or "workflow"
    return value.replace("_", "-")


def _run_workflow_impl(
    workflow_type: str,
    mode: str,
    feature: str,
    version: str,
    strict: bool,
    json_output: bool,
    project_root: str,
) -> int:
    normalized_type = _normalize_workflow_type(workflow_type)
    if normalized_type not in {t.replace("_", "-") for t in WORKFLOW_TYPES}:
        typer.echo(f"Unsupported workflow type: {workflow_type}", err=True)
        return 2

    if mode not in MODES:
        typer.echo(f"Unsupported mode: {mode}", err=True)
        return 2

    root = Path(project_root) if project_root else Path.cwd()
    run_id = generate_run_id(root)
    events_file = run_events_path(root, run_id)
    events: list[dict[str, Any]] = []

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

    # Compatibility behavior:
    # strict mode requires an existing user-story artifact in product/beacon docs.
    if mode == "strict":
        story_candidates = [
            root / "docs" / "product" / version / "user-story",
            root / "docs" / "beacon" / version / "user-story",
            root / "docs" / "product" / "latest" / "user-story",
            root / "docs" / "beacon" / "latest" / "user-story",
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
                "llm_prompts": [],
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "tool_calls": [],
                "artifacts": {"events": str(events_file.relative_to(root))},
                "deviations": [],
                "confirmations": [],
            }
            save_run_state(root, run_id, state)
            if json_output:
                typer.echo(f'{{"run_id":"{run_id}","status":"blocked","reason":"missing_user_story_for_strict_mode"}}')
            else:
                typer.echo(f"Running {normalized_type} in {mode} mode")
                typer.echo(f"Feature: {feature}, Version: {version}")
                typer.echo("Strict mode: enabled")
                typer.echo("Blocked: missing user-story artifact for strict mode")
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
        "llm_prompts": [],
        "token_usage": {"prompt_tokens": 0, "completion_tokens": 0},
        "tool_calls": [{"name": "router.dispatch", "args": {"workflow": normalized_type}}],
        "artifacts": {"events": str(events_file.relative_to(root))},
        "deviations": [],
        "confirmations": [],
    }
    save_run_state(root, run_id, state)

    if json_output:
        typer.echo(f'{{"run_id":"{run_id}","status":"completed","reason":"{state["reason"]}"}}')
    else:
        typer.echo(f"Running {normalized_type} in {mode} mode")
        typer.echo(f"Feature: {feature}, Version: {version}")
        if strict:
            typer.echo("Strict mode: enabled")
    return 0


@app.command()
def workflow(
    workflow_type: str = typer.Argument("workflow", help="Workflow type: workflow/team/auto-test"),
    mode: str = typer.Option("normal", "--mode", "-m", help="Run mode: normal/debug/strict/dry-run/replay"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature name"),
    version: str = typer.Option("v1.0.0", "--version", "-v", help="Version"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Run Beacon workflow."""
    code = _run_workflow_impl(
        workflow_type=workflow_type,
        mode=mode,
        feature=feature,
        version=version,
        strict=strict,
        json_output=json_output,
        project_root=project_root,
    )
    raise typer.Exit(code=code)


if __name__ == "__main__":
    app()
