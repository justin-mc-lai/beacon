"""Beacon reopen command - create a new revision from current active one."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.material_sync import sync_change_loop_requirement_package
from beacon.utils.git_alignment import check_truth_authoring_branch
from beacon.utils.revision_state import reopen_revision_state
from beacon.utils.truth_review_gate import mark_package_materials_stale
from beacon.utils.story_state import reopen_story_state
from beacon.utils.cli_version_guard import resolve_target_version_guarded

app = typer.Typer(name="reopen", help="Create a new active revision for a feature", invoke_without_command=True, no_args_is_help=False)


def _reopen_impl(feature: str, project: Optional[str], version: str, reason: str, json_output: bool) -> int:
    project_root = Path(project) if project else Path.cwd()
    project_root = project_root.expanduser().resolve()
    resolved_version = resolve_target_version_guarded(project_root, version, command_name="beacon reopen")
    branch_guard = check_truth_authoring_branch(
        project_root,
        version=resolved_version,
        operation="reopen",
    )
    if bool(branch_guard.get("blocked")):
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(branch_guard.get("reason_code") or "truth_canonical_branch_mismatch"),
            "truth_authoring_branch": branch_guard,
            "reason": reason,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(
                "Beacon reopen blocked: requirement truth must be authored on "
                f"{branch_guard.get('truth_canonical', 'main')}"
            )
        return 2
    previous_revision, next_revision = reopen_revision_state(project_root, version=resolved_version, feature=feature, reason=reason)
    reopen_story_state(project_root, version=resolved_version, feature=feature, reason=reason)
    materials_stale = mark_package_materials_stale(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    try:
        requirement_package = sync_change_loop_requirement_package(
            project_root,
            version=resolved_version,
            feature=feature,
        )
    except Exception as exc:  # noqa: BLE001
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": "requirement_package_sync_failed",
            "message": f"failed to sync machine requirement package: {exc}",
            "previous_revision_id": previous_revision.get("revision_id", ""),
            "new_revision_id": next_revision.get("revision_id", ""),
            "reason": reason,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon reopen blocked: machine requirement package sync failed")
        return 2
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": resolved_version,
        "status": "reopened",
        "previous_revision_id": previous_revision.get("revision_id", ""),
        "new_revision_id": next_revision.get("revision_id", ""),
        "reason": reason,
        "requirement_package": requirement_package,
        "materials_stale": materials_stale,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"✓ Reopened {feature}: {payload['previous_revision_id']} -> {payload['new_revision_id']}")
    return 0


@app.callback(invoke_without_command=True)
def reopen_entry(
    ctx: typer.Context,
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    reason: str = typer.Option("change-request", "--reason", help="Reason for new revision"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    if ctx.invoked_subcommand is None:
        raise typer.Exit(code=_reopen_impl(feature, project, version, reason, json_output))
