# Beacon Implementation Plan

- plan_id: `plan-beacon-truth-map-center-and-package-cutover-r1`
- feature: `beacon-truth-map-center-and-package-cutover`
- version: `v1.5.2`
- revision_id: `R1`
- baseline_hash: `sha256:1d0b9715183aab32b8598743578e797f0902b044bfb93c82473a2d4418323823`
- delivery_baseline_id: `impl-delivery-baseline-v1.5.2-beacon-truth-map-center-and-package-cutover-R1`
- delivery_baseline_source_hash: `sha256:0e0609e2d0c483de7e9f1c4e48df63c97f22b000ae2b8e7f7bcb376d480962de`
- plan_hash: `sha256:3a589f283eba63095d05da348de8421300ae474a917fb51c71093218ce8db0e1`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.5.2/user-story/beacon-truth-map-center-and-package-cutover.md`
- prd: `docs/beacon/v1.5.2/prd/beacon-truth-map-center-and-package-cutover.md`
- test_case: `docs/beacon/v1.5.2/qa/test-cases/beacon-truth-map-center-and-package-cutover.md`
- ac_matrix: `docs/beacon/v1.5.2/.machine/qa/beacon-truth-map-center-and-package-cutover.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.5.2/.machine/qa/beacon-truth-map-center-and-package-cutover.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.5.2/.machine/qa/beacon-truth-map-center-and-package-cutover.qa9-matrix.json`
- research_projection: `docs/beacon/v1.5.2/.machine/user-story/beacon-truth-map-center-and-package-cutover.json`
- architecture_blueprint: `docs/beacon/v1.5.2/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-truth-map-center-and-package-cutover" --project-root . --version v1.5.2`
- run_command: `beacon implement team-run "beacon-truth-map-center-and-package-cutover" --project . --version v1.5.2`
- dev_run_command: `beacon implement dev-run "beacon-truth-map-center-and-package-cutover" --project . --version v1.5.2`
- qa_team_command: `beacon qa team-run "beacon-truth-map-center-and-package-cutover" --project . --version v1.5.2`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.5.2`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.5.2/.machine/execution/git-workflow-beacon-truth-map-center-and-package-cutover.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:docs/beacon/v1.5.2/research/beacon-truth-map-center-and-package-cutover.md`
- source_artifact: `docs/beacon/v1.5.2/.machine/user-story/beacon-truth-map-center-and-package-cutover.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 `features/<slug>/*.md` is authoritative for normal production and con...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-009, TC-010
- mapped_scenario_ids: SC-001, SC-002, SC-003
- mapped_qa_case_ids: TC-001, TC-009, TC-010
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 Commands and skills must call truth-map resolver before reading truth.
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002, TC-011, TC-012, TC-013
- mapped_scenario_ids: SC-004, SC-005, SC-006, SC-007
- mapped_qa_case_ids: TC-002, TC-011, TC-012, TC-013
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 Legacy triptych is not a canonical source in v1.5.2.
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003, TC-014, TC-015
- mapped_scenario_ids: SC-008, SC-009, SC-010
- mapped_qa_case_ids: TC-003, TC-014, TC-015
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 `doctor` can rebuild legacy triptych from package truth.
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004, TC-016
- mapped_scenario_ids: SC-011, SC-012
- mapped_qa_case_ids: TC-004, TC-016
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 `change` can absorb legacy triptych into package truth.
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-005, TC-017
- mapped_scenario_ids: SC-013, SC-014
- mapped_qa_case_ids: TC-005, TC-017
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 Missing JSON twins do not block Markdown truth validity.
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-006, TC-018, TC-019
- mapped_scenario_ids: SC-015, SC-016, SC-017
- mapped_qa_case_ids: TC-006, TC-018, TC-019
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 QA/release/gate use resolver and parser outputs from package truth.
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-007, TC-020, TC-021, TC-022, TC-023
- mapped_scenario_ids: SC-018, SC-019, SC-020, SC-021, SC-022
- mapped_qa_case_ids: TC-007, TC-020, TC-021, TC-022, TC-023
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — AC-008 Drift against package truth is reported; package truth remains author...
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TC-008, TC-024, TC-025
- mapped_scenario_ids: SC-023, SC-024, SC-025
- mapped_qa_case_ids: TC-008, TC-024, TC-025
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
