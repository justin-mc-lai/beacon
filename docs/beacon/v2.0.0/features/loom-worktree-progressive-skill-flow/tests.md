---
slug: loom-worktree-progressive-skill-flow
version: v2.0.0
status: draft
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-worktree-progressive-skill-flow/truth.md
---

# Tests

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-WT-SKILL-001 | TC-WT-001 | contract | path exists | flow md present |
| AC-WT-SKILL-002 | TC-WT-002 | contract | path exists | example present |
| AC-WT-SKILL-003 | TC-WT-003 | contract | grep beacon-goal | references flow |
| AC-WT-SKILL-004 | TC-WT-004 | unit | pytest progressive | ref in plan |
| AC-WT-SKILL-005 | TC-WT-005 | unit | cargo skill_load | ref in plan |
| AC-WT-SKILL-006 | TC-WT-006 | unit | progressive | bulk forbidden |
| AC-WT-SKILL-007 | TC-WT-007 | integration | pytest test_worktree_skill_flow | all pass |

## Legal / Illegal

| TC | Path | Assertion |
|----|------|-----------|
| LEGAL-01 | progressive implement | includes worktree ref |
| ILLEGAL-01 | missing shared ref file | fail test |
