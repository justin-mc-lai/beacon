---
slug: loom-git-worktree-implement-harness
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/truth.md
---

# Tests: loom-git-worktree-implement-harness

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-099 | TC-W1-001 | integration | `cargo test -p beacon-orchestrator tc099_real_git_worktree` | git worktree exists |
| AC-042 | TC-W1-000 | contract | `cargo test -p beacon-core iteration_result_schema` | schema fields |
| AC-100 | TC-W1-002 | integration | `cargo test -p beacon-orchestrator tc100_implement_harness_one_iter` | IterationResult ok |
| AC-099 | TC-W1-003 | negative | `cargo test -p beacon-orchestrator tc099_illegal_combo` | blocked |

## Legal / Illegal

| TC ID | Path | Assertion |
|-------|------|-----------|
| TC-W1-LEGAL-01 | legal walk | happy path satisfies AC |
| TC-W1-ILLEGAL-01 | illegal | fail-closed reason_code |
