"""Public loop-goal run surface (R7 dual runtime)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.loop_goal_state import build_resume, init, read_state

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
