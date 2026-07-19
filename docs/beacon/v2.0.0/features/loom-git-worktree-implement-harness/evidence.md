---
slug: loom-git-worktree-implement-harness
version: v2.0.0
status: frozen
revision_id: R1
---

# Evidence Index: loom-git-worktree-implement-harness

| Surface | Authority | Canonical Artifact | Status |
|---------|-----------|--------------------|--------|
| requirement_truth | requirement_truth | docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/truth.md | frozen |
| acceptance | acceptance_truth | docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/truth.md | frozen |
| test_case | test_truth | docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/tests.md | frozen |
| planner | support_advisory | .beacon/state/planner-review/beacon-v2-rust-kernel-redesign/pln-review-20260719t110159z.json | accepted |
| program | support_advisory | docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/feature-graph.json | frozen |
| parent-kernel | support_advisory | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md | indexed |
| change | support_advisory | docs/beacon/v2.0.0/change/loom-kernel-closure-w1w5-v200.md | indexed |

## Boundary

Index only — formal implement/QA verdicts appended after wave implementation.

## Implement evidence (W1 R1 code)

- Implemented: `packages/beacon-rs/beacon-orchestrator/src/git_worktree.rs`
- Implemented: `packages/beacon-rs/beacon-orchestrator/src/implement_harness.rs`
- Integration tests: `packages/beacon-rs/beacon-orchestrator/tests/w1_worktree_implement_harness.rs`
- CLI: `beacon-v2 worktree resolve --materialize`, `beacon-v2 implement iterate`
- Commands run (2026-07-19T11:41:18Z):
  - `cargo test -p beacon-orchestrator --test w1_worktree_implement_harness` → 5 passed
    - tc099_real_git_worktree
    - tc100_implement_harness_one_iter
    - tc099_illegal_combo
    - iteration_result_schema_from_harness
    - tc_w1_legal_modes_walk
- Assertions: real `git worktree add` (`.git` is file), ImplementHarnessBackend not subprocess echo, AC-042 schema fields present.
- Non-claim: does not mark W2–W5 complete; does not default-switch production `beacon`.

