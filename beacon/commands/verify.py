"""Beacon verify command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.project_skills import evaluate_project_profile_gate, run_profile_orchestration

app = typer.Typer(name="verify", help="Run project-aware verification")


def _parse_params(values: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for raw in values:
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
    param: list[str] = typer.Option([], "--param", help="Template param key=value (repeatable)"),
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Target version"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run verification-stage orchestration and immediately evaluate evidence gate."""
    root = Path(project_root) if project_root else Path.cwd()
    code, orchestration = run_profile_orchestration(
        root,
        version=version,
        feature=feature,
        profile_id=profile or None,
        stage="verify",
        dry_run=dry_run,
        params=_parse_params(param),
    )
    gate = evaluate_project_profile_gate(root, version=version, feature=feature, profile_id=profile or None)
    payload = {
        "schema_version": "1.0",
        "status": orchestration.get("status", "unknown"),
        "orchestration": orchestration,
        "gate": gate,
    }
    exit_code = code
    if gate.get("status") == "blocked" and not dry_run:
        exit_code = 2
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon verify status: {payload['status']}")
        typer.echo(f"gate: {gate.get('status')}")
    raise typer.Exit(code=exit_code)
