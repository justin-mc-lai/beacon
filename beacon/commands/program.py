"""Program harness CLI — validate-graph, sea guard, freeze gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.program_freeze_gate import (
    build_program_freeze_gate,
    validate_program_freeze_authenticated,
    write_program_freeze_gate,
)
from beacon.utils.program_driver import program_drive_start, program_drive_status
from beacon.utils.program_graph import feature_graph_path, load_feature_graph
from beacon.utils.program_orchestrator import build_program_orchestrator_state, write_program_orchestrator_state
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(
    name="program",
    help="Program-level graph validation and freeze gate.",
    no_args_is_help=True,
)


@app.command("validate-graph")
def validate_graph_cmd(
    program: str = typer.Argument(..., help="Program slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Validate feature-graph.json required fields."""
    project_root = Path(project).resolve() if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    graph_path = feature_graph_path(project_root, resolved_version, program)
    payload, errors = load_feature_graph(graph_path)
    result = {
        "schema_version": "1.0",
        "program_slug": program,
        "version": resolved_version,
        "path": str(graph_path.relative_to(project_root)) if graph_path.exists() else str(graph_path),
        "status": "pass" if not errors else "blocked",
        "blocked": bool(errors),
        "errors": errors,
        "graph": payload,
    }
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps({"status": result["status"], "errors": errors}, ensure_ascii=False))
    if errors:
        raise typer.Exit(code=2)


@app.command("guard-sea-single-lake")
def guard_sea_single_lake_cmd(
    program: str = typer.Argument(..., help="Program slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    lake_or_ocean: str = typer.Option("海", "--lake-or-ocean", help="海 or 湖"),
    feature_graph_ack: bool = typer.Option(False, "--feature-graph-ack", help="P4 user ack recorded"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Block sea-level single-lake freeze when graph ack is missing."""
    blocked = lake_or_ocean == "海" and not feature_graph_ack
    result = {
        "schema_version": "1.0",
        "program_slug": program,
        "lake_or_ocean": lake_or_ocean,
        "feature_graph_ack": feature_graph_ack,
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": "sea_single_lake_without_graph_ack" if blocked else "",
    }
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps({"blocked": blocked}, ensure_ascii=False))
    if blocked:
        raise typer.Exit(code=2)


@app.command("freeze")
def freeze_cmd(
    program: str = typer.Argument(..., help="Program slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    lake_or_ocean: str = typer.Option("海", "--lake-or-ocean", help="海 or 湖"),
    feature_graph_ack: bool = typer.Option(True, "--feature-graph-ack/--no-feature-graph-ack", help="P4 ack"),
    authenticated: bool = typer.Option(
        True,
        "--authenticated/--status-only",
        help="Require hash-authenticated promotion receipts (default true; status-only is fail-closed for v1.6.11+)",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Run program freeze gate and write program-truth-freeze.json."""
    project_root = Path(project).resolve() if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    if authenticated:
        gate = validate_program_freeze_authenticated(
            project_root,
            version=resolved_version,
            program_slug=program,
        )
        # still honor sea graph ack / parity from base builder fields
        base = build_program_freeze_gate(
            project_root,
            version=resolved_version,
            program_slug=program,
            lake_or_ocean=lake_or_ocean,
            feature_graph_ack=feature_graph_ack,
        )
        findings = list(gate.get("findings") or []) + [
            f for f in (base.get("findings") or []) if f not in (gate.get("findings") or [])
        ]
        blocked = bool(findings) or bool(gate.get("blocked")) or bool(base.get("blocked"))
        gate = {
            **gate,
            **{k: base.get(k) for k in ("lakes", "program_slug", "version") if k in base},
            "findings": findings,
            "blocked": blocked,
            "status": "blocked" if blocked else "frozen",
            "lake_or_ocean": lake_or_ocean,
            "feature_graph_ack": feature_graph_ack,
            "authenticated_mode": True,
        }
    else:
        gate = build_program_freeze_gate(
            project_root,
            version=resolved_version,
            program_slug=program,
            lake_or_ocean=lake_or_ocean,
            feature_graph_ack=feature_graph_ack,
        )
        gate["authenticated_mode"] = False
        gate["reason_code"] = gate.get("reason_code") or "status_only_program_freeze"
        # v1.6.11+ refuse status-only soft path
        try:
            major, minor, patch = resolved_version.lstrip("v").split(".")
            ver_tuple = (int(major), int(minor), int(patch))
        except Exception:  # noqa: BLE001
            ver_tuple = (0, 0, 0)
        if ver_tuple >= (1, 6, 11):
            gate = {
                **gate,
                "blocked": True,
                "status": "blocked",
                "reason_code": "status_only_program_freeze_forbidden",
                "findings": list(gate.get("findings") or [])
                + [{"kind": "authenticated_freeze", "code": "status_only_program_freeze_forbidden"}],
            }
    out_path = write_program_freeze_gate(project_root, gate)
    gate["path"] = str(out_path.relative_to(project_root))
    if json_output:
        typer.echo(json.dumps(gate, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps({"status": gate["status"], "blocked": gate["blocked"]}, ensure_ascii=False))
    if gate["blocked"]:
        raise typer.Exit(code=2)


@app.command("orchestrate")
def orchestrate_cmd(
    program: str = typer.Argument(..., help="Program slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    write_state: bool = typer.Option(True, "--write-state/--status-only", help="Persist orchestrator fields into program-run-state.json"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Compute program-level phased-lake progress and next deterministic action."""
    project_root = Path(project).resolve() if project else Path.cwd()
    payload = build_program_orchestrator_state(project_root, version=version, program_slug=program)
    if write_state and not payload.get("errors"):
        out_path = write_program_orchestrator_state(project_root, payload)
        payload["program_run_state_path"] = str(out_path.relative_to(project_root))
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps({
            "status": payload.get("status"),
            "current_lake": payload.get("current_lake"),
            "current_stage": payload.get("current_stage"),
            "next_lake": payload.get("next_lake"),
            "resume_action": payload.get("resume_action"),
        }, ensure_ascii=False))
    if payload.get("blocked"):
        raise typer.Exit(code=2)


@app.command("drive")
def drive_cmd(
    program: str = typer.Argument(..., help="Program slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    status_only: bool = typer.Option(False, "--status-only", help="Show drive status without dispatching"),
    max_turns: Optional[int] = typer.Option(None, "--max-turns", help="Max drive turns this run"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Drive program lakes: dispatch next lake-stage to the host agent until a stop condition.

    Release is never dispatched (human gate). Stops emit reason_code + resume_action.
    """
    project_root = Path(project).resolve() if project else Path.cwd()
    if status_only:
        payload = program_drive_status(project_root, version=version, program_slug=program)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(json.dumps({
                "status": payload.get("state"),
                "current_lake": (payload.get("orchestrator") or {}).get("current_lake"),
                "resume_action": (payload.get("orchestrator") or {}).get("resume_action"),
            }, ensure_ascii=False))
        return
    result = program_drive_start(
        project_root,
        version=version,
        program_slug=program,
        run_loop=True,
        max_turns=max_turns,
    )
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps({
            "status": result.get("status"),
            "reason_code": result.get("reason_code"),
            "resume_action": result.get("resume_action"),
            "turn_n": (result.get("driver") or {}).get("turn_n"),
        }, ensure_ascii=False))
    if result.get("blocked"):
        raise typer.Exit(code=2)
