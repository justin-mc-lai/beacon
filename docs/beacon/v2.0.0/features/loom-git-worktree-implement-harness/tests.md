---
slug: loom-git-worktree-implement-harness
version: v2.0.0
status: frozen
revision_id: R2
truth_ref: docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/truth.md
---

# Tests: loom-git-worktree-implement-harness (R2)

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-042 | TC-W1-003 | contract | `python3 -m pytest tests/test_v200_branch_ref_hierarchy.py -q` | IterationResult / harness path keeps AC-042 schema obligations |
| AC-099 | TC-W1-001 | contract | `python3 -m pytest tests/test_v200_branch_ref_hierarchy.py::test_ensure_worktree_lane_blocks_parent_create -q` | illegal parent create fail-closed |
| AC-100 | TC-W1-002 | integration | `python3 -m pytest tests/test_v200_branch_ref_hierarchy.py -q` + implement harness suite | ImplementHarness iterate in admitted worktree returns IterationResult |
| AC-BR-001 | TC-BR-001 | unit | `pytest tests/test_v200_branch_ref_hierarchy.py::test_resolve_targets_always_leaf -q` | feature_branch contains slug leaf |
| AC-BR-002 | TC-BR-002 | unit | `pytest tests/test_v200_branch_ref_hierarchy.py::test_hierarchy_preflight_detects_parent_child -q` | collision detected |
| AC-BR-003 | TC-BR-003 | unit | `pytest tests/test_v200_branch_ref_hierarchy.py::test_program_level_uses_leaf_checkout -q` | aggregation metadata + leaf checkout |
| AC-BR-004 | TC-BR-004 | unit | `pytest tests/test_v200_branch_ref_hierarchy.py::test_implement_blocked_without_admission_on_main -q` | no main soft fallback |
| AC-BR-005 | TC-BR-005 | contract | `pytest tests/test_v200_branch_ref_hierarchy.py::test_reason_codes_documented -q` | reason codes present |
| AC-BR-006 | TC-BR-006 | contract | `pytest tests/test_v200_branch_ref_hierarchy.py -q` | suite green |

## Illegal

| AC | TC | Assertion |
|----|-----|-----------|
| AC-BR-002 | TC-BR-ILLEGAL-01 | create parent while children exist → fail |
| AC-BR-004 | TC-BR-ILLEGAL-02 | admit fail + implement on main → blocked |
