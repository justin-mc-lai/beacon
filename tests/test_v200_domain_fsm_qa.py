"""v2.0.0 Domain FSM QA gate tests."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.domain_fsm_qa import (
    REASON_ILLEGAL_CASE_MISSING,
    REASON_LEGAL_WALK_MISSING,
    apply_domain_fsm_to_scorecard,
    consume_golden_negative_for_qa,
    evaluate_domain_fsm_qa_gate,
)

ROOT = Path(__file__).resolve().parents[1]

DOMAIN_TRUTH = """---
slug: demo-domain
version: v2.0.0
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

## Illegal transitions

- Order.placed without Product

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | place with product |
| AC-002 | reject without product |
"""

GOOD = """
## Coverage Matrix

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-001 | TC-001 | legal walk | pytest | draft→placed |
| AC-002 | TC-003 | illegal | pytest | without product fails |
"""

NO_LEGAL = """
## Coverage Matrix

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-002 | TC-003 | illegal | pytest | fails |
"""

NO_ILLEGAL = """
## Coverage Matrix

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-001 | TC-001 | legal walk | pytest | ok |
"""


def test_legal_walk_required() -> None:
    gate = evaluate_domain_fsm_qa_gate(truth_markdown=DOMAIN_TRUTH, tests_markdown=NO_LEGAL)
    assert gate["blocked"] is True
    codes = {f.get("reason_code") for f in gate["findings"]}
    assert REASON_LEGAL_WALK_MISSING in codes


def test_illegal_required() -> None:
    gate = evaluate_domain_fsm_qa_gate(truth_markdown=DOMAIN_TRUTH, tests_markdown=NO_ILLEGAL)
    assert gate["blocked"] is True
    codes = {f.get("reason_code") for f in gate["findings"]}
    assert REASON_ILLEGAL_CASE_MISSING in codes
    good = evaluate_domain_fsm_qa_gate(truth_markdown=DOMAIN_TRUTH, tests_markdown=GOOD)
    assert good["blocked"] is False, good


def test_missing_coverage_blocks_release() -> None:
    gate = evaluate_domain_fsm_qa_gate(truth_markdown=DOMAIN_TRUTH, tests_markdown="")
    scorecard = {"release_ready": True, "continue_decision": "ready_for_release", "stop_reasons": []}
    updated = apply_domain_fsm_to_scorecard(scorecard, gate)
    assert updated["release_ready"] is False
    assert updated.get("domain_fsm_qa_blocked") is True


def test_golden_negative_consumed() -> None:
    result = consume_golden_negative_for_qa(ROOT, version="v2.0.0")
    # if version falls back to v167 fixture content
    if not result.get("consumed"):
        result = consume_golden_negative_for_qa(ROOT, version="v1.6.7")
    assert result["expected_fail"] is True
    assert result["consumed"] is True, result
