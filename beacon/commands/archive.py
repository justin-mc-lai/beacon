"""Beacon archive governance command surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.archive_governance import (
    ARCHIVE_STATUSES,
    archive_governance_supported,
    build_archive_plan,
    load_archive_read_model,
    materialize_archive_governance,
)
from beacon.utils.versioning import resolve_target_version


app = typer.Typer(name="archive", help="Archive governance and historical requirement isolation")


@app.command("plan")
def plan(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    feature: str = typer.Option("", "--feature", help="Optional feature name"),
    archive_status: str = typer.Option("", "--archive-status", help=f"Archive status: {', '.join(ARCHIVE_STATUSES)}"),
    reason: str = typer.Option("", "--reason", help="Archive reason"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Preview archive governance outputs without mutating state."""
    root = Path(project_root) if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    if not archive_governance_supported(resolved_version):
        payload = {
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "archive_governance_not_supported",
            "version": resolved_version,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon archive plan blocked")
        raise typer.Exit(2)
    payload = {
        "schema_version": "1.0",
        "status": "planned",
        "version": resolved_version,
        "archive_plan": build_archive_plan(
            root,
            version=resolved_version,
            feature=feature,
            archive_status=archive_status,
            reason=reason,
        ),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon archive plan: {resolved_version}")
        if feature:
            typer.echo(f"feature: {feature}")
        if archive_status:
            typer.echo(f"archive_status: {archive_status}")


@app.command("apply")
def apply(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    feature: str = typer.Option("", "--feature", help="Optional feature name"),
    archive_status: str = typer.Option("", "--archive-status", help=f"Archive status: {', '.join(ARCHIVE_STATUSES)}"),
    reason: str = typer.Option("", "--reason", help="Archive reason"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Write archive governance materials."""
    root = Path(project_root) if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    if not archive_governance_supported(resolved_version):
        payload = {
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "archive_governance_not_supported",
            "version": resolved_version,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon archive apply blocked")
        raise typer.Exit(2)
    payload = materialize_archive_governance(
        root,
        version=resolved_version,
        feature=feature,
        archive_status=archive_status,
        reason=reason,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon archive apply: {payload.get('status')}")
        typer.echo(f"plan_ref: {payload.get('plan_ref', '')}")
        typer.echo(f"index_ref: {payload.get('index_ref', '')}")
        if payload.get("feature_ref"):
            typer.echo(f"feature_ref: {payload.get('feature_ref')}")


@app.command("status")
def status(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    feature: str = typer.Option("", "--feature", help="Optional feature name"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show archive governance state."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = load_archive_read_model(root, version=version, feature=feature)
    payload["status"] = "pass"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon archive status: {payload.get('version', '')}")
        feature_payload = payload.get("feature") if isinstance(payload.get("feature"), dict) else {}
        if feature_payload:
            typer.echo(f"feature: {feature_payload.get('feature', '')}")
            typer.echo(f"archive_status: {feature_payload.get('status', 'active')}")


@app.command("explain")
def explain(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Explain Beacon archive semantics."""
    root = Path(project_root) if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    payload = {
        "schema_version": "1.0",
        "version": resolved_version,
        "status_model": list(ARCHIVE_STATUSES),
        "support_position": "support-command",
        "lifecycle_position": "not-a-primary-stage",
        "commands": [
            "beacon archive plan",
            "beacon archive apply",
            "beacon archive status",
            "beacon archive explain",
        ],
        "skill": "beacon:beacon-archive",
        "boundary": "brainstorm remains read-only before archive; archive writes formal governance truth",
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon archive explain")
        typer.echo("status_model: active, superseded, archived-learnable, archived-reference-only")
        typer.echo("support_position: support-command")
