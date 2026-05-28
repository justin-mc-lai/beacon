# Beacon Implementation Plan

- plan_id: `plan-design-project-truth-initialization-contract-r4`
- feature: `design-project-truth-initialization-contract`
- version: `v1.4.11`
- revision_id: `R4`
- baseline_hash: `sha256:4a4e149fb3c15700e4c3c4e09e64d9993c2b49d4a63b19aaad338f4551b9d08a`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.11-design-project-truth-initialization-contract-R4`
- delivery_baseline_source_hash: `sha256:016cb1e94501df5980ba27f47aafa326c7a6a07f39b54d004c6d83560f128aa2`
- plan_hash: `sha256:dd94f9aec4577230c2edb914f07f1e5417d4fbd4cbb3949acae98f9f95471e0e`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.11/user-story/design-project-truth-initialization-contract.md`
- prd: `docs/beacon/v1.4.11/prd/design-project-truth-initialization-contract.md`
- test_case: `docs/beacon/v1.4.11/qa/test-cases/design-project-truth-initialization-contract.md`
- revision_delta: `docs/beacon/v1.4.11/.machine/execution/revision-delta-design-project-truth-initialization-contract.json`
- ac_matrix: `docs/beacon/v1.4.11/.machine/qa/design-project-truth-initialization-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.11/.machine/qa/design-project-truth-initialization-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.11/.machine/qa/design-project-truth-initialization-contract.qa9-matrix.json`
- research_projection: `docs/beacon/v1.4.11/.machine/user-story/design-project-truth-initialization-contract.json`
- architecture_blueprint: `docs/beacon/v1.4.11/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "design-project-truth-initialization-contract" --project-root . --version v1.4.11`
- run_command: `beacon implement team-run "design-project-truth-initialization-contract" --project . --version v1.4.11`
- dev_run_command: `beacon implement dev-run "design-project-truth-initialization-contract" --project . --version v1.4.11`
- qa_team_command: `beacon qa team-run "design-project-truth-initialization-contract" --project . --version v1.4.11`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `main`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.4.11/.machine/execution/git-workflow-design-project-truth-initialization-contract.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:docs/beacon/v1.4.11/research/design-project-truth-initialization-contract.md`
- source_artifact: `docs/beacon/v1.4.11/.machine/user-story/design-project-truth-initialization-contract.json`
- section_count: `0`

## Revision Delta
- revision_id: `R4`
- source_revision_id: `R3`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.4.11/.machine/execution/revision-delta-design-project-truth-initialization-contract.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-DESIGN-TRUTH-001, TC-DESIGN-TRUTH-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-DESIGN-TRUTH-001, TC-DESIGN-TRUTH-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-DESIGN-TRUTH-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-DESIGN-TRUTH-003
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 AC-002, AC-003
- status: `completed`
- mapped_ac_ids: AC-007, AC-004, AC-008
- mapped_test_ids: TC-DESIGN-TRUTH-007, TC-DESIGN-TRUTH-004, TC-DESIGN-TRUTH-008
- mapped_scenario_ids: SC-004, SC-007, SC-008
- mapped_qa_case_ids: TC-DESIGN-TRUTH-004, TC-DESIGN-TRUTH-007, TC-DESIGN-TRUTH-008
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-DESIGN-TRUTH-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-DESIGN-TRUTH-005
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: AC-009, AC-010
- mapped_test_ids: TC-DESIGN-TRUTH-009, TC-DESIGN-TRUTH-010
- mapped_scenario_ids: SC-009, SC-010
- mapped_qa_case_ids: TC-DESIGN-TRUTH-009, TC-DESIGN-TRUTH-010
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 AC-006
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-DESIGN-TRUTH-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-DESIGN-TRUTH-006
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
