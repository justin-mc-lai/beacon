"""Feature package materialization and validation commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.feature_package import materialize_feature_package, validate_feature_package
from beacon.utils.plan_goal_task_closure import materialize_deterministic_scaffold, version_requires_task_closure
from beacon.utils.versioning import resolve_target_version


def materialize_feature_package_entry(
    feature: str = typer.Argument(..., help="Feature name or slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing feature package files"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Materialize v1.5.0 feature-centric package as a parallel read model."""

    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    if version_requires_task_closure(resolved_version, feature):
        payload = materialize_deterministic_scaffold(
            project_root, version=resolved_version, feature=feature, force=force
        )
    else:
        payload = materialize_feature_package(project_root, version=resolved_version, feature=feature, force=force)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Feature package materialized: {payload['package_dir']}")
    typer.echo(f"Validation: {payload['validation'].get('status')}")


def validate_feature_package_entry(
    feature: str = typer.Argument(..., help="Feature name or slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Validate v1.5.0 feature package without changing canonical gate truth."""

    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = validate_feature_package(project_root, version=resolved_version, feature=feature, write_report=True)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Feature package validation: {payload['status']}")
    if payload.get("report_path"):
        typer.echo(f"Report: {payload['report_path']}")
    for item in payload.get("diagnostics", []):
        typer.echo(f"- {item.get('severity')}: {item.get('code')} ({item.get('path')})")
