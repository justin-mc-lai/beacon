---
slug: beacon-loop-goal-v166
version: v1.6.6
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.6/features/beacon-loop-goal-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tasks: Loop Goal Orchestrator v1.6.6

## Task List

- [x] TASK-001 truth → `beacon-gen-truth` — freeze truth.md + tests.md + tasks.md + evidence.md
- [x] TASK-002 implement → `beacon-gen-implement` — create `beacon/utils/loop_goal_state.py` with init, transition, read_state, check_stop_when
- [x] TASK-003 implement → `beacon-gen-implement` — create `.agents/skills/beacon-loop-goal/SKILL.md` with full decision tree + state machine + skill routing matrix
- [-] TASK-004 implement → `beacon-gen-implement` — integrate `loop-goal` status view into `beacon/commands/status.py` (deferred)
- [x] TASK-005 implement → `beacon-gen-implement` — create `tests/test_v166_loop_goal.py` with 10 test cases
- [x] TASK-006 qa → `beacon-eval-qa` — 10/10 tests pass, 10/10 AC verified, SKILL.md stable
- [ ] TASK-007 release → `beacon-eval-release` — update SUMMARY.md delivery status, release note
