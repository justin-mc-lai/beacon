"""CLI: beacon task — project scheduled tasks (ledger + wake + logs + timers)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.scheduled_task import (
    create_task,
    doctor_tasks,
    install_timer,
    list_executions,
    list_tasks,
    load_task,
    read_events,
    resume_task,
    set_enabled,
    suspend_task,
    uninstall_timer,
    wake_task,
)

app = typer.Typer(
    name="task",
    help="Project scheduled tasks: ledger, wake, suspend, execution logs, opt-in OS timers.",
    no_args_is_help=True,
)


def _root(project: str) -> Path:
    return Path(project).expanduser().resolve()


def _emit(payload: dict, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        status = payload.get("status") or payload.get("state") or ""
        typer.echo(f"status: {status}")
        if payload.get("task_id"):
            typer.echo(f"task_id: {payload.get('task_id')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
        if payload.get("count") is not None:
            typer.echo(f"count: {payload.get('count')}")
        if payload.get("execution"):
            ex = payload["execution"]
            typer.echo(f"exec_id: {ex.get('exec_id')} exec_status: {ex.get('status')}")
        if payload.get("tasks"):
            for t in payload["tasks"]:
                typer.echo(
                    f"- {t.get('task_id')}  state={t.get('state')}  host={t.get('host')}  title={t.get('title')}"
                )


@app.command("create")
def task_create(
    title: str = typer.Option("", "--title", help="Task title"),
    utterance: str = typer.Option("", "--utterance", "-u", help="Agent utterance / prompt"),
    cron: str = typer.Option("", "--cron", help="Cron expr (stored; mac timer may use interval)"),
    every_sec: Optional[int] = typer.Option(None, "--every-sec", help="Interval seconds for timer"),
    tz: str = typer.Option("Asia/Shanghai", "--tz", help="Timezone name"),
    host: str = typer.Option("dry_run", "--host", help="codex|claude|bridge|none|dry_run"),
    kind: str = typer.Option("agent_prompt", "--kind", help="agent_prompt|goal_tick|cli_command"),
    version: str = typer.Option("v1.6.9", "--version", "-v"),
    goal_run_id: str = typer.Option("", "--goal-run-id"),
    cli_command: str = typer.Option("", "--cli-command"),
    on_suspended: str = typer.Option("skip_until_resume", "--on-suspended"),
    disabled: bool = typer.Option(False, "--disabled"),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = create_task(
        _root(project),
        title=title or utterance[:80],
        utterance=utterance,
        cron=cron,
        every_sec=every_sec,
        timezone_name=tz,
        host=host,
        kind=kind,
        version=version,
        goal_run_id=goal_run_id,
        enabled=not disabled,
        on_suspended=on_suspended,
        cli_command=cli_command,
    )
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("list")
def task_list(
    project: str = typer.Option(".", "--project", "-p"),
    include_disabled: bool = typer.Option(True, "--include-disabled/--active-only"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = list_tasks(_root(project), include_disabled=include_disabled)
    _emit(payload, json_output)


@app.command("get")
def task_get(
    task_id: str = typer.Argument(...),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = load_task(_root(project), task_id)
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("enable")
def task_enable(
    task_id: str = typer.Argument(...),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = set_enabled(_root(project), task_id, enabled=True)
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("disable")
def task_disable(
    task_id: str = typer.Argument(...),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = set_enabled(_root(project), task_id, enabled=False)
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("wake")
def task_wake(
    task_id: str = typer.Option("", "--task-id", help="Task id"),
    task_id_arg: Optional[str] = typer.Argument(None),
    once: bool = typer.Option(True, "--once/--no-once"),
    force: bool = typer.Option(False, "--force", help="Wake even if suspended"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Force dry_run host for this wake"),
    trigger: str = typer.Option("wake", "--trigger"),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    tid = task_id or task_id_arg or ""
    if not tid:
        _emit({"status": "blocked", "blocked": True, "reason_code": "task_id_required"}, json_output)
        raise typer.Exit(2)
    payload = wake_task(
        _root(project),
        tid,
        once=once,
        trigger=trigger,
        force=force,
        dry_run_force=dry_run,
    )
    _emit(payload, json_output)
    code = 0
    if payload.get("status") in {"failed", "blocked"}:
        code = 2
    raise typer.Exit(code)


@app.command("suspend")
def task_suspend(
    task_id: str = typer.Argument(...),
    reason: str = typer.Option("host_interrupted", "--reason"),
    resume_pack_ref: str = typer.Option("", "--resume-pack-ref"),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = suspend_task(_root(project), task_id, reason_code=reason, resume_pack_ref=resume_pack_ref)
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("resume")
def task_resume(
    task_id: str = typer.Argument(...),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = resume_task(_root(project), task_id)
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("log")
def task_log(
    task_id: str = typer.Argument(...),
    limit: int = typer.Option(50, "--limit"),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Show execution logs (UD-ST-010)."""
    payload = list_executions(_root(project), task_id, limit=limit)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"task_id: {task_id} executions: {payload.get('count')}")
        for ex in payload.get("executions") or []:
            typer.echo(
                f"- {ex.get('exec_id')}  {ex.get('status')}  {ex.get('started_at')}  reason={ex.get('reason_code')}"
            )
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("events")
def task_events(
    task_id: str = typer.Argument(...),
    limit: int = typer.Option(100, "--limit"),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = read_events(_root(project), task_id, limit=limit)
    _emit(payload if json_output else payload, json_output)
    if not json_output:
        for ev in payload.get("events") or []:
            typer.echo(f"- {ev.get('ts')}  {ev.get('event')}  {ev.get('detail')}")
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("install-timer")
def task_install_timer(
    task_id: str = typer.Argument(...),
    confirm: bool = typer.Option(False, "--confirm"),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = install_timer(_root(project), task_id, confirm=confirm)
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("uninstall-timer")
def task_uninstall_timer(
    task_id: str = typer.Argument(...),
    confirm: bool = typer.Option(False, "--confirm"),
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = uninstall_timer(_root(project), task_id, confirm=confirm)
    _emit(payload, json_output)
    raise typer.Exit(0 if not payload.get("blocked") else 2)


@app.command("doctor")
def task_doctor(
    project: str = typer.Option(".", "--project", "-p"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = doctor_tasks(_root(project))
    _emit(payload, json_output)
    raise typer.Exit(0 if payload.get("status") == "ok" else 1)
