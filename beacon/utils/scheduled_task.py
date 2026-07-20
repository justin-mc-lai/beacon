"""Project Scheduled Task ledger + wake runner + execution logs (v1.6.9 / v2.0.0).

UD-ST-001..010: project-authoritative tasks, multi-host agent, suspend/resume,
thin OS timers (opt-in), append-only execution logs. Never auto-release.
"""

from __future__ import annotations

import json
import os
import platform
import shlex
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_TASK = "scheduled-task.v1"
SCHEMA_EXEC = "scheduled-task-execution.v1"
SCHEMA_EVENT = "scheduled-task-event.v1"

VALID_STATES = frozenset(
    {
        "scheduled",
        "armed",
        "running",
        "suspended",
        "waiting_human",
        "succeeded",
        "failed",
        "disabled",
    }
)
VALID_HOSTS = frozenset({"codex", "claude", "bridge", "none", "dry_run"})
VALID_KINDS = frozenset({"agent_prompt", "goal_tick", "cli_command"})
SUSPEND_SKIP_DEFAULT = "skip_until_resume"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def tasks_root(project_root: Path | str) -> Path:
    return Path(project_root).expanduser().resolve() / ".beacon" / "tasks"


def task_dir(project_root: Path | str, task_id: str) -> Path:
    return tasks_root(project_root) / task_id


def task_json_path(project_root: Path | str, task_id: str) -> Path:
    return task_dir(project_root, task_id) / "task.json"


def events_path(project_root: Path | str, task_id: str) -> Path:
    return task_dir(project_root, task_id) / "events.jsonl"


def executions_dir(project_root: Path | str, task_id: str) -> Path:
    return task_dir(project_root, task_id) / "executions"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def append_event(
    project_root: Path | str,
    task_id: str,
    *,
    event: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "schema": SCHEMA_EVENT,
        "ts": _now_iso(),
        "task_id": task_id,
        "event": event,
        "detail": detail or {},
    }
    path = events_path(project_root, task_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def load_task(project_root: Path | str, task_id: str) -> dict[str, Any]:
    path = task_json_path(project_root, task_id)
    if not path.is_file():
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": "scheduled_task_not_found",
            "task_id": task_id,
        }
    data = _read_json(path)
    data["status"] = "ok"
    data["blocked"] = False
    return data


def save_task(project_root: Path | str, task: dict[str, Any]) -> dict[str, Any]:
    task_id = str(task.get("task_id") or "")
    if not task_id:
        raise ValueError("task_id required")
    task = dict(task)
    task["schema"] = SCHEMA_TASK
    task["audit"] = dict(task.get("audit") or {})
    task["audit"]["updated_at"] = _now_iso()
    path = task_json_path(project_root, task_id)
    # strip runtime echo fields
    for k in ("status", "blocked", "reason_code"):
        task.pop(k, None)
    _write_json(path, task)
    return task


def create_task(
    project_root: Path | str,
    *,
    title: str,
    utterance: str = "",
    cron: str = "",
    every_sec: int | None = None,
    timezone_name: str = "Asia/Shanghai",
    host: str = "dry_run",
    kind: str = "agent_prompt",
    version: str = "v1.6.9",
    goal_run_id: str = "",
    enabled: bool = True,
    on_suspended: str = SUSPEND_SKIP_DEFAULT,
    max_turns: int = 8,
    timeout_sec: int = 3600,
    cli_command: str = "",
) -> dict[str, Any]:
    host = (host or "dry_run").strip().lower()
    kind = (kind or "agent_prompt").strip().lower()
    if host not in VALID_HOSTS:
        return {"status": "blocked", "blocked": True, "reason_code": "invalid_host", "allowed": sorted(VALID_HOSTS)}
    if kind not in VALID_KINDS:
        return {"status": "blocked", "blocked": True, "reason_code": "invalid_kind", "allowed": sorted(VALID_KINDS)}
    if on_suspended not in {SUSPEND_SKIP_DEFAULT, "auto_resume_on_wake"}:
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": "invalid_on_suspended",
            "allowed": [SUSPEND_SKIP_DEFAULT, "auto_resume_on_wake"],
        }

    task_id = _new_id("st")
    now = _now_iso()
    schedule: dict[str, Any] = {
        "expr": "cron" if cron else ("every" if every_sec else "manual"),
        "cron": cron or "",
        "every_sec": every_sec,
        "timezone": timezone_name,
        "next_fire_at": "",
        "enabled": bool(enabled),
        "on_suspended": on_suspended,
    }
    task = {
        "schema": SCHEMA_TASK,
        "task_id": task_id,
        "title": title or utterance[:80] or task_id,
        "kind": kind,
        "schedule": schedule,
        "agent": {
            "host": host,
            "bridge_cmd_env": "BEACON_HOST_GOAL_BRIDGE_CMD",
            "skill_hint": "beacon-goal" if kind == "goal_tick" else "",
            "max_turns": int(max_turns),
            "timeout_sec": int(timeout_sec),
        },
        "payload": {
            "utterance": utterance,
            "goal_run_id": goal_run_id,
            "version": version,
            "worktree_policy": "admit_required" if kind == "goal_tick" else "readonly",
            "cli_command": cli_command,
        },
        "state": "scheduled" if enabled else "disabled",
        "suspend": {
            "reason_code": "",
            "resume_pack_ref": "",
            "blocked_streak": 0,
            "since": "",
        },
        "audit": {
            "created_at": now,
            "updated_at": now,
            "last_fire_at": "",
            "last_exec_id": "",
            "last_result_ref": "",
            "events_log": f".beacon/tasks/{task_id}/events.jsonl",
            "executions_dir": f".beacon/tasks/{task_id}/executions",
            "timer_installed": False,
            "timer_ref": "",
        },
    }
    save_task(project_root, task)
    append_event(project_root, task_id, event="task_created", detail={"title": task["title"], "host": host, "kind": kind})
    out = load_task(project_root, task_id)
    out["status"] = "ok"
    return out


def list_tasks(project_root: Path | str, *, include_disabled: bool = True) -> dict[str, Any]:
    root = tasks_root(project_root)
    items: list[dict[str, Any]] = []
    if root.is_dir():
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            path = child / "task.json"
            if not path.is_file():
                continue
            try:
                data = _read_json(path)
            except Exception:  # noqa: BLE001
                continue
            if not include_disabled and data.get("state") == "disabled":
                continue
            items.append(
                {
                    "task_id": data.get("task_id"),
                    "title": data.get("title"),
                    "state": data.get("state"),
                    "host": (data.get("agent") or {}).get("host"),
                    "kind": data.get("kind"),
                    "cron": (data.get("schedule") or {}).get("cron"),
                    "last_fire_at": (data.get("audit") or {}).get("last_fire_at"),
                    "last_exec_id": (data.get("audit") or {}).get("last_exec_id"),
                }
            )
    return {"status": "ok", "count": len(items), "tasks": items, "root": str(root)}


def set_enabled(project_root: Path | str, task_id: str, *, enabled: bool) -> dict[str, Any]:
    task = load_task(project_root, task_id)
    if task.get("blocked"):
        return task
    task["schedule"] = dict(task.get("schedule") or {})
    task["schedule"]["enabled"] = bool(enabled)
    task["state"] = "scheduled" if enabled else "disabled"
    save_task(project_root, task)
    append_event(project_root, task_id, event="enabled" if enabled else "disabled", detail={})
    return load_task(project_root, task_id)


def suspend_task(
    project_root: Path | str,
    task_id: str,
    *,
    reason_code: str = "host_interrupted",
    resume_pack_ref: str = "",
) -> dict[str, Any]:
    task = load_task(project_root, task_id)
    if task.get("blocked"):
        return task
    prev = task.get("state")
    task["state"] = "suspended"
    task["suspend"] = {
        "reason_code": reason_code or "host_interrupted",
        "resume_pack_ref": resume_pack_ref or (task.get("suspend") or {}).get("resume_pack_ref") or "",
        "blocked_streak": int((task.get("suspend") or {}).get("blocked_streak") or 0) + 1,
        "since": _now_iso(),
    }
    save_task(project_root, task)
    append_event(
        project_root,
        task_id,
        event="suspended",
        detail={"from": prev, "reason_code": reason_code, "resume_pack_ref": resume_pack_ref},
    )
    return load_task(project_root, task_id)


def resume_task(project_root: Path | str, task_id: str) -> dict[str, Any]:
    task = load_task(project_root, task_id)
    if task.get("blocked"):
        return task
    prev = task.get("state")
    if prev not in {"suspended", "waiting_human", "failed"}:
        # still allow re-arm
        pass
    task["state"] = "scheduled"
    sus = dict(task.get("suspend") or {})
    sus["reason_code"] = ""
    sus["since"] = ""
    task["suspend"] = sus
    save_task(project_root, task)
    append_event(project_root, task_id, event="resumed", detail={"from": prev})
    return load_task(project_root, task_id)


def _write_execution(project_root: Path | str, task_id: str, exec_row: dict[str, Any]) -> Path:
    d = executions_dir(project_root, task_id)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{exec_row['exec_id']}.json"
    _write_json(path, exec_row)
    return path


def list_executions(project_root: Path | str, task_id: str, *, limit: int = 50) -> dict[str, Any]:
    task = load_task(project_root, task_id)
    if task.get("blocked"):
        return task
    d = executions_dir(project_root, task_id)
    rows: list[dict[str, Any]] = []
    if d.is_dir():
        files = sorted(d.glob("ex-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for path in files[: max(1, limit)]:
            try:
                rows.append(_read_json(path))
            except Exception:  # noqa: BLE001
                continue
    return {
        "status": "ok",
        "task_id": task_id,
        "count": len(rows),
        "executions": rows,
        "events_log": str(events_path(project_root, task_id)),
    }


def read_events(project_root: Path | str, task_id: str, *, limit: int = 100) -> dict[str, Any]:
    task = load_task(project_root, task_id)
    if task.get("blocked"):
        return task
    path = events_path(project_root, task_id)
    rows: list[dict[str, Any]] = []
    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()
        for line in lines[-max(1, limit) :]:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return {"status": "ok", "task_id": task_id, "count": len(rows), "events": rows}


def _resolve_spawn_cmd(host: str, utterance: str, project_root: Path, task_id: str) -> tuple[list[str] | None, str]:
    """Return argv or None for dry/none; reason note."""
    if host in {"dry_run", "none"}:
        return None, "dry_run_or_none"
    if host == "bridge":
        tmpl = os.environ.get("BEACON_HOST_GOAL_BRIDGE_CMD", "").strip()
        if not tmpl:
            return None, "bridge_cmd_missing"
        # write prompt file
        prompt = task_dir(project_root, task_id) / "last_prompt.txt"
        prompt.write_text(utterance + "\n", encoding="utf-8")
        cmd = tmpl.format(
            prompt_file=str(prompt),
            run_id=task_id,
            project=str(project_root),
        )
        return shlex.split(cmd), "bridge"
    if host == "codex":
        return ["codex", "exec", utterance], "codex"
    if host == "claude":
        return ["claude", "-p", utterance], "claude"
    return None, "unknown_host"


def wake_task(
    project_root: Path | str,
    task_id: str,
    *,
    once: bool = True,
    trigger: str = "wake",
    force: bool = False,
    dry_run_force: bool = False,
) -> dict[str, Any]:
    """Fire one execution cycle. Always writes execution log (UD-ST-010)."""
    _ = once  # reserved for multi-shot loops
    root = Path(project_root).expanduser().resolve()
    task = load_task(root, task_id)
    if task.get("blocked"):
        return task

    exec_id = _new_id("ex")
    started = _now_iso()
    host = str((task.get("agent") or {}).get("host") or "dry_run")
    if dry_run_force:
        host = "dry_run"

    state = str(task.get("state") or "scheduled")
    on_sus = str((task.get("schedule") or {}).get("on_suspended") or SUSPEND_SKIP_DEFAULT)

    # skip if disabled
    if state == "disabled" or not (task.get("schedule") or {}).get("enabled", True):
        exec_row = {
            "schema": SCHEMA_EXEC,
            "exec_id": exec_id,
            "task_id": task_id,
            "started_at": started,
            "ended_at": _now_iso(),
            "trigger": trigger,
            "host": host,
            "status": "skipped",
            "reason_code": "task_disabled",
            "agent_exit_code": None,
            "stdout_ref": "",
            "resume_pack_ref": "",
            "goal_run_id": (task.get("payload") or {}).get("goal_run_id") or "",
        }
        path = _write_execution(root, task_id, exec_row)
        append_event(root, task_id, event="wake_skipped", detail={"exec_id": exec_id, "reason_code": "task_disabled"})
        return {"status": "skipped", "reason_code": "task_disabled", "execution": exec_row, "execution_path": str(path)}

    # suspended policy
    if state == "suspended" and on_sus == SUSPEND_SKIP_DEFAULT and not force:
        exec_row = {
            "schema": SCHEMA_EXEC,
            "exec_id": exec_id,
            "task_id": task_id,
            "started_at": started,
            "ended_at": _now_iso(),
            "trigger": trigger,
            "host": host,
            "status": "skipped",
            "reason_code": "suspended_skip_until_resume",
            "agent_exit_code": None,
            "stdout_ref": "",
            "resume_pack_ref": (task.get("suspend") or {}).get("resume_pack_ref") or "",
            "goal_run_id": (task.get("payload") or {}).get("goal_run_id") or "",
        }
        path = _write_execution(root, task_id, exec_row)
        append_event(
            root,
            task_id,
            event="wake_skipped",
            detail={"exec_id": exec_id, "reason_code": "suspended_skip_until_resume"},
        )
        return {
            "status": "skipped",
            "reason_code": "suspended_skip_until_resume",
            "execution": exec_row,
            "execution_path": str(path),
        }

    if state == "suspended" and on_sus == "auto_resume_on_wake":
        resume_task(root, task_id)
        task = load_task(root, task_id)

    # mark running
    task["state"] = "running"
    save_task(root, task)
    append_event(root, task_id, event="wake_started", detail={"exec_id": exec_id, "host": host, "trigger": trigger})

    utterance = str((task.get("payload") or {}).get("utterance") or task.get("title") or "")
    kind = str(task.get("kind") or "agent_prompt")
    timeout = int((task.get("agent") or {}).get("timeout_sec") or 3600)

    agent_exit: int | None = None
    stdout_text = ""
    reason_code = ""
    final_status = "succeeded"
    resume_pack_ref = ""

    try:
        if kind == "cli_command":
            cmd_s = str((task.get("payload") or {}).get("cli_command") or "").strip()
            if not cmd_s or host == "dry_run":
                stdout_text = f"[dry_run] would run cli: {cmd_s or '(empty)'}"
                agent_exit = 0
            else:
                proc = subprocess.run(
                    cmd_s,
                    shell=True,
                    cwd=str(root),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
                agent_exit = int(proc.returncode)
                stdout_text = (proc.stdout or "") + (proc.stderr or "")
                if agent_exit != 0:
                    final_status = "failed"
                    reason_code = "cli_nonzero_exit"
        elif kind == "goal_tick":
            # thin: record intent to tick goal; do not auto-release
            goal_run_id = str((task.get("payload") or {}).get("goal_run_id") or "")
            if host == "dry_run" or not goal_run_id:
                stdout_text = f"[dry_run] goal_tick goal_run_id={goal_run_id or '(none)'}"
                agent_exit = 0
            else:
                try:
                    from beacon.utils.product_goal_runtime import tick_goal_run

                    tick_payload = tick_goal_run(root, goal_run_id, execute=True)
                    stdout_text = json.dumps(tick_payload, ensure_ascii=False)[:8000]
                    agent_exit = 0 if not tick_payload.get("blocked") else 2
                    if tick_payload.get("blocked"):
                        final_status = "suspended"
                        reason_code = str(tick_payload.get("reason_code") or "goal_tick_blocked")
                except Exception as exc:  # noqa: BLE001
                    final_status = "failed"
                    reason_code = "goal_tick_error"
                    stdout_text = str(exc)
                    agent_exit = 1
        else:
            # agent_prompt
            argv, note = _resolve_spawn_cmd(host, utterance, root, task_id)
            if argv is None:
                stdout_text = f"[dry_run] host={host} note={note} utterance={utterance[:500]}"
                agent_exit = 0
                if host == "bridge" and note == "bridge_cmd_missing":
                    final_status = "failed"
                    reason_code = "bridge_cmd_missing"
                    agent_exit = 2
            else:
                try:
                    proc = subprocess.run(
                        argv,
                        cwd=str(root),
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                    agent_exit = int(proc.returncode)
                    stdout_text = (proc.stdout or "") + (proc.stderr or "")
                    if agent_exit != 0:
                        final_status = "failed"
                        reason_code = "agent_nonzero_exit"
                except FileNotFoundError:
                    final_status = "failed"
                    reason_code = "agent_binary_missing"
                    stdout_text = f"host binary missing for {host}"
                    agent_exit = 127
                except subprocess.TimeoutExpired:
                    final_status = "suspended"
                    reason_code = "agent_timeout"
                    stdout_text = "timeout"
                    agent_exit = 124
    except Exception as exc:  # noqa: BLE001
        final_status = "failed"
        reason_code = "wake_internal_error"
        stdout_text = str(exc)
        agent_exit = 1

    # persist stdout snippet
    exec_dir = executions_dir(root, task_id)
    exec_dir.mkdir(parents=True, exist_ok=True)
    log_path = exec_dir / f"{exec_id}.log"
    log_path.write_text(stdout_text[:200_000], encoding="utf-8")

    ended = _now_iso()
    exec_row = {
        "schema": SCHEMA_EXEC,
        "exec_id": exec_id,
        "task_id": task_id,
        "started_at": started,
        "ended_at": ended,
        "trigger": trigger,
        "host": host,
        "status": final_status,
        "reason_code": reason_code,
        "agent_exit_code": agent_exit,
        "stdout_ref": f".beacon/tasks/{task_id}/executions/{exec_id}.log",
        "resume_pack_ref": resume_pack_ref,
        "goal_run_id": (task.get("payload") or {}).get("goal_run_id") or "",
    }
    path = _write_execution(root, task_id, exec_row)

    # update task state
    task = load_task(root, task_id)
    task["audit"] = dict(task.get("audit") or {})
    task["audit"]["last_fire_at"] = ended
    task["audit"]["last_exec_id"] = exec_id
    task["audit"]["last_result_ref"] = f".beacon/tasks/{task_id}/executions/{exec_id}.json"

    if final_status == "suspended":
        task["state"] = "suspended"
        task["suspend"] = {
            "reason_code": reason_code or "suspended",
            "resume_pack_ref": resume_pack_ref,
            "blocked_streak": int((task.get("suspend") or {}).get("blocked_streak") or 0) + 1,
            "since": ended,
        }
    elif final_status == "failed":
        task["state"] = "failed"
    elif final_status == "succeeded":
        task["state"] = "scheduled"
    else:
        task["state"] = "scheduled"

    save_task(root, task)
    append_event(
        root,
        task_id,
        event="wake_finished",
        detail={
            "exec_id": exec_id,
            "status": final_status,
            "reason_code": reason_code,
            "agent_exit_code": agent_exit,
        },
    )

    return {
        "status": final_status,
        "blocked": final_status in {"failed"} and reason_code not in {""},
        "reason_code": reason_code or final_status,
        "execution": exec_row,
        "execution_path": str(path),
        "task": load_task(root, task_id),
        "never_auto_release": True,
    }


def install_timer(
    project_root: Path | str,
    task_id: str,
    *,
    confirm: bool = False,
) -> dict[str, Any]:
    task = load_task(project_root, task_id)
    if task.get("blocked"):
        return task
    if not confirm:
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": "timer_install_requires_confirm",
            "message": "Pass --confirm to install OS timer (thin wake only).",
            "planned_command": f"beacon task wake --task-id {task_id} --once --project {Path(project_root).resolve()}",
        }

    root = Path(project_root).expanduser().resolve()
    wake_cmd = f"beacon task wake --task-id {shlex.quote(task_id)} --once --project {shlex.quote(str(root))}"
    system = platform.system().lower()
    timer_ref = ""
    written: list[str] = []

    every = (task.get("schedule") or {}).get("every_sec")
    cron = str((task.get("schedule") or {}).get("cron") or "").strip()
    # default interval 3600 if only cron text (we still use StartInterval for simplicity on mac)
    interval = int(every) if every else 3600

    if system == "darwin":
        agents = Path.home() / "Library" / "LaunchAgents"
        agents.mkdir(parents=True, exist_ok=True)
        label = f"com.beacon.task.{task_id}"
        plist = agents / f"{label}.plist"
        # Minimal StartInterval wake (cron parsing left as future); still thin wake.
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{label}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>{wake_cmd}</string>
  </array>
  <key>StartInterval</key><integer>{interval}</integer>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>{root / '.beacon' / 'tasks' / task_id / 'timer.stdout.log'}</string>
  <key>StandardErrorPath</key><string>{root / '.beacon' / 'tasks' / task_id / 'timer.stderr.log'}</string>
</dict>
</plist>
"""
        plist.write_text(content, encoding="utf-8")
        written.append(str(plist))
        timer_ref = str(plist)
        try:
            subprocess.run(["launchctl", "unload", str(plist)], capture_output=True, check=False)
            subprocess.run(["launchctl", "load", str(plist)], capture_output=True, check=False)
        except Exception:  # noqa: BLE001
            pass
    else:
        # Write a crontab line helper file (does not auto-install without crontab access)
        lines_path = task_dir(root, task_id) / "crontab.line"
        # if cron empty use hourly
        cron_expr = cron or "0 * * * *"
        line = f"{cron_expr} {wake_cmd}  # beacon-task:{task_id}\n"
        lines_path.write_text(line, encoding="utf-8")
        written.append(str(lines_path))
        timer_ref = str(lines_path)

    task = load_task(root, task_id)
    task["audit"] = dict(task.get("audit") or {})
    task["audit"]["timer_installed"] = True
    task["audit"]["timer_ref"] = timer_ref
    save_task(root, task)
    append_event(root, task_id, event="timer_installed", detail={"timer_ref": timer_ref, "written": written, "cron": cron})
    return {
        "status": "ok",
        "task_id": task_id,
        "timer_ref": timer_ref,
        "written": written,
        "wake_command": wake_cmd,
        "note": "OS timer is thin wake only; ledger remains authoritative",
    }


def uninstall_timer(
    project_root: Path | str,
    task_id: str,
    *,
    confirm: bool = False,
) -> dict[str, Any]:
    task = load_task(project_root, task_id)
    if task.get("blocked"):
        return task
    if not confirm:
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": "timer_uninstall_requires_confirm",
        }
    root = Path(project_root).expanduser().resolve()
    removed: list[str] = []
    timer_ref = str((task.get("audit") or {}).get("timer_ref") or "")
    if timer_ref and Path(timer_ref).is_file():
        p = Path(timer_ref)
        if p.suffix == ".plist":
            try:
                subprocess.run(["launchctl", "unload", str(p)], capture_output=True, check=False)
            except Exception:  # noqa: BLE001
                pass
        p.unlink(missing_ok=True)
        removed.append(str(p))
    # also try standard label path
    label_plist = Path.home() / "Library" / "LaunchAgents" / f"com.beacon.task.{task_id}.plist"
    if label_plist.is_file():
        try:
            subprocess.run(["launchctl", "unload", str(label_plist)], capture_output=True, check=False)
        except Exception:  # noqa: BLE001
            pass
        label_plist.unlink(missing_ok=True)
        removed.append(str(label_plist))

    task = load_task(root, task_id)
    task["audit"] = dict(task.get("audit") or {})
    task["audit"]["timer_installed"] = False
    task["audit"]["timer_ref"] = ""
    save_task(root, task)
    append_event(root, task_id, event="timer_uninstalled", detail={"removed": removed})
    return {"status": "ok", "task_id": task_id, "removed": removed, "ledger_intact": True}


def doctor_tasks(project_root: Path | str) -> dict[str, Any]:
    listed = list_tasks(project_root)
    drift: list[dict[str, Any]] = []
    for item in listed.get("tasks") or []:
        tid = str(item.get("task_id"))
        task = load_task(project_root, tid)
        installed = bool((task.get("audit") or {}).get("timer_installed"))
        ref = str((task.get("audit") or {}).get("timer_ref") or "")
        exists = bool(ref and Path(ref).exists())
        if installed and not exists:
            drift.append({"task_id": tid, "issue": "timer_ref_missing", "ref": ref})
        if exists and not installed:
            drift.append({"task_id": tid, "issue": "timer_file_without_flag", "ref": ref})
    return {
        "status": "ok" if not drift else "drift",
        "task_count": listed.get("count"),
        "drift": drift,
        "never_auto_release": True,
        "public_entry": "beacon task",
    }
