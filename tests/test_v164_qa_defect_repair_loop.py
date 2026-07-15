"""Tests for beacon-qa-defect-repair-loop-v164."""

from __future__ import annotations

from beacon.utils.qa_attribution import RELEASE_BLOCKING_FAMILIES, ROUTE_RECOMMENDATIONS
from beacon.utils.qa_repair_loop import (
    REASON_REGRESSION_SKIPPED,
    REASON_REPAIR_CHAIN_BROKEN,
    build_repair_loop_verdict,
    classify_defect,
)


def test_defect_classification() -> None:
    for family in ROUTE_RECOMMENDATIONS:
        result = classify_defect(failure_family=family)
        assert result["blocked"] is False
        assert result["defect_classification"]["family"] == family
    blocked = classify_defect(failure_family="unknown-family")
    assert blocked["blocked"] is True


def test_repair_route_field() -> None:
    result = classify_defect(failure_family="implementation_gap")
    assert result["repair_route"] == "beacon-implement"
    assert result["defect_classification"]["reason_code"] == "implementation_gap"


def test_route_rules_release_blocking() -> None:
    assert classify_defect(failure_family="implementation_gap")["repair_route"] == "beacon-implement"
    assert classify_defect(failure_family="truth_drift")["repair_route"] == "beacon-change"
    assert classify_defect(failure_family="coverage_gap")["repair_route"] == "beacon-test-case"
    assert classify_defect(failure_family="execution_lapse")["repair_route"] == "beacon-qa"
    assert "implementation_gap" in RELEASE_BLOCKING_FAMILIES
    assert "truth_drift" in RELEASE_BLOCKING_FAMILIES
    assert "coverage_gap" in RELEASE_BLOCKING_FAMILIES


def test_regression_trigger() -> None:
    verdict = build_repair_loop_verdict(
        defect_finding={"failure_family": "implementation_gap"},
        fix_evidence={"executed": True},
        regression_evidence=None,
    )
    assert verdict["regression_required"] is True
    assert verdict["blocked"] is True
    assert verdict["reason_code"] == REASON_REGRESSION_SKIPPED


def test_closure_evidence_chain() -> None:
    incomplete = build_repair_loop_verdict(
        defect_finding={"failure_family": "truth_drift"},
        fix_evidence=None,
        regression_evidence=None,
    )
    assert incomplete["blocked"] is True
    assert incomplete["reason_code"] == REASON_REPAIR_CHAIN_BROKEN
    complete = build_repair_loop_verdict(
        defect_finding={"failure_family": "truth_drift"},
        fix_evidence={"executed": True},
        regression_evidence={"executed": True},
    )
    assert complete["blocked"] is False
    assert complete["closure_chain"]["missing_segments"] == []
