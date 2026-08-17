from __future__ import annotations

from pathlib import Path

from beacon.utils.deep_loop import all_findings_routed, load_deep_artifact, route_deep_finding, run_deep_loop

from v141_deep_helpers import FEATURE, VERSION, seed_deep_project


def test_requirement_and_story_gaps_route_correctly() -> None:
    assert route_deep_finding("prd_gap")["target_surface"] == "change"
    assert route_deep_finding("user_story_gap")["target_surface"] == "user-story"
    assert route_deep_finding("acceptance_gap")["target_surface"] == "test-case"


def test_implementation_and_qa_gaps_route_correctly() -> None:
    assert route_deep_finding("implementation_gap")["target_surface"] == "implement"
    assert route_deep_finding("qa_evidence")["target_surface"] == "qa"


def test_release_risks_route_to_closure_waiver_or_backlog() -> None:
    route = route_deep_finding("release_risk")
    assert route["target_surface"] == "release"
    assert "waiver" in route["route"]
    assert "backlog" in route["route"]


def test_no_orphan_deep_findings(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    risk = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="risk_register")
    assert risk["orphan_finding_count"] == 0
    assert all_findings_routed(risk["findings"]) is True
