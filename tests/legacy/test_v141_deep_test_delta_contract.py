from __future__ import annotations

from pathlib import Path

from beacon.utils.deep_loop import load_deep_artifact, run_deep_loop, should_reopen_deep_from_qa

from v141_deep_helpers import FEATURE, VERSION, seed_deep_project


def test_pre_qa_delta_derivation(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    delta = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="test_delta")
    assert delta["deltas"]
    assert all(item["delta_state"] == "proposed" for item in delta["deltas"])
    assert all(item["route_target"] == "test-case" for item in delta["deltas"])


def test_qa_remains_execution_owner(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    delta = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="test_delta")
    assert delta["qa_execution_owner"] == "qa"
    assert delta["deep_execution_boundary"] == "deep derives deltas but does not execute QA"
    assert all(item["execution_status"] == "not_executed_by_deep" for item in delta["deltas"])


def test_qa_feedback_reenters_deep_only_for_structural_gaps() -> None:
    assert should_reopen_deep_from_qa("visual typo only", severity="P2") is False
    assert should_reopen_deep_from_qa("state and fact source consistency broken", severity="P3") is False
    assert should_reopen_deep_from_qa("state and fact source consistency broken", severity="P2") is True
