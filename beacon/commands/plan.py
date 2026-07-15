"""Program plan CLI — public entry `beacon plan start`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.program_plan_runtime import build_plan_start_payload, emit_plan_start_json
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(
    name="plan",
    help="Version-level program plan harness (umbrella entry).",
    no_args_is_help=True,
)


@app.command("start")
def start_cmd(
    utterance: str = typer.Argument(..., help="Program utterance (sea-level intent)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    program: str = typer.Option("", "--program", help="Explicit program slug"),
    mode: str = typer.Option("auto-detect", "--mode", help="auto|interactive|auto-detect"),
    source: str = typer.Option("", "--source", help="Source URL for auto inventory"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Bootstrap program artifacts and classify plan_mode (does not write package truth)."""
    project_root = Path(project).resolve() if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = build_plan_start_payload(
        project_root,
        version=resolved_version,
        utterance=utterance,
        program_slug=program,
        mode_flag=mode,
        source=source,
    )
    if json_output:
        typer.echo(emit_plan_start_json(payload))
        gov_check = payload.get("governance_precheck") or {}
        if gov_check.get("blocked"):
            raise typer.Exit(code=2)
        return
    gov_check = payload.get("governance_precheck") or {}
    output: dict[str, object] = {
        "program_slug": payload.get("program_slug"),
        "plan_mode": payload.get("plan_mode"),
        "delegate_skill": payload.get("delegate_skill"),
    }
    if gov_check:
        output["governance_precheck"] = gov_check.get("status")
    typer.echo(json.dumps(output, ensure_ascii=False))
    if gov_check.get("blocked"):
        typer.echo(
            f"\u2717 governance precheck blocked: {gov_check.get('reason_code')} — {gov_check.get('recommendation')}",
            err=True,
        )
        raise typer.Exit(code=2)
