"""v2.0.0 Loom goal trace bundle tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

from beacon.utils.agent_trace import EVENT_TYPES, read_trace_events, trace_path
from beacon.utils.goal_agent_driver import driver_run_once, driver_start
from beacon.utils.goal_durable_supervisor import append_execution_log, execution_log_path
from beacon.utils.loom_trace import (
    aggregate_goal_trace,
    assert_no_full_chat_authority,
    event_types_contract,
    record_driver_turn_trace,
)
from beacon.utils.product_goal_runtime import run_goal_facade


def _fake_spawn(code=0):
    def _spawn(argv, cwd, timeout):
        return subprocess.CompletedProcess(list(argv), code, stdout="ok", stderr="")

    return _spawn


def test_driver_writes_trace(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="trace longrun", version="v2.0.0")
    rid = run["run_id"]
    driver_start(tmp_path, rid, longrun=True, run_loop=False, bridge_cmd="true")
    driver_run_once(tmp_path, rid, spawn_fn=_fake_spawn(), bridge_cmd="true")
    events = read_trace_events(tmp_path, rid)
    assert events, "expected agent_trace events from driver turn"
    types = {e.get("event_type") for e in events}
    assert "tool_call" in types or "output" in types


def test_trace_path(tmp_path: Path) -> None:
    p = trace_path(tmp_path, "r1")
    assert p.name == "r1.jsonl"
    assert ".beacon" in str(p) and "traces" in str(p)


def test_event_types() -> None:
    c = event_types_contract()
    assert "tool_call" in c["event_types"]
    assert "output" in c["event_types"]
    assert set(c["event_types"]) == set(EVENT_TYPES)


def test_cli_trace_aggregate(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="agg", version="v2.0.0")
    rid = run["run_id"]
    record_driver_turn_trace(tmp_path, rid, turn_n=1, prompt_path="p.md", exit_code=0)
    agg = aggregate_goal_trace(tmp_path, rid)
    assert agg["status"] == "ok"
    assert agg["agent_event_count"] >= 2
    assert agg["full_chat_authority"] is False


def test_no_full_chat() -> None:
    payload = {"full_chat_authority": False, "authority": "resume-pack-digest"}
    assert assert_no_full_chat_authority(payload)["ok"] is True
    bad = assert_no_full_chat_authority({"full_chat_authority": True, "authority": "full_chat"})
    assert bad["ok"] is False


def test_verbose_path_only(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="v", version="v2.0.0")
    rid = run["run_id"]
    record_driver_turn_trace(tmp_path, rid, turn_n=1, prompt_path="/tmp/turn-1.prompt.md")
    agg = aggregate_goal_trace(tmp_path, rid, verbose=True)
    assert agg["verbose_mode"] == "path_refs_and_events"
    blob = str(agg)
    assert "full_chat" not in blob or agg["full_chat_authority"] is False


def test_dual_logs(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="dual", version="v2.0.0")
    rid = run["run_id"]
    append_execution_log(tmp_path, rid, stage="implement", event="heartbeat", summary="h")
    record_driver_turn_trace(tmp_path, rid, turn_n=1)
    assert execution_log_path(tmp_path, rid).exists()
    assert trace_path(tmp_path, rid).exists()
    agg = aggregate_goal_trace(tmp_path, rid)
    assert agg["dual_channel"] is True


def test_resume_digest(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="rd", version="v2.0.0")
    agg = aggregate_goal_trace(tmp_path, run["run_id"])
    assert agg["authority"] == "resume-pack-digest"


def test_index_update(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="idx", version="v2.0.0")
    rid = run["run_id"]
    record_driver_turn_trace(tmp_path, rid, turn_n=1)
    agg = aggregate_goal_trace(tmp_path, rid)
    assert agg["agent_event_count"] >= 1


def test_legal_illegal() -> None:
    tests = Path(__file__).resolve().parents[1] / "docs/beacon/v2.0.0/features/loom-goal-trace-bundle/tests.md"
    text = tests.read_text(encoding="utf-8")
    assert "legal" in text.lower() and "illegal" in text.lower()
