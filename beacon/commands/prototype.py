"""Beacon prototype command - contract-driven professional UI prototype generation."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import json
import typer

from beacon.utils.prototype_utils import (
    bind_prototype_bundle,
    compile_prototype_plan,
    evaluate_prototype_status,
    freeze_prototype,
    prototype_dir,
    review_prototype_bundle,
    write_prototype_plan,
    write_prototype_bundle,
)
from beacon.utils.versioning import resolve_operational_docs_version, resolve_target_version

app = typer.Typer(name="prototype", help="Generate and manage static UI prototypes")


def _resolved_operational_version(project_root: Path, version: str, command_name: str) -> str:
    try:
        return resolve_operational_docs_version(project_root, version, command_name=command_name)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc


@app.command()
def plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Compile structured prototype plan from requirement contracts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype plan")
    try:
        result = write_prototype_plan(project_root, resolved_version, feature)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    payload = {
        "feature": feature,
        "version": resolved_version,
        "prototype_mode": result["plan"].get("prototype_mode"),
        "required_pages": result["plan"].get("required_pages", []),
        "required_states": result["plan"].get("required_states", []),
        "path": str(result["path"].relative_to(project_root)),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Prototype plan compiled: {result['path']}")


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
    resolved_version = _resolved_operational_version(project_root, version, "prototype create")
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
            if path.is_dir():
                continue
            target = out_root / path.name
            target.write_bytes(path.read_bytes())

    payload = {
        "feature": feature,
        "version": resolved_version,
        "ui_kit": "bootstrap-5.3.x",
        "prototype_type": result["contract"]["prototype_archetype"],
        "prototype_mode": result.get("prototype_mode", "minimal"),
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
    resolved_version = _resolved_operational_version(project_root, version, "prototype preview")
    status = evaluate_prototype_status(project_root, resolved_version, feature)
    html_path = status["files"]["index_html"]
    if not html_path.exists():
        typer.echo(f"Prototype not found: {html_path}", err=True)
        raise typer.Exit(1)

    root = status["root"]
    typer.echo(f"Prototype preview ready: {html_path}")
    typer.echo(f"Open directly: file://{html_path}")
    typer.echo(f'Quick serve: python3 -m http.server 4173 --directory "{root}"')


@app.command("directory")
def directory(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show the unified prototype directory page and its style-analysis contract."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype directory")
    status = evaluate_prototype_status(project_root, resolved_version, feature)
    html_path = status["files"]["index_html"]
    if not html_path.exists():
        typer.echo(f"Prototype directory not found: {html_path}", err=True)
        raise typer.Exit(1)

    coverage_path = status["files"]["coverage_report"]
    coverage = {}
    if coverage_path.exists():
        try:
            loaded = json.loads(coverage_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                coverage = loaded
        except Exception:  # noqa: BLE001
            coverage = {}

    style_analysis_path = status["files"]["ui_style_analysis_json"]
    payload = {
        "feature": feature,
        "version": resolved_version,
        "directory_page": str(html_path.relative_to(project_root)),
        "style_analysis_path": (
            str(style_analysis_path.relative_to(project_root))
            if style_analysis_path.exists()
            else ""
        ),
        "required_pages": coverage.get("required_pages", []),
        "required_states": coverage.get("required_states", []),
        "generated_pages": coverage.get("generated_pages", []),
        "generated_state_variants": coverage.get("generated_state_variants", []),
        "review_status": status.get("review_status"),
        "design_review_outcome": status.get("design_review_outcome"),
        "gate_ready": bool(status.get("gate_ready")),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo("Beacon Prototype Directory")
    typer.echo("=" * 28)
    typer.echo(f"feature       : {feature}")
    typer.echo(f"version       : {resolved_version}")
    typer.echo(f"directory     : {html_path}")
    typer.echo(f"style_analysis: {style_analysis_path if style_analysis_path.exists() else 'missing'}")
    typer.echo(f"pages         : {len(payload.get('generated_pages', []))}")
    typer.echo(f"state_variants: {len(payload.get('generated_state_variants', []))}")
    typer.echo(f"review        : {payload.get('review_status')}")
    typer.echo(f"gate_ready    : {payload.get('gate_ready')}")


@app.command()
def review(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Review a generated prototype against requirement and delivery contracts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype review")
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
def bind(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Bind prototype route-closure cases to implementation-map runtime targets."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype bind")
    try:
        payload = bind_prototype_bundle(project_root, resolved_version, feature)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)
    if json_output:
        serializable = {
            "feature": feature,
            "version": resolved_version,
            "bound_cases": payload.get("bound_cases", 0),
            "path": str(Path(payload.get("path", "")).relative_to(project_root)),
        }
        typer.echo(json.dumps(serializable, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Prototype bound: {payload.get('bound_cases', 0)} cases")
    typer.echo(f"✓ Implementation map: {payload.get('path')}")


@app.command()
def freeze(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Freeze a prototype by persisting source and artifact fingerprints."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "prototype freeze")
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
    resolved_version = _resolved_operational_version(project_root, version, "prototype status")
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
