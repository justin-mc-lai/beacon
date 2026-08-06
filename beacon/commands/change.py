"""Beacon change command - public router for frozen-truth change loops."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.commands.reopen import _reopen_impl
from beacon.utils.change_refreeze import run_change_refreeze_chain
from beacon.utils.help_support import build_help_payload
from beacon.utils.change_surface import build_change_command
from beacon.utils.program_change_intent import (
    append_change_intent_log,
    require_promotion_diff_before_refreeze,
    rerun_program_freeze_after_structural_refreeze,
)
from beacon.utils.versioning import resolve_target_version


def _change_payload(project_root: Path, *, version: str, feature: str, reason: str) -> dict:
    help_payload = build_help_payload(
        project_root,
        version=version,
        feature=feature,
        change_intent=reason,
    )
    change_loop = help_payload.get("change_loop", {}) if isinstance(help_payload.get("change_loop"), dict) else {}
    next_step = help_payload.get("next_step", {}) if isinstance(help_payload.get("next_step"), dict) else {}
    recommended_command = str(change_loop.get("route") or next_step.get("command") or "").strip()
    if not recommended_command:
        recommended_command = build_change_command(
            feature=feature,
            project_root=project_root,
            version=version,
            reason=reason,
        )
    return {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "status": "change_loop_ready",
        "reason": reason,
        "route": "reopen -> revise -> freeze",
        "recommended_command": recommended_command,
        "change_loop": change_loop,
        "next_step": next_step,
    }


def _change_impl(
    feature: str,
    project: Optional[str],
    version: str,
    reason: str,
    reopen_now: bool,
    refreeze_chain: bool,
    program: Optional[str],
    json_output: bool,
) -> int:
    project_root = (Path(project) if project else Path.cwd()).expanduser().resolve()
    try:
        resolved_version = resolve_target_version(project_root, version)
        from beacon.utils.version_defaults import guard_external_docs_axis

        guard_external_docs_axis(project_root, resolved_version, command_name="beacon change")
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        return 2
    change_intent_log: dict[str, str] = {}
    if program:
        log_path = append_change_intent_log(
            project_root,
            version=resolved_version,
            program_slug=program,
            utterance=reason,
            affected_slugs=[feature],
        )
        change_intent_log = {"path": str(log_path.relative_to(project_root))}
    if refreeze_chain and program:
        promo_gate = require_promotion_diff_before_refreeze(
            project_root,
            version=resolved_version,
            program_slug=program,
        )
        if promo_gate.get("blocked"):
            payload = {
                "schema_version": "1.0",
                "status": "blocked",
                "reason_code": promo_gate.get("reason_code"),
                "feature": feature,
                "program": program,
                "version": resolved_version,
                "recommended_command": promo_gate.get("recommended_command"),
                "change_intent_log": change_intent_log,
            }
            if json_output:
                typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                typer.echo(f"Change blocked: {payload.get('reason_code')}")
                typer.echo(f"Next route: {payload.get('recommended_command')}")
            return 2
    if refreeze_chain:
        payload = run_change_refreeze_chain(
            project_root,
            version=resolved_version,
            feature=feature,
            reason=reason,
        )
        if program and payload.get("refreeze_status") == "complete":
            payload["program_freeze_rerun"] = rerun_program_freeze_after_structural_refreeze(
                project_root,
                version=resolved_version,
                program_slug=program,
            )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Change refreeze {payload.get('refreeze_status')}: {feature}")
            if payload.get("blocked_reason"):
                typer.echo(f"Blocked reason: {payload.get('blocked_reason')}")
            typer.echo(f"Next route: {(payload.get('next_route') or {}).get('command', '')}")
        return 0 if payload.get("refreeze_status") == "complete" else 2
    if reopen_now:
        return _reopen_impl(feature, str(project_root), resolved_version, reason, json_output)
    payload = _change_payload(project_root, version=resolved_version, feature=feature, reason=reason)
    if change_intent_log:
        payload["change_intent_log"] = change_intent_log
        payload["next_route_hint"] = "beacon-pln-review (promotion_diff) before refreeze"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Change loop ready for {feature}")
        typer.echo(f"Next route: {payload['recommended_command']}")
    return 0


def change_entry(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    reason: str = typer.Option("change-request", "--reason", help="Reason for reopening truth"),
    program: Optional[str] = typer.Option(None, "--program", help="Program slug for change-intent-log.jsonl append"),
    reopen_now: bool = typer.Option(False, "--reopen-now", help="Immediately reopen the active revision"),
    refreeze_chain: bool = typer.Option(False, "--refreeze-chain", help="Run governed change -> PRD -> story -> test-case -> clarity -> freeze closure"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Prepare the change loop or optionally reopen immediately."""
    raise typer.Exit(
        code=_change_impl(feature, project, version, reason, reopen_now, refreeze_chain, program, json_output)
    )
