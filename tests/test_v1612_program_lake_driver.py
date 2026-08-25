"""Contract tests for the program-level lake driver (v1.6.12).

Covers prd.md acceptance criteria:
- multi-lake sequential advance (A truth→implement→qa closed then B starts)
- release-stage stop with resume_action=await_human_gate (never dispatched)
- upstream-unclosed dependency no-dispatch
- crash-resume idempotence (filesystem evidence only)
- blocked_streak / budget stops emit reason_code + resume_action
- goal termination takeover hint only when a program route has a next lake
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.product_goal_runtime import run_goal_facade
from beacon.utils.program_driver import (
    BLOCKED_STREAK_LIMIT,
    REASON_BUDGET,
    REASON_HUMAN_GATE,
    REASON_SPAWN_FAILED,
    REASON_STREAK,
    REASON_UPSTREAM,
    REASON_USER_STOP,
    STAGE_SKILLS,
    assert_no_auto_release_policy,
    load_drive_state,
    program_drive_once,
    program_drive_loop,
    program_drive_start,
    program_drive_status,
    program_drive_stop,
)

runner = CliRunner()
VERSION = "v1.6.12"
PROGRAM = "sea-demo"


def _graph_path(root: Path, program: str = PROGRAM) -> Path:
    return root / "docs" / "beacon" / VERSION / "programs" / program / "feature-graph.json"


def _write_graph(root: Path, lakes: list[dict], *, program: str = PROGRAM, frozen: bool = True) -> None:
    directory = _graph_path(root, program).parent
    directory.mkdir(parents=True, exist_ok=True)
    graph: dict = {
        "program_slug": program,
        "version": VERSION,
        "scope_mode": "full_parity",
        "lakes": lakes,
    }
    if frozen:
        graph["program_plan_frozen"] = True
    _graph_path(root, program).write_text(json.dumps(graph), encoding="utf-8")


def _freeze_truth(root: Path, lake: str, *, program: str = PROGRAM) -> None:
    path = _graph_path(root, program)
    graph = json.loads(path.read_text(encoding="utf-8"))
    for row in graph["lakes"]:
        if row.get("slug") == lake:
            row["status"] = "frozen"
    path.write_text(json.dumps(graph), encoding="utf-8")


def _close_impl(root: Path, lake: str) -> None:
    path = root / ".beacon" / "state" / f"implementation-{lake}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": "pass"}), encoding="utf-8")


def _close_qa(root: Path, lake: str) -> None:
    path = root / ".beacon" / "qa" / "features" / lake / "status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"status": "pass", "verdict": "passed", "evidence_done": True}),
        encoding="utf-8",
    )


def _close_all(root: Path, lake: str, *, program: str = PROGRAM) -> None:
    _freeze_truth(root, lake, program=program)
    _close_impl(root, lake)
    _close_qa(root, lake)


def _fake_spawn(exit_code: int = 0, calls: list | None = None, effects: list | None = None):
    def _spawn(argv, cwd, timeout):
        if calls is not None:
            calls.append(list(argv))
        if effects:
            fn = effects.pop(0)
            if fn:
                fn()
        return subprocess.CompletedProcess(list(argv), exit_code, stdout="ok", stderr="")

    return _spawn


BRIDGE = "cat {prompt_file}"


def _prompt(root: Path, turn_n: int, program: str = PROGRAM) -> str:
    return (root / ".beacon" / "state" / "program-drive" / program / f"turn-{turn_n}.prompt.md").read_text(
        encoding="utf-8"
    )


LAKE_A = {"slug": "lake-a", "depends_on": [], "parity_subset": ["auth"], "status": "planned"}
LAKE_B = {"slug": "lake-b", "depends_on": ["lake-a"], "parity_subset": ["billing"], "status": "planned"}


def test_no_release_in_dispatch_map():
    assert_no_auto_release_policy()
    assert set(STAGE_SKILLS) == {"truth", "implement", "qa"}


def test_multi_lake_sequential_advance_then_human_gate(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A), dict(LAKE_B)])
    effects = [
        lambda: _freeze_truth(root, "lake-a"),
        lambda: _close_impl(root, "lake-a"),
        lambda: _close_qa(root, "lake-a"),
        lambda: _freeze_truth(root, "lake-b"),
        lambda: _close_impl(root, "lake-b"),
        lambda: _close_qa(root, "lake-b"),
    ]
    calls: list = []
    out = program_drive_loop(
        root,
        version=VERSION,
        program_slug=PROGRAM,
        spawn_fn=_fake_spawn(0, calls, effects),
        bridge_cmd=BRIDGE,
        max_loop_turns=10,
    )
    # exactly one turn per lake-stage: A(truth/implement/qa) + B(truth/implement/qa)
    assert len(calls) == 6
    p1 = _prompt(root, 1)
    assert "beacon-gen-truth" in p1 and "lake-a" in p1 and "lake-b" not in p1
    assert "beacon-gen-implement" in _prompt(root, 2)
    assert "beacon-eval-qa" in _prompt(root, 3)
    p4 = _prompt(root, 4)
    assert "beacon-gen-truth" in p4 and "lake-b" in p4
    last = out["last"]
    assert last["status"] == "halt_terminal"
    assert last["reason_code"] == REASON_HUMAN_GATE
    assert last["resume_action"] == "await_human_gate"
    assert last["blocked"] is False
    assert out["auto_release"] is False
    state_path = root / "docs" / "beacon" / VERSION / "programs" / PROGRAM / "program-drive-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["turn_n"] == 6
    # re-driving a completed program never spawns again
    calls2: list = []
    again = program_drive_once(
        root, version=VERSION, program_slug=PROGRAM, spawn_fn=_fake_spawn(0, calls2), bridge_cmd=BRIDGE
    )
    assert calls2 == []
    assert again["reason_code"] == REASON_HUMAN_GATE


def test_release_stage_never_dispatched_when_all_lakes_closed(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A), dict(LAKE_B)])
    _close_all(root, "lake-a")
    _close_all(root, "lake-b")
    calls: list = []
    out = program_drive_once(
        root, version=VERSION, program_slug=PROGRAM, spawn_fn=_fake_spawn(0, calls), bridge_cmd=BRIDGE
    )
    assert calls == []
    assert out["status"] == "halt_terminal"
    assert out["reason_code"] == REASON_HUMAN_GATE
    assert out["resume_action"] == "await_human_gate"
    assert out["auto_release"] is False


def test_dependency_blocks_downstream_dispatch_normal_order(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A), dict(LAKE_B)])
    calls: list = []
    out = program_drive_once(
        root, version=VERSION, program_slug=PROGRAM, spawn_fn=_fake_spawn(0, calls), bridge_cmd=BRIDGE
    )
    # A is not closed yet -> driver must dispatch A, never B
    assert out["status"] == "requeue"
    prompt = _prompt(root, 1)
    assert "lake-a" in prompt
    assert "lake-b" not in prompt


def test_dependency_blocked_current_lake_stops_without_dispatch(tmp_path: Path):
    root = tmp_path
    # misordered graph: dependent lake listed before its dependency
    _write_graph(root, [dict(LAKE_B), dict(LAKE_A)])
    calls: list = []
    out = program_drive_once(
        root, version=VERSION, program_slug=PROGRAM, spawn_fn=_fake_spawn(0, calls), bridge_cmd=BRIDGE
    )
    assert calls == []
    assert out["blocked"] is True
    assert out["reason_code"] == REASON_UPSTREAM
    assert out["resume_action"] == "none"
    assert "lake-a" in str(out.get("recommended_command") or "")


def test_crash_resume_continues_from_evidence(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A), dict(LAKE_B)])
    _close_all(root, "lake-a")
    calls: list = []
    once1 = program_drive_once(
        root,
        version=VERSION,
        program_slug=PROGRAM,
        spawn_fn=_fake_spawn(0, calls, [lambda: _freeze_truth(root, "lake-b")]),
        bridge_cmd=BRIDGE,
    )
    assert once1["status"] == "requeue"
    p1 = _prompt(root, 1)
    assert "beacon-gen-truth" in p1 and "lake-b" in p1 and "lake-a" not in p1
    # simulated crash: a fresh process reloads persisted state and filesystem evidence only
    once2 = program_drive_once(
        root,
        version=VERSION,
        program_slug=PROGRAM,
        spawn_fn=_fake_spawn(0, calls, [lambda: _close_impl(root, "lake-b")]),
        bridge_cmd=BRIDGE,
    )
    assert once2["status"] == "requeue"
    p2 = _prompt(root, 2)
    assert "beacon-gen-implement" in p2 and "lake-b" in p2
    assert "beacon-gen-truth" not in p2  # B truth not redone
    assert "lake-a" not in p2  # closed lake never redone
    state = load_drive_state(root, VERSION, PROGRAM)
    assert int(state["turn_n"]) == 2


def test_blocked_streak_stop_emits_contract(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A)])
    calls: list = []
    out = program_drive_loop(
        root,
        version=VERSION,
        program_slug=PROGRAM,
        spawn_fn=_fake_spawn(0, calls),
        bridge_cmd=BRIDGE,
        max_loop_turns=8,
    )
    assert len(calls) == BLOCKED_STREAK_LIMIT
    last = out["last"]
    assert last["status"] == "halt_terminal"
    assert last["reason_code"] == REASON_STREAK
    assert last["resume_action"] == "replay_substep"
    assert last["blocked"] is True


def test_budget_stop_emits_contract(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A)])
    calls: list = []
    out = program_drive_start(
        root,
        version=VERSION,
        program_slug=PROGRAM,
        run_loop=True,
        max_turns=2,
        max_loop_turns=8,
        spawn_fn=_fake_spawn(0, calls),
        bridge_cmd=BRIDGE,
    )
    assert len(calls) == 2
    assert out["status"] == "halt_budget"
    assert out["reason_code"] == REASON_BUDGET
    assert out["resume_action"] == "replay_substep"


def test_host_failure_stop(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A)])
    calls: list = []
    out = program_drive_once(
        root, version=VERSION, program_slug=PROGRAM, spawn_fn=_fake_spawn(3, calls), bridge_cmd=BRIDGE
    )
    assert len(calls) == 1
    assert out["status"] == "halt_terminal"
    assert out["reason_code"] == REASON_SPAWN_FAILED
    assert out["resume_action"] == "replay_substep"
    assert out["blocked"] is True


def test_drive_status_and_user_stop(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A)])
    started = program_drive_start(
        root, version=VERSION, program_slug=PROGRAM, run_loop=False, bridge_cmd=BRIDGE
    )
    assert started["status"] == "arming"
    status = program_drive_status(root, version=VERSION, program_slug=PROGRAM)
    assert status["state"] == "arming"
    assert status["lock_present"] is True
    assert status["auto_release"] is False
    stopped = program_drive_stop(root, version=VERSION, program_slug=PROGRAM)
    assert stopped["reason_code"] == REASON_USER_STOP
    status2 = program_drive_status(root, version=VERSION, program_slug=PROGRAM)
    assert status2["lock_present"] is False
    once = program_drive_once(
        root, version=VERSION, program_slug=PROGRAM, spawn_fn=_fake_spawn(0), bridge_cmd=BRIDGE
    )
    assert once["status"] == "halt_terminal"
    assert once["reason_code"] == REASON_USER_STOP


def test_missing_graph_blocks_with_reason(tmp_path: Path):
    calls: list = []
    out = program_drive_once(
        tmp_path, version=VERSION, program_slug="ghost", spawn_fn=_fake_spawn(0, calls), bridge_cmd=BRIDGE
    )
    assert calls == []
    assert out["blocked"] is True
    assert out["reason_code"] == "feature_graph_invalid"
    assert out["resume_action"] == "none"


def test_goal_facade_takeover_hint_when_next_lake_exists(tmp_path: Path):
    root = tmp_path
    _write_graph(root, [dict(LAKE_A), dict(LAKE_B)])
    _close_all(root, "lake-a")
    payload = run_goal_facade(root, utterance="继续海的下一个湖", version=VERSION, feature="lake-a")
    takeover = payload.get("program_takeover") or {}
    assert "beacon program drive sea-demo" in str(takeover.get("command") or "")
    assert takeover.get("next_lake") == "lake-b"
    recommended = payload.get("recommended_next") or {}
    assert "beacon program drive" in str(recommended.get("program") or "")
    events = [str(h.get("event") or "") for h in payload.get("history") or []]
    assert "program_takeover_hint" in events


def test_goal_facade_no_hint_without_program_binding(tmp_path: Path):
    payload = run_goal_facade(tmp_path, utterance="plain single lake goal", version=VERSION)
    assert not payload.get("program_takeover")
    recommended = payload.get("recommended_next") or {}
    assert "program" not in recommended
    assert {"human", "longrun", "complete", "release"} <= set(recommended)


def test_cli_drive_status_only_and_blocked_exit(tmp_path: Path):
    # blocked: graph missing -> exit code 2
    result = runner.invoke(
        app,
        ["program", "drive", "ghost", "--project", str(tmp_path), "--version", VERSION, "--json"],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "feature_graph_invalid"

    # status-only on a seeded program -> exit 0
    _write_graph(tmp_path, [dict(LAKE_A)])
    result2 = runner.invoke(
        app,
        [
            "program",
            "drive",
            PROGRAM,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--status-only",
            "--json",
        ],
    )
    assert result2.exit_code == 0
    payload2 = json.loads(result2.stdout)
    assert payload2["program_slug"] == PROGRAM
    assert payload2["auto_release"] is False
    assert (payload2.get("orchestrator") or {}).get("current_lake") == "lake-a"


@pytest.mark.parametrize(
    "stage,skill",
    [("truth", "beacon-gen-truth"), ("implement", "beacon-gen-implement"), ("qa", "beacon-eval-qa")],
)
def test_stage_skill_routing_matrix(stage: str, skill: str):
    assert STAGE_SKILLS[stage] == skill
