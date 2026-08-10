from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "docs" / "beacon" / "v1.4.0" / "prd" / "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md"


def test_dual_read_required_before_cutover():
    text = PRD.read_text(encoding="utf-8")
    assert "双读并记录差异" in text
    assert "达到一致性阈值后切主" in text


def test_reason_and_gate_consistency_checked():
    text = PRD.read_text(encoding="utf-8")
    assert "blocked reason 是否一致" in text
    assert "downgrade / fallback 路线是否一致" in text
    assert "gate 结果是否保持 fail-closed" in text


def test_inconsistent_cutover_fails_closed():
    text = PRD.read_text(encoding="utf-8")
    assert "一致性不足时，保留 Python 作为主判定器" in text


def test_compatibility_window_retains_legacy_fallback():
    text = PRD.read_text(encoding="utf-8")
    assert "保留一段兼容窗口" in text
