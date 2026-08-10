from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.qa_attribution import (
    FAILURE_FAMILIES,
    build_qa_attribution,
    route_for_failure_family,
    summarize_qa_attributions,
    validate_qa_attribution,
)
from beacon.utils.release_scorecard import summarize_release_scorecard
from beacon.utils.runtime import write_json


def test_finite_failure_taxonomy() -> None:
    assert set(FAILURE_FAMILIES) == {
        "implementation_gap",
        "truth_drift",
        "coverage_gap",
        "execution_lapse",
        "skill_defect",
        "runner_admission_blocker",
        "evidence_insufficient",
    }

    payload = build_qa_attribution(
        failure_family="unknown_family",
        affected_ac_ids=["AC-001"],
        evidence_refs=[".beacon/evidence/qa.json"],
    )

    assert payload["failure_family"] == "evidence_insufficient"
    assert payload["validation"]["status"] == "pass"


def test_non_runner_attribution_requires_ac_and_evidence() -> None:
    payload = build_qa_attribution(
        failure_family="implementation_gap",
        affected_ac_ids=[],
        evidence_refs=[],
    )

    reason_codes = {item["reason_code"] for item in payload["validation"]["issues"]}
    assert payload["validation"]["blocked"] is True
    assert "qa_attribution_ac_binding_missing" in reason_codes
    assert "qa_attribution_evidence_refs_missing" in reason_codes


def test_runner_blocker_can_precede_ac_evaluation() -> None:
    payload = build_qa_attribution(
        failure_family="runner_admission_blocker",
        affected_ac_ids=[],
        evidence_refs=[".beacon/evidence/runner.json"],
        runner_reached_ac_evaluation=False,
        blocker_reason="missing browser session",
        admission_surface="browser",
    )

    assert payload["validation"]["status"] == "pass"
    assert payload["route_recommendation"] == "blocked"


def test_failure_family_route_matrix() -> None:
    assert route_for_failure_family("implementation_gap") == "beacon-implement"
    assert route_for_failure_family("truth_drift") == "beacon-change"
    assert route_for_failure_family("coverage_gap") == "beacon-test-case"
    assert route_for_failure_family("execution_lapse") == "beacon-qa"
    assert route_for_failure_family("skill_defect") == "beacon-change"
    assert route_for_failure_family("runner_admission_blocker") == "blocked"
    assert route_for_failure_family("evidence_insufficient") == "beacon-qa"

    payload = build_qa_attribution(
        failure_family="truth_drift",
        affected_ac_ids=["AC-001"],
        evidence_refs=[".beacon/evidence/qa.json"],
        route_recommendation="beacon-implement",
    )

    assert payload["validation"]["blocked"] is True
    assert payload["validation"]["issues"][0]["reason_code"] == "qa_attribution_route_mismatch"


def test_ambiguous_or_missing_evidence_fails_closed() -> None:
    payload = build_qa_attribution(failure_family="", affected_ac_ids=["AC-001"], evidence_refs=[])

    reason_codes = {item["reason_code"] for item in payload["validation"]["issues"]}
    assert payload["failure_family"] == "evidence_insufficient"
    assert payload["validation"]["blocked"] is True
    assert "qa_attribution_evidence_refs_missing" in reason_codes
    assert payload["release_pass_evidence"] is False


def test_skill_defect_is_proposal_only(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills" / "beacon" / "beacon-qa" / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text("original", encoding="utf-8")

    payload = build_qa_attribution(
        failure_family="skill_defect",
        affected_ac_ids=["AC-001"],
        evidence_refs=[".beacon/evidence/qa.json"],
    )

    assert payload["proposal_only"] is True
    assert payload["validation"]["status"] == "pass"
    assert skill_path.read_text(encoding="utf-8") == "original"

    mutation_payload = dict(payload)
    mutation_payload["mutation_attempted"] = True
    validation = validate_qa_attribution(mutation_payload)
    assert validation["blocked"] is True
    assert validation["issues"][0]["reason_code"] == "qa_attribution_skill_mutation_forbidden"


def test_attribution_cannot_claim_truth_or_verdict_authority() -> None:
    payload = build_qa_attribution(
        failure_family="coverage_gap",
        affected_ac_ids=["AC-001"],
        evidence_refs=[".beacon/evidence/qa.json"],
        authority_boundary="release_verdict",
    )

    reason_codes = {item["reason_code"] for item in payload["validation"]["issues"]}
    assert payload["validation"]["blocked"] is True
    assert "qa_attribution_authority_bypass" in reason_codes


def test_summarize_fails_closed_on_raw_authority_claims() -> None:
    summary = summarize_qa_attributions(
        [
            {
                "failure_family": "implementation_gap",
                "affected_ac_ids": ["AC-001"],
                "evidence_refs": [".beacon/evidence/qa.json"],
                "truth_authority": True,
                "release_pass_evidence": True,
            }
        ]
    )

    attribution = summary["attributions"][0]
    reason_codes = {item["reason_code"] for item in attribution["validation"]["issues"]}
    assert summary["status"] == "blocked"
    assert summary["blocked_count"] == 1
    assert attribution["truth_authority"] is True
    assert attribution["release_pass_evidence"] is True
    assert "qa_attribution_authority_bypass" in reason_codes


def test_release_consumes_only_formal_qa_closure(tmp_path: Path) -> None:
    feature = "qa-evidence-attribution-layer"
    attribution = build_qa_attribution(
        failure_family="implementation_gap",
        affected_ac_ids=["AC-001"],
        evidence_refs=[".beacon/evidence/qa.json"],
    )
    summary = summarize_qa_attributions([attribution])
    scorecard = {
        "schema_version": "1.0",
        "feature": feature,
        "version": "v1.4.10",
        "release_ready": True,
        "continue_decision": "ready_for_release",
        "unresolved_closure_outcomes": [],
        "qa_attribution": summary,
    }
    path = tmp_path / ".beacon" / "qa" / "features" / feature / "scorecard.json"
    write_json(path, scorecard)
    payload = {
        "release_ready": True,
        "feature_qa_scorecard": json.loads(path.read_text(encoding="utf-8")),
        "qa_attribution_release_support": {
            "status": summary["status"],
            "support_evidence_only": True,
            "runtime_evidence_only": True,
            "truth_authority": False,
            "verdict_authority": False,
            "release_pass_evidence": False,
            "formal_qa_source": "feature_qa_scorecard",
            "attribution_count": summary["attribution_count"],
            "release_blocking_count": summary["release_blocking_count"],
        },
    }

    release_summary = summarize_release_scorecard(payload)

    assert release_summary["qa_attribution_count"] == 1
    assert release_summary["qa_attribution_release_blocking_count"] == 1
    assert release_summary["qa_attribution_release_pass_evidence"] is False
