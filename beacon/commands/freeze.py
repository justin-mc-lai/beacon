"""Beacon freeze command - formalize frozen revision baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.feature_package import sync_truth_frontmatter_status, validate_feature_package
from beacon.utils.git_alignment import check_truth_authoring_branch
from beacon.utils.material_sync import sync_change_loop_requirement_package
from beacon.utils.requirement_clarity import (
    write_requirement_clarity_report,
    write_requirement_clarity_writeback,
)
from beacon.utils.revision_delta import materialize_revision_delta
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.story_state import freeze_story_state, feature_slug
from beacon.utils.truth_integrity import build_truth_integrity_gate
from beacon.utils.truth_review_gate import build_truth_review_gate_payload
from beacon.utils.truth_map import feature_package_authoritative, feature_package_ready, rebuild_machine_json
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="freeze", help="Freeze current feature revision as implementation baseline", invoke_without_command=True, no_args_is_help=False)


def _freeze_impl(feature: str, project: Optional[str], version: str, json_output: bool) -> int:
    project_root = (Path(project) if project else Path.cwd()).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    branch_guard = check_truth_authoring_branch(
        project_root,
        version=resolved_version,
        operation="freeze",
    )
    if bool(branch_guard.get("blocked")):
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(branch_guard.get("reason_code") or "truth_canonical_branch_mismatch"),
            "truth_authoring_branch": branch_guard,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(
                "Beacon freeze blocked: requirement truth must be authored on "
                f"{branch_guard.get('truth_canonical', 'main')}"
            )
        return 2
    integrity_gate = build_truth_integrity_gate(
        project_root,
        version=resolved_version,
        feature=feature,
        mode="block",
    )
    clarity_gate = integrity_gate.get("requirement_clarity") if isinstance(integrity_gate.get("requirement_clarity"), dict) else {}
    clarity_report = write_requirement_clarity_report(
        project_root,
        version=resolved_version,
        feature=feature,
        payload=clarity_gate,
    )
    clarity_writeback = write_requirement_clarity_writeback(
        project_root,
        version=resolved_version,
        feature=feature,
        gate_payload=clarity_gate,
        report=clarity_report,
        source="freeze",
    )
    if bool(integrity_gate.get("blocked")):
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(integrity_gate.get("reason_code") or "truth_integrity_blocked"),
            "truth_integrity_gate": integrity_gate,
            "requirement_clarity_gate": clarity_gate,
            "requirement_clarity_report": clarity_report,
            "requirement_clarity_writeback": clarity_writeback,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon freeze blocked: truth integrity gate failed")
        return 2
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
            "truth_integrity_gate": integrity_gate,
            "requirement_clarity_gate": clarity_gate,
            "requirement_clarity_report": clarity_report,
            "requirement_clarity_writeback": clarity_writeback,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon freeze blocked: machine requirement package sync failed")
        return 2
    package_gate_enabled = feature_package_authoritative(resolved_version) or feature_package_ready(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    post_validation = {
        "status": "skipped",
        "blocked": False,
        "reason_code": "",
        "skip_reason": "legacy_split_truth",
        "diagnostics": [],
    }
    if package_gate_enabled:
        post_validation = validate_feature_package(
            project_root,
            version=resolved_version,
            feature=feature,
            write_report=True,
        )
    if str(post_validation.get("status") or "").lower() == "blocked":
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(post_validation.get("reason_code") or "feature_package_validation_failed"),
            "truth_integrity_gate": integrity_gate,
            "feature_package_validation": post_validation,
            "requirement_clarity_gate": clarity_gate,
            "requirement_clarity_report": clarity_report,
            "requirement_clarity_writeback": clarity_writeback,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon freeze blocked: feature package validation failed")
        return 2

    truth_review = build_truth_review_gate_payload(
        project_root,
        version=resolved_version,
        feature=feature,
        write_report=True,
    )
    if bool(truth_review.get("blocked")) or not bool(truth_review.get("review_gate_pass", True)):
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(truth_review.get("reason_code") or "truth_review_gate_failed"),
            "truth_review_gate": truth_review,
            "truth_integrity_gate": integrity_gate,
            "feature_package_validation": post_validation,
            "requirement_clarity_gate": clarity_gate,
            "requirement_clarity_report": clarity_report,
            "requirement_clarity_writeback": clarity_writeback,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon freeze blocked: truth review gate failed")
            for f in (truth_review.get("findings") or [])[:12]:
                if isinstance(f, dict):
                    typer.echo(f"  - [{f.get('kind')}] {f.get('text')}")
        return 2

    revision = freeze_revision_state(project_root, version=resolved_version, feature=feature)
    freeze_story_state(project_root, version=resolved_version, feature=feature)
    truth_frontmatter_sync = (
        sync_truth_frontmatter_status(
            project_root,
            version=resolved_version,
            feature=feature,
            status="frozen",
        )
        if package_gate_enabled
        else {"updated": False, "reason": "legacy_split_truth"}
    )
    # v1.6.10+: freeze-time tasks ledger derived from AC (implement evidence spine)
    tasks_sync: dict = {"updated": False}
    try:
        from beacon.utils.versioning import normalize_version as _nv

        def _sv(v: str):
            n = (_nv(v) or "v0.0.0").lstrip("v").split(".")
            return int(n[0]), int(n[1]), int(n[2] if len(n) > 2 else 0)

        if package_gate_enabled:
            from beacon.utils.feature_package import package_paths, render_tasks_package

            tpath = package_paths(project_root, version=resolved_version, feature=feature)["tasks"]
            content = render_tasks_package(project_root, version=resolved_version, feature=feature)
            tpath.parent.mkdir(parents=True, exist_ok=True)
            tpath.write_text(content, encoding="utf-8")
            tasks_sync = {"updated": True, "path": str(tpath.relative_to(project_root)), "source": "acceptance_criteria"}
    except Exception as _tasks_exc:  # noqa: BLE001
        tasks_sync = {"updated": False, "error": str(_tasks_exc)}
    revision_delta = materialize_revision_delta(project_root, version=resolved_version, feature=feature)
    # Rebuild machine json so .machine source hashes stay in sync with frozen
    # truth. Without this, any post-freeze truth edit leaves .machine stale and
    # truth-map verify reports machine_json_source_hash_stale.
    machine_rebuild = (
        rebuild_machine_json(project_root, version=resolved_version, feature=feature)
        if package_gate_enabled
        else {"status": "skipped", "reason": "legacy_split_truth", "written": []}
    )
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": resolved_version,
        "revision_id": revision.get("revision_id", ""),
        "status": "frozen",
        "baseline_hash": revision.get("baseline_hash", ""),
        "story_path": str((project_root / "docs" / "beacon" / resolved_version / ".machine" / "user-story" / f"{feature_slug(feature)}.json").relative_to(project_root)),
        "requirement_package": requirement_package,
        "revision_delta": revision_delta,
        "machine_rebuild": machine_rebuild,
        "truth_frontmatter_sync": truth_frontmatter_sync,
        "truth_integrity_gate": integrity_gate,
        "requirement_clarity_gate": clarity_gate,
        "requirement_clarity_report": clarity_report,
        "requirement_clarity_writeback": clarity_writeback,
        "truth_review_gate": truth_review,
        "tasks_sync": tasks_sync,
    }
    # v1.6.10 lifecycle agent_trace
    try:
        from beacon.utils.agent_trace import record_lifecycle_stage_trace

        payload["agent_trace"] = record_lifecycle_stage_trace(
            project_root,
            harness="freeze",
            stage="freeze",
            feature_slug=feature,
            event_type="output",
            summary=f"freeze ok revision={payload.get('revision_id')}",
            reason_code="",
            payload={
                "status": "frozen",
                "revision_id": payload.get("revision_id"),
                "baseline_hash": payload.get("baseline_hash"),
                "version": resolved_version,
            },
            fail_closed=False,
        )
    except Exception as _trc_exc:  # noqa: BLE001
        payload["agent_trace"] = {"status": "blocked", "reason_code": "agent_trace_append_failed", "error": str(_trc_exc)}

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
