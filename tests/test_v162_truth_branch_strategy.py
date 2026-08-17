"""Truth branch strategy (v1.6.2 R4 rules, now carried by the shared execution flow).

Rules under test (unchanged since R4):
- truth authoring stays on canonical main, never the feature worktree
- implement must merge main before writing (feature_worktree_reconcile)
- implement/qa/release stay in admitted worktrees
"""
from __future__ import annotations

from pathlib import Path

TRUTH_PATH = Path("skills/beacon/references/git-worktree-execution-flow.md")


def _truth_text() -> str:
    return Path(TRUTH_PATH).read_text(encoding="utf-8")


# ---- AC-016 truth tier downgrade ----

def test_truth_tier_downgrade() -> None:
    """Truth authoring stays on canonical main; writing truth on a worktree is illegal."""
    src = _truth_text()
    assert "Truth / freeze / refreeze" in src and "truth_canonical" in src
    assert "truth_canonical_branch_mismatch" in src
    assert "Write requirement revision on feature worktree" in src


# ---- AC-017 implement merge main preamble ----

def test_implement_merge_main_preamble() -> None:
    """Delivery must align with main via merge before implement writes."""
    src = _truth_text()
    assert "Align delivery with main via `git merge`" in src
    assert "feature_worktree_reconcile" in src or "reconcile" in src
    assert "implement" in src.lower()


# ---- AC-018 Tier A preserved ----

def test_tier_a_preserved() -> None:
    """Implement/QA/release stay in admitted worktrees."""
    src = _truth_text()
    for surface in ("Implement", "QA", "release"):
        assert surface.lower() in src.lower(), f"{surface} missing from execution flow"
    assert "admitted" in src
