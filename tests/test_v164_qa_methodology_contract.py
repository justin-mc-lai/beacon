"""Tests for beacon-qa-methodology-contract-v164."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.planner_review_runtime import (
    REASON_ADVERSARIAL_REVIEW_MISSING,
    build_qa_release_adversarial_review,
    ensure_qa_release_adversarial_lane,
    validate_adversarial_review_delivery,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GLOBAL_BOUNDARIES = PROJECT_ROOT / "docs" / "beacon" / "global-boundaries.md"
QA_SKILL = PROJECT_ROOT / "skills" / "beacon" / "beacon-eval-qa" / "SKILL.md"


def test_first_principles_clause() -> None:
    text = GLOBAL_BOUNDARIES.read_text(encoding="utf-8")
    section = text.split("## 5. Skill 哲学边界", 1)[1].split("## 6.", 1)[0]
    assert "第一性原理" in section
    assert "最小可验证单元" in section
    assert "为什么" in section
    assert section.count("默认哲学") >= 1


def test_adversarial_clause() -> None:
    text = GLOBAL_BOUNDARIES.read_text(encoding="utf-8")
    section = text.split("## 5. Skill 哲学边界", 1)[1].split("## 6.", 1)[0]
    assert "对抗式审查" in section
    assert "3" in section and "5" in section
    assert "adversarial_review_missing" in section
    assert "看起来没问题" in section


def test_qa_skill_contract_mandatory() -> None:
    text = QA_SKILL.read_text(encoding="utf-8")
    assert "对抗式审查" in text
    assert "adversarial_review_missing" in text
    blocked = validate_adversarial_review_delivery({"failure_points": ["a"], "verification_evidence": []})
    assert blocked["blocked"] is True
    assert blocked["reason_code"] == REASON_ADVERSARIAL_REVIEW_MISSING


def test_adversarial_lane_mandatory() -> None:
    selected = ensure_qa_release_adversarial_lane(prompt="qa release check")
    reviewers = {item["reviewer"] for item in selected}
    assert "adversarial-reviewer" in reviewers
    blocked = build_qa_release_adversarial_review(
        prompt="qa release",
        failure_points=["gap-1"],
        verification_evidence=[],
    )
    assert blocked["blocked"] is True
    assert blocked["adversarial_lane_mandatory"] is True
    passed = build_qa_release_adversarial_review(
        prompt="qa release",
        failure_points=["gap-1", "gap-2", "gap-3"],
        verification_evidence=["ev-1", "ev-2", "ev-3"],
    )
    assert passed["blocked"] is False
