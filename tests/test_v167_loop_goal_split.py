"""Contract tests for beacon-loop-discover-goal-finish-v167 R3."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.goal_queue import (
    REASON_LOOP_CANNOT_COMPLETE,
    assert_not_product_complete_authority,
    enqueue_discovery,
    list_queued,
    reject_loop_product_complete,
)
from beacon.utils.product_goal_runtime import consume_discovery_queue

ROOT = Path(__file__).resolve().parents[1]


def test_loop_skill_support_meta() -> None:
    text = (ROOT / "skills/beacon/beacon-goal/references/modes/loop-goal.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "support" in lowered
    assert "beacon-goal" in text or "$beacon-goal" in text
    assert "metadata_entry: support_discovery" in text or "support/internal" in lowered


def test_no_coequal_entry_in_examples() -> None:
    paths = [
        ROOT / "skills/beacon/examples/goal-one-shot-30s.md",
        ROOT / "skills/beacon/SKILL.md",
        ROOT / "skills/beacon/beacon-goal/SKILL.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        # Forbidden: instructing users to run loop then goal as required pipeline
        # Allow negative examples with 不要/❌
        if "先" in text and "loop" in text.lower() and "goal" in text.lower():
            assert "不要" in text or "❌" in text or "禁止" in text
        # Must not list dual primary entries without support qualifier
        assert "两个主编排" not in text or "不需要" in text


def test_loop_cannot_mark_complete() -> None:
    rejected = reject_loop_product_complete(attempted_by="beacon-loop-goal")
    assert rejected["allowed"] is False
    assert rejected["reason_code"] == REASON_LOOP_CANNOT_COMPLETE
    assert rejected["redirect"] == "beacon-goal"
    cleaned = assert_not_product_complete_authority(
        {"product_complete": True, "qa_verdict": "pass", "release_ready": True}
    )
    assert cleaned["product_complete"] is False
    assert cleaned["release_ready"] is False
    assert cleaned["reason_code"] == REASON_LOOP_CANNOT_COMPLETE


def test_loop_points_to_goal() -> None:
    text = (ROOT / "skills/beacon/beacon-goal/references/modes/loop-goal.md").read_text(encoding="utf-8")
    assert "beacon-goal" in text or "$beacon-goal" in text
    assert "交付" in text or "goal run" in text or "一句话" in text


def test_queue_handoff_to_goal(tmp_path: Path) -> None:
    enq = enqueue_discovery(
        tmp_path,
        utterance="发现：需要补 domain fsm",
        version="v1.6.7",
        feature="demo",
    )
    assert enq["status"] == "pass"
    assert enq["item"]["may_mark_product_complete"] is False
    assert list_queued(tmp_path)
    consumed = consume_discovery_queue(tmp_path, version="v1.6.7")
    assert consumed.get("run_id")
    assert consumed.get("from_queue_item") == enq["item"]["id"]
