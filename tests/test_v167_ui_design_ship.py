"""Contract tests for beacon-ui-design-ship-gate-v167."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.ui_design_ship import (
    REASON_DESIGN_MISSING,
    apply_ui_design_to_scorecard,
    build_ui_design_ship_gate,
    evaluate_ui_state_matrix,
    golden_commerce_matrix_present,
    parse_ui_state_matrix,
)

ROOT = Path(__file__).resolve().parents[1]

MATRIX = """
# UI State Matrix

| Order state | Page | Badge | Primary action |
|-------------|------|-------|----------------|
| draft | checkout | gray Draft | Place order |
| placed | order detail | blue Placed | Pay |
| paid | order detail | green Paid | Ship |
"""

TRUTH = """---
slug: ux-demo
version: v1.6.7
ux_required: true
---

# Checkout UI

## Domain FSM — Order

| State | From | Guard |
|-------|------|-------|
| draft | - | - |
| placed | draft | ok |
| paid | placed | ok |
"""


def test_matrix_schema() -> None:
    parsed = parse_ui_state_matrix(MATRIX)
    assert parsed["schema"] == "ui-state-matrix.v1"
    assert parsed["has_matrix"] is True
    assert "draft" in parsed["state_names"]
    result = evaluate_ui_state_matrix(
        matrix_markdown=MATRIX,
        truth_markdown=TRUTH,
        domain_states=["draft", "placed", "paid"],
    )
    assert result["blocked"] is False, result["findings"]
    assert result["schema"] == "ui-state-matrix.v1"
    assert "draft" in result["overlap"]


def test_missing_design_blocks_ship(tmp_path: Path) -> None:
    # no DESIGN.md, ux required via explicit flag
    gate = build_ui_design_ship_gate(
        tmp_path,
        version="v1.6.7",
        feature="ux-demo",
        truth_markdown=TRUTH,
        matrix_markdown=MATRIX,
        ux_required=True,
    )
    assert gate["required"] is True
    assert gate["blocked"] is True
    assert gate["reason_code"] == REASON_DESIGN_MISSING
    assert gate["release_ready_allowed"] is False
    # with DESIGN baseline
    (tmp_path / "DESIGN.md").write_text("# Design\n\ntokens\n", encoding="utf-8")
    gate2 = build_ui_design_ship_gate(
        tmp_path,
        version="v1.6.7",
        feature="ux-demo",
        truth_markdown=TRUTH,
        matrix_markdown=MATRIX,
        ux_required=True,
    )
    assert gate2["blocked"] is False, gate2["findings"]
    assert gate2["release_ready_allowed"] is True


def test_scorecard_design_checks() -> None:
    scorecard = {"release_ready": True, "continue_decision": "ready_for_release", "stop_reasons": []}
    gate = {
        "required": True,
        "blocked": True,
        "reason_code": REASON_DESIGN_MISSING,
        "design_alignment": {"status": "blocked", "required": True},
        "ui_state_matrix": {"status": "pass", "schema": "ui-state-matrix.v1"},
    }
    updated = apply_ui_design_to_scorecard(scorecard, gate)
    assert updated["release_ready"] is False
    assert "design_alignment" in updated
    assert "ui_state_matrix" in updated
    assert updated["ui_design_ship_blocked"] is True


def test_golden_has_matrix() -> None:
    result = golden_commerce_matrix_present(ROOT, version="v1.6.7")
    assert result["exists"] is True
    assert result["has_matrix"] is True
    assert result["status"] == "pass"
    assert any(s.lower() in {"draft", "placed", "paid", "shipped", "cancelled"} for s in result["state_names"])
