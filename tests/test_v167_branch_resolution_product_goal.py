"""Product-goal lakes must not inherit git-scope-graph program branch."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.execution_branch_contract import (
    find_program_level_git_workflow,
    resolve_workspace_branch_targets,
)
from beacon.utils.workspace_admission import load_admission_contract, validate_workspace_admission

ROOT = Path(__file__).resolve().parents[1]
PRODUCT_LAKES = [
    "beacon-domain-fsm-authority-v167",
    "beacon-golden-commerce-fixture-v167",
    "beacon-domain-fsm-qa-gate-v167",
    "beacon-product-goal-runtime-v167",
    "beacon-ui-design-ship-gate-v167",
    "beacon-loop-discover-goal-finish-v167",
    "beacon-ralph-implement-boundary-v167",
]


def test_product_goal_lakes_not_git_scope_graph_branch() -> None:
    contract = load_admission_contract(ROOT, version="v1.6.7")
    for feature in PRODUCT_LAKES:
        targets = resolve_workspace_branch_targets(
            ROOT,
            version="v1.6.7",
            feature=feature,
            admission_contract={**contract, "version": "v1.6.7"},
        )
        branch = str(targets.get("feature_branch") or "")
        assert "git-scope-graph" not in branch, (feature, targets)
        assert "beacon-loop-goal-v166" not in branch, (feature, targets)


def test_find_program_workflow_feature_aware() -> None:
    scoped = find_program_level_git_workflow(
        ROOT, version="v1.6.7", feature="beacon-domain-fsm-authority-v167"
    )
    assert scoped is not None
    branch = str(scoped.get("expected_branch") or "")
    assert "git-scope-graph" not in branch
    # product-goal program workflow or topology aggregation
    assert "v1.6.7" in branch or branch.startswith("beacon/")


def test_main_accepted_for_product_goal_admission() -> None:
    """On main (truth_canonical), product-goal lakes must not fail branch_alignment."""
    result = validate_workspace_admission(
        ROOT,
        version="v1.6.7",
        feature="beacon-domain-fsm-authority-v167",
        cwd=ROOT,
    )
    assert result.get("valid") is True, result
    assert result.get("reason_code") != "branch_alignment_required"
