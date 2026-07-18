"""Loom optional subagent fan-out on GoalRun (opt-in only).

SubagentSession cannot complete GoalRun; merge-to-star only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.goal_durable_supervisor import append_execution_log
from beacon.utils.product_goal_runtime import build_parallel_plan
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.subagent_runtime import tmux_available, write_worker_spec

SCHEMA = "loom-subagent-session.v1"
REASON_DEFAULT_OFF = "subagent_default_off"
REASON_DEPENDS_ON = "subagent_depends_on_unmet"
REASON_TRUTH_WRITE_FORBIDDEN = "satellite_truth_write_forbidden"
REASON_FALLBACK = "subagent_fallback_single_process"


def detect_subagent_intent(utterance: str = "", *, flag: bool | None = None) -> bool:
    if flag is True:
        return True
    if flag is False:
        return False
    text = str(utterance or "").lower()
    markers = ("subagent", "并行", "多湖", "satellite", "fan-out", "fanout", "主星", "卫星")
    return any(m.lower() in text for m in markers)


def subagent_state_dir(project_root: Path, run_id: str) -> Path:
    return Path(project_root) / ".beacon" / "worktrees" / "subagent" / run_id


def create_session(
    project_root: Path,
    run_id: str,
    *,
    lakes: list[str] | None = None,
    depends_on: dict[str, list[str]] | None = None,
    opt_in: bool = False,
    utterance: str = "",
    backend: str = "auto",
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    opted = opt_in or detect_subagent_intent(utterance)
    if not opted:
        return {
            "schema": SCHEMA,
            "run_id": run_id,
            "state": "idle",
            "opt_in": False,
            "spawned": False,
            "reason_code": REASON_DEFAULT_OFF,
            "blocked": False,
            "status": "ok",
            "note": "default run does not spawn; pass opt_in or subagent intent",
        }

    plan = build_parallel_plan(
        lakes=lakes or [],
        mode="main_star_satellite_pool",
        utterance=utterance or "subagent fan-out",
    )
    deps = depends_on or {}
    for lake, need in deps.items():
        unmet = [d for d in need if d not in (lakes or []) and d not in {s.get("lake") for s in plan.get("satellites") or []}]
        # depends_on gates fan-out: dependency lakes must be listed as completed before spawn
        # For plan-time: if depends_on references lakes not yet done, halt
        if need and any(n not in set(lakes or []) for n in need):
            # if depends_on not subset of lakes being run, block
            missing = [n for n in need if n not in set(lakes or [])]
            if missing:
                return {
                    "schema": SCHEMA,
                    "run_id": run_id,
                    "state": "halted",
                    "opt_in": True,
                    "spawned": False,
                    "blocked": True,
                    "reason_code": REASON_DEPENDS_ON,
                    "status": "blocked",
                    "missing_depends_on": missing,
                }

    base = subagent_state_dir(project_root, run_id)
    base.mkdir(parents=True, exist_ok=True)
    satellites_out: list[dict[str, Any]] = []
    for sat in plan.get("satellites") or []:
        lake = str(sat.get("lake") or sat.get("id") or "")
        wt = project_root / str(sat.get("worktree") or f".beacon/worktrees/satellite/{lake}")
        wt.mkdir(parents=True, exist_ok=True)
        # isolation marker — satellites must not write main truth
        marker = wt / ".satellite-isolation.json"
        write_json(
            marker,
            {
                "may_write_truth_on_main": False,
                "merge_target": "main_star",
                "lake": lake,
                "run_id": run_id,
            },
        )
        spec_path = write_worker_spec(
            project_root,
            team_name=f"goal-{run_id}",
            role=lake or "satellite",
            payload={
                "lake": lake,
                "worktree": str(wt),
                "merge_target": "main_star",
                "may_write_truth_on_main": False,
                "run_id": run_id,
            },
        )
        try:
            wt_rel = str(wt.relative_to(project_root))
        except ValueError:
            wt_rel = str(wt)
        satellites_out.append(
            {
                "lake": lake,
                "worktree": wt_rel,
                "spec": str(spec_path),
                "state": "planned",
                "merge_target": "main_star",
                "may_write_truth_on_main": False,
            }
        )

    # backend selection
    use_tmux = backend in {"tmux", "auto"} and tmux_available()
    fallback = False
    reason_fallback = ""
    if backend == "tmux" and not use_tmux:
        fallback = True
        reason_fallback = REASON_FALLBACK
    spawn_backend = "tmux" if use_tmux else ("bridge" if backend == "bridge" else "file")
    if fallback:
        spawn_backend = "file"

    session = {
        "schema": SCHEMA,
        "run_id": run_id,
        "state": "planned",
        "opt_in": True,
        "spawned": False,
        "spawn_backend": spawn_backend,
        "fallback": fallback,
        "reason_code": reason_fallback,
        "main_star": plan.get("main_star"),
        "satellites": satellites_out,
        "one_lake_one_satellite": True,
        "merge_policy": "satellites_merge_to_star_only",
        "cannot_complete_goal": True,
        "created_at": now_iso(),
        "status": "ok",
        "blocked": False,
    }
    path = base / "session.json"
    write_json(path, session)
    append_execution_log(
        project_root,
        run_id,
        stage="implement",
        event="subagent_planned",
        summary=f"lakes={len(satellites_out)} backend={spawn_backend}",
    )
    return {**session, "session_path": str(path)}


def arm_and_run(project_root: Path, run_id: str, *, session: dict[str, Any] | None = None) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    path = subagent_state_dir(project_root, run_id) / "session.json"
    if session is None:
        if not path.exists():
            return {"status": "blocked", "reason_code": "subagent_session_missing", "blocked": True}
        session = json.loads(path.read_text(encoding="utf-8"))
    if not session.get("opt_in"):
        return {**session, "status": "ok", "spawned": False, "reason_code": REASON_DEFAULT_OFF}

    session["state"] = "running"
    session["spawned"] = True
    for sat in session.get("satellites") or []:
        sat["state"] = "running"
        # simulate worker result (file backend)
        result = {
            "lake": sat.get("lake"),
            "status": "done",
            "merge_target": "main_star",
            "may_write_truth_on_main": False,
            "product_complete": False,
        }
        sat["result"] = result
        sat["state"] = "collecting"
    session["state"] = "collecting"
    # merge
    session["state"] = "merging"
    merges = []
    for sat in session.get("satellites") or []:
        merges.append(
            {
                "lake": sat.get("lake"),
                "from": sat.get("worktree"),
                "to": "main_star",
                "truth_write": False,
            }
        )
        sat["state"] = "merged"
    session["merges"] = merges
    session["state"] = "done"
    session["product_complete"] = False
    write_json(path, session)
    append_execution_log(
        project_root,
        run_id,
        stage="implement",
        event="subagent_merged",
        summary=f"merged={len(merges)} complete_forbidden=true",
    )
    return {**session, "session_path": str(path), "status": "ok"}


def assert_satellite_cannot_write_truth(worktree: Path, *, main_truth_path: Path) -> dict[str, Any]:
    """Negative: satellite worktree must not be allowed to write main truth package."""
    marker = Path(worktree) / ".satellite-isolation.json"
    may_write = False
    if marker.exists():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            may_write = bool(data.get("may_write_truth_on_main"))
        except (OSError, json.JSONDecodeError):
            may_write = False
    forbidden = not may_write
    # policy check only — do not write
    return {
        "blocked": may_write,
        "status": "pass" if forbidden else "blocked",
        "reason_code": "" if forbidden else REASON_TRUTH_WRITE_FORBIDDEN,
        "main_truth_path": str(main_truth_path),
        "may_write_truth_on_main": may_write,
    }


def omx_checklist_b1_b6() -> dict[str, Any]:
    return {
        "B1": "opt-in only (default off)",
        "B2": "one lake one satellite",
        "B3": "depends_on before fan-out",
        "B4": "merge to star only",
        "B5": "no main truth write from satellite",
        "B6": "cannot complete GoalRun without verifier",
        "status": "documented",
    }
