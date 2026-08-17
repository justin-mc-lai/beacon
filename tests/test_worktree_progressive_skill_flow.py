"""AC-WT-SKILL: shared worktree norms + progressive skill mount (v1.6.8 / v2.0.0)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.product_goal_runtime import (
    WORKTREE_EXAMPLE_REF,
    WORKTREE_FLOW_REF,
    build_stage_plan,
    progressive_worktree_refs,
)

ROOT = Path(__file__).resolve().parents[1]


def test_tc_wt_001_shared_ref_exists() -> None:
    p = ROOT / WORKTREE_FLOW_REF
    assert p.is_file(), p
    text = p.read_text(encoding="utf-8")
    assert "Standard sequence" in text or "standard sequence" in text.lower() or "canonical_truth" in text
    assert "cherry-pick" in text.lower() or "cherry_pick" in text


def test_tc_wt_002_example_exists() -> None:
    p = ROOT / WORKTREE_EXAMPLE_REF
    assert p.is_file(), p
    assert "worktree" in p.read_text(encoding="utf-8").lower()


def test_tc_wt_003_goal_skill_references_flow() -> None:
    text = (ROOT / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    assert "git-worktree-execution-flow" in text


def test_tc_wt_004_progressive_refs_python() -> None:
    for stage in ("goal", "implement", "qa", "release", "truth"):
        payload = progressive_worktree_refs(stage)
        assert payload["required"] is True
        assert any("git-worktree-execution-flow" in r for r in payload["references"])
    plan = build_stage_plan(utterance="implement frozen lake")
    stages = {s["stage"]: s for s in plan}
    assert "goal" not in stages  # goal is facade, not lifecycle stage
    assert stages["plan"].get("public_entry_skill") == "beacon-goal"
    entry_refs = stages["plan"].get("public_entry_worktree_refs") or {}
    assert any("git-worktree-execution-flow" in r for r in entry_refs.get("references", []))
    impl = stages["implement"]
    assert any("git-worktree-execution-flow" in r for r in impl.get("references", []))


def test_tc_wt_006_bulk_forbidden_bounded() -> None:
    plan = build_stage_plan(utterance="x")
    # must not explode into 30+ skill loads per stage
    for s in plan:
        assert len(s.get("skills") or []) < 20
