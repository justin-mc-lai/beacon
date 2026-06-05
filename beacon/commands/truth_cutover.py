"""Legacy truth cutover commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.legacy_cutover import run_legacy_project_cutover
from beacon.utils.versioning import resolve_target_version


app = typer.Typer(
    name="truth-cutover",
    help="Detect and repair legacy/mixed project truth state before v1.5.2 execution.",
    no_args_is_help=True,
)


@app.command("run")
def run_cmd(
    feature: str = typer.Argument(..., help="Feature name or slug"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "--target-version", "-v", help="Target Beacon docs version"),
    apply: bool = typer.Option(False, "--apply", help="Run safe cutover repair phases instead of inventory-only"),
    agent: str = typer.Option("codex", "--agent", help="Agent surface to verify"),
    resume_intent: str = typer.Option("refreeze", "--resume-intent", help="Original operator intent to resume after cutover"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Run legacy/mixed truth cutover inventory or safe repair phases."""

    project_root = (Path(project) if project else Path.cwd()).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    payload = run_legacy_project_cutover(
        project_root,
        version=resolved_version,
        feature=feature,
        apply=apply,
        agent=agent,
        resume_intent=resume_intent,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Truth cutover: {payload.get('status')}")
        for name, phase in (payload.get("phases") or {}).items():
            typer.echo(f"- {name}: {phase.get('status')} {phase.get('reason_code') or ''}")
        resume = payload.get("resume") if isinstance(payload.get("resume"), dict) else {}
        if resume.get("next_command"):
            typer.echo(f"Resume: {resume['next_command']}")
    raise typer.Exit(code=2 if payload.get("blocked") else 0)
