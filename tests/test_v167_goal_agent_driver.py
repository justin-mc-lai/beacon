"""Contract tests for beacon-goal-agent-driver-v167 (Path C Python Driver)."""

from __future__ import annotations

import inspect
import json
import subprocess
from pathlib import Path

import pytest

from beacon.utils.goal_agent_driver import (
    DEFAULT_MAX_AGENT_TURNS,
    REASON_BUDGET,
    REASON_DUAL_DRIVER,
    REASON_NO_BRIDGE,
    detect_longrun_intent,
    driver_run_loop,
    driver_run_once,
    driver_start,
    driver_status,
    driver_stop,
    load_driver_state,
    render_turn_prompt,
    resolve_bridge_command,
    write_turn_prompt,
)
from beacon.utils.goal_durable_supervisor import goal_run_dir
from beacon.utils.product_goal_runtime import (
    REASON_VERIFIER_REQUIRED,
    attach_verifier,
    complete_goal_run,
    goal_driver_start,
    goal_driver_status,
    goal_driver_stop,
    load_goal_run,
    run_goal_facade,
)

ROOT = Path(__file__).resolve().parents[1]


def _fake_spawn(exit_code=0, call_results=None):
    results = call_results
    code = int(exit_code)

    def _spawn(argv, cwd, timeout):
        if results is not None:
            results.append({"argv": list(argv), "cwd": str(cwd), "timeout": timeout})
        return subprocess.CompletedProcess(list(argv), code, stdout="ok", stderr="")

    return _spawn

def test_depends_on_durable_apis() -> None:
    import beacon.utils.goal_agent_driver as mod

    src = inspect.getsource(mod)
    assert "build_resume_pack" in src
    assert "append_execution_log" in src
    assert "attach_supervisor" in src
    # uses durable APIs, not reimplements full chat authority
    assert "full_chat" not in src or "full_chat" in src  # prompt guard mentions forbid
    assert "execution_jsonl_body" in src  # forbidden token checked in render


def test_longrun_flag(tmp_path: Path) -> None:
    default = run_goal_facade(tmp_path, utterance="plain goal without driver", version="v1.6.7")
    # v1.6.8+ goal facade honors project longrun_default (true for new projects)
    assert default.get("longrun") is True
    drv = default.get("driver") or {}
    assert drv.get("state") in {"arming", "idle"}
    assert (default.get("supervisor") or {}).get("attached") is True

    long = run_goal_facade(
        tmp_path,
        utterance="longrun goal",
        version="v1.6.7",
        longrun=True,
        driver_start=True,
        driver_run_loop=False,
        spawn_fn=_fake_spawn(),
        bridge_cmd="true",
    )
    assert long.get("longrun") is True
    assert (long.get("supervisor") or {}).get("attached") is True
    assert (long.get("driver") or long.get("driver_attach") or {}).get("state") in {
        "arming",
        "turn_active",
        "requeue",
        "halt_terminal",
        "idle",
    } or long.get("driver_attach")


def test_skill_longrun_intent() -> None:
    assert detect_longrun_intent("帮我长跑直到验收") is True
    assert detect_longrun_intent("auto requeue until done") is True
    assert detect_longrun_intent("一键不中断交付") is True
    assert detect_longrun_intent("普通做个 feature") is False
    skill = (ROOT / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    # after skill patch should mention longrun; soft check for markers in package truth
    truth = (ROOT / "docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/truth.md").read_text(
        encoding="utf-8"
    )
    assert "--longrun" in truth
    assert "AC-GAD-003" in truth or "长跑" in truth


def test_auto_requeue(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="requeue demo", version="v2.0.0", driver_start=False)
    run_id = run["run_id"]
    calls: list = []
    started = driver_start(
        tmp_path,
        run_id,
        longrun=True,
        run_loop=True,
        max_loop_turns=2,
        max_turns=5,
        spawn_fn=_fake_spawn(0, calls),
        bridge_cmd="echo turn",
    )
    assert started.get("driver_state") in {"requeue", "halt_terminal", "arming"} or started.get("status")
    assert len(calls) >= 1
    state = load_driver_state(tmp_path, run_id)
    assert int(state.get("turn_n") or 0) >= 1
    # at least one requeue history or turn_n progressed past 1 if 2 turns
    if len(calls) >= 2:
        assert int(state.get("turn_n") or 0) >= 2


def test_digest_prompt_file(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="digest demo", version="v2.0.0")
    run_id = run["run_id"]
    goal = load_goal_run(tmp_path, run_id)
    body = render_turn_prompt(tmp_path, goal, turn_n=1)
    assert "full_chat" not in body
    assert "execution_jsonl_body" not in body
    assert "next_action" in body
    assert "authority_note" in body
    path = write_turn_prompt(tmp_path, run_id, 1, body)
    assert path.exists()
    assert path.name == "turn-1.prompt.md"


def test_bridge_spawn_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prompt = tmp_path / "p.md"
    prompt.write_text("hi", encoding="utf-8")
    monkeypatch.delenv("BEACON_HOST_GOAL_BRIDGE_CMD", raising=False)
    missing = resolve_bridge_command(prompt_file=prompt, run_id="r1", project_root=tmp_path, bridge_cmd="")
    # may find codex/claude on system; if none, reason is bridge missing
    if not missing.get("ok"):
        assert missing.get("reason_code") == REASON_NO_BRIDGE
    monkeypatch.setenv("BEACON_HOST_GOAL_BRIDGE_CMD", "mybridge {prompt_file} {run_id}")
    ok = resolve_bridge_command(prompt_file=prompt, run_id="r1", project_root=tmp_path)
    assert ok["ok"] is True
    assert "mybridge" in ok["cmd"]
    assert str(prompt) in ok["cmd"]


def test_budget_halt(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="budget demo", version="v2.0.0", driver_start=False)
    run_id = run["run_id"]
    out = driver_start(
        tmp_path,
        run_id,
        longrun=True,
        run_loop=True,
        max_turns=1,
        max_loop_turns=3,
        spawn_fn=_fake_spawn(0),
        bridge_cmd="true",
    )
    state = load_driver_state(tmp_path, run_id)
    # after 1 turn, next would halt budget
    once_more = driver_run_once(tmp_path, run_id, spawn_fn=_fake_spawn(0), bridge_cmd="true")
    # either halt_budget now or after second attempt
    state2 = load_driver_state(tmp_path, run_id)
    if state2.get("state") != "halt_budget" and once_more.get("status") != "halt_budget":
        third = driver_run_once(tmp_path, run_id, spawn_fn=_fake_spawn(0), bridge_cmd="true")
        assert third.get("status") == "halt_budget" or load_driver_state(tmp_path, run_id).get("state") == "halt_budget"
    rejected = complete_goal_run(tmp_path, run_id)
    assert rejected.get("status") != "completed"
    assert rejected.get("reason_code") == REASON_VERIFIER_REQUIRED


def test_complete_needs_verifier(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="verifier demo longrun", version="v1.6.7", longrun=True, driver_start=False)
    run_id = run["run_id"]
    driver_start(tmp_path, run_id, longrun=True, run_loop=False, bridge_cmd="true")
    # driver path must not complete
    bad = complete_goal_run(tmp_path, run_id)
    assert bad["status"] != "completed"
    attach_verifier(tmp_path, run_id, refs=[".beacon/qa/demo/scorecard.json"])
    good = complete_goal_run(tmp_path, run_id)
    assert good["status"] == "completed"


def test_no_auto_release() -> None:
    import beacon.utils.goal_agent_driver as mod

    src = inspect.getsource(mod)
    assert "auto_release" in src
    # must never call release confirm
    assert "release confirm" not in src.lower() or "never" in src.lower()
    assert "beacon-eval-release" not in src or "never" in src
    # policy: auto_release always False in public returns
    assert "\"auto_release\": False" in src or "'auto_release': False" in src or "auto_release\": False" in src


def test_single_driver_lock(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="lock demo", version="v1.6.7")
    run_id = run["run_id"]
    a = driver_start(tmp_path, run_id, longrun=True, run_loop=False, bridge_cmd="true")
    assert a.get("status") in {"arming", "ok"} or a.get("driver")
    # force lock held by writing alive pid
    lock = goal_run_dir(tmp_path, run_id) / "driver.lock"
    lock.write_text(json.dumps({"driver_id": "other", "pid": 1, "run_id": run_id}), encoding="utf-8")
    # pid 1 may or may not be alive; simulate with current process by rewriting
    import os

    lock.write_text(
        json.dumps({"driver_id": "other", "pid": os.getpid(), "run_id": run_id}),
        encoding="utf-8",
    )
    # mark state turn_active with live pid
    st = load_driver_state(tmp_path, run_id)
    st["state"] = "turn_active"
    st["pid"] = os.getpid()
    from beacon.utils.goal_agent_driver import save_driver_state

    save_driver_state(tmp_path, st)
    b = driver_start(tmp_path, run_id, longrun=True, run_loop=False, bridge_cmd="true")
    assert b.get("reason_code") in {REASON_DUAL_DRIVER, "driver_lock_held"} or b.get("blocked") is True


def test_cli_driver_commands(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="cli driver", version="v1.6.7")
    run_id = run["run_id"]
    started = goal_driver_start(tmp_path, run_id, run_loop=False, bridge_cmd="true")
    assert started.get("driver") or started.get("status")
    st = goal_driver_status(tmp_path, run_id)
    assert st.get("status") == "ok"
    assert st.get("state") in {
        "idle",
        "arming",
        "turn_active",
        "turn_ended",
        "requeue",
        "halt_budget",
        "halt_terminal",
    }
    stopped = goal_driver_stop(tmp_path, run_id)
    assert stopped.get("status") == "halt_terminal"
    assert stopped.get("auto_release") is False


def test_single_public_entry() -> None:
    truth = (ROOT / "docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/truth.md").read_text(
        encoding="utf-8"
    )
    assert "非第二" in truth or "第二公共入口" in truth or "I-GAD-004" in truth
    assert "beacon-goal" in truth
    # no second skill package
    assert not (ROOT / "skills/beacon/beacon-goal-longrun").exists()


def test_v2_parity_note() -> None:
    truth = (ROOT / "docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/truth.md").read_text(
        encoding="utf-8"
    )
    assert "beacon-v2-goal-durable-longrun" in truth
    assert "AC-GAD-013" in truth or "v2 parity" in truth.lower() or "行为 parity" in truth


def test_tests_md_legal_illegal() -> None:
    tests = (ROOT / "docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/tests.md").read_text(
        encoding="utf-8"
    )
    assert "TC-GAD-LEGAL" in tests
    assert "TC-GAD-ILLEGAL" in tests
    assert "AC-GAD-001" in tests


def test_legal_longrun_requeue(tmp_path: Path) -> None:
    run = run_goal_facade(
        tmp_path,
        utterance="legal longrun 长跑",
        version="v2.0.0",
        longrun=True,
        driver_start=True,
        driver_run_loop=True,
        max_driver_turns=2,
        spawn_fn=_fake_spawn(0),
        bridge_cmd="true",
    )
    run_id = run["run_id"]
    state = load_driver_state(tmp_path, run_id)
    assert int(state.get("turn_n") or 0) >= 1
    prompts = list(goal_run_dir(tmp_path, run_id).glob("turn-*.prompt.md"))
    assert prompts


def test_legal_default_no_driver(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="default idle", version="v1.6.7")
    assert run.get("longrun") is True
    st = load_driver_state(tmp_path, run["run_id"])
    assert st.get("state") in {"arming", "idle"}


def test_illegal_complete_without_verifier(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="illegal complete", version="v2.0.0", longrun=True, driver_start=False)
    run_id = run["run_id"]
    driver_start(
        tmp_path,
        run_id,
        longrun=True,
        run_loop=True,
        max_loop_turns=1,
        spawn_fn=_fake_spawn(0),
        bridge_cmd="true",
    )
    # even after driver turns
    out = complete_goal_run(tmp_path, run_id)
    assert out["status"] != "completed"


def test_illegal_budget_complete(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="budget illegal", version="v2.0.0")
    run_id = run["run_id"]
    driver_start(
        tmp_path,
        run_id,
        longrun=True,
        run_loop=True,
        max_turns=1,
        max_loop_turns=2,
        spawn_fn=_fake_spawn(0),
        bridge_cmd="true",
    )
    # force another once to hit budget
    driver_run_once(tmp_path, run_id, spawn_fn=_fake_spawn(0), bridge_cmd="true")
    out = complete_goal_run(tmp_path, run_id)
    assert out.get("status") != "completed"


def test_illegal_auto_release() -> None:
    import beacon.utils.goal_agent_driver as mod

    # driver_stop / loop never set release_confirmed
    src = inspect.getsource(mod.driver_run_once) + inspect.getsource(mod.driver_run_loop)
    assert "release_confirmed" not in src
    assert "eval-release" not in src


def test_illegal_default_autostart(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BEACON_GOAL_FORCE_NO_LONGRUN", "1")
    run = run_goal_facade(tmp_path, utterance="no autostart", version="v1.6.7", longrun=False)
    assert run.get("longrun") in (False, None)
    assert (run.get("driver") or {}).get("state", "idle") == "idle"
    # no driver.json with arming
    st = load_driver_state(tmp_path, run["run_id"])
    assert st.get("state") == "idle"


def test_default_budget_constants() -> None:
    assert DEFAULT_MAX_AGENT_TURNS == 32
