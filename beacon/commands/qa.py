"""Beacon QA command - primary surface for v1.1.8 testing and browser acceptance."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.qa_runtime import (
    list_qa_sessions,
    load_current_qa_session,
    load_qa_session,
    load_qa_status,
    qa_sessions_root,
    set_current_qa_session,
    write_qa_session,
)

app = typer.Typer(name="qa", help="QA primary surface (v1.1.8)")
session_app = typer.Typer(name="session", help="QA login/session state helpers")
app.add_typer(session_app, name="session")


def _beacon_exec(args: list[str], *, cwd: Path) -> int:
    cmd = [sys.executable, "-m", "beacon.main", *args]
    result = subprocess.run(cmd, cwd=cwd)
    return int(result.returncode)


@app.command(
    "run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run(ctx: typer.Context):
    """Primary alias of `beacon auto-test create ...`."""
    code = _beacon_exec(["auto-test", "create", *ctx.args], cwd=Path.cwd())
    raise typer.Exit(code=code)


@app.command("status")
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Read canonical QA status, falling back to legacy auto-test status."""
    project_root = Path(project) if project else Path.cwd()
    payload = load_qa_status(project_root)
    if not payload:
        typer.echo("No QA status found. Run `beacon qa run ...` first.")
        raise typer.Exit(1)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon QA Status")
    typer.echo("=" * 40)
    typer.echo(f"Status: {payload.get('status', 'N/A')}")
    typer.echo(f"Version: {payload.get('version', 'N/A')}")
    typer.echo(f"Run ID: {payload.get('run_id', 'N/A')}")
    typer.echo(f"Scope: {payload.get('scope', 'N/A')}")
    layers = payload.get("selected_layers")
    if isinstance(layers, list):
        typer.echo(f"Layers: {', '.join(str(x) for x in layers)}")


@app.command(
    "import",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def import_results(ctx: typer.Context):
    """Primary alias of `beacon auto-test import-qa-use ...`."""
    code = _beacon_exec(["auto-test", "import-qa-use", *ctx.args], cwd=Path.cwd())
    raise typer.Exit(code=code)


@session_app.command("save")
def session_save(
    session_id: str = typer.Argument(..., help="Session id"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    origin: str = typer.Option("", "--origin", help="Origin or base URL"),
    runner_type: str = typer.Option("agent-browser", "--runner-type", help="Runner type"),
    profile_ref: str = typer.Option("", "--profile-ref", help="Browser profile ref"),
    cookies_ref: str = typer.Option("", "--cookies-ref", help="Cookies artifact path"),
    storage_state_ref: str = typer.Option("", "--storage-state-ref", help="Storage state artifact path"),
    expires_at: str = typer.Option("", "--expires-at", help="Expiry timestamp"),
    sensitivity: str = typer.Option("internal", "--sensitivity", help="Sensitivity label"),
    scope: Optional[list[str]] = typer.Option(None, "--scope", help="Allowed scopes/origins"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Save a canonical QA session manifest."""
    project_root = Path(project) if project else Path.cwd()
    payload = {
        "origin": origin,
        "runner_type": runner_type,
        "profile_ref": profile_ref,
        "cookies_ref": cookies_ref,
        "storage_state_ref": storage_state_ref,
        "expires_at": expires_at,
        "sensitivity": sensitivity,
        "scopes": list(scope or []),
    }
    refs = write_qa_session(project_root, session_id, payload)
    current_ref = set_current_qa_session(project_root, session_id)
    result = {"session_id": session_id, **refs, **current_ref}
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ QA session saved: {session_id}")
    typer.echo(f"  Manifest: {project_root / refs['manifest']}")


@session_app.command("list")
def session_list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """List QA sessions."""
    project_root = Path(project) if project else Path.cwd()
    rows = list_qa_sessions(project_root)
    current = load_current_qa_session(project_root)
    current_id = str(current.get("session_id", "") or "")
    payload = {"current_session_id": current_id, "sessions": rows}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"QA Sessions ({len(rows)} found):")
    for row in rows:
        marker = "*" if str(row.get("session_id", "")) == current_id else "-"
        typer.echo(f"{marker} {row.get('session_id')} ({row.get('runner_type', 'unknown')} @ {row.get('origin', '-')})")


@session_app.command("use")
def session_use(
    session_id: str = typer.Argument(..., help="Session id"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Set the current QA session."""
    project_root = Path(project) if project else Path.cwd()
    payload = load_qa_session(project_root, session_id)
    if not payload:
        typer.echo(f"Session not found: {session_id}", err=True)
        raise typer.Exit(2)
    refs = set_current_qa_session(project_root, session_id)
    result = {"session_id": session_id, **refs}
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Current QA session: {session_id}")


@session_app.command("show")
def session_show(
    session_id: str = typer.Argument("", help="Session id (default current)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show current or named QA session."""
    project_root = Path(project) if project else Path.cwd()
    target = session_id.strip() or str(load_current_qa_session(project_root).get("session_id", "") or "")
    if not target:
        typer.echo("No current QA session selected", err=True)
        raise typer.Exit(2)
    payload = load_qa_session(project_root, target)
    if not payload:
        typer.echo(f"Session not found: {target}", err=True)
        raise typer.Exit(2)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
