"""Beacon orchestration command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.project_skills import run_profile_orchestration

app = typer.Typer(name="orchestrate", help="Run project-skill orchestration")


def _parse_params(values: Optional[list[str]]) -> dict[str, str]:
    params: dict[str, str] = {}
    for raw in values or []:
        text = str(raw or "").strip()
        if not text:
            continue
        key, sep, value = text.partition("=")
        if not sep:
            raise typer.BadParameter(f"invalid --param `{text}`, expected key=value")
        params[key.strip()] = value.strip()
    return params


@app.command("run")
def run(
    feature: str = typer.Argument(..., help="Feature name"),
    profile: str = typer.Option("", "--profile", help="Profile id"),
    stage: str = typer.Option("", "--stage", help="Optional stage filter"),
    param: list[str] = typer.Option([], "--param", help="Template param key=value (repeatable)"),
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target version"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run a project profile orchestration graph."""
    root = Path(project_root) if project_root else Path.cwd()
    code, payload = run_profile_orchestration(
        root,
        version=version,
        feature=feature,
        profile_id=profile or None,
        stage=stage or None,
        dry_run=dry_run,
        params=_parse_params(param),
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon orchestration status: {payload.get('status')}")
        typer.echo(f"profile: {payload.get('profile_id', '')}")
        typer.echo(f"run_id: {payload.get('run_id', '')}")
    raise typer.Exit(code=code)
