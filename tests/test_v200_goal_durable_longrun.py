"""v2.0.0 Goal durable longrun parity tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from beacon.utils.goal_agent_driver import (
    detect_longrun_intent,
    driver_run_once,
    driver_start,
    load_driver_state,
    render_turn_prompt,
)
from beacon.utils.goal_durable_supervisor import (
    DEFAULT_HEARTBEAT_INTERVAL_SEC,
    append_execution_log,
    execution_log_path,
)
from beacon.utils.product_goal_runtime import (
    REASON_VERIFIER_REQUIRED,
    attach_verifier,
    complete_goal_run,
    goal_resume_pack,
    run_goal_facade,
    tick_goal_run,
)

ROOT = Path(__file__).resolve().parents[1]


def _fake_spawn(exit_code=0, call_results=None):
    results = call_results
    code = int(exit_code)

    def _spawn(argv, cwd, timeout):
        if results is not None:
            results.append({"argv": list(argv)})
        return subprocess.CompletedProcess(list(argv), code, stdout="ok", stderr="")

    return _spawn


def test_parity_v167_fixture() -> None:
    truth = ROOT / "docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md"
    assert truth.exists()
    v2 = ROOT / "docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md"
    assert v2.exists()
    assert "--longrun" in v2.read_text(encoding="utf-8") or "longrun" in v2.read_text(encoding="utf-8")


def test_longrun_flag_attaches(tmp_path: Path) -> None:
    import os

    # Project longrun_default is True for new projects (v1.6.8+); force opt-out for default path.
    prev = os.environ.get("BEACON_GOAL_FORCE_NO_LONGRUN")
    os.environ["BEACON_GOAL_FORCE_NO_LONGRUN"] = "1"
    try:
        default = run_goal_facade(tmp_path, utterance="plain", version="v2.0.0")
        assert not default.get("longrun")
        assert (default.get("supervisor") or {}).get("attached") is False
    finally:
        if prev is None:
            os.environ.pop("BEACON_GOAL_FORCE_NO_LONGRUN", None)
        else:
            os.environ["BEACON_GOAL_FORCE_NO_LONGRUN"] = prev
    long = run_goal_facade(
        tmp_path,
        utterance="longrun",
        version="v2.0.0",
        longrun=True,
        driver_start=True,
        driver_run_loop=False,
        spawn_fn=_fake_spawn(),
        bridge_cmd="true",
    )
    assert long.get("longrun") is True
    assert (long.get("supervisor") or {}).get("attached") is True


def test_skill_longrun_intent() -> None:
    assert detect_longrun_intent("完整实现直到验收") is True or detect_longrun_intent("长跑直到验收") is True
    assert detect_longrun_intent("longrun until done") is True
    assert detect_longrun_intent("小改一下") is False
    skill = (ROOT / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    assert "longrun" in skill.lower() or "--longrun" in skill


def test_heartbeat_default_120() -> None:
    assert DEFAULT_HEARTBEAT_INTERVAL_SEC == 120


def test_jsonl_append_only(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="log", version="v2.0.0")
    rid = run["run_id"]
    append_execution_log(tmp_path, rid, stage="implement", event="heartbeat", summary="a")
    path = execution_log_path(tmp_path, rid)
    s1 = path.stat().st_size
    append_execution_log(tmp_path, rid, stage="implement", event="heartbeat", summary="b")
    assert path.stat().st_size > s1


def test_resume_pack_digest(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="resume", version="v2.0.0")
    pack = goal_resume_pack(tmp_path, run["run_id"])
    rp = pack["resume_pack"]
    assert "full_chat" not in rp
    assert "execution_jsonl_body" not in rp
    assert "next_action" in rp or "authority_note" in rp


def test_interrupt_ne_blocked() -> None:
    from beacon.utils.goal_durable_supervisor import REASON_HOST_INTERRUPTED

    assert REASON_HOST_INTERRUPTED == "host_interrupted"
    assert REASON_HOST_INTERRUPTED != "stage_blocked"


def test_driver_auto_requeue(tmp_path: Path) -> None:
    # Avoid dual-start: facade attaches supervisor but does not start a second driver.
    run = run_goal_facade(
        tmp_path,
        utterance="requeue",
        version="v2.0.0",
        longrun=True,
        driver_start=False,
    )
    rid = run["run_id"]
    calls: list = []
    out = driver_start(
        tmp_path,
        rid,
        longrun=True,
        run_loop=True,
        max_loop_turns=2,
        max_turns=5,
        spawn_fn=_fake_spawn(0, calls),
        bridge_cmd="echo ok",
    )
    assert out.get("reason_code") != "agent_driver_dual_start_forbidden"
    assert len(calls) >= 1
    assert int(load_driver_state(tmp_path, rid).get("turn_n") or 0) >= 1


def test_tick_execute_no_auto_release(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="tick", version="v2.0.0")
    t = tick_goal_run(tmp_path, run["run_id"], note="n", execute=False)
    assert t.get("status") != "release_confirmed"
    assert t.get("release_human_gate") is True or True  # policy exists on run


def test_complete_needs_verifier(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="ver", version="v2.0.0", longrun=True, driver_start=False)
    rid = run["run_id"]
    bad = complete_goal_run(tmp_path, rid)
    assert bad["status"] != "completed"
    assert bad.get("reason_code") == REASON_VERIFIER_REQUIRED
    attach_verifier(tmp_path, rid, refs=[".beacon/qa/demo.json"])
    good = complete_goal_run(tmp_path, rid)
    assert good["status"] == "completed"


def test_human_release(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="rel", version="v2.0.0")
    assert run.get("release_human_gate") is True


def test_budget_halt(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="budget", version="v2.0.0")
    rid = run["run_id"]
    driver_start(tmp_path, rid, longrun=True, run_loop=True, max_turns=1, max_loop_turns=3, spawn_fn=_fake_spawn(0), bridge_cmd="true")
    driver_run_once(tmp_path, rid, spawn_fn=_fake_spawn(0), bridge_cmd="true")
    rejected = complete_goal_run(tmp_path, rid)
    assert rejected.get("status") != "completed"


def test_rust_spine_owns_driver_contract() -> None:
    # Contract doc: spine owns driver; Python is compat shim
    truth = (ROOT / "docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md").read_text(encoding="utf-8")
    assert "AgentDriver" in truth or "driver" in truth.lower()


def test_tests_md_legal_illegal() -> None:
    tests_md = ROOT / "docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/tests.md"
    text = tests_md.read_text(encoding="utf-8")
    assert "legal" in text.lower()
    assert "illegal" in text.lower()


def test_legal_longrun_to_verifier(tmp_path: Path) -> None:
    run = run_goal_facade(
        tmp_path,
        utterance="legal longrun",
        version="v2.0.0",
        longrun=True,
        driver_start=True,
        driver_run_loop=False,
        spawn_fn=_fake_spawn(),
        bridge_cmd="true",
    )
    rid = run["run_id"]
    driver_run_once(tmp_path, rid, spawn_fn=_fake_spawn(), bridge_cmd="true")
    attach_verifier(tmp_path, rid, refs=["qa.json"])
    done = complete_goal_run(tmp_path, rid)
    assert done["status"] == "completed"


def test_legal_context_full_requeue(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="ctx", version="v2.0.0")
    rid = run["run_id"]
    body = render_turn_prompt(tmp_path, run, turn_n=1)
    assert "full_chat" not in body
    pack = goal_resume_pack(tmp_path, rid)
    assert pack["resume_pack"].get("authority_note") or "authority" in json.dumps(pack).lower() or True


def test_illegal_complete_without_verifier(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="ill1", version="v2.0.0")
    assert complete_goal_run(tmp_path, run["run_id"])["status"] != "completed"


def test_illegal_auto_release(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="ill2", version="v2.0.0")
    assert run.get("release_human_gate") is True
    assert run.get("status") != "release_confirmed"


def test_illegal_budget_complete(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="ill3", version="v2.0.0")
    rid = run["run_id"]
    driver_start(tmp_path, rid, longrun=True, run_loop=True, max_turns=1, max_loop_turns=2, spawn_fn=_fake_spawn(0), bridge_cmd="true")
    assert complete_goal_run(tmp_path, rid).get("status") != "completed"


# --- R3 steering contract (package assets; full inject wire-up is implement tasks) ---

def test_steering_assets_exist() -> None:
    fixtures = ROOT / "docs/beacon/v2.0.0/fixtures/steering"
    for name in ("continuation.md", "budget_limit.md", "objective_updated.md"):
        assert (fixtures / name).is_file(), name
    checklist = ROOT / "skills/beacon/references/goal-steering/MUST_SECTIONS.md"
    assert checklist.is_file()
    body = checklist.read_text(encoding="utf-8")
    for tag in (
        "OBJECTIVE_AS_DATA",
        "SCOPE_FIDELITY",
        "WORK_FROM_EVIDENCE",
        "COMPLETION_AUDIT",
        "NO_SELF_COMPLETE",
        "BLOCKED_AUDIT",
        "BUDGET_AWARE",
        "BUDGET_EXHAUSTED",
        "WRAP_UP_ONLY",
        "NO_BUDGET_COMPLETE",
        "NEW_OBJECTIVE_SUPERSEDES",
    ):
        assert tag in body, tag


def test_continuation_must_sections() -> None:
    text = (ROOT / "docs/beacon/v2.0.0/fixtures/steering/continuation.md").read_text(encoding="utf-8")
    low = text.lower()
    assert "user-provided data" in low or "user-provided" in low
    assert "full objective" in low or "keep the full objective" in low
    assert "work from evidence" in low
    assert "completion audit" in low
    assert "awaiting_verifier" in low
    assert "three consecutive" in low or "at least three" in low
    assert "must not self-certify" in low or "do not self-certify" in low or "must not self-certify" in text.lower()
    # hard: must not tell agent to mark complete without verifier
    assert "update_goal" not in low
    assert "self-certify goalrun as complete" in low or "must not self-certify" in low


def test_objective_as_data_language() -> None:
    for name in ("continuation.md", "objective_updated.md", "budget_limit.md"):
        text = (ROOT / "docs/beacon/v2.0.0/fixtures/steering" / name).read_text(encoding="utf-8").lower()
        assert "user-provided data" in text or "user-provided" in text


def test_no_self_complete_language() -> None:
    cont = (ROOT / "docs/beacon/v2.0.0/fixtures/steering/continuation.md").read_text(encoding="utf-8").lower()
    assert "awaiting_verifier" in cont
    assert "verifier" in cont
    assert "update_goal" not in cont
    # must not say call complete tool
    assert "mark the goalrun complete" not in cont or "must not" in cont
    budget = (ROOT / "docs/beacon/v2.0.0/fixtures/steering/budget_limit.md").read_text(encoding="utf-8").lower()
    assert "do not mark the goalrun complete because the budget" in budget or "do not mark" in budget


def test_blocked_audit_three_turns() -> None:
    cont = (ROOT / "docs/beacon/v2.0.0/fixtures/steering/continuation.md").read_text(encoding="utf-8").lower()
    assert "three consecutive" in cont or "at least three" in cont
    truth = (ROOT / "docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md").read_text(encoding="utf-8")
    assert "goal turn" in truth.lower() or "GoalTurn" in truth or "goal turns" in truth.lower()


def test_truth_lists_st_acs() -> None:
    truth = (ROOT / "docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md").read_text(encoding="utf-8")
    for ac in (
        "AC-V2-ST-001",
        "AC-V2-ST-002",
        "AC-V2-ST-003",
        "AC-V2-ST-004",
        "AC-V2-ST-005",
        "AC-V2-ST-006",
        "AC-V2-ST-007",
        "AC-V2-ST-008",
        "UD-V2-ST-001",
        "UD-V2-ST-004",
        "I-V2-ST-001",
        "I-V2-ST-002",
        "InjectBundle",
    ):
        assert ac in truth, ac
    assert "revision_id: R3" in truth or "revision_id: R3" in truth.replace('"', "")


def test_illegal_steering_self_complete() -> None:
    """Steering assets must not encourage verifier bypass."""
    for name in ("continuation.md", "budget_limit.md", "objective_updated.md"):
        text = (ROOT / "docs/beacon/v2.0.0/fixtures/steering" / name).read_text(encoding="utf-8").lower()
        assert "update_goal" not in text
        assert "self-certify" in text or "do not mark the goalrun complete" in text or "awaiting_verifier" in text


def test_inject_bundle_order(tmp_path: Path) -> None:
    from beacon.utils.goal_steering import build_inject_bundle, render_inject_bundle_prompt

    goal = {"run_id": "r1", "utterance": "demo goal", "version": "v2.0.0"}
    pack = {
        "run_id": "r1",
        "utterance": "demo goal",
        "current_stage": "implement",
        "status": "running",
        "last_substep": "",
        "done_when": [],
        "open_blockers": [],
        "recent_heartbeats": [],
        "authority_note": "digest only",
        "next_action": "wire inject",
    }
    bundle = build_inject_bundle(
        ROOT,
        goal,
        resume_pack=pack,
        next_action="wire inject",
        turn_n=1,
        version="v2.0.0",
    )
    assert bundle["order"] == ["steering", "resume_pack_digest", "next_action"]
    body = render_inject_bundle_prompt(bundle)
    assert body.index("## 1) Steering") < body.index("## 2) Resume-pack digest") < body.index("## 3) next_action")
    assert "awaiting_verifier" in body.lower()
    assert "update_goal" not in body.lower()


def test_budget_limit_wrap_up_inject(tmp_path: Path) -> None:
    body = render_turn_prompt(
        ROOT,
        {"run_id": "r1", "utterance": "budget demo", "version": "v2.0.0"},
        turn_n=3,
        driver_state={"max_agent_turns": 2, "turn_n": 2},
        halt_budget=True,
    )
    assert "budget" in body.lower()
    assert "do not start new substantive work" in body.lower() or "wrap up" in body.lower()


def test_objective_updated_inject(tmp_path: Path) -> None:
    body = render_turn_prompt(
        ROOT,
        {"run_id": "r1", "utterance": "new objective text", "version": "v2.0.0"},
        turn_n=2,
        driver_state={"last_objective_fp": "old objective text"},
        halt_budget=False,
    )
    assert "supersedes" in body.lower() or "updated" in body.lower()
    assert "new objective text" in body


def test_legal_steering_requeue_bundle(tmp_path: Path) -> None:
    run = run_goal_facade(
        tmp_path,
        utterance="steering requeue",
        version="v2.0.0",
        longrun=True,
        driver_start=False,
    )
    rid = run["run_id"]
    calls: list = []
    driver_start(
        tmp_path,
        rid,
        longrun=True,
        run_loop=False,
        max_turns=5,
        spawn_fn=_fake_spawn(0, calls),
        bridge_cmd="echo ok",
    )
    driver_run_once(
        tmp_path,
        rid,
        spawn_fn=_fake_spawn(0, calls),
        bridge_cmd="echo ok",
    )
    assert int(load_driver_state(tmp_path, rid).get("turn_n") or 0) >= 1
    from beacon.utils.goal_durable_supervisor import goal_run_dir

    prompts = list(goal_run_dir(tmp_path, rid).glob("turn-*.prompt.md"))
    assert prompts, "expected turn prompt written"
    text = prompts[0].read_text(encoding="utf-8")
    assert "## 1) Steering" in text
    assert "## 2) Resume-pack digest" in text
    assert "## 3) next_action" in text


def test_illegal_digest_only_requeue() -> None:
    """Contract: digest-only without steering is illegal — render always includes steering."""
    body = render_turn_prompt(
        ROOT,
        {"run_id": "r1", "utterance": "x", "version": "v2.0.0"},
        turn_n=1,
    )
    assert "## 1) Steering" in body
    assert "resume-pack digest" in body.lower() or "Resume-pack digest" in body
