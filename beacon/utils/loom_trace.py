"""Loom Goal trace bundle: aggregate agent_trace + execution.jsonl for a run."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.agent_trace import (
    EVENT_TYPES,
    SCHEMA_VERSION,
    append_event,
    build_event,
    get_run_trace_index,
    read_trace_events,
    trace_path,
)
from beacon.utils.goal_durable_supervisor import execution_log_path, read_execution_log_tail


def record_driver_turn_trace(
    project_root: Path,
    run_id: str,
    *,
    turn_n: int,
    prompt_path: str = "",
    exit_code: int = 0,
    summary: str = "",
) -> dict[str, Any]:
    """Hook: driver turn → agent_trace append (path refs only, no full chat)."""
    call_ev = build_event(
        run_id=run_id,
        event_type="tool_call",
        summary=f"driver turn {turn_n}",
        iteration=turn_n,
        payload={
            "turn_n": turn_n,
            "prompt_path": prompt_path,
            "authority": "resume-pack-digest",
        },
        harness="goal-driver",
    )
    out1 = append_event(project_root, call_ev)
    out_ev = build_event(
        run_id=run_id,
        event_type="output",
        summary=summary or f"turn {turn_n} exit={exit_code}",
        iteration=turn_n,
        payload={"turn_n": turn_n, "exit_code": exit_code, "chat_body": None},
        harness="goal-driver",
    )
    out2 = append_event(project_root, out_ev)
    return {
        "status": "ok" if out1.get("status") == "pass" and out2.get("status") == "pass" else "blocked",
        "run_id": run_id,
        "trace_path": str(trace_path(project_root, run_id)),
        "events_appended": 2,
        "results": [out1, out2],
    }


def aggregate_goal_trace(project_root: Path, run_id: str, *, verbose: bool = False) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    agent_events = read_trace_events(project_root, run_id)
    exec_tail = read_execution_log_tail(project_root, run_id, limit=50)
    index = get_run_trace_index(project_root, run_id) or {}
    dual = bool(agent_events) or execution_log_path(project_root, run_id).exists()
    sanitized = []
    for ev in agent_events:
        item = dict(ev)
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        if "full_chat" in payload:
            payload = {k: v for k, v in payload.items() if k != "full_chat"}
            item["payload"] = payload
        sanitized.append(item)
    result: dict[str, Any] = {
        "schema": "loom-goal-trace-bundle.v1",
        "run_id": run_id,
        "agent_trace_schema": SCHEMA_VERSION,
        "agent_trace_path": str(trace_path(project_root, run_id)),
        "execution_log_path": str(execution_log_path(project_root, run_id)),
        "agent_event_count": len(sanitized),
        "execution_event_count": len(exec_tail),
        "dual_channel": dual,
        "index": index,
        "status": "ok",
        "authority": "resume-pack-digest",
        "full_chat_authority": False,
    }
    if verbose:
        # path refs + events (no full chat body)
        result["agent_events"] = sanitized
        result["execution_tail"] = exec_tail
        result["verbose_mode"] = "path_refs_and_events"
    else:
        result["agent_event_types"] = [str(e.get("event_type") or "") for e in sanitized]
        result["verbose_mode"] = "summary"
    return result


def assert_no_full_chat_authority(payload: dict[str, Any]) -> dict[str, Any]:
    ok = payload.get("full_chat_authority") is False
    # reject if payload claims full chat as authority
    if payload.get("authority") == "full_chat":
        ok = False
    return {"ok": ok, "blocked": not ok, "status": "pass" if ok else "blocked"}


def event_types_contract() -> dict[str, Any]:
    return {"schema": SCHEMA_VERSION, "event_types": sorted(EVENT_TYPES)}
