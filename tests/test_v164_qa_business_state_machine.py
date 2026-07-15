"""Tests for beacon-qa-business-state-machine-v164."""

from __future__ import annotations

from beacon.utils.coverage import project_qa_layer_confidence
from beacon.utils.qa_acceptance import build_qa_profile_completeness
from beacon.utils.qa_state_machine import (
    REASON_FSM_EXTRACT_FAILED,
    REASON_UNREACHABLE_STATE_REACHED,
    build_state_coverage_model,
    derive_boundary_test_cases,
    extract_fsm_from_truth,
)

TRUTH_WITH_FSM = """
## State Machine

```
[Idle] --AC-001--> [Loaded]
[Loaded] --AC-002--> [Ready]
[不可达态] --never--> [Blocked]
```
"""


def test_fsm_extract_from_truth() -> None:
    fsm = extract_fsm_from_truth(TRUTH_WITH_FSM)
    assert fsm["blocked"] is False
    assert "Idle" in fsm["states"]
    assert "Ready" in fsm["states"]
    assert any(item["from"] == "Idle" for item in fsm["transitions"])
    blocked = extract_fsm_from_truth("no transitions here")
    assert blocked["blocked"] is True
    assert blocked["reason_code"] == REASON_FSM_EXTRACT_FAILED


def test_state_coverage_model() -> None:
    fsm = extract_fsm_from_truth(TRUTH_WITH_FSM)
    covered = build_state_coverage_model(
        fsm,
        covered_transitions=[("Idle", "Loaded"), ("Loaded", "Ready")],
        covered_boundary_states=["Idle", "Ready"],
    )
    assert covered["transition_coverage_ratio"] == 1.0
    assert covered["transition_gaps"] == []


def test_state_machine_coverage_field() -> None:
    fsm = extract_fsm_from_truth(TRUTH_WITH_FSM)
    coverage = build_state_coverage_model(fsm, covered_transitions=[("Idle", "Loaded")])
    profile = build_qa_profile_completeness(profile="complete", state_machine_coverage=coverage)
    assert "state_machine_coverage" in profile
    projection = project_qa_layer_confidence(profile)
    assert projection["state_machine_coverage"] == coverage


def test_boundary_coverage_derivation() -> None:
    fsm = extract_fsm_from_truth(TRUTH_WITH_FSM)
    cases = derive_boundary_test_cases(fsm)
    kinds = {item["kind"] for item in cases}
    assert "initial_entry" in kinds
    assert "terminal_exit" in kinds
    partial = build_state_coverage_model(fsm, covered_transitions=[], covered_boundary_states=[])
    assert partial["boundary_gaps"]


def test_unreachable_state_reject() -> None:
    fsm = extract_fsm_from_truth(TRUTH_WITH_FSM)
    blocked = build_state_coverage_model(fsm, reached_unreachable=["不可达态"])
    assert blocked["blocked"] is True
    assert blocked["reason_code"] == REASON_UNREACHABLE_STATE_REACHED


def test_confidence_chain_integration() -> None:
    fsm = extract_fsm_from_truth(TRUTH_WITH_FSM)
    coverage = build_state_coverage_model(
        fsm,
        covered_transitions=[("Idle", "Loaded")],
        covered_boundary_states=[],
    )
    profile = build_qa_profile_completeness(
        profile="browser",
        browser_required=True,
        executed_layers=["unit"],
        state_machine_coverage=coverage,
    )
    chain = profile["confidence_chain"]
    assert any("state_machine_gap" in item.get("gap_markers", []) for item in chain["layers"])
