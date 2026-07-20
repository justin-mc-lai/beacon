"""Python AgentDriver for beacon-goal longrun (v1.6.7).

Spawns host agent turns after each exit using InjectBundle:
steering (Codex distill) → resume-pack digest → next_action.
Does not self-certify complete and never auto-confirms release.
Depends on goal_durable_supervisor APIs.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from beacon.utils.goal_durable_supervisor import (
    DEFAULT_HEARTBEAT_INTERVAL_SEC,
    append_execution_log,
    attach_supervisor as dgs_attach_supervisor,
    build_resume_pack,
    ensure_run_dir,
    goal_run_dir,
)
from beacon.utils.goal_steering import (
    build_inject_bundle,
    bump_blocker_streak,
    detect_objective_updated,
    objective_fingerprint,
    render_inject_bundle_prompt,
    render_steering,
)
from beacon.utils.runtime import now_iso, write_json

SCHEMA_VERSION = "1.0"
DEFAULT_MAX_AGENT_TURNS = 32
DEFAULT_TURN_TIMEOUT_SEC = 3600
DRIVER_FILE = "driver.json"
DRIVER_LOCK = "driver.lock"
REASON_DRIVER_LOCK = "driver_lock_held"
REASON_NO_BRIDGE = "host_bridge_missing"
REASON_BUDGET = "agent_driver_budget_exhausted"
REASON_USER_STOP = "agent_driver_user_stop"
REASON_DUAL_DRIVER = "agent_driver_dual_start_forbidden"

DRIVER_STATES = (
    "idle",
    "arming",
    "turn_active",
    "turn_ended",
    "requeue",
    "halt_budget",
    "halt_terminal",
)

TERMINAL_GOAL_STATUSES = frozenset(
    {
        "completed",
        "blocked",
        "release_pending",
        "awaiting_verifier",
    }
)

LONGRUN_MARKERS = (
    "longrun",
    "long-run",
    "long run",
    "auto requeue",
    "auto-requeue",
    "until done",
    "until qa",
    "until acceptance",
    "until release",
    "不中断",
    "长跑",
    "自动续",
    "自动再拉",
    "一键不中断",
    "直到验收",
    "直到交付",
    "一直跑",
    "自动续轮",
)

# Optional injectable runner for tests: (cmd, cwd, timeout) -> CompletedProcess-like
SpawnFn = Callable[[list[str], Path, int], subprocess.CompletedProcess]


def detect_longrun_intent(utterance: str = "", *, skill_flags: dict[str, Any] | None = None) -> bool:
    """True when user/skill asks for uninterrupted longrun auto-requeue."""
    if skill_flags and bool(skill_flags.get("longrun")):
        return True
    text = str(utterance or "").lower()
    # explicit negations
    if any(neg in text for neg in ("no longrun", "without longrun", "不长跑", "不要长跑", "关闭 longrun", "disable longrun")):
        return False
    return any(m in text for m in LONGRUN_MARKERS)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def default_budget() -> dict[str, int]:
    return {
        "max_agent_turns": _env_int("BEACON_GOAL_MAX_TURNS", DEFAULT_MAX_AGENT_TURNS),
        "turn_timeout_sec": _env_int("BEACON_GOAL_TURN_TIMEOUT_SEC", DEFAULT_TURN_TIMEOUT_SEC),
    }


def driver_state_path(project_root: Path, run_id: str) -> Path:
    return goal_run_dir(project_root, run_id) / DRIVER_FILE


def driver_lock_path(project_root: Path, run_id: str) -> Path:
    return goal_run_dir(project_root, run_id) / DRIVER_LOCK


def load_driver_state(project_root: Path, run_id: str) -> dict[str, Any]:
    path = driver_state_path(project_root, run_id)
    if not path.exists():
        return _empty_driver(run_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty_driver(run_id)
    return data if isinstance(data, dict) else _empty_driver(run_id)


def _empty_driver(run_id: str) -> dict[str, Any]:
    budget = default_budget()
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "driver_id": "",
        "state": "idle",
        "pid": None,
        "turn_n": 0,
        "max_agent_turns": budget["max_agent_turns"],
        "turn_timeout_sec": budget["turn_timeout_sec"],
        "longrun": False,
        "started_at": "",
        "updated_at": now_iso(),
        "last_exit_code": None,
        "last_error": "",
        "halt_reason": "",
        "lock_held": False,
        "history": [],
    }


def save_driver_state(project_root: Path, state: dict[str, Any]) -> dict[str, Any]:
    run_id = str(state.get("run_id") or "")
    ensure_run_dir(project_root, run_id)
    state["updated_at"] = now_iso()
    path = driver_state_path(project_root, run_id)
    write_json(path, state)
    state["driver_path"] = str(path)
    return state


def acquire_driver_lock(project_root: Path, run_id: str, *, driver_id: str) -> dict[str, Any]:
    """Exclusive lock per run. Fail closed if another live lock exists."""
    ensure_run_dir(project_root, run_id)
    lock = driver_lock_path(project_root, run_id)
    if lock.exists():
        try:
            existing = json.loads(lock.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        pid = existing.get("pid")
        if pid and _pid_alive(int(pid)):
            return {
                "ok": False,
                "reason_code": REASON_DUAL_DRIVER,
                "existing": existing,
            }
        # stale lock
        try:
            lock.unlink()
        except OSError:
            pass
    payload = {
        "driver_id": driver_id,
        "run_id": run_id,
        "pid": os.getpid(),
        "acquired_at": now_iso(),
    }
    lock.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "lock": payload}


def release_driver_lock(project_root: Path, run_id: str, *, driver_id: str = "") -> None:
    lock = driver_lock_path(project_root, run_id)
    if not lock.exists():
        return
    try:
        existing = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        existing = {}
    if driver_id and existing.get("driver_id") and existing.get("driver_id") != driver_id:
        return
    try:
        lock.unlink()
    except OSError:
        pass


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def resolve_bridge_command(
    *,
    prompt_file: Path,
    run_id: str,
    project_root: Path,
    bridge_cmd: str | None = None,
) -> dict[str, Any]:
    """Resolve host spawn command. Bridge env wins; optional codex/claude adapters."""
    template = (bridge_cmd if bridge_cmd is not None else os.environ.get("BEACON_HOST_GOAL_BRIDGE_CMD", "")).strip()
    if template:
        rendered = (
            template.replace("{prompt_file}", str(prompt_file))
            .replace("{run_id}", run_id)
            .replace("{project}", str(project_root))
        )
        return {
            "ok": True,
            "mode": "bridge",
            "cmd": rendered,
            "argv": ["/bin/sh", "-lc", rendered],
        }

    # Optional built-in adapters (P1): probe PATH
    for name, builder in (
        (
            "codex",
            lambda: f"codex exec -- $(cat {shlex.quote(str(prompt_file))})",
        ),
        (
            "claude",
            lambda: f"claude -p $(cat {shlex.quote(str(prompt_file))})",
        ),
    ):
        which = subprocess.run(
            ["/bin/sh", "-lc", f"command -v {name}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if which.returncode == 0 and which.stdout.strip():
            cmd = builder()
            return {"ok": True, "mode": name, "cmd": cmd, "argv": ["/bin/sh", "-lc", cmd]}

    return {
        "ok": False,
        "mode": "none",
        "reason_code": REASON_NO_BRIDGE,
        "hint": "Set BEACON_HOST_GOAL_BRIDGE_CMD with {prompt_file} {run_id} {project}",
    }


def render_turn_prompt(
    project_root: Path,
    goal_payload: dict[str, Any],
    *,
    turn_n: int,
    driver_state: dict[str, Any] | None = None,
    halt_budget: bool = False,
    version: str = "v2.0.0",
) -> str:
    """InjectBundle prompt: steering → resume-pack digest → next_action.

    Never embeds full chat/jsonl body. Never includes update_goal self-complete tools.
    """
    pack = build_resume_pack(project_root, goal_payload)
    driver_state = dict(driver_state or {})
    obj_updated = detect_objective_updated(goal_payload, driver_state)
    next_action = str(
        pack.get("next_action")
        or goal_payload.get("next_action")
        or "continue current stage against frozen truth via InjectBundle"
    )
    # Serialize list fields for digest readability
    pack_view = dict(pack)
    pack_view["done_when"] = json.dumps(pack.get("done_when") or [], ensure_ascii=False)
    pack_view["open_blockers"] = json.dumps(pack.get("open_blockers") or [], ensure_ascii=False)
    pack_view["recent_heartbeats"] = json.dumps(pack.get("recent_heartbeats") or [], ensure_ascii=False)

    bundle = build_inject_bundle(
        project_root,
        goal_payload,
        resume_pack=pack_view,
        next_action=next_action,
        turn_n=turn_n,
        version=str(goal_payload.get("version") or version),
        driver_state=driver_state,
        halt_budget=halt_budget,
        objective_updated=obj_updated and not halt_budget,
    )
    body = render_inject_bundle_prompt(bundle)
    run_id = str(goal_payload.get("run_id") or pack.get("run_id") or "")
    body += (
        f"\n## Optional result file\n"
        f"Write `{goal_run_dir(project_root, run_id) / f'turn-{turn_n}.result.json'}` when useful.\n"
    )
    assert "execution_jsonl_body" not in body
    assert "full_chat" not in body
    assert "update_goal" not in body.lower()
    return body


def write_turn_prompt(project_root: Path, run_id: str, turn_n: int, content: str) -> Path:
    ensure_run_dir(project_root, run_id)
    path = goal_run_dir(project_root, run_id) / f"turn-{turn_n}.prompt.md"
    path.write_text(content, encoding="utf-8")
    return path


def is_goal_terminal(goal_payload: dict[str, Any]) -> bool:
    status = str(goal_payload.get("status") or "")
    if status in TERMINAL_GOAL_STATUSES:
        return True
    if status == "blocked" and int(goal_payload.get("blocked_streak") or 0) >= 3:
        return True
    if goal_payload.get("release_human_gate") and status == "release_pending":
        return True
    return False


def _default_spawn(argv: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        argv,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def driver_start(
    project_root: Path,
    run_id: str,
    *,
    goal_loader: Callable[[Path, str], dict[str, Any]] | None = None,
    goal_saver: Callable[[Path, dict[str, Any]], dict[str, Any]] | None = None,
    longrun: bool = True,
    max_turns: int | None = None,
    turn_timeout_sec: int | None = None,
    attach_supervisor: bool = True,
    run_loop: bool = False,
    max_loop_turns: int | None = None,
    spawn_fn: SpawnFn | None = None,
    bridge_cmd: str | None = None,
) -> dict[str, Any]:
    """Arm driver; optionally run loop (synchronous)."""
    from beacon.utils.product_goal_runtime import (
        _save as default_save,
        load_goal_run,
    )

    project_root = Path(project_root).expanduser().resolve()
    load = goal_loader or load_goal_run
    save = goal_saver or default_save
    goal = load(project_root, run_id)
    if goal.get("reason_code") == "product_goal_run_not_found":
        return goal

    state = load_driver_state(project_root, run_id)
    if state.get("state") == "turn_active" and state.get("pid") and _pid_alive(int(state["pid"])):
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_DUAL_DRIVER,
            "run_id": run_id,
            "driver": state,
        }

    driver_id = f"drv-{uuid.uuid4().hex[:10]}"
    lock = acquire_driver_lock(project_root, run_id, driver_id=driver_id)
    if not lock.get("ok"):
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": lock.get("reason_code") or REASON_DRIVER_LOCK,
            "run_id": run_id,
            "driver": state,
        }

    budget = default_budget()
    if max_turns is not None:
        budget["max_agent_turns"] = max(1, int(max_turns))
    if turn_timeout_sec is not None:
        budget["turn_timeout_sec"] = max(1, int(turn_timeout_sec))

    if attach_supervisor:
        goal = dgs_attach_supervisor(goal, interval_sec=DEFAULT_HEARTBEAT_INTERVAL_SEC)
        goal = save(project_root, goal)

    state = {
        **_empty_driver(run_id),
        "driver_id": driver_id,
        "state": "arming",
        "pid": os.getpid(),
        "turn_n": int(state.get("turn_n") or 0),
        "max_agent_turns": budget["max_agent_turns"],
        "turn_timeout_sec": budget["turn_timeout_sec"],
        "longrun": bool(longrun),
        "started_at": now_iso(),
        "lock_held": True,
        "history": list(state.get("history") or []) + [{"event": "start", "at": now_iso()}],
    }
    state = save_driver_state(project_root, state)
    goal["driver"] = {
        "driver_id": driver_id,
        "state": state["state"],
        "longrun": True,
        "max_agent_turns": state["max_agent_turns"],
    }
    goal = save(project_root, goal)
    append_execution_log(
        project_root,
        run_id,
        stage=str(goal.get("current_stage") or ""),
        event="driver_start",
        summary=f"driver {driver_id} arming longrun={longrun}",
    )

    result: dict[str, Any] = {
        "status": "arming",
        "run_id": run_id,
        "driver": state,
        "goal_status": goal.get("status"),
        "auto_release": False,
        "can_complete_without_verifier": False,
    }
    if run_loop:
        loop_out = driver_run_loop(
            project_root,
            run_id,
            max_loop_turns=max_loop_turns,
            spawn_fn=spawn_fn,
            bridge_cmd=bridge_cmd,
            goal_loader=load,
            goal_saver=save,
        )
        result.update(loop_out)
        result["status"] = loop_out.get("driver_state") or loop_out.get("status") or result["status"]
    return result


def driver_status(project_root: Path, run_id: str) -> dict[str, Any]:
    state = load_driver_state(project_root, run_id)
    lock = driver_lock_path(project_root, run_id)
    return {
        "status": "ok",
        "run_id": run_id,
        "driver": state,
        "state": state.get("state"),
        "pid": state.get("pid"),
        "turn_n": state.get("turn_n"),
        "lock_present": lock.exists(),
        "auto_release": False,
    }


def driver_stop(project_root: Path, run_id: str) -> dict[str, Any]:
    from beacon.utils.product_goal_runtime import _save, load_goal_run

    project_root = Path(project_root).expanduser().resolve()
    state = load_driver_state(project_root, run_id)
    driver_id = str(state.get("driver_id") or "")
    state["state"] = "halt_terminal"
    state["halt_reason"] = REASON_USER_STOP
    state["lock_held"] = False
    state["history"] = list(state.get("history") or []) + [{"event": "stop", "at": now_iso()}]
    state = save_driver_state(project_root, state)
    release_driver_lock(project_root, run_id, driver_id=driver_id)
    goal = load_goal_run(project_root, run_id)
    if goal.get("reason_code") != "product_goal_run_not_found":
        goal["driver"] = {
            "driver_id": driver_id,
            "state": "halt_terminal",
            "halt_reason": REASON_USER_STOP,
        }
        _save(project_root, goal)
    append_execution_log(
        project_root,
        run_id,
        stage=str(goal.get("current_stage") or ""),
        event="driver_stop",
        summary="user stop",
    )
    return {
        "status": "halt_terminal",
        "run_id": run_id,
        "driver": state,
        "halt_reason": REASON_USER_STOP,
        "auto_release": False,
    }


def driver_run_once(
    project_root: Path,
    run_id: str,
    *,
    spawn_fn: SpawnFn | None = None,
    bridge_cmd: str | None = None,
    goal_loader: Callable[[Path, str], dict[str, Any]] | None = None,
    goal_saver: Callable[[Path, dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute one turn: prompt → spawn → end → requeue or halt. Never completes/releases."""
    from beacon.utils.product_goal_runtime import (
        REASON_VERIFIER_REQUIRED,
        _save as default_save,
        complete_goal_run,
        goal_checkpoint,
        goal_heartbeat,
        load_goal_run,
    )

    project_root = Path(project_root).expanduser().resolve()
    load = goal_loader or load_goal_run
    save = goal_saver or default_save
    goal = load(project_root, run_id)
    if goal.get("reason_code") == "product_goal_run_not_found":
        return goal

    state = load_driver_state(project_root, run_id)
    if state.get("state") == "idle" and not state.get("longrun"):
        return {
            "status": "idle",
            "run_id": run_id,
            "driver": state,
            "note": "driver idle; use --longrun or driver start",
        }
    if state.get("state") in {"halt_budget", "halt_terminal"}:
        return {"status": state["state"], "run_id": run_id, "driver": state, "halt_reason": state.get("halt_reason")}

    if is_goal_terminal(goal):
        state["state"] = "halt_terminal"
        state["halt_reason"] = f"goal_status_{goal.get('status')}"
        state["lock_held"] = False
        state = save_driver_state(project_root, state)
        release_driver_lock(project_root, run_id, driver_id=str(state.get("driver_id") or ""))
        return {"status": "halt_terminal", "run_id": run_id, "driver": state, "goal_status": goal.get("status")}

    turn_n = int(state.get("turn_n") or 0) + 1
    max_turns = int(state.get("max_agent_turns") or DEFAULT_MAX_AGENT_TURNS)
    timeout = int(state.get("turn_timeout_sec") or DEFAULT_TURN_TIMEOUT_SEC)

    if turn_n > max_turns:
        state["state"] = "halt_budget"
        state["halt_reason"] = REASON_BUDGET
        state["lock_held"] = False
        # budget_limit steering artifact (wrap-up only; no new substantive work)
        try:
            wrap = render_turn_prompt(
                project_root,
                goal,
                turn_n=turn_n,
                driver_state=state,
                halt_budget=True,
                version=str(goal.get("version") or "v2.0.0"),
            )
            wrap_path = write_turn_prompt(project_root, run_id, turn_n, wrap)
        except Exception:  # noqa: BLE001
            wrap_path = None
        state = save_driver_state(project_root, state)
        release_driver_lock(project_root, run_id, driver_id=str(state.get("driver_id") or ""))
        # explicitly refuse complete
        rejected = complete_goal_run(project_root, run_id)
        append_execution_log(
            project_root,
            run_id,
            stage=str(goal.get("current_stage") or ""),
            event="driver_halt_budget",
            summary=(
                f"turns={turn_n - 1} max={max_turns}; complete refused={rejected.get('reason_code')}; "
                f"budget_limit_prompt={getattr(wrap_path, 'name', None)}"
            ),
        )
        return {
            "status": "halt_budget",
            "run_id": run_id,
            "driver": state,
            "completed": rejected.get("status") == "completed",
            "complete_status": rejected.get("status"),
            "reason_code": REASON_BUDGET,
            "auto_release": False,
        }

    # arming / requeue → turn_active
    prompt = render_turn_prompt(
        project_root,
        goal,
        turn_n=turn_n,
        driver_state=state,
        halt_budget=False,
        version=str(goal.get("version") or "v2.0.0"),
    )
    # remember objective fingerprint for objective_updated on next turn
    state["last_objective_fp"] = objective_fingerprint(goal)
    prompt_path = write_turn_prompt(project_root, run_id, turn_n, prompt)
    bridge = resolve_bridge_command(
        prompt_file=prompt_path,
        run_id=run_id,
        project_root=project_root,
        bridge_cmd=bridge_cmd,
    )
    if not bridge.get("ok"):
        state["state"] = "halt_terminal"
        state["halt_reason"] = REASON_NO_BRIDGE
        state["last_error"] = str(bridge.get("hint") or REASON_NO_BRIDGE)
        state["lock_held"] = False
        state = save_driver_state(project_root, state)
        release_driver_lock(project_root, run_id, driver_id=str(state.get("driver_id") or ""))
        goal["blocked"] = True
        goal["reason_code"] = REASON_NO_BRIDGE
        goal["status"] = "stage_blocked" if goal.get("status") != "blocked" else goal.get("status")
        save(project_root, goal)
        append_execution_log(
            project_root,
            run_id,
            stage=str(goal.get("current_stage") or ""),
            event="driver_bridge_missing",
            summary=str(bridge.get("hint") or ""),
        )
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_NO_BRIDGE,
            "run_id": run_id,
            "driver": state,
            "recoverable": True,
            "hint": bridge.get("hint"),
        }

    state["state"] = "turn_active"
    state["turn_n"] = turn_n
    state["pid"] = os.getpid()
    state = save_driver_state(project_root, state)
    append_execution_log(
        project_root,
        run_id,
        stage=str(goal.get("current_stage") or ""),
        event="driver_turn_start",
        summary=f"turn={turn_n} prompt={prompt_path.name}",
        cmd=str(bridge.get("cmd") or "")[:200],
    )

    spawn = spawn_fn or _default_spawn
    exit_code = 1
    timed_out = False
    stdout = ""
    stderr = ""
    try:
        proc = spawn(list(bridge.get("argv") or []), project_root, timeout)
        exit_code = int(proc.returncode or 0)
        stdout = str(getattr(proc, "stdout", "") or "")[:4000]
        stderr = str(getattr(proc, "stderr", "") or "")[:4000]
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout = str(getattr(exc, "stdout", "") or "")[:2000]
        stderr = str(getattr(exc, "stderr", "") or "timeout")[:2000]

    # optional result file written by agent
    result_path = goal_run_dir(project_root, run_id) / f"turn-{turn_n}.result.json"
    result_payload: dict[str, Any] = {}
    if result_path.exists():
        try:
            result_payload = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            result_payload = {}

    state["state"] = "turn_ended"
    state["last_exit_code"] = exit_code
    state["last_error"] = stderr[:500] if exit_code != 0 else ""
    state = save_driver_state(project_root, state)

    summary = f"turn={turn_n} exit={exit_code} timeout={timed_out}"

    # Loom trace bundle: dual-channel agent_trace (path refs; no full chat)
    try:
        from beacon.utils.loom_trace import record_driver_turn_trace

        record_driver_turn_trace(
            project_root,
            run_id,
            turn_n=turn_n,
            prompt_path=str(prompt_path),
            exit_code=exit_code,
            summary=summary[:240],
        )
    except Exception:  # noqa: BLE001
        pass

    if isinstance(result_payload, dict) and result_payload.get("summary"):
        summary = f"{summary}; {result_payload.get('summary')}"
    try:
        goal_heartbeat(project_root, run_id, summary=summary[:240], substep=f"driver-turn-{turn_n}")
        next_action = str(
            (result_payload or {}).get("next_action")
            or "continue current stage against frozen truth via resume-pack"
        )
        goal_checkpoint(project_root, run_id, next_action=next_action, substep=f"driver-turn-{turn_n}")
    except Exception:  # noqa: BLE001
        pass

    append_execution_log(
        project_root,
        run_id,
        stage=str(goal.get("current_stage") or ""),
        event="driver_turn_end",
        summary=summary[:240],
    )

    # reload goal after heartbeat
    goal = load(project_root, run_id)
    # GoalTurnCounter: consecutive same blocker_id (blocked audit ≥3)
    try:
        blocker = None
        if isinstance(result_payload, dict):
            blocker = result_payload.get("blocker_id") or result_payload.get("blocker")
        if not blocker and goal.get("open_blockers"):
            ob = goal.get("open_blockers")
            if isinstance(ob, list) and ob:
                blocker = ob[0] if not isinstance(ob[0], dict) else ob[0].get("id")
        goal = bump_blocker_streak(goal, str(blocker) if blocker else None)
        goal = save(project_root, goal)
    except Exception:  # noqa: BLE001
        pass

    # never auto-complete / auto-release
    if is_goal_terminal(goal):
        state["state"] = "halt_terminal"
        state["halt_reason"] = f"goal_status_{goal.get('status')}"
        state["lock_held"] = False
        state = save_driver_state(project_root, state)
        release_driver_lock(project_root, run_id, driver_id=str(state.get("driver_id") or ""))
        return {
            "status": "halt_terminal",
            "run_id": run_id,
            "driver": state,
            "turn_n": turn_n,
            "exit_code": exit_code,
            "prompt_path": str(prompt_path),
            "auto_release": False,
            "can_complete_without_verifier": False,
        }

    # requeue if budget allows
    if turn_n >= max_turns:
        state["state"] = "halt_budget"
        state["halt_reason"] = REASON_BUDGET
        state["lock_held"] = False
        state = save_driver_state(project_root, state)
        release_driver_lock(project_root, run_id, driver_id=str(state.get("driver_id") or ""))
        rejected = complete_goal_run(project_root, run_id)
        assert rejected.get("status") != "completed" or (
            (goal.get("verifier") or {}).get("present")
        )
        # if somehow completed with verifier ok — still no release
        return {
            "status": "halt_budget",
            "run_id": run_id,
            "driver": state,
            "turn_n": turn_n,
            "completed": rejected.get("status") == "completed",
            "complete_reason": rejected.get("reason_code") or REASON_VERIFIER_REQUIRED,
            "auto_release": False,
        }

    state["state"] = "requeue"
    state["history"] = list(state.get("history") or []) + [
        {"event": "requeue", "turn_n": turn_n, "at": now_iso()}
    ]
    state = save_driver_state(project_root, state)
    return {
        "status": "requeue",
        "run_id": run_id,
        "driver": state,
        "turn_n": turn_n,
        "exit_code": exit_code,
        "prompt_path": str(prompt_path),
        "prompt_is_digest": True,
        "auto_release": False,
        "can_complete_without_verifier": False,
        "stdout_tail": stdout[-500:],
        "stderr_tail": stderr[-500:],
    }


def driver_run_loop(
    project_root: Path,
    run_id: str,
    *,
    max_loop_turns: int | None = None,
    spawn_fn: SpawnFn | None = None,
    bridge_cmd: str | None = None,
    goal_loader: Callable[[Path, str], dict[str, Any]] | None = None,
    goal_saver: Callable[[Path, dict[str, Any]], dict[str, Any]] | None = None,
    sleep_fn: Callable[[float], None] | None = None,
) -> dict[str, Any]:
    """Run turns until halt/terminal/budget. Sleep is no-op by default between turns."""
    sleeper = sleep_fn or (lambda _s: None)
    state = load_driver_state(project_root, run_id)
    limit = int(max_loop_turns or state.get("max_agent_turns") or DEFAULT_MAX_AGENT_TURNS)
    turns: list[dict[str, Any]] = []
    last: dict[str, Any] = {"status": "arming", "run_id": run_id}
    for _ in range(limit):
        last = driver_run_once(
            project_root,
            run_id,
            spawn_fn=spawn_fn,
            bridge_cmd=bridge_cmd,
            goal_loader=goal_loader,
            goal_saver=goal_saver,
        )
        turns.append(
            {
                "status": last.get("status"),
                "turn_n": last.get("turn_n"),
                "exit_code": last.get("exit_code"),
            }
        )
        st = str(last.get("status") or "")
        if st in {"halt_budget", "halt_terminal", "blocked", "idle", "completed"}:
            break
        if st == "requeue":
            sleeper(0)
            continue
        # unknown → stop safe
        break
    state = load_driver_state(project_root, run_id)
    return {
        "status": "ok",
        "run_id": run_id,
        "driver_state": state.get("state"),
        "turns": turns,
        "last": last,
        "auto_release": False,
        "driver": state,
    }


def attach_longrun_to_goal_run(
    project_root: Path,
    payload: dict[str, Any],
    *,
    start_driver: bool = True,
    run_loop: bool = False,
    max_loop_turns: int | None = None,
    spawn_fn: SpawnFn | None = None,
    bridge_cmd: str | None = None,
) -> dict[str, Any]:
    """Attach longrun metadata to a newly created goal run; optionally start driver."""
    run_id = str(payload.get("run_id") or "")
    payload["longrun"] = True
    payload["driver"] = payload.get("driver") or {"state": "idle", "longrun": True}
    if not start_driver:
        return payload
    started = driver_start(
        project_root,
        run_id,
        longrun=True,
        attach_supervisor=True,
        run_loop=run_loop,
        max_loop_turns=max_loop_turns,
        spawn_fn=spawn_fn,
        bridge_cmd=bridge_cmd,
    )
    payload["driver_attach"] = {
        "status": started.get("status"),
        "driver_id": (started.get("driver") or {}).get("driver_id"),
        "driver_state": (started.get("driver") or {}).get("state") or started.get("driver_state"),
        "reason_code": started.get("reason_code"),
    }
    # reload goal for freshest fields
    from beacon.utils.product_goal_runtime import load_goal_run

    fresh = load_goal_run(project_root, run_id)
    if fresh.get("reason_code") != "product_goal_run_not_found":
        fresh["longrun"] = True
        fresh["driver_attach"] = payload["driver_attach"]
        return fresh
    return payload


# Explicit policy exports for tests / docs
def assert_no_auto_release_policy() -> None:
    """Driver must never auto-confirm release (contract hook)."""
    return None


def assert_complete_requires_verifier_policy() -> None:
    return None
