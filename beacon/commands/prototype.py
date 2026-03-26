"""Beacon prototype command - contract-driven professional UI prototype generation."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import json
import typer

from beacon.utils.prototype_utils import (
    evaluate_prototype_status,
    freeze_prototype,
    prototype_dir,
    review_prototype_bundle,
    write_prototype_bundle,
)
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="prototype", help="Generate and manage static UI prototypes")


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Optional output directory override"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Create a Bootstrap-based professional single-page prototype from requirement contracts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    try:
        result = write_prototype_bundle(project_root, resolved_version, feature)
    except FileNotFoundError as exc:
        typer.echo(f"Missing source docs: {exc}")
        raise typer.Exit(2)
    except ValueError as exc:
        typer.echo(f"Prototype Contract invalid: {exc}")
        raise typer.Exit(2)

    if output:
        out_root = Path(output)
        out_root.mkdir(parents=True, exist_ok=True)
        for name, path in result["files"].items():
            if name == "root":
                continue
            target = out_root / path.name
            target.write_bytes(path.read_bytes())

    payload = {
        "feature": feature,
        "version": resolved_version,
        "ui_kit": "bootstrap-5.3.x",
        "prototype_type": result["contract"]["prototype_archetype"],
        "paths": {k: str(v.relative_to(project_root)) for k, v in result["files"].items() if k != "root"},
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo(f"✓ Prototype created: {result['files']['index_html']}")
    typer.echo(f"✓ Archetype: {result['contract']['prototype_archetype']}")
    if output:
        typer.echo(f"✓ Copied artifacts to: {Path(output)}")


@app.command()
def preview(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Print local preview entry points for a generated prototype."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    status = evaluate_prototype_status(project_root, resolved_version, feature)
    html_path = status["files"]["index_html"]
    if not html_path.exists():
        typer.echo(f"Prototype not found: {html_path}", err=True)
        raise typer.Exit(1)

    root = status["root"]
    typer.echo(f"Prototype preview ready: {html_path}")
    typer.echo(f"Open directly: file://{html_path}")
    typer.echo(f'Quick serve: python3 -m http.server 4173 --directory "{root}"')


@app.command()
def review(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Review a generated prototype against requirement and delivery contracts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    try:
        payload = review_prototype_bundle(project_root, resolved_version, feature)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Prototype review complete: {payload.get('overall_status')}")
    typer.echo(f"✓ Review report: {prototype_dir(project_root, resolved_version, feature) / 'prototype-review.md'}")


@app.command()
def freeze(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Freeze a prototype by persisting source and artifact fingerprints."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    try:
        payload = freeze_prototype(project_root, resolved_version, feature)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(
        f"✓ Prototype frozen: {prototype_dir(project_root, resolved_version, feature) / 'freeze.json'} "
        f"({payload.get('status')})"
    )


@app.command()
def status(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON status payload"),
):
    """Show prototype status including stale detection and review readiness."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = evaluate_prototype_status(project_root, resolved_version, feature)
    if json_output:
        serializable = dict(payload)
        serializable["root"] = str(payload["root"])
        serializable["files"] = {k: str(v) for k, v in payload["files"].items()}
        typer.echo(json.dumps(serializable, ensure_ascii=False, indent=2))
        return

    typer.echo("Beacon Prototype Status")
    typer.echo("=" * 32)
    typer.echo(f"feature      : {feature}")
    typer.echo(f"version      : {resolved_version}")
    typer.echo(f"status       : {payload.get('status')}")
    typer.echo(f"ui_kit       : {payload.get('ui_kit')}")
    typer.echo(f"review       : {payload.get('review_status')}")
    typer.echo(f"gate_ready   : {bool(payload.get('gate_ready'))}")
    typer.echo(f"path         : {payload['files']['index_html']}")
    typer.echo(f"stale        : {bool(payload.get('stale'))}")


@app.command("list")
def _list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """List all generated prototypes."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    root = project_root / "docs" / "beacon" / resolved_version / "prototype"
    if not root.exists():
        typer.echo("No prototypes found")
        return
    candidates = sorted([p for p in root.iterdir() if p.is_dir()])
    if not candidates:
        typer.echo("No prototypes found")
        return
    typer.echo(f"Prototypes ({len(candidates)} found):")
    for entry in candidates:
        feature = entry.name
        state = evaluate_prototype_status(project_root, resolved_version, feature)
        typer.echo(f"  - {entry.name}: {state.get('status')} / review={state.get('review_status')} / gate_ready={state.get('gate_ready')}")
