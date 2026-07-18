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
    consume_discovery_queue,
    delegate_implement_to_ralph,
    enrich_goal_status,
    goal_checkpoint,
    goal_driver_run_loop,
    goal_driver_start,
    goal_driver_status,
    goal_driver_stop,
    goal_heartbeat,
    goal_memory_reindex,
    goal_memory_search,
    goal_resume_pack,
    goal_supervise_attach,
    goal_supervise_detach,
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
    longrun: bool = typer.Option(
        False,
        "--longrun",
        help="One-shot longrun: attach supervisor + start AgentDriver for this run (default run stays idle)",
    ),
    driver_start_flag: bool = typer.Option(
        True,
        "--driver-start/--no-driver-start",
        help="With --longrun, start driver (default true)",
    ),
    driver_loop: bool = typer.Option(
        False,
        "--driver-loop",
        help="With --longrun, run driver loop in-process (uses BEACON_HOST_GOAL_BRIDGE_CMD)",
    ),
    max_driver_turns: Optional[int] = typer.Option(
        None,
        "--max-driver-turns",
        help="Override max agent turns for longrun driver",
    ),
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
        longrun=longrun,
        driver_start=driver_start_flag,
        driver_run_loop=driver_loop,
        max_driver_turns=max_driver_turns,
    )
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("status")
def goal_status(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    root = _root(project)
    payload = load_goal_run(root, run_id)
    payload = enrich_goal_status(root, payload)
    payload["entry_contract"] = public_entry_contract()
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("status") not in {"blocked"} or payload.get("reason_code") != "product_goal_run_not_found" else 2)


@app.command("tick")
def goal_tick(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    note: str = typer.Option("", "--note"),
    execute: bool = typer.Option(False, "--execute", help="Dispatch stage workers (ralph/qa plan); never auto-release"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = tick_goal_run(_root(project), run_id, note=note, execute=execute)
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


@app.command("consume-queue")
def goal_consume_queue(
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    version: str = typer.Option("auto", "--version", "-v"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Consume one support discovery queue item into a goal run."""
    payload = consume_discovery_queue(_root(project), version=version)
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("status") in {"running", "pass", "awaiting_verifier", "completed"} or payload.get("run_id") else (0 if payload.get("status") == "empty" else 2))


@app.command("delegate-ralph")
def goal_delegate_ralph(
    run_id: str = typer.Option(..., "--run-id"),
    feature: str = typer.Option("", "--feature", "-f"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Delegate implement stage to Ralph (implement-only; not product complete)."""
    payload = delegate_implement_to_ralph(_root(project), run_id, feature=feature)
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("implement_delegate") == "ralph" else 2)


@app.command("design-stage")
def design_stage(
    run_id: str = typer.Option(..., "--run-id", help="Product goal run id"),
    project: str = typer.Option(".", "--project", "-p", help="Project root"),
    force: bool = typer.Option(False, "--force", help="Overwrite DESIGN.md"),
    surface: str = typer.Option("auto", "--surface"),
    company_template: str = typer.Option("auto", "--company-template"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Run UX design stage for a goal run (baseline + company template + lint)."""
    from beacon.utils.product_goal_runtime import run_design_stage_for_goal
    from pathlib import Path
    import json as _json

    payload = run_design_stage_for_goal(
        Path(project),
        run_id,
        force=force,
        surface=surface,
        company_template=company_template,
    )
    if json_output:
        typer.echo(_json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"status: {payload.get('status')}")
        ds = payload.get("design_stage") if isinstance(payload.get("design_stage"), dict) else {}
        typer.echo(f"design: {ds.get('baseline', {}).get('status')} lint: {ds.get('lint', {}).get('status')}")
    if payload.get("blocked"):
        raise typer.Exit(2)



@app.command("supervise")
def goal_supervise(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    interval_sec: int = typer.Option(120, "--interval-sec", help="Heartbeat interval seconds (default 120, min 30)"),
    once: bool = typer.Option(False, "--once", help="Single poll then return (no system daemon)"),
    detach: bool = typer.Option(False, "--detach", help="Detach supervisor session"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Opt-in durable supervisor. Not auto-started by `goal run`."""
    root = _root(project)
    if detach:
        payload = goal_supervise_detach(root, run_id)
    else:
        payload = goal_supervise_attach(root, run_id, interval_sec=interval_sec, once=once)
    _emit(payload if isinstance(payload, dict) else {"status": "ok"}, json_output)
    raise typer.Exit(0 if payload.get("status") in {"active", "stopped", "ok"} or payload.get("supervisor") else 2)


@app.command("heartbeat")
def goal_heartbeat_cmd(
    run_id: str = typer.Option(..., "--run-id"),
    summary: str = typer.Option(..., "--summary"),
    substep: str = typer.Option("", "--substep"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = goal_heartbeat(_root(project), run_id, summary=summary, substep=substep)
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("run_id") else 2)


@app.command("checkpoint")
def goal_checkpoint_cmd(
    run_id: str = typer.Option(..., "--run-id"),
    next_action: str = typer.Option(..., "--next-action"),
    substep: str = typer.Option("", "--substep"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = goal_checkpoint(_root(project), run_id, next_action=next_action, substep=substep)
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("run_id") else 2)


@app.command("resume-pack")
def goal_resume_pack_cmd(
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(True, "--json/--no-json"),
) -> None:
    """Emit digest-only resume pack (no full chat/jsonl)."""
    payload = goal_resume_pack(_root(project), run_id)
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("status") == "ok" else 2)


@app.command("memory")
def goal_memory_cmd(
    action: str = typer.Argument(..., help="reindex | search"),
    run_id: str = typer.Option(..., "--run-id"),
    query: str = typer.Option("", "--query", "-q"),
    limit: int = typer.Option(10, "--limit"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """P2 sqlite FTS memory (support_advisory only; cannot complete goal)."""
    root = _root(project)
    act = action.strip().lower()
    if act == "reindex":
        payload = goal_memory_reindex(root, run_id)
    elif act == "search":
        payload = goal_memory_search(root, run_id, query, limit=limit)
    else:
        payload = {"status": "blocked", "reason_code": "invalid_memory_action", "allowed": ["reindex", "search"]}
        _emit(payload, json_output)
        raise typer.Exit(2)
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("status") in {"ok", "empty"} else 2)


@app.command("driver")
def goal_driver(
    action: str = typer.Argument(..., help="start | status | stop | loop"),
    run_id: str = typer.Option(..., "--run-id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p"),
    run_loop: bool = typer.Option(False, "--loop", help="For start: run turns in-process"),
    max_turns: Optional[int] = typer.Option(None, "--max-turns"),
    turn_timeout_sec: Optional[int] = typer.Option(None, "--turn-timeout-sec"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """AgentDriver control: auto requeue host turns via resume-pack (never auto-release)."""
    root = _root(project)
    act = action.strip().lower()
    if act == "start":
        payload = goal_driver_start(
            root,
            run_id,
            run_loop=run_loop,
            max_turns=max_turns,
            turn_timeout_sec=turn_timeout_sec,
        )
    elif act == "status":
        payload = goal_driver_status(root, run_id)
    elif act == "stop":
        payload = goal_driver_stop(root, run_id)
    elif act == "loop":
        payload = goal_driver_run_loop(root, run_id, max_loop_turns=max_turns)
    else:
        payload = {
            "status": "blocked",
            "reason_code": "invalid_driver_action",
            "allowed": ["start", "status", "stop", "loop"],
        }
        _emit(payload, json_output)
        raise typer.Exit(2)
    _emit(payload if isinstance(payload, dict) else {"status": "ok"}, json_output)
    raise typer.Exit(0 if payload.get("status") not in {"blocked"} or payload.get("driver") else 2)

