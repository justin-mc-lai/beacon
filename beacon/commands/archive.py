"""Beacon archive governance command surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.archive_governance import (
    ARCHIVE_STATUSES,
    archive_governance_supported,
    build_archive_inventory,
    build_archive_lineage,
    build_archive_plan,
    load_archive_read_model,
    materialize_archive_governance,
)
from beacon.utils.support_surface_projection import build_support_surface_projection
from beacon.utils.version_truth_catalog import (
    apply_catalog_plan,
    build_catalog_plan,
    catalog_supported,
    load_catalog_status,
)
from beacon.utils.versioning import resolve_target_version


catalog_app = typer.Typer(name="catalog", help="Version truth catalog plan/apply/bootstrap/status")


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
    payload["support_surface_projection"] = build_support_surface_projection(
        root,
        version=str(payload.get("version") or version),
        feature=feature,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon archive status: {payload.get('version', '')}")
        typer.echo(f"operator_doc: {payload['support_surface_projection'].get('primary_operator_doc_ref', '')}")
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
            "beacon archive catalog plan",
            "beacon archive catalog apply",
            "beacon archive catalog bootstrap",
            "beacon archive catalog status",
            "beacon archive lineage",
            "beacon archive inventory",
            "beacon doctor verify-version-truth-catalog --strict",
        ],
        "skill": "beacon:beacon-archive",
        "boundary": "brainstorm remains read-only before archive; archive writes formal governance truth",
        "support_surface_projection": build_support_surface_projection(root, version=resolved_version),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon archive explain")
        typer.echo("status_model: active, superseded, archived-learnable, archived-reference-only")
        typer.echo("support_position: support-command")
        typer.echo(f"operator_doc: {payload['support_surface_projection'].get('primary_operator_doc_ref', '')}")


@catalog_app.command("plan")
def catalog_plan(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Target version for active window cutover"),
    active: str = typer.Option("", "--active", help="Comma-separated active versions (bootstrap)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Preview version-truth-catalog changes without mutating disk."""
    root = Path(project_root) if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    if not catalog_supported(resolved_version):
        raise typer.Exit(2)
    active_versions = [item.strip() for item in active.split(",") if item.strip()] if active else None
    payload = {
        "schema_version": "1.0",
        "status": "planned",
        "version": resolved_version,
        "catalog_plan": build_catalog_plan(root, active_versions=active_versions, target_version=resolved_version),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        plan = payload["catalog_plan"]
        typer.echo(f"Catalog plan: active={plan.get('active_versions')} relocations={plan.get('relocation_count')}")


@catalog_app.command("apply")
def catalog_apply(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Target version for active window cutover"),
    active: str = typer.Option("", "--active", help="Comma-separated active versions"),
    confirm: bool = typer.Option(False, "--confirm", help="Apply relocations and commit catalog MD"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Commit version-truth-catalog MD and optionally relocate version trees."""
    root = Path(project_root) if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    active_versions = [item.strip() for item in active.split(",") if item.strip()] if active else None
    plan = build_catalog_plan(root, active_versions=active_versions, target_version=resolved_version)
    payload = apply_catalog_plan(root, plan, confirm=confirm)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Catalog apply: {payload.get('status')}")


@catalog_app.command("bootstrap")
def catalog_bootstrap(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    active: str = typer.Option("", "--active", help="Comma-separated active versions"),
    confirm: bool = typer.Option(False, "--confirm", help="One-shot bootstrap relocate + catalog commit"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """One-shot bootstrap: catalog MD + relocate non-active trees + INDEX."""
    root = Path(project_root) if project_root else Path.cwd()
    active_versions = [item.strip() for item in active.split(",") if item.strip()] if active else None
    plan = build_catalog_plan(root, active_versions=active_versions)
    payload = apply_catalog_plan(root, plan, confirm=confirm)
    payload["bootstrap"] = True
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Catalog bootstrap: {payload.get('status')} relocations={plan.get('relocation_count')}")


@catalog_app.command("status")
def catalog_status_cmd(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show version-truth-catalog active/archive state."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = load_catalog_status(root)
    payload["status"] = "pass"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Catalog authoritative: {payload.get('catalog_authoritative')}")
        typer.echo(f"Active versions: {', '.join(payload.get('active_versions') or [])}")


app.add_typer(catalog_app, name="catalog")


@app.command("lineage")
def lineage(
    feature: str = typer.Argument(..., help="Feature slug"),
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    from_version: str = typer.Option("", "--from", help="Start version (inclusive)"),
    to_version: str = typer.Option("", "--to", help="End version (inclusive)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Trace feature truth evolution across active and archived version roots."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = build_archive_lineage(
        root,
        feature=feature,
        from_version=from_version,
        to_version=to_version,
    )
    payload["status"] = "pass"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Lineage {feature}: {payload.get('hop_count')} hops")


@app.command("inventory")
def inventory(
    project_root: Optional[str] = typer.Option(None, "--project-root", "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version scope (auto = active catalog set)"),
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived version roots"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Build feature × AC inventory from truth.md tables."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = build_archive_inventory(root, version=version, include_archived=include_archived)
    payload["status"] = "pass"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Inventory rows: {payload.get('row_count')} versions={payload.get('versions')}")
