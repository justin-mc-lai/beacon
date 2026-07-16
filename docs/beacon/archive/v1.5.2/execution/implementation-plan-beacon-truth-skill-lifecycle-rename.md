# Beacon Implementation Plan

- plan_id: `plan-beacon-truth-skill-lifecycle-rename-r3`
- feature: `beacon-truth-skill-lifecycle-rename`
- version: `v1.5.2`
- revision_id: `R3`
- baseline_hash: `sha256:c6887853b9d3cf8f27238b9ea5b1a4c1c7637c50fc6b850c5a26f032c5f4bfb4`
- delivery_baseline_id: `impl-delivery-baseline-v1.5.2-beacon-truth-skill-lifecycle-rename-R3`
- delivery_baseline_source_hash: `sha256:baea00c080fda17f6104b7fc1d8d049e2aede594a78a7d42d879abddd4c6c785`
- plan_hash: `sha256:717632179484a2dd63857385b23899676f49d7df1a350bd7a47e8b2e1cd60ceb`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/truth.md`
- prd: `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/truth.md`
- test_case: `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/tests.md`
- truth: `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/truth.md`
- tests: `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/tests.md`
- tasks: `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/tasks.md`
- evidence: `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename`
- revision_delta: `docs/beacon/archive/v1.5.2/.machine/execution/revision-delta-beacon-truth-skill-lifecycle-rename.json`
- story_scenario_map: `docs/beacon/archive/v1.5.2/.machine/qa/beacon-truth-skill-lifecycle-rename.story-scenario-map.json`
- research_projection: `docs/beacon/archive/v1.5.2/.machine/user-story/beacon-truth-skill-lifecycle-rename.json`
- architecture_blueprint: `docs/beacon/archive/v1.5.2/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-truth-skill-lifecycle-rename" --project-root . --version v1.5.2`
- run_command: `beacon implement team-run "beacon-truth-skill-lifecycle-rename" --project . --version v1.5.2`
- dev_run_command: `beacon implement dev-run "beacon-truth-skill-lifecycle-rename" --project . --version v1.5.2`
- qa_team_command: `beacon qa team-run "beacon-truth-skill-lifecycle-rename" --project . --version v1.5.2`
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
- git_workflow_ref: `docs/beacon/archive/v1.5.2/.machine/execution/git-workflow-beacon-truth-skill-lifecycle-rename.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.5.2/research/beacon-truth-skill-lifecycle-rename.md`
- source_artifact: `docs/beacon/archive/v1.5.2/.machine/user-story/beacon-truth-skill-lifecycle-rename.json`
- section_count: `0`

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.5.2/.machine/execution/revision-delta-beacon-truth-skill-lifecycle-rename.json`

## Tasks

### ITASK-001 — AC-001 Beacon exposes `beacon-truth` as the preferred v1.5.2+ human-facing t...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 `beacon-truth` must preserve distinct modes for definition, acceptanc...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 Every `beacon-truth` mode must resolve feature truth through `beacon...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 Existing `beacon-prd`, `beacon-user-story`, and `beacon-test-case` sk...
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 Root Beacon and brainstorm guidance must describe the preferred truth...
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 `beacon-truth` must not turn brainstorm, change-refreeze, QA, or rele...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 Coverage truth remains in `features/<slug>/tests.md`; `truth.md` owns...
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — AC-008 The new lifecycle language must preserve the closure route from suppo...
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008, TC-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
