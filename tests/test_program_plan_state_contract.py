from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.program_plan_state import (
    INVALID_TRANSITIONS,
    PROGRAM_PLAN_STATES,
    is_valid_transition,
    tig_block_recovery_state,
    transition,
)


def test_program_plan_states_declared():
    assert "plan_mode_selected" in PROGRAM_PLAN_STATES
    assert "program_frozen" in PROGRAM_PLAN_STATES


@pytest.mark.parametrize("from_state,to_state", INVALID_TRANSITIONS)
def test_invalid_transitions_blocked(from_state: str, to_state: str):
    result = transition(from_state, to_state)
    assert result.ok is False
    assert result.reason_code == "invalid_transition"
    assert is_valid_transition(from_state, to_state) is False


def test_skip_feature_graph_ack_to_program_frozen_blocked():
    result = transition("program_intent_captured", "lakes_frozen")
    assert result.ok is False


def test_skip_plan_mode_to_inventory_blocked():
    result = transition("program_intent_captured", "program_inventory")
    assert result.ok is False


def test_change_open_to_delivery_blocked_routes_pln_review():
    result = transition("program_change_open", "program_delivery")
    assert result.ok is False
    assert result.recovery_route == "beacon-pln-review"


def test_change_open_to_frozen_without_review_blocked():
    result = transition("program_change_open", "program_frozen")
    assert result.ok is False
    assert result.recovery_route == "beacon-pln-review"


def test_valid_happy_path_chain():
    chain = [
        ("program_intent_captured", "plan_mode_selected"),
        ("plan_mode_selected", "program_inventory"),
        ("program_inventory", "program_reviewed"),
        ("program_reviewed", "feature_graph_ack"),
        ("feature_graph_ack", "lakes_truth_in_progress"),
        ("lakes_truth_in_progress", "lakes_frozen"),
        ("lakes_frozen", "program_frozen"),
    ]
    for from_state, to_state in chain:
        result = transition(from_state, to_state)
        assert result.ok is True, (from_state, to_state, result.reason_code)


def test_tig_block_recovery_state():
    assert tig_block_recovery_state() == "lakes_truth_in_progress"


def test_change_substate_refreeze_path():
    assert transition("program_change_open", "program_change_review").ok is True
    assert transition("program_change_review", "program_refreeze").ok is True
    assert transition("program_refreeze", "program_frozen").ok is True
