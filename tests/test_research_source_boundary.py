from __future__ import annotations

from pathlib import Path


def test_boundaries_should_state_workflow_and_gate_do_not_consume_research_directly():
    root = Path(__file__).resolve().parents[1]
    path = root / "docs" / "beacon" / "archive" / "v1.1.1" / "execution" / "boundaries.md"
    text = path.read_text(encoding="utf-8")
    assert "workflow / gate 只消费主链层" in text
    assert "research 直接参与 gate" in text
