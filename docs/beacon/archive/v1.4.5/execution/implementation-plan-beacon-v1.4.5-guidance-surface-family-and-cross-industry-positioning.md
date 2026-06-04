# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning-r3`
- feature: `beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning`
- version: `v1.4.5`
- revision_id: `R3`
- baseline_hash: `sha256:ceca681d5f40834c26ba68f7db28a0888641faae504332b7fa3b3b2e8a8a415e`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.5-beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning-R3`
- delivery_baseline_source_hash: `sha256:b696025b56db67837853f4afbe023b25bb66b95a4227c4c68047f17481f64168`
- plan_hash: `sha256:e248c9a43087c3145a46c0e6537b4a5952ee684bfe511474a6359db7e9babcb9`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.5/user-story/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.md`
- prd: `docs/beacon/archive/v1.4.5/prd/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.md`
- test_case: `docs/beacon/archive/v1.4.5/qa/test-cases/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.md`
- revision_delta: `docs/beacon/archive/v1.4.5/.machine/execution/revision-delta-beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.json`
- ac_matrix: `docs/beacon/archive/v1.4.5/.machine/qa/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.5/.machine/qa/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.5/.machine/qa/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/archive/v1.4.5/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning" --project-root . --version v1.4.5`
- run_command: `beacon implement team-run "beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning" --project . --version v1.4.5`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning" --project . --version v1.4.5`
- qa_team_command: `beacon qa team-run "beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning" --project . --version v1.4.5`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.5`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.4.5/.machine/execution/git-workflow-beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.5/.machine/execution/revision-delta-beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.json`

## Tasks

### ITASK-001 — FR-001 Beacon 必须冻结 guidance surface family
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-GUIDE45-001, TC-GUIDE45-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-GUIDE45-001, TC-GUIDE45-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 Beacon 必须冻结 guidance surface family 的统一边界
- status: `completed`
- mapped_ac_ids: AC-006, AC-005, AC-007
- mapped_test_ids: TC-GUIDE45-006, TC-GUIDE45-005, TC-GUIDE45-007
- mapped_scenario_ids: SC-005, SC-006, SC-007
- mapped_qa_case_ids: TC-GUIDE45-005, TC-GUIDE45-006, TC-GUIDE45-007
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 Beacon 必须表达通用闭环
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-GUIDE45-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-GUIDE45-003
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 软件开发生命周期必须被定义为 domain materialization
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-GUIDE45-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-GUIDE45-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 Beacon 必须允许非软件行业场景使用 guidance surface
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TC-GUIDE45-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: TC-GUIDE45-008
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 guidance surface 的 route explainability 必须统一
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

### ITASK-007 — FR-007 Beacon 必须冻结 guidance-oriented skill philosophy
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

### ITASK-008 — FR-008 support-surface requirement 默认不得被自动抬升为 browser QA
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
