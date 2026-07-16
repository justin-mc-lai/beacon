"""Public Product Goal facade CLI (v1.6.7) — single entry for delivery orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.product_goal_runtime import (
    PUBLIC_ENTRY,
    attach_verifier,
    complete_goal_run,
    load_goal_run,
    public_entry_contract,
    record_blocker,
    run_goal_facade,
    tick_goal_run,
)

app = typer.Typer(
    name="goal",
    help="Product Goal facade: one utterance → plan/truth/implement/qa until verifier complete.",
    no_args_is_help=True,
)


def _root(project: Optional[str]) -> Path:
    return Path(project).expanduser().resolve() if project else Path.cwd().resolve()


def _emit(payload: dict, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon goal: {payload.get('status')}")
        if payload.get("run_id"):
            typer.echo(f"run_id: {payload.get('run_id')}")
        if payload.get("current_stage"):
            typer.echo(f"stage: {payload.get('current_stage')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
        if payload.get("state_path"):
            typer.echo(f"state: {payload.get('state_path')}")


@app.command("run")
def goal_run(
    utterance: str = typer.Argument(..., help="One-sentence product goal"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    version: str = typer.Option("auto", "--version", "-v"),
    feature: str = typer.Option("", "--feature", "-f"),
    lake: list[str] = typer.Option([], "--lake", help="Optional lake slugs for parallel pool"),
    worktree_mode: str = typer.Option(
        "",
        "--worktree-mode",
        help="single_worktree | main_star_satellite_pool (auto if empty)",
    ),
    auto_tick: bool = typer.Option(False, "--auto-tick", help="Advance plan/truth stages in facade only"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Unique public CLI entry equivalent to $beacon-goal."""
    mode = worktree_mode.strip() or None
    if mode and mode not in {"single_worktree", "main_star_satellite_pool"}:
        payload = {
            "status": "blocked",
            "blocked": True,
            "reason_code": "invalid_worktree_mode",
            "public_entry": PUBLIC_ENTRY,
        }
        _emit(payload, json_output)
        raise typer.Exit(2)
    payload = run_goal_facade(
        _root(project),
        utterance=utterance,
        version=version,
        feature=feature,
        lakes=list(lake or []),
        worktree_mode=mode,  # type: ignore[arg-type]
        auto_tick=auto_tick,
    )
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("status")
def goal_status(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = load_goal_run(_root(project), run_id)
    payload["entry_contract"] = public_entry_contract()
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("status") not in {"blocked"} or payload.get("reason_code") != "product_goal_run_not_found" else 2)


@app.command("tick")
def goal_tick(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    note: str = typer.Option("", "--note"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = tick_goal_run(_root(project), run_id, note=note)
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("resume")
def goal_resume(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = load_goal_run(_root(project), run_id)
    if payload.get("status") == "blocked" and int(payload.get("blocked_streak") or 0) < 3:
        payload["status"] = "running"
        payload["blocked"] = False
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("run_id") else 2)


@app.command("block")
def goal_block(
    run_id: str = typer.Option(..., "--run-id"),
    reason_code: str = typer.Option("manual_block", "--reason-code"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = record_blocker(_root(project), run_id, reason_code=reason_code)
    _emit(payload, json_output)
    raise typer.Exit(2 if payload.get("blocked") else 0)


@app.command("attach-verifier")
def goal_attach_verifier(
    run_id: str = typer.Option(..., "--run-id"),
    ref: list[str] = typer.Option(..., "--ref", help="Evidence ref paths (repeatable)"),
    source: str = typer.Option("beacon-eval-qa", "--source"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = attach_verifier(_root(project), run_id, refs=list(ref or []), source=source)
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("verifier", {}).get("present") else 2)


@app.command("complete")
def goal_complete(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    force: bool = typer.Option(False, "--force", help="Dev-only; still records force flag"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = complete_goal_run(_root(project), run_id, force=force)
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("status") == "completed" else 2)


@app.command("entry-contract")
def goal_entry_contract(json_output: bool = typer.Option(True, "--json/--no-json")) -> None:
    payload = public_entry_contract()
    _emit(payload, json_output)
    raise typer.Exit(0)
