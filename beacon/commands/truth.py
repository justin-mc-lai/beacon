"""Beacon truth CLI: init, verify, show for v1.4.12+."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.manifest import add_feature, load_manifest_or_fail, ManifestMissingError
from beacon.utils.feature_package import materialize_feature_package, validate_feature_package
from beacon.utils.truth_format import (
    validate_prd_format,
    validate_test_case_format,
    validate_user_story_format,
)
from beacon.utils.truth_map import feature_package_authoritative
from beacon.utils.truth_template import (
    render_prd_template,
    render_test_case_template,
    render_user_story_template,
)
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(
    name="truth",
    help="Truth triptych template and format management.",
    no_args_is_help=True,
)


def _resolve_root(project: Optional[str]) -> Path:
    return Path(project).resolve() if project else Path.cwd()


def _write_truth_file(path: Path, content: str, *, force: bool = False) -> Path:
    """Write truth content to file, creating parent dirs as needed."""
    if path.exists() and not force:
        typer.echo(f"File already exists: {path}. Use --force to overwrite.", err=True)
        raise typer.Exit(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@app.command("init")
def init_cmd(
    kind: str = typer.Argument("all", help="Kind: prd, user-story, test-case, or all"),
    feature: str = typer.Option(..., "--feature", "-f", help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    lang: str = typer.Option("en", "--lang", "-l", help="Language: en|zh"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
) -> None:
    """Initialize truth files."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")

    if lang not in ("en", "zh"):
        typer.echo(f"Invalid --lang: {lang}. Must be 'en' or 'zh'.", err=True)
        raise typer.Exit(2)

    if feature_package_authoritative(resolved):
        if kind not in {"all", "package"}:
            typer.echo(
                f"v1.5.2+ truth init writes the authoritative feature package; unsupported kind: {kind}",
                err=True,
            )
            raise typer.Exit(2)
        payload = materialize_feature_package(project_root, version=resolved, feature=feature, force=force)
        for path in payload.get("written", []):
            typer.echo(f"✓ Created package truth: {path}")
        for path in payload.get("skipped", []):
            typer.echo(f"- Preserved package truth: {path}")
        return

    base = project_root / "docs" / "beacon" / resolved
    kinds = ["prd", "user-story", "test-case"] if kind == "all" else [kind]
    written: list[str] = []

    for k in kinds:
        if k == "prd":
            content = render_prd_template(feature_slug=slug, version=resolved, lang=lang)
            path = base / "prd" / f"{slug}.md"
        elif k == "user-story":
            content = render_user_story_template(feature_slug=slug, version=resolved, lang=lang)
            path = base / "user-story" / f"{slug}.md"
        elif k == "test-case":
            content = render_test_case_template(feature_slug=slug, version=resolved, lang=lang)
            path = base / "qa" / "test-cases" / f"{slug}.md"
        else:
            typer.echo(f"Unknown kind: {k}. Use prd, user-story, test-case, or all.", err=True)
            raise typer.Exit(2)

        _write_truth_file(path, content, force=force)
        written.append(str(path))
        typer.echo(f"✓ Created {k}: {path}")

    # Register in manifest if init all
    if kind == "all":
        try:
            add_feature(project_root, resolved, feature, language=lang)
            typer.echo(f"✓ Registered feature '{slug}' in manifest")
        except Exception as e:
            typer.echo(f"⚠ Manifest registration skipped: {e}", err=True)


@app.command("verify")
def verify_cmd(
    feature: str = typer.Option(..., "--feature", "-f", help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    strict: bool = typer.Option(False, "--strict", help="Fail on any non-compliance"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """Verify truth format compliance."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")
    base = project_root / "docs" / "beacon" / resolved

    if feature_package_authoritative(resolved):
        payload = validate_feature_package(project_root, version=resolved, feature=feature, write_report=True)
        status = str(payload.get("status") or "unknown")
        if status != "pass":
            typer.echo(f"✗ feature package: {status}", err=True)
            for issue in payload.get("diagnostics", []):
                typer.echo(f"  - {issue.get('code', 'unknown')}", err=True)
            raise typer.Exit(2)
        typer.echo(f"✓ Feature package truth passes validation for feature '{slug}'")
        return

    # Try to get paths from manifest first, fall back to fixed paths
    try:
        manifest = load_manifest_or_fail(project_root, resolved)
        feature_entry = None
        for f in manifest.get("features", []):
            if f.get("slug") == slug:
                feature_entry = f
                break
        if feature_entry:
            paths = {
                "prd": project_root / feature_entry.get("truth_paths", {}).get("prd", ""),
                "user_story": project_root / feature_entry.get("truth_paths", {}).get("user_story", ""),
                "test_case": project_root / feature_entry.get("truth_paths", {}).get("test_case", ""),
            }
        else:
            paths = {
                "prd": base / "prd" / f"{slug}.md",
                "user_story": base / "user-story" / f"{slug}.md",
                "test_case": base / "qa" / "test-cases" / f"{slug}.md",
            }
    except ManifestMissingError:
        paths = {
            "prd": base / "prd" / f"{slug}.md",
            "user_story": base / "user-story" / f"{slug}.md",
            "test_case": base / "qa" / "test-cases" / f"{slug}.md",
        }

    all_pass = True

    for kind, path in paths.items():
        if not path.exists():
            typer.echo(f"✗ {kind}: file not found: {path}", err=True)
            all_pass = False
            continue

        content = path.read_text(encoding="utf-8")

        if kind == "prd":
            result = validate_prd_format(content, strict=strict)
        elif kind == "user_story":
            result = validate_user_story_format(content, strict=strict)
        else:
            result = validate_test_case_format(content, strict=strict)

        status = result.get("status", "unknown")
        if status == "pass":
            typer.echo(f"✓ {kind}: format compliant ({', '.join(result.get('sections_found', [])[:5])}...)")
        else:
            typer.echo(f"✗ {kind}: format non-compliant", err=True)
            for issue in result.get("issues", []):
                typer.echo(f"  - {issue}", err=True)
            all_pass = False

    if not all_pass:
        raise typer.Exit(2)
    typer.echo(f"✓ All truth documents pass format verification for feature '{slug}'")


@app.command("show")
def show_cmd(
    kind: str = typer.Argument(..., help="Kind: prd, user-story, or test-case"),
    feature: str = typer.Option(..., "--feature", "-f", help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    lang: str = typer.Option("en", "--lang", "-l", help="Language: en|zh"),
) -> None:
    """Show the expected template specification without reading files."""
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")

    if lang not in ("en", "zh"):
        typer.echo(f"Invalid --lang: {lang}. Must be 'en' or 'zh'.", err=True)
        raise typer.Exit(2)

    if kind == "prd":
        content = render_prd_template(feature_slug=slug, version=version, lang=lang)
    elif kind == "user-story":
        content = render_user_story_template(feature_slug=slug, version=version, lang=lang)
    elif kind == "test-case":
        content = render_test_case_template(feature_slug=slug, version=version, lang=lang)
    else:
        typer.echo(f"Unknown kind: {kind}. Use prd, user-story, or test-case.", err=True)
        raise typer.Exit(2)

    typer.echo(content)
