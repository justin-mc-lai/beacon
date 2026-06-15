from __future__ import annotations

import pytest

from beacon.utils.agent_eval_state import (
    AGENT_EVAL_STATES,
    INVALID_TRANSITIONS,
    catalog_missing_recovery_route,
    is_valid_transition,
    live_blocked_recovery_route,
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
