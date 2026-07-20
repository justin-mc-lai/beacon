---
slug: loom-git-worktree-implement-harness
version: v2.0.0
status: frozen
revision_id: R2
---

# Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| requirement_truth | requirement_truth | docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/truth.md | frozen R2 | truth |
| test_truth | test_truth | docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/tests.md | frozen R2 | truth |
| research | support_advisory | docs/beacon/v2.0.0/research/branch-ref-hierarchy-collision-admit-main-fallback-pln-review.md | accepted GO 1A/2A/3A | change |
| change_r2 | support_advisory | docs/beacon/v2.0.0/change/loom-git-worktree-implement-harness-branch-hierarchy-r2.md | indexed | change |
| suite | test_truth | tests/test_v200_branch_ref_hierarchy.py | 9 passed | implement |
| admit_proof | support_advisory | run_workspace_admit leaf pass (loom-git-worktree + durable-longrun) | verified 2026-07-20 | implement |

## Boundary

Index only.

## R2 implement (2026-07-20)

- `beacon/utils/branch_ref_hierarchy.py` leaf + hierarchy preflight
- `execution_branch_contract` program-level keeps aggregation metadata, checkout always leaf
- `workspace_admission` / `git_alignment` refuse parent-with-children create
- `gate_workspace_admission_or_block` uses `implement_on_canonical_without_admission`
- Admit: `loom-git-worktree-implement-harness` → `beacon/v2.0.0/loom-git-worktree-implement-harness` **pass**
- Admit: `beacon-v2-goal-durable-longrun` → `beacon/v2.0.0/beacon-v2-goal-durable-longrun` **pass**
- Shared Python covers v1.6.8 runtime admit path
