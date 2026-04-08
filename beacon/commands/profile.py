"""Beacon project profile command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.project_skills import create_project_profile, load_project_profile
from beacon.utils.skill_discovery import load_skill_discovery

app = typer.Typer(name="profile", help="Manage Beacon project skill profiles")


@app.command("create")
def create(
    project: str = typer.Argument(..., help="Project name"),
    profile_id: str = typer.Argument(..., help="Profile id"),
    example: str = typer.Option("", "--example", help="Bootstrap from example profile, e.g. rolo-uat"),
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Create or update a project skill profile in beacon.config.yaml."""
    root = Path(project_root) if project_root else Path.cwd()
    path = create_project_profile(root, project=project, profile_id=profile_id, example=example or None)
    payload = {
        "schema_version": "1.0",
        "status": "created",
        "project": project,
        "profile_id": profile_id,
        "config_path": str(path),
        "example": example or "",
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ profile `{profile_id}` written to {path}")


@app.command("show")
def show(
    profile_id: str = typer.Argument(..., help="Profile id"),
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show a resolved project skill profile."""
    root = Path(project_root) if project_root else Path.cwd()
    profile = load_project_profile(root, profile_id)
    if not profile:
        typer.echo(f"Unknown profile: {profile_id}", err=True)
        raise typer.Exit(2)
    payload = {"schema_version": "1.0", "profile_id": profile_id, "profile": profile}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("discovery")
def discovery(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show the latest discovery result for project profile review."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = load_skill_discovery(root)
    if not payload:
        typer.echo("No skill discovery result found", err=True)
        raise typer.Exit(2)
    output = {
        "schema_version": "1.0",
        "status": str(payload.get("status", "preview") or "preview"),
        "recommended_profile_id": str(payload.get("recommended_profile_id", "") or ""),
        "selected_template": str(payload.get("selected_template", "") or ""),
        "payload": payload,
    }
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
