"""Contract tests for beacon-domain-fsm-qa-gate-v167."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.domain_fsm_qa import (
    REASON_COVERAGE_MISSING,
    REASON_ILLEGAL_CASE_MISSING,
    REASON_LEGAL_WALK_MISSING,
    apply_domain_fsm_to_scorecard,
    build_domain_fsm_coverage,
    consume_golden_negative_for_qa,
    evaluate_domain_fsm_qa_gate,
    parse_domain_qa_matrix,
)

ROOT = Path(__file__).resolve().parents[1]

DOMAIN_TRUTH = """---
slug: demo-domain
version: v1.6.7
domain_required: true
---

## Domain Model

| Entity | Key | Precedence |
|--------|-----|------------|
| Product | product_id | root |
| Order | order_id | requires Product |

## Domain FSM — Order

| State | From | Guard |
|-------|------|-------|
| draft | - | - |
| placed | draft | product.listed |
| paid | placed | payment.ok |

## Illegal transitions

- Order.placed without Product

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | User can place Order with listed Product |
| AC-002 | System rejects order without product (illegal) |
"""

GOOD_TESTS = """
## Coverage Matrix

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-001 | TC-001 | legal walk | pytest | draft→placed succeeds |
| AC-001 | TC-002 | legal walk | pytest | placed→paid succeeds |
| AC-002 | TC-003 | illegal | pytest | place without product fails |
"""

BAD_TESTS_NO_ILLEGAL = """
## Coverage Matrix

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-001 | TC-001 | legal walk | pytest | draft→placed succeeds |
"""

BAD_TESTS_NO_LEGAL = """
## Coverage Matrix

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-002 | TC-003 | illegal | pytest | place without product fails |
"""


def test_matrix_requires_legal_walk() -> None:
    matrix = parse_domain_qa_matrix(GOOD_TESTS)
    assert matrix["has_legal_walk"] is True
    gate = evaluate_domain_fsm_qa_gate(truth_markdown=DOMAIN_TRUTH, tests_markdown=BAD_TESTS_NO_LEGAL)
    assert gate["blocked"] is True
    codes = {f.get("reason_code") for f in gate["findings"]}
    assert REASON_LEGAL_WALK_MISSING in codes


def test_matrix_requires_illegal() -> None:
    gate = evaluate_domain_fsm_qa_gate(truth_markdown=DOMAIN_TRUTH, tests_markdown=BAD_TESTS_NO_ILLEGAL)
    assert gate["blocked"] is True
    codes = {f.get("reason_code") for f in gate["findings"]}
    assert REASON_ILLEGAL_CASE_MISSING in codes
    good = evaluate_domain_fsm_qa_gate(truth_markdown=DOMAIN_TRUTH, tests_markdown=GOOD_TESTS)
    assert good["blocked"] is False, good["findings"]
    assert good["release_ready_allowed"] is True


def test_missing_coverage_blocks_ready() -> None:
    coverage = build_domain_fsm_coverage(
        truth_markdown=DOMAIN_TRUTH,
        tests_markdown="## Coverage Matrix\n\n| AC | TC |\n|----|----|\n| AC-001 | TC-001 |\n",
    )
    assert coverage["required"] is True
    assert coverage["blocked"] is True
    scorecard = {
        "release_ready": True,
        "continue_decision": "ready_for_release",
        "stop_reasons": [],
    }
    gate = evaluate_domain_fsm_qa_gate(truth_markdown=DOMAIN_TRUTH, tests_markdown="")
    updated = apply_domain_fsm_to_scorecard(scorecard, gate)
    assert updated["release_ready"] is False
    assert updated["continue_decision"] != "ready_for_release"
    assert updated.get("domain_fsm_qa_blocked") is True
    assert "domain_fsm_coverage" in updated
    # empty matrix should surface legal/illegal missing rather than silent pass
    assert gate["reason_code"] in {
        REASON_LEGAL_WALK_MISSING,
        REASON_ILLEGAL_CASE_MISSING,
        REASON_COVERAGE_MISSING,
        "domain_fsm_coverage_below_threshold",
    } or gate["blocked"]


def test_golden_negative_consumed() -> None:
    result = consume_golden_negative_for_qa(ROOT, version="v1.6.7")
    assert result["expected_fail"] is True
    assert result["consumed"] is True, result
    assert result["blocked"] is False
