# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope-r1`
- feature: `Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope`
- version: `v1.3.7`
- revision_id: `R1`
- baseline_hash: `sha256:5e4ae6019a8b41d3c7c1db525f09d293642769bd03e3486da1e5f6dcf0c8b27f`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.7-beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope-R1`
- delivery_baseline_source_hash: `sha256:adb4b25e4ba203dea68954a5161268cc8c5d45ff9b5a2dd65b751b3c32acabfe`
- plan_hash: `sha256:9b927098c5065d4f3191972d37e785fcbab08b43b77522b52912c62fdd4cb984`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.7/user-story/beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope.md`
- prd: `docs/beacon/archive/v1.3.7/prd/beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope.md`
- test_case: `docs/beacon/archive/v1.3.7/qa/test-cases/beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope.md`
- ac_matrix: `docs/beacon/archive/v1.3.7/.machine/qa/beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.3.7/.machine/qa/beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.3.7/.machine/qa/beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope.qa9-matrix.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope" --project-root . --version v1.3.7`
- run_command: `beacon implement team-run "Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope" --project . --version v1.3.7`
- dev_run_command: `beacon implement dev-run "Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope" --project . --version v1.3.7`
- qa_team_command: `beacon qa team-run "Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope" --project . --version v1.3.7`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.7`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.3.7/.machine/execution/git-workflow-beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-006, TC-011
- mapped_scenario_ids: SC-001, SC-002, SC-003
- mapped_qa_case_ids: TC-001, TC-006, TC-011
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-002, AC-003
- mapped_test_ids: TC-002, TC-003, TC-007, TC-012, TC-008, TC-013
- mapped_scenario_ids: SC-004, SC-005, SC-006, SC-007, SC-008, SC-009, SC-010, SC-011, SC-012, SC-013, SC-014, SC-015, SC-016, SC-017, SC-018, SC-019, SC-020, SC-021
- mapped_qa_case_ids: TC-002, TC-003, TC-007, TC-008, TC-012, TC-013
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-004, AC-005
- mapped_test_ids: TC-004, TC-005, TC-009, TC-010
- mapped_scenario_ids: SC-022, SC-023, SC-024, SC-025, SC-026, SC-027, SC-028, SC-029, SC-030, SC-031, SC-032, SC-033
- mapped_qa_case_ids: TC-004, TC-005, TC-009, TC-010
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -
