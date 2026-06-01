"""Beacon manifest CLI: version-level feature manifest management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.manifest import (
    ManifestMissingError,
    add_feature,
    list_features,
    load_manifest,
    remove_feature,
    sync_manifest,
    verify_manifest,
)
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(
    name="manifest",
    help="Version-level feature manifest management.",
    no_args_is_help=True,
)


def _resolve_root(project: Optional[str]) -> Path:
    return Path(project).resolve() if project else Path.cwd()


@app.command("show")
def show(
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
) -> None:
    """Display the full manifest for a version."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    manifest = load_manifest(project_root, resolved)
    if manifest is None:
        typer.echo(f"Manifest not found for {resolved}. Run 'beacon manifest sync' to create one.", err=True)
        raise typer.Exit(2)
    if json_output:
        typer.echo(json.dumps(manifest, indent=2, ensure_ascii=False))
    else:
        typer.echo(f"Version: {manifest.get('version', resolved)}")
        typer.echo(f"Features: {len(manifest.get('features', []))}")
        typer.echo(f"Generated: {manifest.get('generated_at', 'unknown')}")
        for feature in manifest.get("features", []):
            typer.echo(f"  - {feature.get('slug', '?')} ({feature.get('status', '?')}, lang={feature.get('language', '?')})")


@app.command("features")
def features(
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """List all feature slugs in the manifest."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    try:
        manifest = load_manifest_or_fail(project_root, resolved)
    except ManifestMissingError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(2)
    for feature in manifest.get("features", []):
        typer.echo(feature.get("slug", "?"))


@app.command("add-feature")
def add_feature_cmd(
    feature: str = typer.Argument(..., help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    lang: str = typer.Option("en", "--lang", help="Language (en|zh)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """Add a feature to the manifest."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    entry = add_feature(project_root, resolved, feature, language=lang)
    typer.echo(f"✓ Added feature '{entry.get('slug', feature)}' to manifest for {resolved}")


@app.command("remove-feature")
def remove_feature_cmd(
    feature: str = typer.Argument(..., help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """Remove a feature from the manifest."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    if remove_feature(project_root, resolved, feature):
        typer.echo(f"✓ Removed feature '{feature}' from manifest for {resolved}")
    else:
        typer.echo(f"Feature '{feature}' not found in manifest for {resolved}", err=True)
        raise typer.Exit(2)


@app.command("verify")
def verify_cmd(
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    strict: bool = typer.Option(False, "--strict", help="Fail on any inconsistency"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """Verify manifest consistency with disk."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    result = verify_manifest(project_root, resolved, strict=strict)
    if result["status"] == "pass":
        typer.echo(f"✓ Manifest verified for {resolved} ({result['feature_count']} features)")
    else:
        typer.echo(f"✗ Manifest verification failed for {resolved}", err=True)
        if result.get("missing_paths"):
            typer.echo(f"  Missing paths:", err=True)
            for path in result["missing_paths"]:
                typer.echo(f"    - {path}", err=True)
        if result.get("extra_files") and strict:
            typer.echo(f"  Extra files on disk:", err=True)
            for path in result["extra_files"]:
                typer.echo(f"    - {path}", err=True)
        raise typer.Exit(2)


@app.command("paths")
def paths_cmd(
    feature: str = typer.Argument(..., help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    kind: str = typer.Option("prd", "--kind", "-k", help="Kind: prd|user-story|test-case"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """Show fixed paths for a feature."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    from beacon.utils.manifest import compute_feature_paths, _slugify
    slug = _slugify(feature)
    all_paths = compute_feature_paths(project_root, resolved, slug)
    kind_map = {"prd": "prd", "user-story": "user_story", "test-case": "test_case"}
    key = kind_map.get(kind, "prd")
    if key in all_paths:
        typer.echo(all_paths[key])
    else:
        typer.echo(f"Unknown kind: {kind}", err=True)
        raise typer.Exit(2)


@app.command("sync")
def sync_cmd(
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """Scan disk and rebuild manifest from existing files."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    manifest = sync_manifest(project_root, resolved)
    feature_count = len(manifest.get("features", []))
    typer.echo(f"✓ Manifest synced for {resolved} ({feature_count} features)")


# Fix import for features command
from beacon.utils.manifest import load_manifest_or_fail
