---
slug: beacon-loop-goal-v166
version: v1.6.6
status: draft
revision_id: R5
language: zh
truth_ref: docs/beacon/v1.6.6/features/beacon-loop-goal-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tasks: Loop Goal Orchestrator v1.6.6

## Task List

- [x] TASK-001 truth → `beacon-gen-truth` — freeze truth.md + tests.md + tasks.md + evidence.md
- [x] TASK-002 implement → `beacon-gen-implement` — create `beacon/utils/loop_goal_state.py` with init, transition, read_state, check_stop_when
- [x] TASK-003 implement → `beacon-gen-implement` — create `.agents/skills/beacon-loop-goal/SKILL.md` with full decision tree + state machine + skill routing matrix
- [x] TASK-003A change → `beacon-gen-change` — freeze `beacon-loop-goal` as public host-visible governor skill; update taxonomy, agent surface expected list, inventory/counts, and release governance coverage
- [x] TASK-003B implement → `beacon-gen-implement` — implement R2 public skill release shape in packaged skill source, agent surface taxonomy, agent eval inventory, fixtures, and regression tests
- [-] TASK-004 implement → `beacon-gen-implement` — integrate `loop-goal` status view into `beacon/commands/status.py` (deferred)
- [x] TASK-005 implement → `beacon-gen-implement` — create `tests/test_v166_loop_goal.py` with 10 test cases
- [x] TASK-006 qa → `beacon-eval-qa` — R2 QA passed for AC-001..011 with run `run-20260715T135541350657`
- [-] TASK-007 release → `beacon-eval-release` — release evaluator owns final verdict after acceptance/read-model projection is complete
- [x] TASK-008 change → `beacon-gen-change` — R3 refreeze `review_routing` as public loop-goal decision contract (AC-012..014)
- [x] TASK-009 implement → `beacon-gen-implement` — add `review_routing` to public SKILL.md state machine, decision tree, and routing matrix
- [x] TASK-010 implement → `beacon-gen-implement` — add loop-goal review decision packet output recording in `loop_goal_state.py`
- [x] TASK-011 implement → `beacon-gen-implement` — add pytest coverage for AC-012..014
- [x] TASK-012 change → `beacon-gen-change` — R4 refreeze Standard Execution Flow admission contract into package truth/tests/tasks/evidence (AC-015..021)
- [ ] TASK-013 implement → `beacon-gen-implement` — add `standard_execution_precheck` to public and packaged `beacon-loop-goal` SKILL.md state machine, decision tree, and routing matrix
- [ ] TASK-014 implement → `beacon-gen-implement` — extend `loop_goal_state.py` with standard execution flow outputs: baseline commit, quarantine ref, verification bundle ref, workspace admission ref
- [ ] TASK-015 implement → `beacon-gen-implement` — implement deterministic precheck helpers for canonical refreeze committed, stale feature-local refreeze quarantine, truth baseline merged, verification bundle completeness, workspace admission pass, and idempotent resume
- [ ] TASK-016 implement → `beacon-gen-implement` — add pytest coverage for TC-LG-015..021
- [ ] TASK-017 qa → `beacon-eval-qa` — run behavioral QA for AC-015..021 after implementation; formal verdict remains evaluator-owned

- [x] TASK-018 change → `beacon-gen-change` — R5 reopen + draft truth-on-main first-principles closure (AC-022..026)
- [ ] TASK-019 implement → `beacon-gen-implement` — complete truth package file write gate: on truth_canonical allow writes without forcing feature worktree; off-canonical deny
- [ ] TASK-020 implement → `beacon-gen-implement` — add CLI command to run standard_execution_precheck verification bundle and write artifact; wire `record_standard_execution_precheck` to require CLI artifact ref
- [ ] TASK-021 implement → `beacon-gen-implement` — ensure truth authoring skill injection stays dual-track; regression tests TC-LG-022..026
- [ ] TASK-022 qa → `beacon-eval-qa` — behavioral QA for AC-022..026 after implementation; formal verdict remains evaluator-owned
