from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "docs" / "beacon" / "v1.4.0" / "prd" / "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md"


def test_four_heavy_modules_are_covered():
    text = PRD.read_text(encoding="utf-8")
    assert "`beacon/commands/qa.py`" in text
    assert "`beacon/commands/implement.py`" in text
    assert "`beacon/commands/prd.py`" in text
    assert "`beacon/commands/release.py`" in text


def test_read_write_vs_judgment_classification():
    text = PRD.read_text(encoding="utf-8")
    assert "先识别哪部分是“事实/写入逻辑”，哪部分是“解释/判断逻辑”" in text


def test_judgment_logic_migrates_first():
    text = PRD.read_text(encoding="utf-8")
    assert "优先迁出后者" in text
    assert "迁移时保留 legacy 对账开关" in text


def test_shared_governance_view_across_modules():
    text = PRD.read_text(encoding="utf-8")
    assert "至少需要把以下模块纳入同一瘦身治理视角" in text
