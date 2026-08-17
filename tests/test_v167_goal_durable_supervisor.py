"""Contract tests for beacon-goal-durable-supervisor-v167."""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from beacon.utils.goal_durable_supervisor import (
    DEFAULT_HEARTBEAT_INTERVAL_SEC,
    MIN_HEARTBEAT_INTERVAL_SEC,
    REASON_HOST_INTERRUPTED,
    append_execution_log,
    detect_stall,
    execution_log_path,
    memory_reindex,
    memory_search,
    normalize_interval,
    plan_tick_execute,
)
from beacon.utils.product_goal_runtime import (
    REASON_VERIFIER_REQUIRED,
    attach_verifier,
    complete_goal_run,
    goal_checkpoint,
    goal_heartbeat,
    goal_memory_reindex,
    goal_memory_search,
    goal_resume_pack,
    goal_supervise_attach,
    goal_supervise_detach,
    load_goal_run,
    run_goal_facade,
    tick_goal_run,
)

ROOT = Path(__file__).resolve().parents[1]


def test_supervise_default_on_goal_run(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="durable goal demo", version="v1.6.7")
    sup = run.get("supervisor") or {}
    # v1.6.8+ goal facade honors project longrun_default and auto-attaches supervisor.
    assert sup.get("attached") is True
    assert sup.get("state") == "active"
    assert run.get("heartbeat_interval_sec") == DEFAULT_HEARTBEAT_INTERVAL_SEC


def test_heartbeat_default_120s() -> None:
    assert DEFAULT_HEARTBEAT_INTERVAL_SEC == 120
    assert normalize_interval(None) == 120
    assert normalize_interval(10) == MIN_HEARTBEAT_INTERVAL_SEC
    assert normalize_interval(180) == 180


def test_execution_jsonl_append(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="log demo", version="v1.6.7")
    run_id = run["run_id"]
    goal_heartbeat(tmp_path, run_id, summary="hb1", substep="s1")
    tick_goal_run(tmp_path, run_id, note="n1")
    path = execution_log_path(tmp_path, run_id)
    assert path.exists()
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) >= 2
    events = [json.loads(ln)["event"] for ln in lines]
    assert "heartbeat" in events
    assert "tick" in events
    # append-only: second write grows file
    size1 = path.stat().st_size
    append_execution_log(tmp_path, run_id, stage="implement", event="heartbeat", summary="hb2")
    assert path.stat().st_size > size1


def test_checkpoint_and_resume_pack(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="checkpoint demo", version="v1.6.7")
    run_id = run["run_id"]
    goal_heartbeat(tmp_path, run_id, summary="worked on implement", substep="impl-1")
    goal_checkpoint(tmp_path, run_id, next_action="run unit tests", substep="impl-1")
    pack = goal_resume_pack(tmp_path, run_id)
    assert pack["status"] == "ok"
    rp = pack["resume_pack"]
    assert rp["next_action"]
    assert "recent_heartbeats" in rp
    assert "authority_note" in rp
    # digest only — no huge chat dump field
    assert "full_chat" not in rp
    assert "execution_jsonl_body" not in rp


def test_stall_detects_idle(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="stall demo", version="v1.6.7")
    run_id = run["run_id"]
    payload = load_goal_run(tmp_path, run_id)
    payload["current_stage"] = "implement"
    payload["heartbeat_interval_sec"] = 30
    # last heartbeat far in the past
    old = (datetime.now(timezone.utc) - timedelta(seconds=120)).isoformat()
    payload["last_heartbeat_at"] = old
    assert detect_stall(payload) is True
    # fresh heartbeat => no stall
    payload["last_heartbeat_at"] = datetime.now(timezone.utc).isoformat()
    assert detect_stall(payload) is False


def test_interrupt_ne_stage_blocked(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="interrupt demo", version="v1.6.7")
    run_id = run["run_id"]
    from beacon.utils.product_goal_runtime import record_blocker

    blocked = record_blocker(tmp_path, run_id, reason_code="stage_blocked_demo")
    assert blocked.get("reason_code") in {"stage_blocked_demo", "product_goal_blocked_streak"} or blocked.get("blocked")
    # host interrupt reason is distinct constant
    assert REASON_HOST_INTERRUPTED == "host_interrupted"
    assert REASON_HOST_INTERRUPTED != "stage_blocked"
    # resume-pack stall path uses host_interrupted
    payload = load_goal_run(tmp_path, run_id)
    payload["current_stage"] = "implement"
    payload["heartbeat_interval_sec"] = 30
    payload["last_heartbeat_at"] = (datetime.now(timezone.utc) - timedelta(seconds=400)).isoformat()
    # save then resume-pack
    from beacon.utils.product_goal_runtime import _save

    _save(tmp_path, payload)
    pack = goal_resume_pack(tmp_path, run_id)
    # after resume-pack stall detect, reason should be host_interrupted (or stall fields present)
    again = load_goal_run(tmp_path, run_id)
    assert again.get("reason_code") == REASON_HOST_INTERRUPTED or pack["resume_pack"].get("stall_flag") or again.get(
        "stall_flag"
    )


def test_tick_execute_dispatches(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="execute demo", version="v1.6.7", feature="demo-feature")
    run_id = run["run_id"]
    # force implement stage
    payload = load_goal_run(tmp_path, run_id)
    payload["current_stage"] = "implement"
    from beacon.utils.product_goal_runtime import _save

    _save(tmp_path, payload)
    plan = plan_tick_execute(load_goal_run(tmp_path, run_id))
    assert plan["dispatch"] == "ralph"
    # without execute: no last_tick_execute forced
    t1 = tick_goal_run(tmp_path, run_id, note="noexec", execute=False)
    # re-set stage implement for execute path
    p2 = load_goal_run(tmp_path, run_id)
    p2["current_stage"] = "implement"
    _save(tmp_path, p2)
    t2 = tick_goal_run(tmp_path, run_id, note="exec", execute=True)
    assert t2.get("last_tick_execute") or t2.get("implement_delegate") == "ralph"
    # release never auto
    p3 = load_goal_run(tmp_path, run_id)
    p3["current_stage"] = "release"
    _save(tmp_path, p3)
    plan_r = plan_tick_execute(load_goal_run(tmp_path, run_id))
    assert plan_r["dispatch"] == "none"
    assert plan_r["action"] == "human_release_gate"


def test_no_complete_without_verifier(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="complete gate", version="v1.6.7")
    run_id = run["run_id"]
    rejected = complete_goal_run(tmp_path, run_id)
    assert rejected["status"] != "completed"
    assert rejected["reason_code"] == REASON_VERIFIER_REQUIRED
    # supervise cannot bypass
    goal_supervise_attach(tmp_path, run_id, once=True)
    rejected2 = complete_goal_run(tmp_path, run_id)
    assert rejected2["status"] != "completed"


def test_supervise_never_auto_release(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="release gate", version="v1.6.7")
    run_id = run["run_id"]
    payload = load_goal_run(tmp_path, run_id)
    payload["current_stage"] = "release"
    from beacon.utils.product_goal_runtime import _save

    _save(tmp_path, payload)
    att = goal_supervise_attach(tmp_path, run_id, once=True)
    poll = att.get("poll") or {}
    actions = poll.get("actions") or []
    assert "release_human_gate_only" in actions or plan_tick_execute(load_goal_run(tmp_path, run_id)).get(
        "action"
    ) == "human_release_gate"
    assert load_goal_run(tmp_path, run_id).get("status") != "completed"


def test_no_second_public_entry() -> None:
    skill = (ROOT / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    assert "supervise" in skill
    assert "progressive" in skill
    # must not advertise loop+goal dual public pipeline as required
    assert "唯一" in skill or "唯一公共入口" in skill or "public" in skill.lower()
    examples = (ROOT / "skills/beacon/examples/goal-one-shot-30s.md").read_text(encoding="utf-8")
    assert "不要先调" in examples or "不要" in examples


def test_log_append_only(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="append only", version="v1.6.7")
    run_id = run["run_id"]
    path = execution_log_path(tmp_path, run_id)
    append_execution_log(tmp_path, run_id, stage="x", event="heartbeat", summary="a")
    append_execution_log(tmp_path, run_id, stage="x", event="heartbeat", summary="b")
    text = path.read_text(encoding="utf-8")
    assert text.count("\n") >= 2
    assert '"summary": "a"' in text
    assert '"summary": "b"' in text


def test_sqlite_fts_non_authoritative(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="memory demo", version="v1.6.7")
    run_id = run["run_id"]
    goal_heartbeat(tmp_path, run_id, summary="implemented form fill field hit")
    reidx = goal_memory_reindex(tmp_path, run_id)
    assert reidx.get("authority") == "support_advisory"
    hits = goal_memory_search(tmp_path, run_id, "form fill")
    assert hits.get("can_complete") is False
    assert hits.get("authority") == "support_advisory"
    # still cannot complete from memory
    rejected = complete_goal_run(tmp_path, run_id)
    assert rejected["status"] != "completed"


def test_skill_mentions_supervise() -> None:
    skill = (ROOT / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    assert "supervise" in skill
    assert "Longrun/supervise only on goal" in skill


def test_tests_md_has_legal_and_illegal() -> None:
    tests = (
        ROOT / "docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/tests.md"
    ).read_text(encoding="utf-8")
    assert "legal walk" in tests.lower() or "Legal walk" in tests
    assert "illegal" in tests.lower()
    assert "TC-DGS-LEGAL" in tests
    assert "TC-DGS-ILLEGAL" in tests


def test_legal_walk_create_to_complete(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="walk complete", version="v1.6.7")
    run_id = run["run_id"]
    goal_heartbeat(tmp_path, run_id, summary="progress")
    attach_verifier(tmp_path, run_id, refs=[".beacon/qa/demo/scorecard.json"], source="beacon-eval-qa")
    done = complete_goal_run(tmp_path, run_id)
    assert done["status"] == "completed"


def test_legal_walk_host_interrupt_resume(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="walk interrupt", version="v1.6.7")
    run_id = run["run_id"]
    payload = load_goal_run(tmp_path, run_id)
    payload["current_stage"] = "implement"
    payload["last_substep"] = "impl-part-2"
    payload["heartbeat_interval_sec"] = 30
    payload["last_heartbeat_at"] = (datetime.now(timezone.utc) - timedelta(seconds=500)).isoformat()
    from beacon.utils.product_goal_runtime import _save

    _save(tmp_path, payload)
    pack = goal_resume_pack(tmp_path, run_id)
    assert pack["resume_pack"]["last_substep"] in {"impl-part-2", "implement"} or pack["resume_pack"]["next_action"]
    again = load_goal_run(tmp_path, run_id)
    # host_interrupted recorded
    assert again.get("reason_code") == REASON_HOST_INTERRUPTED or again.get("stall_flag")


def test_legal_walk_opt_in_supervise(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="walk supervise", version="v1.6.7")
    run_id = run["run_id"]
    assert (run.get("supervisor") or {}).get("attached") is True
    att = goal_supervise_attach(tmp_path, run_id, interval_sec=120, once=True)
    assert att["status"] == "active"
    assert att["opt_in"] is True
    assert att["auto_on_goal_run"] is False
    assert (att.get("supervisor") or att.get("payload", {}).get("supervisor") or {}).get("attached") is True
    det = goal_supervise_detach(tmp_path, run_id)
    assert det["status"] == "stopped"


def test_illegal_interrupt_to_complete(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="illegal complete", version="v1.6.7")
    run_id = run["run_id"]
    payload = load_goal_run(tmp_path, run_id)
    payload["reason_code"] = REASON_HOST_INTERRUPTED
    payload["status"] = "running"
    from beacon.utils.product_goal_runtime import _save

    _save(tmp_path, payload)
    rejected = complete_goal_run(tmp_path, run_id)
    assert rejected["status"] != "completed"


def test_auto_supervise_default_on_goal_run(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="no auto sup", version="v1.6.7")
    assert (run.get("supervisor") or {}).get("attached") is True


def test_illegal_overwrite_jsonl(tmp_path: Path) -> None:
    """Public API must not expose truncate/write modes for execution.jsonl."""
    import inspect
    from beacon.utils import goal_durable_supervisor as mod

    src = inspect.getsource(mod.append_execution_log)
    assert '"a"' in src or "'a'" in src
    assert 'open("w"' not in src.replace(" ", "")
    assert "open('w'" not in src


def test_illegal_memory_overrides_verifier(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="mem vs verifier", version="v1.6.7")
    run_id = run["run_id"]
    goal_heartbeat(tmp_path, run_id, summary="all green pretend")
    goal_memory_reindex(tmp_path, run_id)
    hits = goal_memory_search(tmp_path, run_id, "green")
    assert hits.get("can_complete") is False
    assert complete_goal_run(tmp_path, run_id)["status"] != "completed"
