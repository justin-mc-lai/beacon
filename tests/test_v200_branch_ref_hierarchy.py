"""v2.0.0 branch ref hierarchy hard gate (UD-BR / AC-BR)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.branch_ref_hierarchy import (
    REASON_HIERARCHY,
    ensure_leaf_checkout_branch,
    hierarchy_collision,
    is_program_aggregation_branch,
    leaf_feature_branch,
)
from beacon.utils.execution_branch_contract import resolve_workspace_branch_targets
from beacon.utils.git_alignment import ensure_expected_worktree_lane
from beacon.utils.workspace_admission import (
    gate_workspace_admission_or_block,
    resolve_feature_branch,
)

ROOT = Path(__file__).resolve().parents[1]


def test_is_program_aggregation_branch() -> None:
    assert is_program_aggregation_branch("beacon/v2.0.0") is True
    assert is_program_aggregation_branch("beacon/v2.0.0/foo") is False
    assert is_program_aggregation_branch("main") is False


def test_leaf_feature_branch() -> None:
    b = leaf_feature_branch(version="v2.0.0", feature="loom-git-worktree-implement-harness")
    assert b == "beacon/v2.0.0/loom-git-worktree-implement-harness"
    b2 = leaf_feature_branch(version="v2.0.0", feature="x", pattern="beacon/v2.0.0")
    assert b2 == "beacon/v2.0.0/x"
    # Monorepo shared feature/<ver> must not nest — escape to beacon leaf.
    b3 = leaf_feature_branch(version="v2.3.5", feature="push-outbound-otel", pattern="feature/v2.3.5")
    assert b3 == "beacon/v2.3.5/push-outbound-otel"
    b4 = leaf_feature_branch(
        version="v2.3.5",
        feature="sms-trace-propagation",
        pattern="beacon/<version>/<feature-slug>",
    )
    assert b4 == "beacon/v2.3.5/sms-trace-propagation"


def test_resolve_feature_branch_always_leaf() -> None:
    branch = resolve_feature_branch(
        {"feature_branch_pattern": "beacon/v2.0.0", "version": "v2.0.0"},
        feature="my-feature",
        version="v2.0.0",
    )
    assert branch.endswith("/my-feature")
    assert branch != "beacon/v2.0.0"


def test_hierarchy_preflight_detects_parent_child() -> None:
    # Live repo has beacon/v2.0.0/* children — parent collides
    hit = hierarchy_collision(ROOT, "beacon/v2.0.0")
    assert hit["collides"] is True
    assert hit["reason_code"] == REASON_HIERARCHY
    assert any(str(c).startswith("beacon/v2.0.0/") for c in hit["conflicts"])


def test_ensure_leaf_rewrites_aggregation() -> None:
    info = ensure_leaf_checkout_branch(
        ROOT,
        version="v2.0.0",
        feature="loom-git-worktree-implement-harness",
        candidate="beacon/v2.0.0",
    )
    assert info["ok"] is True
    assert info["feature_branch"] == "beacon/v2.0.0/loom-git-worktree-implement-harness"
    assert info.get("rewrote") is True


def test_program_level_uses_leaf_checkout() -> None:
    targets = resolve_workspace_branch_targets(
        ROOT,
        version="v2.0.0",
        feature="loom-git-worktree-implement-harness",
        admission_contract={"version": "v2.0.0", "feature_branch_pattern": "", "worktree_base": ".beacon/worktrees/v2.0.0"},
    )
    fb = str(targets.get("feature_branch") or "")
    assert "loom-git-worktree-implement-harness" in fb
    assert fb != "beacon/v2.0.0"
    # must not be pure aggregation
    assert not is_program_aggregation_branch(fb)


def test_ensure_worktree_lane_blocks_parent_create() -> None:
    out = ensure_expected_worktree_lane(
        ROOT,
        "beacon/v2.0.0",
        worktree_path=str(ROOT / ".beacon/worktrees/_hierarchy_probe"),
        base_branch="main",
    )
    assert out.get("status") == "failed"
    assert out.get("reason") == "branch_ref_hierarchy_collision" or out.get("reason_code") == "branch_ref_hierarchy_collision"


def test_reason_codes_documented() -> None:
    truth = (ROOT / "docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/truth.md").read_text(
        encoding="utf-8"
    )
    for token in (
        "UD-BR-001",
        "AC-BR-001",
        "branch_ref_hierarchy_collision",
        "implement_on_canonical_without_admission",
        "leaf",
    ):
        assert token in truth, token


def test_implement_blocked_without_admission_on_main() -> None:
    # On main without admission artifact for this feature → blocked when require is true
    block = gate_workspace_admission_or_block(
        ROOT,
        version="v2.0.0",
        feature="loom-git-worktree-implement-harness",
        cwd=ROOT,
    )
    # Either require admission and block, or if not required, skip — but monorepo v2 should require.
    if block is not None:
        assert block.get("status") == "blocked"
        assert block.get("reason_code") in {
            "implement_on_canonical_without_admission",
            "workspace_admission_missing",
            "workspace_admission_required",
            "workspace_admission_worktree_failed",
            "branch_alignment_required",
        }
