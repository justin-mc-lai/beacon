# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write-r2`
- feature: `Beacon v1.3.9 execution projection convergence and QA acceptance dual-write`
- version: `v1.3.9`
- revision_id: `R2`
- baseline_hash: `sha256:da0b4e5fdd2fe575ff8cba7c68d037f006f57fa168bda7f1d30ed7c8c9dd91c3`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.9-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write-R2`
- delivery_baseline_source_hash: `sha256:8c87a12c3593af8c46faf7b940daaf5327a21a31001b1cf102396f04dcb01116`
- plan_hash: `sha256:e68b83e73cda87a5ccefd9e5097478a9123684a70b6cab50505df1453fa00683`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.9/user-story/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- prd: `docs/beacon/archive/v1.3.9/prd/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- test_case: `docs/beacon/archive/v1.3.9/qa/test-cases/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- revision_delta: `docs/beacon/archive/v1.3.9/.machine/execution/revision-delta-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.json`
- ac_matrix: `docs/beacon/archive/v1.3.9/.machine/qa/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.3.9/.machine/qa/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.3.9/.machine/qa/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/archive/v1.3.9/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write" --project-root . --version v1.3.9`
- run_command: `beacon implement team-run "beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write" --project . --version v1.3.9`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write" --project . --version v1.3.9`
- qa_team_command: `beacon qa team-run "beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write" --project . --version v1.3.9`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.9`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.3.9/.machine/execution/git-workflow-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.3.9/.machine/execution/revision-delta-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-009
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006
- mapped_qa_case_ids: TC-001, TC-009
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-002, AC-003
- mapped_test_ids: TC-002, TC-003, TC-010, TC-011
- mapped_scenario_ids: SC-007, SC-008, SC-009, SC-010
- mapped_qa_case_ids: TC-002, TC-003, TC-010, TC-011
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-010, AC-005, AC-004, AC-008, AC-007
- mapped_test_ids: TEST-010, TC-005, TC-004, TC-008, TC-007, TC-012, TC-013, TC-015, TC-016
- mapped_scenario_ids: SC-011, SC-012, SC-013, SC-014, SC-015, SC-016, SC-017, SC-018, SC-019, SC-020, SC-021, SC-022, SC-025, SC-026, SC-027, SC-028, SC-029, SC-030, SC-031, SC-032
- mapped_qa_case_ids: TC-004, TC-005, TC-007, TC-008, TC-012, TC-013, TC-015, TC-016
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-006, AC-011
- mapped_test_ids: TC-006, TEST-011, TC-014
- mapped_scenario_ids: SC-023, SC-024
- mapped_qa_case_ids: TC-006, TC-014
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TC-009
- mapped_scenario_ids: SC-015
- mapped_qa_case_ids: TC-009
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 AC-006
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — FR-007 AC-007
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — FR-008 AC-008
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — FR-009 AC-009
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — FR-010 AC-010
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — FR-011 AC-011
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
