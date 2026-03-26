"""Beacon freeze command - formalize frozen revision baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.story_state import freeze_story_state, feature_slug
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="freeze", help="Freeze current feature revision as implementation baseline", invoke_without_command=True, no_args_is_help=False)


def _freeze_impl(feature: str, project: Optional[str], version: str, json_output: bool) -> int:
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    revision = freeze_revision_state(project_root, version=resolved_version, feature=feature)
    freeze_story_state(project_root, version=resolved_version, feature=feature)
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": resolved_version,
        "revision_id": revision.get("revision_id", ""),
        "status": "frozen",
        "baseline_hash": revision.get("baseline_hash", ""),
        "story_path": str((project_root / "docs" / "beacon" / resolved_version / ".machine" / "user-story" / f"{feature_slug(feature)}.json").relative_to(project_root)),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"✓ Revision frozen: {payload['revision_id']} ({payload['baseline_hash']})")
    return 0


@app.callback(invoke_without_command=True)
def freeze_entry(
    ctx: typer.Context,
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    if ctx.invoked_subcommand is None:
        raise typer.Exit(code=_freeze_impl(feature, project, version, json_output))
