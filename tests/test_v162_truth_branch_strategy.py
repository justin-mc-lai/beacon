"""Tests for beacon-global-workspace-git-admission-v162 R4: truth branch strategy.

R4 changes (truth 分支策略):
- beacon-gen-truth downgraded from Tier A to Tier C (truth written on main)
- GIT_ADMISSION preamble adds implement-merge-main step
- Tier A preserved for implement/qa/release/change
"""
from __future__ import annotations

from pathlib import Path

TRUTH_PATH = Path("docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/truth.md")


def _truth_text() -> str:
    return Path(TRUTH_PATH).read_text(encoding="utf-8")


# ---- AC-016 truth tier downgrade ----

def test_truth_tier_downgrade() -> None:
    """beacon-gen-truth is NOT in Tier A; truth written on main, not worktree."""
    src = _truth_text()
    # beacon-gen-truth must not be in the Tier A row
    tier_a_line = next((ln for ln in src.splitlines() if "| **A** |" in ln), "")
    assert "beacon-gen-truth" not in tier_a_line, f"beacon-gen-truth still in Tier A: {tier_a_line}"
    # beacon-gen-truth must be in Tier C
    tier_c_line = next((ln for ln in src.splitlines() if "| **C** |" in ln), "")
    assert "beacon-gen-truth" in tier_c_line, f"beacon-gen-truth not in Tier C: {tier_c_line}"


# ---- AC-017 implement merge main preamble ----

def test_implement_merge_main_preamble() -> None:
    """GIT_ADMISSION preamble contains implement-merge-main step."""
    src = _truth_text()
    assert "merge main" in src, "preamble missing 'merge main' step"
    # the merge-main step must be gated to implement only
    assert "implement only" in src or "implement 前" in src, "merge-main step not gated to implement"


# ---- AC-018 Tier A preserved ----

def test_tier_a_preserved() -> None:
    """implement/qa/release/change stay in Tier A worktree."""
    src = _truth_text()
    tier_a_line = next((ln for ln in src.splitlines() if "| **A** |" in ln), "")
    for skill in ("beacon-gen-implement", "beacon-eval-qa", "beacon-eval-release", "beacon-gen-change"):
        assert skill in tier_a_line, f"{skill} missing from Tier A: {tier_a_line}"
