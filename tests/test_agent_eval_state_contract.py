from __future__ import annotations

import pytest

from beacon.utils.agent_eval_state import (
    AGENT_EVAL_STATES,
    INVALID_TRANSITIONS,
    LIVE_ORCHESTRATION_INVALID,
    LIVE_ORCHESTRATION_STATES,
    catalog_missing_recovery_route,
    is_valid_transition,
    live_blocked_recovery_route,
    live_orchestration_transition,
    surface_only_inflates_behavior_evidence,
    transition,
)


def test_agent_eval_states_declared():
    assert "EvalRequested" in AGENT_EVAL_STATES
    assert "Terminal" in AGENT_EVAL_STATES


@pytest.mark.parametrize("from_state,to_state", INVALID_TRANSITIONS)
def test_invalid_transitions_blocked(from_state: str, to_state: str):
    result = transition(from_state, to_state)
    assert result.ok is False
    assert result.reason_code == "invalid_transition"
    assert is_valid_transition(from_state, to_state) is False


def test_skip_execution_to_score_synthesis_blocked():
    result = transition("EvalRequested", "ScoreSynthesis")
    assert result.ok is False
    assert result.reason_code == "invalid_transition"


def test_simulated_to_formal_qa_pass_blocked():
    result = transition("simulated", "formal_qa_pass")
    assert result.ok is False


def test_lane_execution_to_truth_write_blocked():
    result = transition("LaneExecution", "truth_write")
    assert result.ok is False


def test_valid_happy_path_chain():
    chain = [
        ("EvalRequested", "CatalogResolved"),
        ("CatalogResolved", "CaseSetMaterialized"),
        ("CaseSetMaterialized", "RunnerAdmission"),
        ("RunnerAdmission", "LaneExecution"),
        ("LaneExecution", "ScoreSynthesis"),
        ("ScoreSynthesis", "EvidencePersisted"),
        ("EvidencePersisted", "Terminal"),
    ]
    for from_state, to_state in chain:
        result = transition(from_state, to_state)
        assert result.ok is True, (from_state, to_state, result.reason_code)


def test_recovery_live_blocked_route():
    assert "replay" in live_blocked_recovery_route()
    assert live_blocked_recovery_route() == "beacon eval run --runner replay --split regression-core"


def test_recovery_catalog_missing_route():
    assert "catalog" in catalog_missing_recovery_route()
    assert "--materialize" in catalog_missing_recovery_route()


def test_live_orchestration_states_declared():
    for state in ("SurfacePreflight", "HostExecution", "Grading"):
        assert state in LIVE_ORCHESTRATION_STATES


@pytest.mark.parametrize("from_state,to_state", LIVE_ORCHESTRATION_INVALID)
def test_live_orchestration_invalid(from_state: str, to_state: str):
    result = live_orchestration_transition(from_state, to_state)
    assert result.ok is False
    assert result.reason_code == "invalid_transition"


def test_live_orchestration_happy_path():
    chain = [
        ("SurfacePreflight", "HostExecution"),
        ("HostExecution", "Grading"),
        ("Grading", "LaneExecution"),
    ]
    for from_state, to_state in chain:
        result = live_orchestration_transition(from_state, to_state)
        assert result.ok is True, (from_state, to_state, result.reason_code)


def test_surface_only_does_not_inflate_behavior_evidence():
    assert surface_only_inflates_behavior_evidence(surface_pass_count=38, host_pass_count=0, matrix_total=38) is True
    assert surface_only_inflates_behavior_evidence(surface_pass_count=38, host_pass_count=38, matrix_total=38) is False


@pytest.mark.parametrize(
    "from_state,to_state",
    [
        ("ScoreSynthesis", "release_ready"),
    ],
)
def test_score_synthesis_to_release_ready_blocked(from_state: str, to_state: str):
    result = transition(from_state, to_state)
    assert result.ok is False
    assert result.reason_code == "invalid_transition"
