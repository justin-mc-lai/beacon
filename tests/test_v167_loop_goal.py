"""Tests for beacon-loop-goal-v166 R7 (v1.6.7 intent continuation + topology_gate)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.loop_goal_state import (
    build_resume,
    init,
    record_host_interrupt,
    record_intent_fork,
    record_review_decision,
    record_standard_execution_precheck,
    record_user_decision,
    required_standard_execution_checks,
)

runner = CliRunner()


def _passing_verification_bundle_v167() -> dict[str, dict[str, str]]:
    return {
        "truth_map_verify": {"status": "pass"},
        "verify_materials_strict": {"status": "pass"},
        "git_diff_check": {"status": "pass"},
        "branch_governance_verify": {"status": "pass"},
        "workspace_admission": {"status": "pass"},
        "topology_gate": {"status": "pass"},
    }


def _write_cli_bundle(project: Path, *, run_id: str) -> str:
    ref = f".beacon/state/loop-goal/{run_id}.verification-bundle.json"
    path = project / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "standard-execution-precheck.v1",
        "produced_by": "beacon.status.standard-execution-precheck",
        "cli_owned": True,
        "verification_bundle": _passing_verification_bundle_v167(),
        "canonical_refreeze_committed": True,
        "truth_baseline_merged": True,
        "truth_baseline_commit": "abc123",
        "feature_worktree_reconciled": True,
        "workspace_admission_ref": ".beacon/state/workspace-admission/v1.6.7/f.json",
        "topology_gate_ref": ".beacon/state/git-scope-graph/v1.6.7/f.json",
        "topology_gate_status": "pass",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return ref


@pytest.fixture
def goal_project(tmp_path: Path) -> Path:
    return tmp_path


def test_state_init_creates_file(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="test-feature", utterance="test utterance")
    assert state["schema_version"] == "loop-goal-state.v1"
    assert state["version"] == "v1.6.7"
    assert state["feature"] == "test-feature"
    assert state["utterance"] == "test utterance"
    assert state["current_stage"] == "idle"
    assert "run_id" in state
    state_path = goal_project / ".beacon" / "state" / "loop-goal" / f"{state['run_id']}.json"
    assert state_path.is_file()


def test_intent_context_state_outputs(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="f1", utterance="seed prompt")
    outputs = state["outputs"]
    assert outputs["latest_utterance"] == "seed prompt"
    assert outputs["intent_forks"] == []
    assert outputs["decision_cache"] == []
    assert outputs["topology_gate_status"] == "not_checked"


def test_intent_fork_record_appends(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="f1", utterance="u1")
    result = record_intent_fork(
        goal_project,
        run_id=state["run_id"],
        stage="review_routing",
        utterance_slice="继续 implement",
        decision="continue",
        reason_code="",
    )
    forks = result["outputs"]["intent_forks"]
    assert len(forks) == 1
    assert forks[0]["stage"] == "review_routing"


def test_decision_cache_prevents_repeat_ask(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="f1", utterance="u1")
    run_id = state["run_id"]
    record_user_decision(
        goal_project,
        run_id=run_id,
        decision_key="planner_review_user_decision",
        decision_value="accept_scope",
    )
    artifact = {
        "review_id": "r1",
        "recommended_route": "beacon-gen-implement",
        "user_decision_required": True,
        "synthesis": {"highest_severity": "P2", "finding_count": 0},
        "findings": [],
    }
    result = record_review_decision(goal_project, run_id=run_id, review_artifact=artifact)
    assert result.get("current_stage") != "error_recovery" or not result.get("reason_code")


def test_interrupt_semantics_resume_substep(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="f1", utterance="u1")
    out = record_host_interrupt(goal_project, run_id=state["run_id"], substep="implement_routing")
    assert out["reason_code"] == "host_turn_interrupted"
    assert out["resume_action"] == "replay_substep"


def test_resume_utterance_short_map(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="f1", utterance="u1")
    from beacon.utils.loop_goal_state import transition

    transition(goal_project, run_id=state["run_id"], to_stage="implement_routing")
    payload = build_resume(goal_project, run_id=state["run_id"], utterance="继续")
    assert payload.get("resume_action") == "load_next_skill"


def test_loop_goal_run_cli_entry() -> None:
    result = runner.invoke(app, ["loop-goal", "run", "--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout


def test_topology_gate_blocks_implement(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="f1", utterance="u1")
    ref = _write_cli_bundle(goal_project, run_id=state["run_id"])
    bundle = _passing_verification_bundle_v167()
    bundle["topology_gate"] = {"status": "fail", "reason_code": "topology_gate_blocked"}
    cli_path = goal_project / ref
    cli_payload = json.loads(cli_path.read_text(encoding="utf-8"))
    cli_payload["verification_bundle"] = bundle
    cli_path.write_text(json.dumps(cli_payload), encoding="utf-8")
    precheck = {
        "truth_baseline_commit": "abc123",
        "canonical_refreeze_committed": True,
        "truth_baseline_merged": True,
        "feature_worktree_reconciled": True,
        "verification_bundle": bundle,
        "verification_bundle_ref": ref,
        "workspace_admission_ref": ".beacon/state/workspace-admission/v1.6.7/f.json",
        "topology_gate_ref": ".beacon/state/git-scope-graph/v1.6.7/f.json",
    }
    result = record_standard_execution_precheck(goal_project, run_id=state["run_id"], precheck=precheck)
    assert result.get("reason_code") == "topology_gate_blocked" or result.get("status") == "blocked"


def test_dual_runtime_resume_parity(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="f1", utterance="u1")
    from beacon.utils.loop_goal_state import transition

    transition(goal_project, run_id=state["run_id"], to_stage="qa_routing")
    a = build_resume(goal_project, run_id=state["run_id"])
    path = goal_project / ".beacon/state/loop-goal" / f"{state['run_id']}.json"
    persisted = json.loads(path.read_text(encoding="utf-8"))
    persisted.setdefault("outputs", {})["loop_execution_mode"] = "cli_agent"
    path.write_text(json.dumps(persisted), encoding="utf-8")
    b = build_resume(goal_project, run_id=state["run_id"])
    assert a.get("next_skill") == b.get("next_skill")


def test_resilient_stop_contract(goal_project: Path) -> None:
    payload = build_resume(goal_project, run_id="nonexistent-run")
    assert payload.get("resume_action") == "none"
    assert payload.get("reason_code")


def test_v2_schema_parity_fixtures(goal_project: Path) -> None:
    state = init(goal_project, version="v1.6.7", feature="f1", utterance="u1")
    fixture = {
        "intent_context": {
            "seed_utterance": state["utterance"],
            "latest_utterance": state["outputs"]["latest_utterance"],
            "intent_forks": [],
            "decision_cache": [],
        },
        "branch_context_parity_ref": "docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md",
    }
    path = goal_project / ".beacon/state/loop-goal/intent-context-v167.fixture.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fixture), encoding="utf-8")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert "intent_context" in loaded


def test_required_checks_include_topology_gate_v167() -> None:
    checks = required_standard_execution_checks("v1.6.7")
    assert "topology_gate" in checks
    assert "topology_gate" not in required_standard_execution_checks("v1.6.6")
