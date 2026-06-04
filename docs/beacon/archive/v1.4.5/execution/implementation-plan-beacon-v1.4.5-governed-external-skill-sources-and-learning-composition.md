# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.5-governed-external-skill-sources-and-learning-composition-r1`
- feature: `beacon-v1.4.5-governed-external-skill-sources-and-learning-composition`
- version: `v1.4.5`
- revision_id: `R1`
- baseline_hash: `sha256:e701b31a6c36fe9feb98ff47a502fbbd8353c45ba422121a4fac59f76f46aed4`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.5-beacon-v1.4.5-governed-external-skill-sources-and-learning-composition-R1`
- delivery_baseline_source_hash: `sha256:6c5927c6db911904c6a66fb43c2aa110ccee615d083d5613c8944a17252b0ba6`
- plan_hash: `sha256:aa9271bf538fa4853a5d6c90a366ecf1f61b309f8e0ae6af281774235f8e7bd6`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.5/user-story/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`
- prd: `docs/beacon/archive/v1.4.5/prd/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`
- test_case: `docs/beacon/archive/v1.4.5/qa/test-cases/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`
- ac_matrix: `docs/beacon/archive/v1.4.5/.machine/qa/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.5/.machine/qa/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.5/.machine/qa/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.qa9-matrix.json`
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
- plan_command: `beacon implement team-plan "beacon-v1.4.5-governed-external-skill-sources-and-learning-composition" --project-root . --version v1.4.5`
- run_command: `beacon implement team-run "beacon-v1.4.5-governed-external-skill-sources-and-learning-composition" --project . --version v1.4.5`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.5-governed-external-skill-sources-and-learning-composition" --project . --version v1.4.5`
- qa_team_command: `beacon qa team-run "beacon-v1.4.5-governed-external-skill-sources-and-learning-composition" --project . --version v1.4.5`
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
- git_workflow_ref: `docs/beacon/archive/v1.4.5/.machine/execution/git-workflow-beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Tasks

### ITASK-001 — FR-001 Beacon 必须允许外部 skill source 成为一等 capability source
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 Beacon 必须支持 canonical external sample source
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 用户必须可以只声明业务目标与目标结果
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-003
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 Beacon 必须能做 capability selection 与 composition
- status: `completed`
- mapped_ac_ids: AC-006, AC-004
- mapped_test_ids: TC-006, TC-004
- mapped_scenario_ids: SC-004, SC-006
- mapped_qa_case_ids: TC-004, TC-006
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 Beacon 必须记录 success/failure/adoption learning
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-005
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 learning 必须形成可回用 mapping
- status: `completed`
- mapped_ac_ids: AC-007, AC-008
- mapped_test_ids: TC-007, TC-008
- mapped_scenario_ids: SC-007, SC-008
- mapped_qa_case_ids: TC-007, TC-008
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — FR-007 外部 source 治理必须保持边界清楚
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

### ITASK-008 — FR-008 Beacon 必须支持对外部 skill 做 philosophy-first admission
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
