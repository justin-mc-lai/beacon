from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "docs" / "beacon" / "v1.4.0" / "prd" / "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md"
PRD_SKILL = ROOT / "skills" / "beacon" / "beacon-prd" / "SKILL.md"
STORY_SKILL = ROOT / "skills" / "beacon" / "beacon-user-story" / "SKILL.md"
CASE_SKILL = ROOT / "skills" / "beacon" / "beacon-test-case" / "SKILL.md"


def test_diagram_trigger_blocks_template_fill():
    text = PRD.read_text(encoding="utf-8")
    skill_text = PRD_SKILL.read_text(encoding="utf-8")
    assert "若问题复杂度达到 diagram truth 触发条件，则不允许直接模板填空" in text
    assert "Block shallow template fill" in skill_text


def test_state_transition_reasoning_required():
    text = PRD.read_text(encoding="utf-8")
    story_text = STORY_SKILL.read_text(encoding="utf-8")
    assert "必须围绕状态、转移、异常路径、不变量做显式建模推理" in text
    assert "Require explicit state/transition reasoning" in story_text


def test_state_axis_is_reused_when_present():
    text = PRD.read_text(encoding="utf-8")
    assert "是否需要 state axis" in text
    assert "是否存在 state-machine" in text


def test_output_stays_consistent_with_diagram_truth():
    text = PRD.read_text(encoding="utf-8")
    case_text = CASE_SKILL.read_text(encoding="utf-8")
    assert "相关输出应与 diagram truth 保持一致" in text
    assert "diagram / semantic inputs" in case_text
