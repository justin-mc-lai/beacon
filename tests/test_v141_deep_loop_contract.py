from __future__ import annotations

from pathlib import Path

from beacon.utils.deep_loop import (
    DEEP_LOOP_STATES,
    load_deep_artifact,
    reopen_allowed,
    run_deep_loop,
    stable_intent_converges_one_pass,
)

from v141_deep_helpers import FEATURE, VERSION, seed_deep_project


def test_loop_state_machine_is_complete(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    trace = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="loop_trace")
    assert [item["state"] for item in trace["iterations"]] == DEEP_LOOP_STATES
    assert trace["stop_reason"] == "stable_intent_closed"
    assert trace["route_decisions"]
    assert trace["closure_decisions"]


def test_one_pass_closure_for_stable_intent() -> None:
    assert stable_intent_converges_one_pass() is True
    assert stable_intent_converges_one_pass(new_model_element=True) is False


def test_reopen_conditions_are_bounded() -> None:
    assert reopen_allowed() is False
    assert reopen_allowed(new_intent=True) is True
    assert reopen_allowed(new_model_element=True) is True
    assert reopen_allowed(release_blocking_evidence=True) is True
    assert reopen_allowed(qa_structural_defect=True) is True
