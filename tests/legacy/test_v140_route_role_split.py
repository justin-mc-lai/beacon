from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "docs" / "beacon" / "v1.4.0" / "prd" / "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md"
STORY = ROOT / "docs" / "beacon" / "v1.4.0" / "user-story" / "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md"
GLOBAL = ROOT / "docs" / "beacon" / "global-boundaries.md"


def test_ask_role_is_route_preview_execute():
    text = STORY.read_text(encoding="utf-8")
    assert "`ask` 必须被定义为自然语言入口、路由、计划预览与受控执行面。" in text


def test_brainstorm_is_read_only_convergence():
    text = STORY.read_text(encoding="utf-8")
    assert "`brainstorm` 必须被定义为只读收敛、矛盾识别、开放问题澄清与路线建议面。" in text


def test_frozen_truth_changes_route_to_change():
    text = STORY.read_text(encoding="utf-8")
    assert "任何触及 frozen truth 的正式变更都必须回到 `change` 路由" in text


def test_no_new_stage_confusion():
    text = GLOBAL.read_text(encoding="utf-8")
    assert "prd\n→ user-story\n→ test-case\n→ implement\n→ qa\n→ release" in text
    assert "它们是支持面，不是新主流程。" in text
    assert "ask" not in text.split("```text", 1)[1].split("```", 1)[0]
