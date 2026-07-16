"""Public loop-goal run surface (R7 dual runtime)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.loop_goal_state import build_resume, init, read_state
from beacon.utils.goal_queue import enqueue_discovery, reject_loop_product_complete

app = typer.Typer(name="loop-goal", help="Loop-goal orchestrator CLI driver.", no_args_is_help=True)


@app.command("run")
def run(
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    version: str = typer.Option(..., "--version", "-v"),
    feature: str = typer.Option(..., "--feature", "-f"),
    utterance: str = typer.Option("", "--utterance", "-u"),
    resume_run_id: str = typer.Option("", "--run-id"),
    mode: str = typer.Option("cli_agent", "--mode", help="host_skill|cli_agent"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Start or resume a loop-goal run; shares state with host skill (AC-036)."""
    root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    if resume_run_id:
        payload = build_resume(root, run_id=resume_run_id, utterance=utterance)
    elif utterance:
        state = init(root, version=version, feature=feature, utterance=utterance)
        state.setdefault("outputs", {})["loop_execution_mode"] = mode
        payload = build_resume(root, run_id=state["run_id"], utterance=utterance)
    else:
        payload = {"status": "blocked", "reason_code": "loop_goal_run_missing_utterance"}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon loop-goal run: {payload.get('status')}")
        if payload.get("run_id"):
            typer.echo(f"run_id: {payload.get('run_id')}")
        typer.echo(f"resume_action: {payload.get('resume_action', 'none')}")
        typer.echo(f"next_skill: {payload.get('next_skill') or 'none'}")
    raise typer.Exit(code=0 if payload.get("status") == "pass" else 2)


@app.command("discover")
def discover(
    utterance: str = typer.Argument(..., help="Discovery utterance to enqueue for beacon-goal"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    version: str = typer.Option("", "--version", "-v"),
    feature: str = typer.Option("", "--feature", "-f"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Support discovery: write goal-queue item (does not start product delivery)."""
    root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    payload = enqueue_discovery(
        root,
        utterance=utterance,
        version=version,
        feature=feature,
        source="beacon-loop-goal",
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon loop-goal discover: {payload.get('status')}")
        item = payload.get("item") if isinstance(payload.get("item"), dict) else {}
        typer.echo(f"queue_item: {item.get('id')}")
        typer.echo("next: beacon goal run (or beacon-goal) to consume queue / deliver")
    raise typer.Exit(0)


@app.command("mark-complete")
def mark_complete_forbidden(
    json_output: bool = typer.Option(False, "--json"),
):
    """Explicitly rejected: loop cannot mark product complete."""
    payload = reject_loop_product_complete(attempted_by="beacon-loop-goal")
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"blocked: {payload.get('reason_code')}")
        typer.echo(payload.get("message"))
    raise typer.Exit(2)
