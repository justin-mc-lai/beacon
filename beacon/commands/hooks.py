"""Beacon project lifecycle hook toolkit."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.project_hooks import (
    disable_hook,
    hook_status,
    list_hook_contracts,
    plan_hook,
    run_hook,
)

app = typer.Typer(name="hooks", help="Manage project-level lifecycle hook contracts")


def _root(project_root: str) -> Path:
    return Path(project_root) if project_root else Path.cwd()


def _emit(payload: dict, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"status: {payload.get('status', '')}")
    if payload.get("reason_code"):
        typer.echo(f"reason_code: {payload.get('reason_code')}")


@app.command("list")
def list_hooks(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """List project hook contracts from docs/beacon/hooks."""
    root = _root(project_root)
    hooks = list_hook_contracts(root)
    payload = {
        "schema_version": "1.0",
        "status": "pass",
        "project_root": str(root),
        "hook_count": len(hooks),
        "hooks": hooks,
        "truth_root": "docs/beacon/hooks",
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Project Hooks")
    typer.echo("====================")
    for item in hooks:
        frontmatter = item.get("frontmatter", {}) if isinstance(item.get("frontmatter"), dict) else {}
        typer.echo(f"- {item.get('hook_id')}: {frontmatter.get('hook_code', '')} ({item.get('path')})")


@app.command("plan")
def plan(
    hook_id: str = typer.Argument(..., help="Hook id"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Beacon docs version for evidence context"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature context"),
    hook_code: str = typer.Option("", "--hook-code", help="Expected finite hook code"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Plan a hook without executing side effects."""
    payload = plan_hook(_root(project_root), hook_id, version=version, feature=feature, hook_code=hook_code)
    _emit(payload, json_output)


@app.command("run")
def run(
    hook_id: str = typer.Argument(..., help="Hook id"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("", "--version", "-v", help="Beacon docs version for evidence context"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature context"),
    hook_code: str = typer.Option("", "--hook-code", help="Expected finite hook code"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan and write dry-run evidence only"),
    confirm: bool = typer.Option(False, "--confirm", help="Explicitly confirm side-effect hook execution"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run a hook through admission, dry-run, or manual confirmation."""
    payload = run_hook(
        _root(project_root),
        hook_id,
        version=version,
        feature=feature,
        hook_code=hook_code,
        dry_run=dry_run,
        confirm=confirm,
    )
    _emit(payload, json_output)


@app.command("disable")
def disable(
    hook_id: str = typer.Argument(..., help="Hook id"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Disable a project hook contract by setting enabled: false."""
    payload = disable_hook(_root(project_root), hook_id)
    _emit(payload, json_output)


@app.command("status")
def status(
    hook_id: str = typer.Argument(..., help="Hook id"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature context"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show hook admission and latest evidence read model."""
    payload = hook_status(_root(project_root), hook_id, feature=feature)
    _emit(payload, json_output)
