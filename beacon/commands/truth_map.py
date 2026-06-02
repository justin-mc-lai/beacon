"""Truth-map resolver commands for v1.5.1+."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.truth_map import (
    rebuild_machine_json,
    resolve_truth_entrypoint_inventory,
    resolve_truth_map,
    verify_truth_entrypoint_inventory,
    verify_truth_map,
)
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(
    name="truth-map",
    help="Resolve Markdown-first truth maps and resolver-owned machine JSON.",
    no_args_is_help=True,
)


def _project_root(project: Optional[str]) -> Path:
    return Path(project).resolve() if project else Path.cwd()


@app.command("resolve")
def resolve_cmd(
    feature: str = typer.Argument(..., help="Feature name or slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Resolve truth surfaces from static resolver code and Markdown package files."""

    project_root = _project_root(project)
    resolved_version = resolve_target_version(project_root, version)
    payload = resolve_truth_map(project_root, version=resolved_version, feature=feature)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Truth map resolved: {payload.get('feature_slug')}")
    typer.echo(f"Contract: {payload.get('truth_map_contract')}")
    typer.echo(f"Authority: {payload.get('authority_source')}")


@app.command("rebuild-machine")
def rebuild_machine_cmd(
    feature: str = typer.Argument(..., help="Feature name or slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    strict: bool = typer.Option(False, "--strict", help="Block when feature package validation fails"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Regenerate requirement-derived .machine JSON from resolver-selected Markdown."""

    project_root = _project_root(project)
    resolved_version = resolve_target_version(project_root, version)
    payload = rebuild_machine_json(project_root, version=resolved_version, feature=feature, strict=strict)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Machine JSON rebuild: {payload.get('status')}")
    for path in payload.get("written", []):
        typer.echo(f"- {path}")
    if payload.get("blocked"):
        raise typer.Exit(2)


@app.command("verify")
def verify_cmd(
    feature: str = typer.Argument(..., help="Feature name or slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    strict: bool = typer.Option(False, "--strict", help="Exit non-zero on drift or stale machine JSON"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Verify resolver/package alignment and generated machine JSON freshness."""

    project_root = _project_root(project)
    resolved_version = resolve_target_version(project_root, version)
    payload = verify_truth_map(project_root, version=resolved_version, feature=feature, strict=strict)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Truth map verify: {payload.get('status')}")
        for item in payload.get("diagnostics", []):
            typer.echo(f"- {item.get('severity')}: {item.get('code')} ({item.get('path', '')})")
    if strict and payload.get("blocked"):
        raise typer.Exit(2)


@app.command("entrypoint-inventory")
def entrypoint_inventory_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    strict: bool = typer.Option(False, "--strict", help="Exit non-zero when inventory rows are missing or unclassified"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Resolve and verify the v1.5.1 high-risk truth entrypoint inventory."""

    project_root = _project_root(project)
    resolved_version = resolve_target_version(project_root, version)
    payload = (
        verify_truth_entrypoint_inventory(project_root, version=resolved_version, strict=True)
        if strict
        else resolve_truth_entrypoint_inventory(project_root, version=resolved_version)
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Truth entrypoint inventory: {payload.get('status')}")
        for entry in payload.get("entries", []):
            typer.echo(f"- {entry.get('path')}: {entry.get('classification')}")
        for item in payload.get("diagnostics", []):
            typer.echo(f"- {item.get('severity')}: {item.get('code')} ({item.get('path', '')})")
    if strict and payload.get("blocked"):
        raise typer.Exit(2)
