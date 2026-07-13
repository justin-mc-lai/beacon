"""Tests for beacon-loop-goal-v166 (orchestrator state + SKILL.md)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.loop_goal_state import (
    SCHEMA_VERSION,
    VALID_STAGES,
    MAX_REPAIR_LOOPS,
    RELEASE_HUMAN_GATE_STAGES,
    check_release_gate,
    check_stop_when,
    get_skill_for_stage,
    increment_repair_loop,
    init,
    read_state,
    route_to_error_recovery,
    transition,
)


@pytest.fixture
def goal_project(tmp_path: Path) -> Path:
    return tmp_path


class TestStateInit:
    """AC-001: init creates state file with correct schema."""

    def test_state_init_creates_file(self, goal_project: Path):
        state = init(
            goal_project,
            version="v1.6.6",
            feature="test-feature",
            utterance="test utterance",
        )
        assert state["schema_version"] == "loop-goal-state.v1"
        assert state["version"] == "v1.6.6"
        assert state["feature"] == "test-feature"
        assert state["utterance"] == "test utterance"
        assert state["current_stage"] == "idle"
        assert state["auto_decide"] is True
        assert "run_id" in state
        assert len(state["stage_history"]) >= 1
        assert state["stage_history"][0]["stage"] == "idle"
        # Verify file exists
        state_path = goal_project / ".beacon" / "state" / "loop-goal" / f"{state['run_id']}.json"
        assert state_path.is_file()


class TestStageTransition:
    """AC-002: transition updates current_stage and appends history."""

    def test_stage_transition_appends_history(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        result = transition(goal_project, run_id=run_id, to_stage="truth_routing")
        assert result["status"] == "pass"
        assert result["current_stage"] == "truth_routing"
        updated = read_state(goal_project, run_id=run_id)
        assert updated["current_stage"] == "truth_routing"
        assert len(updated["stage_history"]) == 2
        assert updated["stage_history"][1]["stage"] == "truth_routing"
        assert "at" in updated["stage_history"][1]


class TestPrecheckGate:
    """AC-003: governance precheck blocked → stop with reason_code."""

    def test_precheck_gate_blocks_unregistered(self, goal_project: Path):
        state = init(goal_project, version="v9.9.9", feature="f1", utterance="u1")
        run_id = state["run_id"]
        # Simulate blocked precheck → route to error_recovery
        result = route_to_error_recovery(
            goal_project,
            run_id=run_id,
            reason_code="governance_version_not_registered",
        )
        updated = read_state(goal_project, run_id=run_id)
        assert updated["current_stage"] == "error_recovery"


class TestTruthGate:
    """AC-004: truth.md status != frozen → stay in truth_routing."""

    def test_truth_gate_waits_for_frozen(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        # Transition to truth_routing
        transition(goal_project, run_id=run_id, to_stage="truth_routing")
        # Truth not frozen → stay in truth_routing (no transition to implement)
        updated = read_state(goal_project, run_id=run_id)
        assert updated["current_stage"] == "truth_routing"
        assert updated["outputs"]["truth_frozen"] is False


class TestImplementGate:
    """AC-005: tests fail → repair loop, max 3."""

    def test_implement_gate_repair_loop(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        transition(goal_project, run_id=run_id, to_stage="implement_routing")
        # Simulate 3 failed repair attempts
        for i in range(MAX_REPAIR_LOOPS):
            result = increment_repair_loop(goal_project, run_id=run_id)
            assert result["status"] == "pass"
            assert result["repair_loop_count"] == i + 1
        # 4th attempt should exceed max
        result = increment_repair_loop(goal_project, run_id=run_id)
        assert result["status"] == "blocked"
        assert result["reason_code"] == "max_repair_loops_exceeded"
        assert result["recommended_route"] == "beacon-gov-debug"
        updated = read_state(goal_project, run_id=run_id)
        assert updated["current_stage"] == "error_recovery"


class TestQAGate:
    """AC-006: QA fail → repair loop, max 3."""

    def test_qa_gate_repair_loop(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        transition(goal_project, run_id=run_id, to_stage="qa_routing")
        # Simulate QA fail → back to implement
        for i in range(MAX_REPAIR_LOOPS):
            increment_repair_loop(goal_project, run_id=run_id)
        result = increment_repair_loop(goal_project, run_id=run_id)
        assert result["status"] == "blocked"
        assert result["reason_code"] == "max_repair_loops_exceeded"


class TestReleaseHumanGate:
    """AC-007: release gate always requires human confirmation."""

    def test_release_human_gate_blocks_auto(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1", auto_decide=True)
        run_id = state["run_id"]
        transition(goal_project, run_id=run_id, to_stage="release_gate")
        # Even with auto_decide=True, release without human confirmation should be blocked
        result = check_release_gate(goal_project, run_id=run_id, human_confirmed=False)
        assert result["status"] == "blocked"
        assert result["reason_code"] == "release_requires_human_confirmation"
        # With human confirmation, should transition to done
        result = check_release_gate(goal_project, run_id=run_id, human_confirmed=True)
        assert result["status"] == "pass"
        assert result["current_stage"] == "done"


class TestErrorRecovery:
    """AC-008: blocked → error_recovery + recommend beacon-gov-debug."""

    def test_error_recovery_routes_debug(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        result = route_to_error_recovery(goal_project, run_id=run_id, reason_code="test_blocked")
        updated = read_state(goal_project, run_id=run_id)
        assert updated["current_stage"] == "error_recovery"
        last_history = updated["stage_history"][-1]
        assert "blocked" in last_history["status"]


class TestStopWhen:
    """AC-009: stop_when condition satisfied → halt with reason_code."""

    def test_stop_when_halts_delivery(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        # Set a stop_when condition
        transition(goal_project, run_id=run_id, to_stage="truth_routing", stop_when=["user_abort"])
        # Next transition should be stopped
        result = transition(goal_project, run_id=run_id, to_stage="implement_routing")
        assert result["status"] == "stopped"
        assert result["reason_code"] == "stop_when_satisfied"


class TestSkillRouting:
    """AC-010: SKILL.md contains complete decision tree."""

    def test_skill_routing_decision_tree(self):
        # Verify skill routing function maps all stages correctly
        assert get_skill_for_stage("governance_precheck") == "CLI:beacon-plan-start"
        assert get_skill_for_stage("truth_routing") == "beacon-gen-truth"
        assert get_skill_for_stage("implement_routing") == "beacon-gen-implement"
        assert get_skill_for_stage("qa_routing") == "beacon-eval-qa"
        assert get_skill_for_stage("release_gate") == "beacon-eval-release"
        assert get_skill_for_stage("error_recovery") == "beacon-gov-debug"

    def test_skill_md_exists_and_has_decision_tree(self):
        """Verify SKILL.md exists and contains key decision tree elements."""
        skill_path = Path(__file__).parent.parent / ".agents" / "skills" / "beacon-loop-goal" / "SKILL.md"
        assert skill_path.is_file()
        content = skill_path.read_text(encoding="utf-8")
        assert "governance_precheck" in content
        assert "truth_routing" in content
        assert "implement_routing" in content
        assert "qa_routing" in content
        assert "release_gate" in content
        assert "error_recovery" in content
        assert "beacon-gen-truth" in content
        assert "beacon-gen-implement" in content
        assert "beacon-eval-qa" in content
        assert "beacon-eval-release" in content
        assert "beacon-gov-debug" in content
        assert "HUMAN GATE" in content or "human_gate" in content.lower()
