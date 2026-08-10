from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "docs" / "beacon" / "v1.4.0" / "prd" / "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md"


def test_reuse_diagram_and_semantic_first():
    text = PRD.read_text(encoding="utf-8")
    assert "升格现有 diagram truth 到更强的 requirement protocol" in text
    assert "升格现有 semantic dictionary 到更强的用词与映射校验源" in text


def test_minimal_extension_only():
    text = PRD.read_text(encoding="utf-8")
    assert "仅对现有不足概念做最小增量扩展" in text
    assert "`events / invariants / entities` 如确需补充，可作为后续最小扩展" in text


def test_no_forced_business_model_five_folders():
    text = PRD.read_text(encoding="utf-8")
    assert "不在第一步就强制引入新的五件 truth 目录" in text


def test_governance_before_expansion():
    text = PRD.read_text(encoding="utf-8")
    assert "新增大量目录或命令，反而让系统更重" in text
    assert "坚持 reuse before invent，优先升格现有能力" in text
