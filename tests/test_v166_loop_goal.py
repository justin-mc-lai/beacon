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
    build_resume,
    build_status,
    check_release_gate,
    check_stop_when,
    get_skill_for_stage,
    increment_repair_loop,
    init,
    read_state,
    record_review_decision,
    record_standard_execution_precheck,
    route_to_error_recovery,
    transition,
)


@pytest.fixture
def goal_project(tmp_path: Path) -> Path:
    return tmp_path


def _passing_verification_bundle() -> dict[str, dict[str, str]]:
    return {
        "truth_map_verify": {"status": "pass"},
        "verify_materials_strict": {"status": "pass"},
        "git_diff_check": {"status": "pass"},
        "branch_governance_verify": {"status": "pass"},
        "workspace_admission": {"status": "pass"},
    }


def _write_cli_owned_bundle(project: Path, *, run_id: str, extra: dict | None = None) -> str:
    ref = f".beacon/state/loop-goal/{run_id}.verification-bundle.json"
    path = project / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "standard-execution-precheck.v1",
        "produced_by": "beacon.status.standard-execution-precheck",
        "cli_owned": True,
        "verification_bundle": _passing_verification_bundle(),
        "canonical_refreeze_committed": True,
        "truth_baseline_merged": True,
        "truth_baseline_commit": "c57c1f6527dddd654616b57b3091b187b6fd4490",
        "feature_worktree_reconciled": True,
        "stale_feature_refreeze_detected": False,
        "stale_feature_refreeze_quarantine_ref": "",
        "workspace_admission_ref": ".beacon/state/workspace-admission/v1.6.6/f1.json",
    }
    if extra:
        payload.update(extra)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return ref


def _passing_standard_precheck(project: Path | None = None, *, run_id: str = "test-run") -> dict[str, object]:
    ref = ""
    if project is not None:
        ref = _write_cli_owned_bundle(project, run_id=run_id)
    return {
        "truth_baseline_commit": "c57c1f6527dddd654616b57b3091b187b6fd4490",
        "canonical_refreeze_committed": True,
        "feature_worktree_reconciled": True,
        "truth_baseline_merged": True,
        "stale_feature_refreeze_detected": False,
        "stale_feature_refreeze_quarantine_ref": "",
        "verification_bundle": _passing_verification_bundle(),
        "verification_bundle_ref": ref or f".beacon/state/loop-goal/{run_id}.verification-bundle.json",
        "workspace_admission": {"status": "pass"},
        "workspace_admission_ref": ".beacon/state/workspace-admission/v1.6.6/f1.json",
        "cli_owned": True,
        "produced_by": "beacon.status.standard-execution-precheck",
    }


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
        assert get_skill_for_stage("review_routing") == "beacon-pln-review"
        assert get_skill_for_stage("standard_execution_precheck") == "CLI:beacon-status-standard-execution-precheck"
        assert get_skill_for_stage("implement_routing") == "beacon-gen-implement"
        assert get_skill_for_stage("qa_routing") == "beacon-eval-qa"
        assert get_skill_for_stage("release_gate") == "beacon-eval-release"
        assert get_skill_for_stage("error_recovery") == "beacon-gov-debug"

    def test_skill_md_exists_and_has_decision_tree(self):
        """Verify SKILL.md exists and contains key decision tree elements."""
        skill_path = Path(__file__).parent.parent / "skills" / "beacon" / "beacon-goal" / "SKILL.md"
        mode_path = Path(__file__).parent.parent / "skills" / "beacon" / "beacon-goal" / "references" / "modes" / "loop-goal.md"
        assert skill_path.is_file()
        assert mode_path.is_file()
        assert "name: beacon-goal" in skill_path.read_text(encoding="utf-8")
        assert "references/modes/loop-goal.md" in skill_path.read_text(encoding="utf-8")
        content = mode_path.read_text(encoding="utf-8")
        assert "Mode: loop-goal" in content
        assert "Beacon v1.6.0 共享 Preamble" in content
        assert "你正在运行 governor skill" in content
        assert "governance_precheck" in content
        assert "truth_routing" in content
        assert "review_routing" in content
        assert "standard_execution_precheck" in content
        assert "implement_routing" in content
        assert "qa_routing" in content
        assert "release_gate" in content
        assert "error_recovery" in content
        assert "beacon-gen-truth" in content
        assert "beacon-pln-review" in content
        assert "beacon-gen-implement" in content
        assert "beacon-eval-qa" in content
        assert "beacon-eval-release" in content
        assert "beacon-gov-debug" in content
        assert "HUMAN GATE" in content or "human_gate" in content.lower()


class TestReviewDecisionPacket:
    """AC-012..014: planner-review decision packet gates implement routing."""

    def test_review_routing_public_skill_contract(self):
        mode_path = Path(__file__).parent.parent / "skills" / "beacon" / "beacon-goal" / "references" / "modes" / "loop-goal.md"
        content = mode_path.read_text(encoding="utf-8")
        assert "review_routing" in content
        assert "beacon-pln-review" in content
        assert "Planner Review Decision Packet" in content
        assert "record_review_decision" in content

    def test_review_decision_packet_records_outputs(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        artifact = {
            "review_id": "pln-review-test",
            "synthesis": {
                "recommended_route": "continue_delivery",
                "highest_severity": "P2",
                "finding_count": 1,
                "user_decision_required": False,
            },
            "findings": [{"severity": "P2"}],
            "evidence_paths": {
                "runtime": ".beacon/state/planner-review/f1/pln-review-test.json",
            },
        }
        result = record_review_decision(goal_project, run_id=run_id, review_artifact=artifact)
        assert result["status"] == "pass"
        assert result["current_stage"] == "standard_execution_precheck"
        updated = read_state(goal_project, run_id=run_id)
        outputs = updated["outputs"]
        assert outputs["planner_review_id"] == "pln-review-test"
        assert outputs["planner_review_artifact_ref"].endswith("pln-review-test.json")
        assert outputs["planner_review_recommended_route"] == "continue_delivery"
        assert outputs["planner_review_user_decision_required"] is False
        assert outputs["planner_review_highest_severity"] == "P2"
        assert outputs["planner_review_finding_count"] == 1
        audit = outputs.get("planner_review_continue_audit") or {}
        assert audit.get("continued_with_advisory") is True
        assert audit.get("continued_severity") == "P2"

    def test_review_decision_packet_blocks_unsafe_implement_route(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        artifact = {
            "review_id": "pln-review-change",
            "synthesis": {
                "recommended_route": "beacon-gen-change",
                "highest_severity": "P1",
                "finding_count": 1,
                "user_decision_required": True,
            },
            "findings": [{"severity": "P1"}],
            "evidence_paths": {
                "runtime": ".beacon/state/planner-review/f1/pln-review-change.json",
            },
        }
        result = record_review_decision(goal_project, run_id=run_id, review_artifact=artifact)
        assert result["status"] == "blocked"
        assert result["current_stage"] == "drift_routing"
        assert result["recommended_route"] == "beacon-gen-change"
        assert result["reason_code"] == "planner_review_route_beacon_gen_change"
        updated = read_state(goal_project, run_id=run_id)
        assert updated["current_stage"] != "implement_routing"

    def test_review_decision_packet_p1_only_continues_with_audit(self, goal_project: Path):
        """TC-LG-014 R6: naked P1 + continue_delivery must not hard-stop."""
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        artifact = {
            "review_id": "pln-review-p1-only",
            "synthesis": {
                "recommended_route": "continue_delivery",
                "highest_severity": "P1",
                "finding_count": 1,
                "user_decision_required": False,
            },
            "findings": [{"severity": "P1", "title": "advisory"}],
            "evidence_paths": {
                "runtime": ".beacon/state/planner-review/f1/pln-review-p1-only.json",
            },
        }
        result = record_review_decision(goal_project, run_id=run_id, review_artifact=artifact)
        assert result["status"] == "pass"
        assert result["current_stage"] == "standard_execution_precheck"
        assert result["reason_code"] == ""
        outputs = result["outputs"]
        audit = outputs.get("planner_review_continue_audit") or {}
        assert audit.get("continued_with_advisory") is True
        assert audit.get("continued_severity") == "P1"
        metrics = outputs.get("human_stop_metrics") or {}
        assert metrics.get("p1_continue_count") == 1
        assert metrics.get("human_stops_per_run") == 0

    def test_review_decision_packet_p0_blocks(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        artifact = {
            "review_id": "pln-review-p0",
            "synthesis": {
                "recommended_route": "continue_delivery",
                "highest_severity": "P0",
                "finding_count": 1,
                "user_decision_required": False,
            },
            "findings": [{"severity": "P0"}],
            "evidence_paths": {
                "runtime": ".beacon/state/planner-review/f1/pln-review-p0.json",
            },
        }
        result = record_review_decision(goal_project, run_id=run_id, review_artifact=artifact)
        assert result["status"] == "blocked"
        assert result["current_stage"] == "error_recovery"
        assert result["reason_code"] == "planner_review_blocking_finding"
        metrics = result["outputs"].get("human_stop_metrics") or {}
        assert metrics.get("human_stops_per_run") == 1
        assert "planner_review_blocking_finding" in (metrics.get("stop_reason_counts") or {})

    def test_review_decision_packet_incomplete_fail_closed(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        result = record_review_decision(goal_project, run_id=run_id, review_artifact={})
        assert result["status"] == "blocked"
        assert result["reason_code"] == "planner_review_packet_incomplete"


class TestHumanGateAlignment:
    """AC-027 / TC-LG-027: auto-decide table aligns with AC-007/AC-014."""

    def test_human_gate_alignment_skill_contract(self):
        mode_path = Path(__file__).parent.parent / "skills" / "beacon" / "beacon-goal" / "references" / "modes" / "loop-goal.md"
        content = mode_path.read_text(encoding="utf-8")
        assert "P1-only" in content or "Standalone P1" in content
        assert "human confirmation" in content or "HUMAN GATE" in content
        assert "never" in content
        assert "continue audit" in content or "auto-continue" in content
        assert "HUMAN GATE" in content or "human confirm" in content.lower()

    def test_human_gate_alignment_p1_override_stops(self, goal_project: Path):
        state = init(
            goal_project,
            version="v1.6.6",
            feature="f1",
            utterance="u1",
            auto_decide=True,
            human_gate_overrides=["p1"],
        )
        artifact = {
            "review_id": "pln-review-p1-gated",
            "synthesis": {
                "recommended_route": "continue_delivery",
                "highest_severity": "P1",
                "finding_count": 1,
                "user_decision_required": False,
            },
            "findings": [{"severity": "P1"}],
            "evidence_paths": {
                "runtime": ".beacon/state/planner-review/f1/pln-review-p1-gated.json",
            },
        }
        result = record_review_decision(
            goal_project, run_id=state["run_id"], review_artifact=artifact
        )
        assert result["status"] == "blocked"
        assert result["reason_code"] == "planner_review_human_gate_p1"


class TestSameSessionContinue:
    """AC-028 / TC-LG-028."""

    def test_same_session_continue_skill_contract(self):
        mode_path = Path(__file__).parent.parent / "skills" / "beacon" / "beacon-goal" / "references" / "modes" / "loop-goal.md"
        content = mode_path.read_text(encoding="utf-8")
        assert "Same-Session Continue" in content or "same-session" in content.lower()
        assert "immediately load" in content.lower() or "同会话立即加载" in content
        assert "print-only" in content.lower() or "only printing" in content.lower() or "只打印" in content


class TestLoopGoalResume:
    """AC-029 / TC-LG-029."""

    def test_loop_goal_resume_returns_next_skill(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        transition(goal_project, run_id=run_id, to_stage="implement_routing")
        payload = build_resume(goal_project, run_id=run_id)
        assert payload["status"] == "pass"
        assert payload["current_stage"] == "implement_routing"
        assert payload["next_skill"] == "beacon-gen-implement"
        assert payload["resume_action"] == "load_next_skill"
        assert payload["same_session_continue_required"] is True

    def test_loop_goal_resume_noop_forbidden_without_state(self, goal_project: Path):
        payload = build_resume(goal_project, run_id="")
        assert payload["status"] == "blocked"
        assert payload["reason_code"] == "loop_goal_resume_no_runs"

    def test_loop_goal_resume_cli_flag_wired(self):
        status_src = (
            Path(__file__).parent.parent / "beacon" / "commands" / "status.py"
        ).read_text(encoding="utf-8")
        assert "--resume" in status_src
        assert "build_resume" in status_src


class TestObservabilityMetrics:
    """AC-030 / TC-LG-030."""

    def test_observability_metrics_on_status(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        artifact = {
            "review_id": "pln-review-metrics",
            "synthesis": {
                "recommended_route": "continue_delivery",
                "highest_severity": "P1",
                "finding_count": 1,
                "user_decision_required": False,
            },
            "findings": [{"severity": "P1"}],
            "evidence_paths": {
                "runtime": ".beacon/state/planner-review/f1/pln-review-metrics.json",
            },
        }
        record_review_decision(goal_project, run_id=run_id, review_artifact=artifact)
        status = build_status(goal_project, run_id=run_id)
        metrics = status.get("human_stop_metrics") or {}
        assert "human_stops_per_run" in metrics
        assert "stop_reason_counts" in metrics
        assert "p1_continue_count" in metrics
        assert metrics["p1_continue_count"] == 1
        assert "pseudo_stall_flag" in metrics


class TestStandardExecutionPrecheck:
    """AC-015..021: Standard Execution Flow gates implement routing."""

    def test_standard_execution_precheck_public_skill_contract(self):
        mode_path = Path(__file__).parent.parent / "skills" / "beacon" / "beacon-goal" / "references" / "modes" / "loop-goal.md"
        content = mode_path.read_text(encoding="utf-8")
        assert "implement_ready: standard_execution_precheck" in content
        assert "standard_execution_precheck" in content
        assert "pass: implement_routing" in content
        assert "Standard Execution Precheck" in content
        assert "record_standard_execution_precheck" in content
        assert "standard-execution-precheck" in content
        assert "verification_bundle_not_cli_owned" in content or "CLI-owned" in content
        assert "truth_map verify" in content or "truth-map verify" in content
        assert "verify-materials --strict" in content
        assert "git diff --check" in content
        assert "branch-governance verify" in content
        assert "implement check-branch" in content or "workspace admission" in content

    def test_uncommitted_canonical_refreeze_blocks_implement(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        precheck = _passing_standard_precheck(
            goal_project,
            run_id=state["run_id"],
        )
        # Rewrite CLI artifact with uncommitted baseline.
        _write_cli_owned_bundle(
            goal_project,
            run_id=state["run_id"],
            extra={"canonical_refreeze_committed": False},
        )
        precheck["canonical_refreeze_committed"] = False
        result = record_standard_execution_precheck(
            goal_project,
            run_id=state["run_id"],
            precheck=precheck,
        )
        assert result["status"] == "blocked"
        assert result["reason_code"] == "canonical_refreeze_not_committed"
        assert result["current_stage"] == "error_recovery"
        assert read_state(goal_project, run_id=state["run_id"])["current_stage"] != "implement_routing"

    def test_stale_feature_refreeze_requires_quarantine(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        precheck = _passing_standard_precheck(goal_project, run_id=state["run_id"])
        _write_cli_owned_bundle(
            goal_project,
            run_id=state["run_id"],
            extra={
                "stale_feature_refreeze_detected": True,
                "stale_feature_refreeze_quarantine_ref": "",
            },
        )
        precheck["stale_feature_refreeze_detected"] = True
        precheck["stale_feature_refreeze_quarantine_ref"] = ""
        result = record_standard_execution_precheck(
            goal_project,
            run_id=state["run_id"],
            precheck=precheck,
        )
        assert result["status"] == "blocked"
        assert result["reason_code"] == "stale_feature_refreeze_not_quarantined"
        updated = read_state(goal_project, run_id=state["run_id"])
        assert updated["outputs"]["standard_execution_flow_status"] == "blocked"

    def test_truth_baseline_commit_must_be_merged(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        precheck = _passing_standard_precheck(goal_project, run_id=state["run_id"])
        _write_cli_owned_bundle(
            goal_project,
            run_id=state["run_id"],
            extra={"truth_baseline_merged": False},
        )
        precheck["truth_baseline_merged"] = False
        result = record_standard_execution_precheck(
            goal_project,
            run_id=state["run_id"],
            precheck=precheck,
        )
        assert result["status"] == "blocked"
        assert result["reason_code"] == "truth_baseline_not_merged"
        updated = read_state(goal_project, run_id=state["run_id"])
        assert updated["outputs"]["truth_baseline_commit"] == precheck["truth_baseline_commit"]

    def test_standard_execution_verification_bundle_required(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        incomplete = {
            "truth_map_verify": {"status": "pass"},
            "verify_materials_strict": {"status": "pass"},
        }
        precheck = _passing_standard_precheck(goal_project, run_id=state["run_id"])
        _write_cli_owned_bundle(
            goal_project,
            run_id=state["run_id"],
            extra={"verification_bundle": incomplete},
        )
        precheck["verification_bundle"] = incomplete
        result = record_standard_execution_precheck(
            goal_project,
            run_id=state["run_id"],
            precheck=precheck,
        )
        assert result["status"] == "blocked"
        assert result["reason_code"] == "verification_bundle_incomplete"
        assert "git_diff_check" in result["outputs"]["verification_bundle_missing_checks"]
        assert "branch_governance_verify" in result["outputs"]["verification_bundle_missing_checks"]
        assert "workspace_admission" in result["outputs"]["verification_bundle_missing_checks"]

    def test_workspace_admission_ref_recorded_before_implement(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        precheck = _passing_standard_precheck(goal_project, run_id=state["run_id"])
        _write_cli_owned_bundle(
            goal_project,
            run_id=state["run_id"],
            extra={"workspace_admission_ref": ""},
        )
        missing_ref = dict(precheck)
        missing_ref["workspace_admission_ref"] = ""
        result = record_standard_execution_precheck(
            goal_project,
            run_id=state["run_id"],
            precheck=missing_ref,
        )
        assert result["status"] == "blocked"
        assert result["reason_code"] == "workspace_admission_missing"

        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        precheck = _passing_standard_precheck(goal_project, run_id=state["run_id"])
        result = record_standard_execution_precheck(
            goal_project,
            run_id=state["run_id"],
            precheck=precheck,
        )
        assert result["status"] == "pass"
        assert result["current_stage"] == "implement_routing"
        updated = read_state(goal_project, run_id=state["run_id"])
        outputs = updated["outputs"]
        assert outputs["standard_execution_flow_status"] == "pass"
        assert outputs["workspace_admission_ref"].endswith("/f1.json")
        assert outputs["truth_baseline_commit"] == precheck["truth_baseline_commit"]
        bundle_path = goal_project / outputs["verification_bundle_ref"]
        assert bundle_path.is_file()

    def test_standard_execution_precheck_is_idempotent(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        run_id = state["run_id"]
        precheck = _passing_standard_precheck(goal_project, run_id=run_id)
        result = record_standard_execution_precheck(goal_project, run_id=run_id, precheck=precheck)
        assert result["status"] == "pass"
        after_first = read_state(goal_project, run_id=run_id)
        history_len = len(after_first["stage_history"])
        result = record_standard_execution_precheck(goal_project, run_id=run_id, precheck=precheck)
        assert result["status"] == "pass"
        assert result["result"] == "up_to_date"
        after_second = read_state(goal_project, run_id=run_id)
        assert len(after_second["stage_history"]) == history_len
        assert after_second["outputs"]["standard_execution_flow_status"] == "pass"

    def test_cli_owned_precheck_rejects_agent_fabricated_bundle(self, goal_project: Path):
        state = init(goal_project, version="v1.6.6", feature="f1", utterance="u1")
        precheck = _passing_standard_precheck()
        precheck["cli_owned"] = True  # agent claim without artifact file
        result = record_standard_execution_precheck(
            goal_project,
            run_id=state["run_id"],
            precheck=precheck,
        )
        assert result["status"] == "blocked"
        assert result["reason_code"] == "verification_bundle_not_cli_owned"


def test_state_init_creates_file(goal_project: Path):
    TestStateInit().test_state_init_creates_file(goal_project)


def test_stage_transition_appends_history(goal_project: Path):
    TestStageTransition().test_stage_transition_appends_history(goal_project)


def test_precheck_gate_blocks_unregistered(goal_project: Path):
    TestPrecheckGate().test_precheck_gate_blocks_unregistered(goal_project)


def test_truth_gate_waits_for_frozen(goal_project: Path):
    TestTruthGate().test_truth_gate_waits_for_frozen(goal_project)


def test_implement_gate_repair_loop(goal_project: Path):
    TestImplementGate().test_implement_gate_repair_loop(goal_project)


def test_qa_gate_repair_loop(goal_project: Path):
    TestQAGate().test_qa_gate_repair_loop(goal_project)


def test_release_human_gate_blocks_auto(goal_project: Path):
    TestReleaseHumanGate().test_release_human_gate_blocks_auto(goal_project)


def test_error_recovery_routes_debug(goal_project: Path):
    TestErrorRecovery().test_error_recovery_routes_debug(goal_project)


def test_stop_when_halts_delivery(goal_project: Path):
    TestStopWhen().test_stop_when_halts_delivery(goal_project)


def test_skill_routing_decision_tree():
    TestSkillRouting().test_skill_routing_decision_tree()


def test_review_routing_public_skill_contract():
    TestReviewDecisionPacket().test_review_routing_public_skill_contract()


def test_review_decision_packet_records_outputs(goal_project: Path):
    TestReviewDecisionPacket().test_review_decision_packet_records_outputs(goal_project)


def test_review_decision_packet_blocks_unsafe_implement_route(goal_project: Path):
    TestReviewDecisionPacket().test_review_decision_packet_blocks_unsafe_implement_route(goal_project)


def test_standard_execution_precheck_public_skill_contract():
    TestStandardExecutionPrecheck().test_standard_execution_precheck_public_skill_contract()


def test_uncommitted_canonical_refreeze_blocks_implement(goal_project: Path):
    TestStandardExecutionPrecheck().test_uncommitted_canonical_refreeze_blocks_implement(goal_project)


def test_stale_feature_refreeze_requires_quarantine(goal_project: Path):
    TestStandardExecutionPrecheck().test_stale_feature_refreeze_requires_quarantine(goal_project)


def test_truth_baseline_commit_must_be_merged(goal_project: Path):
    TestStandardExecutionPrecheck().test_truth_baseline_commit_must_be_merged(goal_project)


def test_standard_execution_verification_bundle_required(goal_project: Path):
    TestStandardExecutionPrecheck().test_standard_execution_verification_bundle_required(goal_project)


def test_workspace_admission_ref_recorded_before_implement(goal_project: Path):
    TestStandardExecutionPrecheck().test_workspace_admission_ref_recorded_before_implement(goal_project)


def test_standard_execution_precheck_is_idempotent(goal_project: Path):
    TestStandardExecutionPrecheck().test_standard_execution_precheck_is_idempotent(goal_project)
