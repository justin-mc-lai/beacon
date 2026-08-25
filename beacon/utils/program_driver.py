"""Program-level lake driver (v1.6.12).

Consumes ``build_program_orchestrator_state`` routes and dispatches one
lake-stage per turn to a host agent (bridge_cmd/spawn_fn), then recomputes
the route from filesystem evidence only. Never dispatches release; never
self-certifies truth/QA/release verdicts.

Stop contract (AC-039): every stop emits ``reason_code`` +
``resume_action`` (+ ``recommended_command`` when one exists).
"""

from __future__ import annotations

import json
import os
import subprocess
import uuid
from pathlib import Path
from typing import Any

from beacon.utils.goal_agent_driver import (
    DEFAULT_TURN_TIMEOUT_SEC,
    REASON_NO_BRIDGE,
    _default_spawn,
    _env_int,
    _pid_alive,
    resolve_bridge_command,
)
from beacon.utils.program_graph import program_dir
from beacon.utils.program_orchestrator import build_program_orchestrator_state
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import resolve_target_version

SCHEMA_VERSION = "1.0"
DEFAULT_MAX_DRIVE_TURNS = 32
DEFAULT_TURN_TIMEOUT_SEC_DRIVE = DEFAULT_TURN_TIMEOUT_SEC
BLOCKED_STREAK_LIMIT = 3
DRIVE_PROMPT_DIR = ".beacon/state/program-drive"

REASON_HUMAN_GATE = "await_human_gate"
REASON_COMPLETE = "program_complete"
REASON_UPSTREAM = "await_upstream_lake_closure"
REASON_GRAPH_INVALID = "feature_graph_invalid"
REASON_LAKES_MISSING = "program_lakes_missing"
REASON_BUDGET = "program_drive_budget_exhausted"
REASON_STREAK = "program_drive_blocked_streak"
REASON_SPAWN_FAILED = "host_spawn_failed"
REASON_USER_STOP = "program_drive_user_stop"
REASON_DUAL_DRIVER = "program_drive_dual_start_forbidden"

# stage -> skill the host agent must load (release intentionally absent: human gate)
STAGE_SKILLS = {
    "truth": "beacon-gen-truth",
    "implement": "beacon-gen-implement",
    "qa": "beacon-eval-qa",
}
RESUME_STAGE = {
    "prepare_next_lake_truth": "truth",
    "run_lake_implementation": "implement",
    "run_lake_qa": "qa",
}

# Optional injectable runner for tests: (argv, cwd, timeout) -> CompletedProcess-like
SpawnFn = Any


def default_program_budget() -> dict[str, int]:
    return {
        "max_drive_turns": _env_int("BEACON_PROGRAM_MAX_TURNS", DEFAULT_MAX_DRIVE_TURNS),
        "turn_timeout_sec": _env_int("BEACON_PROGRAM_TURN_TIMEOUT_SEC", DEFAULT_TURN_TIMEOUT_SEC),
    }


def drive_lock_path(project_root: Path, program_slug: str) -> Path:
    return Path(project_root).expanduser().resolve() / DRIVE_PROMPT_DIR / f"{program_slug}.lock"


def prompt_dir(project_root: Path, program_slug: str) -> Path:
    return Path(project_root).expanduser().resolve() / DRIVE_PROMPT_DIR / program_slug


def drive_state_path(project_root: Path, version: str, program_slug: str) -> Path:
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    return program_dir(root, resolved, program_slug) / "program-drive-state.json"


def _empty_drive(program_slug: str) -> dict[str, Any]:
    budget = default_program_budget()
    return {
        "schema_version": SCHEMA_VERSION,
        "program_slug": program_slug,
        "driver_id": "",
        "state": "idle",
        "pid": None,
        "turn_n": 0,
        "max_drive_turns": budget["max_drive_turns"],
        "turn_timeout_sec": budget["turn_timeout_sec"],
        "blocked_streak": 0,
        "last_route_fingerprint": "",
        "started_at": "",
        "updated_at": now_iso(),
        "last_exit_code": None,
        "last_error": "",
        "halt_reason": "",
        "last_reason_code": "",
        "last_resume_action": "",
        "last_blocked": False,
        "recommended_command": "",
        "lock_held": False,
        "history": [],
    }


def load_drive_state(project_root: Path, version: str, program_slug: str) -> dict[str, Any]:
    path = drive_state_path(project_root, version, program_slug)
    if not path.exists():
        return _empty_drive(program_slug)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty_drive(program_slug)
    return data if isinstance(data, dict) else _empty_drive(program_slug)


def save_drive_state(project_root: Path, state: dict[str, Any]) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    state["updated_at"] = now_iso()
    path = drive_state_path(root, str(state.get("version") or "auto"), str(state.get("program_slug") or ""))
    write_json(path, state)
    state["drive_state_path"] = str(path)
    return state


def acquire_program_drive_lock(project_root: Path, program_slug: str, *, driver_id: str) -> dict[str, Any]:
    """Exclusive lock per program slug. Fail closed if another live lock exists."""
    lock = drive_lock_path(project_root, program_slug)
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock.exists():
        try:
            existing = json.loads(lock.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        pid = existing.get("pid")
        if pid and _pid_alive(int(pid)):
            return {"ok": False, "reason_code": REASON_DUAL_DRIVER, "existing": existing}
        try:
            lock.unlink()
        except OSError:
            pass
    payload = {
        "driver_id": driver_id,
        "program_slug": program_slug,
        "pid": os.getpid(),
        "acquired_at": now_iso(),
    }
    lock.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "lock": payload}


def release_program_drive_lock(project_root: Path, program_slug: str, *, driver_id: str = "") -> None:
    lock = drive_lock_path(project_root, program_slug)
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


def render_program_turn_prompt(orchestrator: dict[str, Any], *, turn_n: int) -> str:
    """Render the lake-stage turn prompt: current lake + stage -> skill to load."""
    slug = str(orchestrator.get("program_slug") or "")
    version = str(orchestrator.get("version") or "")
    lake = str(orchestrator.get("current_lake") or "")
    stage = str(orchestrator.get("current_stage") or "")
    skill = STAGE_SKILLS.get(stage, "")
    lines = [
        "# Beacon Program Drive",
        "",
        f"- program: {slug} (docs version {version})",
        f"- turn: {turn_n}",
        f"- current lake: {lake}",
        f"- current stage: {stage}",
        f"- resume_action: {orchestrator.get('resume_action')}",
        "",
        "## Task",
        f"Load and execute the `{skill}` skill for lake `{lake}` (stage: {stage}) against the frozen",
        f"program package at docs/beacon/{version}/programs/{slug}/. Complete only this lake-stage.",
        "",
        "## Evidence this stage must leave on disk (the driver reads filesystem evidence only)",
    ]
    if stage == "truth":
        lines.append(
            f"- Freeze truth for `{lake}` so its row in docs/beacon/{version}/programs/{slug}/feature-graph.json carries status=frozen."
        )
    elif stage == "implement":
        lines.append(
            f"- Write implementation closure evidence to .beacon/state/implementation-{lake}.json with status=pass."
        )
    elif stage == "qa":
        lines.append(
            f"- Write QA acceptance evidence to .beacon/qa/features/{lake}/status.json (verdict passed, evidence_done=true)."
        )
    lines += [
        "",
        "## Hard boundaries",
        "- Release is a HUMAN gate: never perform, confirm, or self-certify release.",
        "- Do not fabricate QA verdicts or completion evidence.",
        "- Do not work on lakes other than the current lake.",
        "",
        f"recommended_command: {orchestrator.get('recommended_command')}",
        "",
    ]
    return "\n".join(lines)


def write_turn_prompt(project_root: Path, program_slug: str, turn_n: int, content: str) -> Path:
    directory = prompt_dir(project_root, program_slug)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"turn-{turn_n}.prompt.md"
    path.write_text(content, encoding="utf-8")
    return path


def route_fingerprint(payload: dict[str, Any]) -> str:
    return f"{payload.get('current_lake')}:{payload.get('current_stage')}"


def _finalize(
    project_root: Path,
    state: dict[str, Any],
    *,
    status: str,
    blocked: bool,
    reason_code: str,
    resume_action: str,
    recommended_command: str = "",
    history_event: str = "",
) -> dict[str, Any]:
    """Persist a terminal stop and emit the AC-039 stop contract fields."""
    state["state"] = status
    state["halt_reason"] = reason_code
    state["last_reason_code"] = reason_code
    state["last_resume_action"] = resume_action
    state["last_blocked"] = bool(blocked)
    state["recommended_command"] = recommended_command
    state["lock_held"] = False
    if history_event:
        state["history"] = list(state.get("history") or []) + [
            {"event": history_event, "reason_code": reason_code, "at": now_iso()}
        ]
    state = save_drive_state(project_root, state)
    release_program_drive_lock(
        project_root, str(state.get("program_slug") or ""), driver_id=str(state.get("driver_id") or "")
    )
    return {
        "status": status,
        "blocked": bool(blocked),
        "reason_code": reason_code,
        "resume_action": resume_action,
        "recommended_command": recommended_command,
        "auto_release": False,
        "turn_n": int(state.get("turn_n") or 0),
        "driver": state,
    }


def program_drive_once(
    project_root: Path,
    *,
    version: str = "auto",
    program_slug: str,
    spawn_fn: SpawnFn | None = None,
    bridge_cmd: str | None = None,
) -> dict[str, Any]:
    """One tick: compute route -> dispatch lake-stage -> recompute evidence -> persist state."""
    root = Path(project_root).expanduser().resolve()
    state = load_drive_state(root, version, program_slug)
    if state.get("state") in {"halt_budget", "halt_terminal"}:
        return {
            "status": state["state"],
            "blocked": bool(state.get("last_blocked")),
            "reason_code": str(state.get("last_reason_code") or state.get("halt_reason") or ""),
            "resume_action": str(state.get("last_resume_action") or ""),
            "recommended_command": str(state.get("recommended_command") or ""),
            "auto_release": False,
            "turn_n": int(state.get("turn_n") or 0),
            "driver": state,
        }

    orch = build_program_orchestrator_state(root, version=version, program_slug=program_slug)
    resolved_version = str(orch.get("version") or "")
    state["version"] = resolved_version
    reason = str(orch.get("reason_code") or "")

    if reason in (REASON_GRAPH_INVALID, REASON_LAKES_MISSING):
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=True,
            reason_code=reason,
            resume_action="none",
            history_event="drive_stop",
        )

    resume_action = str(orch.get("resume_action") or "")
    current_lake = str(orch.get("current_lake") or "")
    rows = [row for row in (orch.get("lakes") or []) if isinstance(row, dict)]
    row = next((r for r in rows if str(r.get("lake") or "") == current_lake), {})

    # R6: never dispatch a lake whose upstream lakes are unclosed.
    unclosed_deps = [str(d) for d in (row.get("unclosed_dependencies") or []) if str(d).strip()]
    if current_lake and unclosed_deps:
        rec = f'beacon implement run "{unclosed_deps[0]}" --project {root} --version {resolved_version}'
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=True,
            reason_code=REASON_UPSTREAM,
            resume_action="none",
            recommended_command=rec,
            history_event="drive_stop",
        )

    # Release is always a human gate: never dispatched.
    if resume_action == REASON_HUMAN_GATE or str(orch.get("sea_completion_status")) == "all_lakes_complete":
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=False,
            reason_code=REASON_HUMAN_GATE,
            resume_action=REASON_HUMAN_GATE,
            recommended_command=str(orch.get("recommended_command") or ""),
            history_event="drive_stop",
        )
    if resume_action == REASON_COMPLETE:
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=False,
            reason_code=REASON_COMPLETE,
            resume_action="none",
            history_event="drive_stop",
        )

    streak = int(state.get("blocked_streak") or 0)
    if streak >= BLOCKED_STREAK_LIMIT:
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=True,
            reason_code=REASON_STREAK,
            resume_action="replay_substep",
            history_event="drive_stop",
        )

    turn_n = int(state.get("turn_n") or 0) + 1
    max_turns = int(state.get("max_drive_turns") or DEFAULT_MAX_DRIVE_TURNS)
    timeout = int(state.get("turn_timeout_sec") or DEFAULT_TURN_TIMEOUT_SEC_DRIVE)
    if turn_n > max_turns:
        return _finalize(
            root,
            state,
            status="halt_budget",
            blocked=False,
            reason_code=REASON_BUDGET,
            resume_action="replay_substep",
            history_event="drive_halt_budget",
        )

    stage = RESUME_STAGE.get(resume_action)
    if stage is None:
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=True,
            reason_code=f"unknown_resume_action:{resume_action}",
            resume_action="none",
            history_event="drive_stop",
        )

    fingerprint_pre = route_fingerprint(orch)
    prompt = render_program_turn_prompt(orch, turn_n=turn_n)
    prompt_path = write_turn_prompt(root, program_slug, turn_n, prompt)
    bridge = resolve_bridge_command(
        prompt_file=prompt_path,
        run_id=program_slug,
        project_root=root,
        bridge_cmd=bridge_cmd,
    )
    if not bridge.get("ok"):
        state["last_error"] = str(bridge.get("hint") or REASON_NO_BRIDGE)
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=True,
            reason_code=REASON_NO_BRIDGE,
            resume_action="replay_substep",
            history_event="drive_bridge_missing",
        )

    state.update({"state": "turn_active", "turn_n": turn_n, "pid": os.getpid(), "lock_held": True})
    state = save_drive_state(root, state)

    exit_code = 1
    stderr = ""
    try:
        proc = (spawn_fn or _default_spawn)(list(bridge.get("argv") or []), root, timeout)
        exit_code = int(proc.returncode or 0)
        stderr = str(getattr(proc, "stderr", "") or "")[:2000]
    except subprocess.TimeoutExpired:
        exit_code = 124
    except Exception as exc:  # noqa: BLE001
        stderr = str(exc)[:500]

    # Recompute route from filesystem evidence only — never trust driver memory.
    post = build_program_orchestrator_state(
        root, version=resolved_version, program_slug=str(orch.get("program_slug") or program_slug)
    )
    advanced = route_fingerprint(post) != fingerprint_pre
    streak = 0 if advanced else streak + 1

    state["state"] = "turn_ended"
    state["last_exit_code"] = exit_code
    state["last_error"] = "" if exit_code == 0 else stderr[:500]
    state["last_route_fingerprint"] = route_fingerprint(post)
    state["blocked_streak"] = streak
    state["history"] = list(state.get("history") or []) + [
        {
            "event": "turn",
            "turn_n": turn_n,
            "lake": current_lake,
            "stage": stage,
            "exit_code": exit_code,
            "advanced": advanced,
            "at": now_iso(),
        }
    ]

    if exit_code != 0:
        state["last_error"] = stderr[:500] or f"exit_code={exit_code}"
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=True,
            reason_code=REASON_SPAWN_FAILED,
            resume_action="replay_substep",
            history_event="drive_stop",
        )

    if streak >= BLOCKED_STREAK_LIMIT:
        return _finalize(
            root,
            state,
            status="halt_terminal",
            blocked=True,
            reason_code=REASON_STREAK,
            resume_action="replay_substep",
            history_event="drive_stop",
        )

    state["state"] = "requeue"
    state = save_drive_state(root, state)
    return {
        "status": "requeue",
        "blocked": False,
        "reason_code": "",
        "resume_action": str(post.get("resume_action") or ""),
        "recommended_command": str(post.get("recommended_command") or ""),
        "turn_n": turn_n,
        "exit_code": exit_code,
        "prompt_path": str(prompt_path),
        "route": {
            "current_lake": post.get("current_lake"),
            "current_stage": post.get("current_stage"),
            "next_lake": post.get("next_lake"),
            "sea_completion_status": post.get("sea_completion_status"),
        },
        "auto_release": False,
        "driver": state,
    }


def program_drive_loop(
    project_root: Path,
    *,
    version: str = "auto",
    program_slug: str,
    spawn_fn: SpawnFn | None = None,
    bridge_cmd: str | None = None,
    max_loop_turns: int | None = None,
) -> dict[str, Any]:
    """Run drive ticks until halt/stop condition or loop limit."""
    state = load_drive_state(project_root, version, program_slug)
    limit = int(max_loop_turns or state.get("max_drive_turns") or DEFAULT_MAX_DRIVE_TURNS)
    turns: list[dict[str, Any]] = []
    last: dict[str, Any] = {"status": "arming", "program_slug": program_slug}
    for _ in range(limit):
        last = program_drive_once(
            project_root,
            version=version,
            program_slug=program_slug,
            spawn_fn=spawn_fn,
            bridge_cmd=bridge_cmd,
        )
        turns.append(
            {
                "status": last.get("status"),
                "turn_n": last.get("turn_n"),
                "exit_code": last.get("exit_code"),
                "reason_code": last.get("reason_code"),
            }
        )
        if str(last.get("status") or "") != "requeue":
            break
    return {
        "status": str(last.get("status") or "ok"),
        "blocked": bool(last.get("blocked")),
        "reason_code": str(last.get("reason_code") or ""),
        "resume_action": str(last.get("resume_action") or ""),
        "recommended_command": str(last.get("recommended_command") or ""),
        "program_slug": program_slug,
        "turns": turns,
        "last": last,
        "auto_release": False,
    }


def program_drive_start(
    project_root: Path,
    *,
    version: str = "auto",
    program_slug: str,
    run_loop: bool = True,
    max_turns: int | None = None,
    max_loop_turns: int | None = None,
    turn_timeout_sec: int | None = None,
    spawn_fn: SpawnFn | None = None,
    bridge_cmd: str | None = None,
) -> dict[str, Any]:
    """Arm the program driver; optionally run the drive loop synchronously."""
    root = Path(project_root).expanduser().resolve()
    prior = load_drive_state(root, version, program_slug)
    if prior.get("state") == "turn_active" and prior.get("pid") and _pid_alive(int(prior["pid"])):
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_DUAL_DRIVER,
            "resume_action": "none",
            "program_slug": program_slug,
            "driver": prior,
            "auto_release": False,
        }

    driver_id = f"pdrv-{uuid.uuid4().hex[:10]}"
    lock = acquire_program_drive_lock(root, program_slug, driver_id=driver_id)
    if not lock.get("ok"):
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": str(lock.get("reason_code") or REASON_DUAL_DRIVER),
            "resume_action": "none",
            "program_slug": program_slug,
            "driver": prior,
            "auto_release": False,
        }

    budget = default_program_budget()
    if max_turns is not None:
        budget["max_drive_turns"] = max(1, int(max_turns))
    if turn_timeout_sec is not None:
        budget["turn_timeout_sec"] = max(1, int(turn_timeout_sec))

    orch_probe = build_program_orchestrator_state(root, version=version, program_slug=program_slug)
    state = {
        **_empty_drive(program_slug),
        "driver_id": driver_id,
        "state": "arming",
        "pid": os.getpid(),
        "version": str(orch_probe.get("version") or ""),
        "turn_n": int(prior.get("turn_n") or 0),
        "max_drive_turns": budget["max_drive_turns"],
        "turn_timeout_sec": budget["turn_timeout_sec"],
        "blocked_streak": int(prior.get("blocked_streak") or 0),
        "last_route_fingerprint": str(prior.get("last_route_fingerprint") or ""),
        "started_at": now_iso(),
        "lock_held": True,
        "history": list(prior.get("history") or []) + [{"event": "start", "at": now_iso()}],
    }
    state = save_drive_state(root, state)

    result: dict[str, Any] = {
        "status": "arming",
        "blocked": False,
        "reason_code": "",
        "resume_action": "",
        "program_slug": program_slug,
        "driver": state,
        "auto_release": False,
    }
    if run_loop:
        loop_out = program_drive_loop(
            root,
            version=version,
            program_slug=program_slug,
            spawn_fn=spawn_fn,
            bridge_cmd=bridge_cmd,
            max_loop_turns=max_loop_turns,
        )
        result.update(loop_out)
    return result


def program_drive_status(project_root: Path, *, version: str = "auto", program_slug: str) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    state = load_drive_state(root, version, program_slug)
    orch = build_program_orchestrator_state(root, version=version, program_slug=program_slug)
    return {
        "status": "ok",
        "program_slug": program_slug,
        "state": state.get("state"),
        "pid": state.get("pid"),
        "turn_n": state.get("turn_n"),
        "blocked_streak": state.get("blocked_streak"),
        "lock_present": drive_lock_path(root, program_slug).exists(),
        "orchestrator": {
            "current_lake": orch.get("current_lake"),
            "current_stage": orch.get("current_stage"),
            "next_lake": orch.get("next_lake"),
            "resume_action": orch.get("resume_action"),
            "reason_code": orch.get("reason_code"),
            "sea_completion_status": orch.get("sea_completion_status"),
            "recommended_command": orch.get("recommended_command"),
        },
        "reason_code": str(state.get("last_reason_code") or ""),
        "resume_action": str(state.get("last_resume_action") or ""),
        "auto_release": False,
    }


def program_drive_stop(project_root: Path, *, version: str = "auto", program_slug: str) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    state = load_drive_state(root, version, program_slug)
    state["version"] = str(state.get("version") or "") or version
    state["state"] = "halt_terminal"
    state["halt_reason"] = REASON_USER_STOP
    state["last_reason_code"] = REASON_USER_STOP
    state["last_resume_action"] = "none"
    state["last_blocked"] = False
    state["lock_held"] = False
    state["history"] = list(state.get("history") or []) + [{"event": "stop", "at": now_iso()}]
    state = save_drive_state(root, state)
    release_program_drive_lock(root, program_slug, driver_id=str(state.get("driver_id") or ""))
    return {
        "status": "halt_terminal",
        "blocked": False,
        "reason_code": REASON_USER_STOP,
        "resume_action": "none",
        "program_slug": program_slug,
        "driver": state,
        "auto_release": False,
    }


def assert_no_auto_release_policy() -> None:
    """The program driver must never dispatch the release stage (contract hook)."""
    assert "release" not in STAGE_SKILLS
    assert "await_human_gate" not in RESUME_STAGE.values()
    return None
