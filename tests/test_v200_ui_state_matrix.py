"""v2.0.0 UI state matrix ship gate tests."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.ui_design_ship import (
    apply_ui_design_to_scorecard,
    build_ui_design_ship_gate,
    evaluate_primitives_only_insufficient,
    evaluate_ui_state_matrix,
    golden_commerce_matrix_present,
    parse_ui_state_matrix,
)

ROOT = Path(__file__).resolve().parents[1]

MATRIX = """
# UI State Matrix

| Order state | Page | Badge | Primary action |
|-------------|------|-------|----------------|
| draft | checkout | gray | Place |
| placed | detail | blue | Pay |
| paid | detail | green | Ship |
"""

TRUTH = """---
slug: ux-demo
version: v2.0.0
ux_required: true
---

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
    result = evaluate_ui_state_matrix(
        matrix_markdown=MATRIX,
        truth_markdown=TRUTH,
        domain_states=["draft", "placed", "paid"],
    )
    assert result["blocked"] is False, result


def test_missing_matrix_blocks_release(tmp_path: Path) -> None:
    (tmp_path / "DESIGN.md").write_text("# Design\n", encoding="utf-8")
    gate = build_ui_design_ship_gate(
        tmp_path,
        version="v2.0.0",
        feature="ux-demo",
        truth_markdown=TRUTH,
        matrix_markdown="",
        ux_required=True,
    )
    assert gate["required"] is True
    assert gate["blocked"] is True
    assert gate["release_ready_allowed"] is False
    scorecard = {"release_ready": True, "continue_decision": "ready_for_release", "stop_reasons": []}
    updated = apply_ui_design_to_scorecard(scorecard, gate)
    assert updated["release_ready"] is False
    assert "ui_state_matrix" in updated


def test_primitives_only_insufficient() -> None:
    r = evaluate_primitives_only_insufficient(
        has_design_primitives=True,
        has_ui_state_matrix=False,
        ux_required=True,
    )
    assert r["blocked"] is True
    assert r["release_ready_allowed"] is False
    assert r["not_primitives_only_rule"] is True
    ok = evaluate_primitives_only_insufficient(
        has_design_primitives=True,
        has_ui_state_matrix=True,
        ux_required=True,
    )
    assert ok["blocked"] is False
    assert ok["release_ready_allowed"] is True


def test_v167_inherit() -> None:
    result = golden_commerce_matrix_present(ROOT, version="v2.0.0")
    assert result["exists"] is True
    assert result["has_matrix"] is True
