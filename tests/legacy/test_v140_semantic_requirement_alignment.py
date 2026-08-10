from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "docs" / "beacon" / "v1.4.0" / "prd" / "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md"
PRD_SKILL = ROOT / "skills" / "beacon" / "beacon-prd" / "SKILL.md"
STORY_SKILL = ROOT / "skills" / "beacon" / "beacon-user-story" / "SKILL.md"


def test_semantic_trace_is_shared_input():
    text = PRD.read_text(encoding="utf-8")
    assert "semantic trace 至少应服务于" in text
    assert "semantic trace 可作为校验输入" in text


def test_official_vocabulary_is_reused():
    prd_skill = PRD_SKILL.read_text(encoding="utf-8")
    story_skill = STORY_SKILL.read_text(encoding="utf-8")
    assert "Prefer reusing official wording" in prd_skill
    assert "Prefer official states, actions, modules, and page names" in story_skill


def test_semantic_trace_is_not_second_truth():
    text = PRD.read_text(encoding="utf-8")
    story_skill = STORY_SKILL.read_text(encoding="utf-8")
    assert "不得单独成为 truth root" in text
    assert "Do not invent a second terminology layer" in story_skill


def test_wording_drift_is_reduced():
    text = PRD.read_text(encoding="utf-8")
    assert "避免 requirement 文本与实现/semantic trace 长期漂移" in text
    assert "官方状态名引用" in text
