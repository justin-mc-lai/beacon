"""Public workspace admission surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.workspace_admission import release_workspace_lease, run_workspace_admit, validate_workspace_admission

app = typer.Typer(
    name="workspace",
    help="Workspace git admission and governed worktree lanes.",
    no_args_is_help=True,
)


@app.command("admit")
def admit(
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option(..., "--version", "-v", help="Beacon version (e.g. v1.6.2)"),
    feature: str = typer.Option(..., "--feature", help="Feature slug"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan admission without writing artifact"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Resolve governed branch/worktree and issue a dirty-only workspace admission artifact."""
    project_root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    payload = run_workspace_admit(
        project_root,
        version=version,
        feature=feature,
        dry_run=dry_run,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon workspace admit: {payload.get('status')}")
        if payload.get("worktree_path"):
            typer.echo(f"worktree_path: {payload.get('worktree_path')}")
        if payload.get("branch"):
            typer.echo(f"branch: {payload.get('branch')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
    raise typer.Exit(code=2 if payload.get("status") != "pass" else 0)


@app.command("validate")
def validate(
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option(..., "--version", "-v", help="Beacon version"),
    feature: str = typer.Option(..., "--feature", help="Feature slug"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Validate an existing workspace admission artifact (dirty-only semantics)."""
    project_root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    payload = validate_workspace_admission(project_root, version=version, feature=feature)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon workspace validate: {payload.get('status')}")
        if payload.get("reason_codes"):
            typer.echo(f"reason_codes: {', '.join(payload.get('reason_codes') or [])}")
    raise typer.Exit(code=2 if not payload.get("valid") else 0)


@app.command("release")
def release(
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option(..., "--version", "-v", help="Beacon version"),
    feature: str = typer.Option(..., "--feature", help="Feature slug"),
    holder: str = typer.Option("", "--holder", help="Lease holder override"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Return a pooled workspace lease to available state without deleting the worktree."""
    project_root = Path(project).expanduser().resolve() if project else Path.cwd().resolve()
    payload = release_workspace_lease(project_root, version=version, feature=feature, holder=holder)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon workspace release: {payload.get('status')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
    raise typer.Exit(code=2 if payload.get("status") == "blocked" else 0)
