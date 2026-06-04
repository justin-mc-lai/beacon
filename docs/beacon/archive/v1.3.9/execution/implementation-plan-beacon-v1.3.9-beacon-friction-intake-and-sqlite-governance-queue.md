# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue-r1`
- feature: `Beacon v1.3.9 beacon-friction-intake and sqlite governance queue`
- version: `v1.3.9`
- revision_id: `R1`
- baseline_hash: `sha256:dd1553cd9253fc8d1504178d1cfdb909bac2b45d15dcab8122b97e7d50c7b123`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.9-beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue-R1`
- delivery_baseline_source_hash: `sha256:4cf70da3f0d380875d31ce7bdf7b55f6733d27f2dea5c4f295cb41d037fe5854`
- plan_hash: `sha256:7f3907541d6d06172daf5f7bec2f9f0d71f8ca0aabb1e71d27059017e7563f05`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.9/user-story/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`
- prd: `docs/beacon/archive/v1.3.9/prd/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`
- test_case: `docs/beacon/archive/v1.3.9/qa/test-cases/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`
- ac_matrix: `docs/beacon/archive/v1.3.9/.machine/qa/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.3.9/.machine/qa/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.story-scenario-map.json`
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
- plan_command: `beacon implement team-plan "Beacon v1.3.9 beacon-friction-intake and sqlite governance queue" --project-root . --version v1.3.9`
- run_command: `beacon implement team-run "Beacon v1.3.9 beacon-friction-intake and sqlite governance queue" --project . --version v1.3.9`
- dev_run_command: `beacon implement dev-run "Beacon v1.3.9 beacon-friction-intake and sqlite governance queue" --project . --version v1.3.9`
- qa_team_command: `beacon qa team-run "Beacon v1.3.9 beacon-friction-intake and sqlite governance queue" --project . --version v1.3.9`
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
- git_workflow_ref: `docs/beacon/archive/v1.3.9/.machine/execution/git-workflow-beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: state-machine
- state_axes: -
- review_gates: implementation must preserve the declared state-machine transitions
- qa_coverage_hints: cover state transitions, illegal transitions, and recovery paths

## Tasks

### ITASK-001 — FR-001 `beacon-friction-intake` 必须是统一摩擦录入入口
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must preserve the declared state-machine transitions

### ITASK-002 — FR-002 必须支持 `scan` 与 `capture` 双模式
- status: `completed`
- mapped_ac_ids: AC-101
- mapped_test_ids: TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must preserve the declared state-machine transitions

### ITASK-003 — FR-003 双模式都必须进入全局 sqlite 队列治理
- status: `completed`
- mapped_ac_ids: AC-301
- mapped_test_ids: TC-010, TC-011
- mapped_scenario_ids: SC-010, SC-011
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must preserve the declared state-machine transitions

### ITASK-004 — FR-004 分类模型必须可被 Beacon 产品治理直接消费
- status: `completed`
- mapped_ac_ids: AC-402
- mapped_test_ids: TC-017, TC-014
- mapped_scenario_ids: SC-014, SC-017
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must preserve the declared state-machine transitions

### ITASK-005 — FR-005 `debug_issues` 不得直接替代 friction queue
- status: `completed`
- mapped_ac_ids: AC-302, AC-403, AC-501
- mapped_test_ids: TC-012, TC-013, TC-018, TC-019, TC-011, TC-015, TC-016
- mapped_scenario_ids: SC-011, SC-012, SC-013, SC-015, SC-016, SC-018, SC-019
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must preserve the declared state-machine transitions

### ITASK-006 — FR-006 requirement/change 路由必须显式接受
- status: `completed`
- mapped_ac_ids: AC-003, AC-102, AC-103, AC-201, AC-202, AC-203, AC-303, AC-401, AC-502, AC-503, AC-601, AC-602, AC-603
- mapped_test_ids: TC-003, TC-005, TC-006, TC-007, TC-008, TC-009, TC-014, TC-015, TC-016, TC-020, TC-021, TC-022, TC-023, TC-024, TC-012, TC-013, TC-017, TC-018, TC-019
- mapped_scenario_ids: SC-003, SC-005, SC-006, SC-007, SC-008, SC-009, SC-012, SC-013, SC-014, SC-015, SC-016, SC-017, SC-018, SC-019, SC-020, SC-021
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must preserve the declared state-machine transitions
