# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor-r1`
- feature: `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`
- version: `v1.3.6`
- revision_id: `R1`
- baseline_hash: `sha256:5c8320b05e30a5798461b7060821b178c067fe99cf6286a8f0f581fe0c16e24d`
- plan_hash: `sha256:e23b89cd312c9e1855cc12a1367e6a2a2b65d9bbd73a78916bd749851886717f`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.6/user-story/beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.md`
- prd: `docs/beacon/v1.3.6/prd/beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.md`
- test_case: `docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.md`
- story_scenario_map: `docs/beacon/v1.3.6/.machine/qa/beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.6/.machine/qa/beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.qa9-matrix.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor" --project-root . --version v1.3.6`
- run_command: `beacon implement team-run "beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor" --project . --version v1.3.6`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor" --project . --version v1.3.6`
- qa_team_command: `beacon qa team-run "beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor" --project . --version v1.3.6`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.6`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.6/.machine/execution/git-workflow-beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.json`

## Tasks

### ITASK-001 — FR-001 Unify requirement commands on one host-native semantic runtime contract.
- status: `completed`
- mapped_ac_ids: AC-001, AC-003
- mapped_test_ids: TEST-001, TEST-003, TC-001, TC-003
- mapped_scenario_ids: SC-001, SC-003, SC-004, SC-005, SC-006, SC-007
- mapped_qa_case_ids: TC-001, TC-003
- depends_on: -
- target_modules: -

### ITASK-002 — FR-002 Unify `implement / qa / release` on one delivery kernel and traceability plane.
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-002
- depends_on: ITASK-001
- target_modules: -

### ITASK-003 — FR-003 Keep `help / status / doctor` on the same read-model truth as delivery and release.
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-006
- mapped_scenario_ids: SC-018
- mapped_qa_case_ids: TC-006
- depends_on: ITASK-002
- target_modules: -

### ITASK-004 — FR-004 Preserve the public `7+3` command surface while demoting provider-backed execution to fallback.
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004
- mapped_scenario_ids: SC-008, SC-009, SC-010, SC-011, SC-012
- mapped_qa_case_ids: TC-004
- depends_on: ITASK-003
- target_modules: -

### ITASK-005 — FR-005 Promote `v1.3.6` as the current runtime/package/docs line with coherent release evidence.
- status: `completed`
- mapped_ac_ids: AC-005, AC-007
- mapped_test_ids: TEST-005, TEST-007, TC-005, TC-007
- mapped_scenario_ids: SC-013, SC-014, SC-015, SC-016, SC-017, SC-019
- mapped_qa_case_ids: TC-005, TC-007
- depends_on: ITASK-004
- target_modules: -
