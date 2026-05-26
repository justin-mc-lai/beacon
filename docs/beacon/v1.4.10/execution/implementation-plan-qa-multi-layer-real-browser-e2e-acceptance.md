# Beacon Implementation Plan

- plan_id: `plan-qa-multi-layer-real-browser-e2e-acceptance-r2`
- feature: `qa-multi-layer-real-browser-e2e-acceptance`
- version: `v1.4.10`
- revision_id: `R2`
- baseline_hash: `sha256:70f6f4bd45284e4f98e07500b47a3d7070c6b36913bb16b2fd4a02b79229c81b`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.10-qa-multi-layer-real-browser-e2e-acceptance-R2`
- delivery_baseline_source_hash: `sha256:75f315e585f94de180d33950aa73f024dc990f3bf6ceaef125cd7f47b904dee6`
- plan_hash: `sha256:1348c5792acb7b84b793eb5ebbc459ddce54be4ea32d6ea421f45d7cc70c12a1`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.10/user-story/qa-multi-layer-real-browser-e2e-acceptance.md`
- prd: `docs/beacon/v1.4.10/prd/qa-multi-layer-real-browser-e2e-acceptance.md`
- test_case: `docs/beacon/v1.4.10/qa/test-cases/qa-multi-layer-real-browser-e2e-acceptance.md`
- revision_delta: `docs/beacon/v1.4.10/.machine/execution/revision-delta-qa-multi-layer-real-browser-e2e-acceptance.json`
- ac_matrix: `docs/beacon/v1.4.10/.machine/qa/qa-multi-layer-real-browser-e2e-acceptance.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.10/.machine/qa/qa-multi-layer-real-browser-e2e-acceptance.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.10/.machine/qa/qa-multi-layer-real-browser-e2e-acceptance.qa9-matrix.json`
- research_projection: `docs/beacon/v1.4.10/.machine/user-story/qa-multi-layer-real-browser-e2e-acceptance.json`
- architecture_blueprint: `docs/beacon/v1.4.10/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "qa-multi-layer-real-browser-e2e-acceptance" --project-root . --version v1.4.10`
- run_command: `beacon implement team-run "qa-multi-layer-real-browser-e2e-acceptance" --project . --version v1.4.10`
- dev_run_command: `beacon implement dev-run "qa-multi-layer-real-browser-e2e-acceptance" --project . --version v1.4.10`
- qa_team_command: `beacon qa team-run "qa-multi-layer-real-browser-e2e-acceptance" --project . --version v1.4.10`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.10`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.4.10/.machine/execution/git-workflow-qa-multi-layer-real-browser-e2e-acceptance.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:docs/beacon/v1.4.10/research/qa-multi-layer-real-browser-e2e-acceptance.md`
- source_artifact: `docs/beacon/v1.4.10/.machine/user-story/qa-multi-layer-real-browser-e2e-acceptance.json`
- section_count: `0`

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.4.10/.machine/execution/revision-delta-qa-multi-layer-real-browser-e2e-acceptance.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-010, TC-011, TC-012, TC-002
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, SC-008, SC-009, SC-010, SC-011, SC-012, SC-013, SC-014, SC-015, SC-017, SC-018, SC-019, SC-020, SC-021, SC-022, SC-023, SC-024, SC-026, SC-027
- mapped_qa_case_ids: TC-001, TC-002, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-003, AC-004, AC-006, AC-009, AC-011, AC-012
- mapped_test_ids: TC-003, TEST-004, TEST-006, TEST-009, TEST-011, TEST-012, TC-006, TC-009
- mapped_scenario_ids: SC-007, SC-008, SC-009, SC-016, SC-017, SC-018, SC-025, SC-026, SC-027
- mapped_qa_case_ids: TC-003, TC-006, TC-009
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-007, AC-005, AC-008, AC-010
- mapped_test_ids: TEST-007, TEST-005, TEST-008, TEST-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
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

### ITASK-012 — FR-012 AC-012
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
