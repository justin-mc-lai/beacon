# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation-r1`
- feature: `beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation`
- version: `v1.3.11`
- revision_id: `R1`
- baseline_hash: `sha256:9dcfcdb939173649da64eb6f08a6a521d561c04dd33e6ef5cbd0cae4e7c7a476`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.11-beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation-R1`
- delivery_baseline_source_hash: `sha256:f49e85f06cd897749e84088083b6c272a721e65a6674196c92303d31083149a1`
- plan_hash: `sha256:b8d42db96614c1a259d8c3278135db0d0272c9a787a83ff1aa9b0e955823d394`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.11/user-story/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- prd: `docs/beacon/archive/v1.3.11/prd/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- test_case: `docs/beacon/archive/v1.3.11/qa/test-cases/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- ac_matrix: `docs/beacon/archive/v1.3.11/.machine/qa/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.3.11/.machine/qa/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.3.11/.machine/qa/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/archive/v1.3.11/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation" --project-root . --version v1.3.11`
- run_command: `beacon implement team-run "beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation" --project . --version v1.3.11`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation" --project . --version v1.3.11`
- qa_team_command: `beacon qa team-run "beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation" --project . --version v1.3.11`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.11`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.3.11/.machine/execution/git-workflow-beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Tasks

### ITASK-001 — FR-001 PRD markdown 必须支持重投影
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-002, TC-022, TC-023
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004
- mapped_qa_case_ids: TC-001, TC-002, TC-022, TC-023
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 audit 必须覆盖 full mirror
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-021
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-021
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 transaction 必须支持 latest / supersedes
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 stale mirror 必须 fail-closed
- status: `completed`
- mapped_ac_ids: AC-015
- mapped_test_ids: TEST-015
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 doctor fallback 必须可恢复
- status: `completed`
- mapped_ac_ids: AC-003, AC-004, AC-006, AC-007, AC-008, AC-010, AC-011, AC-012, AC-013, AC-014, AC-016, AC-017, AC-018, AC-019, AC-020, AC-021
- mapped_test_ids: TC-003, TC-004, TEST-006, TEST-007, TEST-008, TEST-010, TEST-011, TEST-012, TEST-013, TEST-014, TEST-016, TEST-017, TEST-018, TEST-019, TEST-020, TEST-021, TC-024, TC-025
- mapped_scenario_ids: SC-005, SC-006, SC-007, SC-008
- mapped_qa_case_ids: TC-003, TC-004, TC-024, TC-025
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
