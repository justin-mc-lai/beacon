---
slug: beacon-worktree-progressive-skill-flow-v168
version: v1.6.8
status: draft
revision_id: R1
---

# Evidence Index: beacon-worktree-progressive-skill-flow-v168

| Surface | Authority | Canonical Artifact | Status |
|---------|-----------|--------------------|--------|
| requirement_truth | requirement_truth | docs/beacon/archive/v1.6.8/features/beacon-worktree-progressive-skill-flow-v168/truth.md | draft |
| acceptance | acceptance_truth | docs/beacon/archive/v1.6.8/features/beacon-worktree-progressive-skill-flow-v168/truth.md | draft |
| test_case | test_truth | docs/beacon/archive/v1.6.8/features/beacon-worktree-progressive-skill-flow-v168/tests.md | draft |
| planner | support_advisory | pln-review chat 2026-07-19 worktree progressive skill | accepted |
| change | support_advisory | docs/beacon/archive/v1.6.8/change/beacon-worktree-progressive-skill-flow-v168.md | indexed |
| shared_ref | support_advisory | skills/beacon/references/git-worktree-execution-flow.md | authored |
| example | support_advisory | skills/beacon/examples/git-worktree-process-correct-30s.md | authored |

## Boundary

Index only — implement/QA behavioral evidence recorded after freeze and code landing.

## Implement evidence (2026-07-19T13:20:32Z)

- Shared ref: `skills/beacon/references/git-worktree-execution-flow.md`
- Example: `skills/beacon/examples/git-worktree-process-correct-30s.md`
- Progressive: `beacon/utils/product_goal_runtime.py` (`progressive_worktree_refs`, stage plan refs)
- Rust: `packages/beacon-rs/beacon-orchestrator/src/skill_load.rs` (worktree_flow_refs)
- Goal/implement/loop/change/truth/refreeze SKILL pointers updated
- Tests: `python3 -m pytest tests/test_worktree_progressive_skill_flow.py` → 5 passed
- Cargo: `cargo test -p beacon-orchestrator --lib worktree` → skill_load worktree tests ok
- Non-claim: does not default-switch beacon; does not auto-create satellite pool
