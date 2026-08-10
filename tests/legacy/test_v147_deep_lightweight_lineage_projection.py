from __future__ import annotations

from pathlib import Path

from beacon.utils.deep_loop import load_deep_artifact, run_deep_loop
from beacon.utils.deep_lineage import build_deep_lineage_projection

from v141_deep_helpers import seed_deep_project

VERSION = "v1.4.7"
FEATURE = "deep lineage feature"


def test_deep_artifacts_expose_lineage_projection(tmp_path: Path) -> None:
    seed_deep_project(tmp_path, feature=FEATURE, docs_version=VERSION)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)
    analysis = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="analysis_report")
    assert analysis["lineage_projection"]["lineage_mode"] in {"source_bound", "machine_inferred"}
    assert analysis["lineage_projection"]["source_truth_refs"]
    assert "candidate_parent_refs" in analysis["lineage_projection"]


def test_source_bound_lineage_accepts_file_level_refs() -> None:
    payload = build_deep_lineage_projection(
        source_truth_refs=["docs/beacon/v1.4.7/prd/feature.md"],
        candidate_parent_refs=[],
        route_target="deep",
        truth_impact="none",
    )
    assert payload["lineage_mode"] == "source_bound"
    assert payload["blocking"] is False
    assert payload["canonical"] is False


def test_machine_inferred_refs_are_marked_non_canonical(tmp_path: Path) -> None:
    seed_deep_project(tmp_path, feature=FEATURE, docs_version=VERSION)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)
    analysis = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="analysis_report")
    refs = analysis["lineage_projection"]["candidate_parent_refs"]
    assert refs
    assert all(ref["inferred"] is True for ref in refs)
    assert all(ref["confidence"] in {"medium", "high"} for ref in refs)
    assert analysis["lineage_projection"]["canonical"] is False


def test_candidate_refs_are_normalized_as_machine_inferred() -> None:
    payload = build_deep_lineage_projection(
        source_truth_refs=["docs/beacon/v1.4.7/prd/feature.md"],
        candidate_parent_refs=[{"ref_type": "ac", "ref_id": "ac-001", "confidence": "certain", "inferred": False}],
        route_target="deep",
        truth_impact="none",
    )
    assert payload["candidate_parent_refs"] == [
        {"ref_type": "AC", "ref_id": "AC-001", "confidence": "medium", "inferred": True}
    ]
    assert payload["canonical"] is False


def test_missing_inferred_parent_ids_do_not_block_deep() -> None:
    payload = build_deep_lineage_projection(
        source_truth_refs=["docs/beacon/v1.4.7/prd/feature.md"],
        candidate_parent_refs=[],
        route_target="deep",
        truth_impact="none",
    )
    assert payload["lineage_mode"] == "source_bound"
    assert payload["blocking"] is False


def test_adoption_required_mode_is_set_for_current_closure_impacts(tmp_path: Path) -> None:
    seed_deep_project(tmp_path, feature=FEATURE, docs_version=VERSION)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)
    delta = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="test_delta")["deltas"][0]
    assert delta["lineage"]["lineage_mode"] == "adoption_required"
    assert delta["lineage"]["truth_impact"] == "acceptance_delta"
    assert delta["lineage"]["blocking"] is True


def test_adoption_routes_to_truth_surface_for_trace_strengthening(tmp_path: Path) -> None:
    seed_deep_project(tmp_path, feature=FEATURE, docs_version=VERSION)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)
    delta = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="test_delta")["deltas"][0]
    assert delta["lineage"]["route_target"] == "test-case"
    assert delta["adoption_contract"] == "adopt through test-case or supplemental QA before claiming QA closure"


def test_canonical_promoted_trace_only_comes_from_truth_surfaces() -> None:
    support_payload = build_deep_lineage_projection(
        source_truth_refs=["docs/beacon/v1.4.7/prd/feature.md"],
        candidate_parent_refs=[{"ref_type": "AC", "ref_id": "AC-001", "confidence": "medium", "inferred": True}],
        route_target="test-case",
        truth_impact="acceptance_delta",
    )
    assert support_payload["lineage_mode"] == "adoption_required"
    assert support_payload["canonical"] is False
    assert support_payload["gate_trust"] == "canonical_only"


def test_qa_release_do_not_trust_l0_l1_as_closure_truth() -> None:
    payload = build_deep_lineage_projection(
        source_truth_refs=["docs/beacon/v1.4.7/prd/feature.md"],
        candidate_parent_refs=[{"ref_type": "AC", "ref_id": "AC-001", "confidence": "medium", "inferred": True}],
        route_target="deep",
        truth_impact="none",
    )
    assert payload["lineage_mode"] == "machine_inferred"
    assert payload["gate_trust"] == "canonical_only"


def test_lineage_projection_preserves_deep_support_boundary(tmp_path: Path) -> None:
    seed_deep_project(tmp_path, feature=FEATURE, docs_version=VERSION)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)
    risk = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="risk_register")
    assert risk["canonical_truth_policy"] == "read_only_frozen_truth"
    assert "trace-on-promotion" in risk["lineage_policy"]
    assert all("lineage" in finding for finding in risk["findings"])
