from __future__ import annotations

from pathlib import Path

from beacon.utils.deep_loop import DEEP_ARTIFACT_FAMILY, deep_artifact_paths, load_deep_artifact, run_deep_loop

from v141_deep_helpers import FEATURE, VERSION, seed_deep_project


def test_artifact_family_is_defined() -> None:
    assert set(DEEP_ARTIFACT_FAMILY) == {
        "analysis_report",
        "state_machine_report",
        "test_delta",
        "risk_register",
        "loop_trace",
        "closure_brief",
        "skip_evidence",
    }


def test_loop_trace_has_required_fields(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE, intent="verify complex business risk")

    trace = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="loop_trace")
    for key in [
        "user_intent_snapshot",
        "iterations",
        "finding_classification",
        "route_decisions",
        "closure_decisions",
        "stop_reason",
        "next_allowed_route",
    ]:
        assert key in trace
    assert trace["user_intent_snapshot"] == "verify complex business risk"


def test_closure_brief_has_release_fields(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    closure = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="closure_brief")
    for key in [
        "deep_requirement_state",
        "verdict",
        "executed_delta_cases",
        "open_findings",
        "waived_findings",
        "accepted_backlog_risks",
        "release_recommendation",
    ]:
        assert key in closure
    refs = deep_artifact_paths(tmp_path, VERSION, FEATURE)
    assert (tmp_path / refs["closure_brief"]["json"]).exists()
    assert (tmp_path / refs["closure_brief"]["markdown"]).exists()
