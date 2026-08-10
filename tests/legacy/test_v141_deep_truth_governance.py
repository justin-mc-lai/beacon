from __future__ import annotations

from pathlib import Path

from beacon.utils.deep_loop import load_deep_artifact, route_deep_finding, run_deep_loop

from v141_deep_helpers import FEATURE, VERSION, seed_deep_project


def test_deep_cannot_write_frozen_truth(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    prd = tmp_path / "docs" / "beacon" / VERSION / "prd" / f"{FEATURE}.md"
    before = prd.read_text(encoding="utf-8")

    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    assert prd.read_text(encoding="utf-8") == before


def test_accepted_requirement_gap_routes_to_change() -> None:
    route = route_deep_finding("requirement_gap")
    assert route["target_surface"] == "change"
    assert route["route"] == "change/refreeze"


def test_machine_projection_is_not_truth(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    analysis = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="analysis_report")
    assert analysis["canonical_truth_policy"] == "read_only_frozen_truth"
    assert analysis["source_refs"]["prd"].startswith(f"docs/beacon/{VERSION}/prd/")
