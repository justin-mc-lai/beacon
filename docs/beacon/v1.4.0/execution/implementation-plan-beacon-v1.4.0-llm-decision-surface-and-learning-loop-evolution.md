# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution-r1`
- feature: `beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution`
- version: `v1.4.0`
- revision_id: `R1`
- baseline_hash: `sha256:8a5a26ddd92a21386c2a13a23aeb358b86309df25edea37d1cebaf8b7726006a`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.0-beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution-R1`
- delivery_baseline_source_hash: `sha256:646712fcd23903612d7f4c1391c2e7d505d611ff39a91a5ab9161dda235b7293`
- plan_hash: `sha256:c1f5cef40f9c483776fd69cbe50bccc839b87be40e8761cdc8e05f6a91985f18`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- prd: `docs/beacon/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- test_case: `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- ac_matrix: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/v1.4.0/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.4.0`
- run_command: `beacon implement team-run "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.0`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.0`
- qa_team_command: `beacon qa team-run "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.0`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.0`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.4.0/.machine/execution/git-workflow-beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

## Tasks

### ITASK-001 — FR-001 核心 skill 必须升级为正式 decision surface
- status: `completed`
- mapped_ac_ids: AC-002, AC-001
- mapped_test_ids: TC-002, TC-001, TC-057, TC-058, TC-059, TC-060, TC-061, TC-062, TC-063, TC-064, TC-065
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-001, TC-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-002 — FR-002 Inputs Contract 必须最小但可机器消费
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-003
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-003 — FR-003 Decision Protocol 必须承载主要判断逻辑
- status: `completed`
- mapped_ac_ids: AC-004, AC-050
- mapped_test_ids: TC-004, TEST-050
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-004
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-004 — FR-004 Anti-Inertia Notes 必须显式纠正常见误锚
- status: `completed`
- mapped_ac_ids: AC-007, AC-008, AC-011, AC-015
- mapped_test_ids: TEST-007, TEST-008, TEST-011, TEST-015
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-005 — FR-005 Learning Notes 必须复用现有 learning plane kernel
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-006 — FR-006 `beacon ask` 必须被冻结为正式的自然语言路由入口
- status: `completed`
- mapped_ac_ids: AC-006, AC-005
- mapped_test_ids: TEST-006, TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-007 — FR-007 `beacon ask` 的 `--execute` 必须有更严格的边界契约
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-008 — FR-008 `brainstorm` 与 `ask` 必须建立清晰分工
- status: `completed`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-009 — FR-009 requirement 三件套必须增加 diagram-aware 深度思考协议
- status: `completed`
- mapped_ac_ids: AC-020, AC-018, AC-017
- mapped_test_ids: TEST-020, TEST-018, TEST-017
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-010 — FR-010 semantic trace 必须成为 requirement 深度思考的共享输入
- status: `completed`
- mapped_ac_ids: AC-021
- mapped_test_ids: TEST-021
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-011 — FR-011 requirement 建模增强优先采用“升格现有 diagram + semantic”，而不是直接新增五件套目录
- status: `completed`
- mapped_ac_ids: AC-025, AC-026, AC-054, AC-023, AC-024, AC-055
- mapped_test_ids: TEST-025, TEST-026, TEST-054, TEST-023, TEST-024, TEST-055
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-012 — FR-012 Python 后端必须逐步退回四类职责
- status: `completed`
- mapped_ac_ids: AC-029
- mapped_test_ids: TEST-029
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-013 — FR-013 Python 职责瘦身必须覆盖 `qa / implement / prd / release`
- status: `completed`
- mapped_ac_ids: AC-033, AC-052
- mapped_test_ids: TEST-033, TEST-052
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-014 — FR-014 skill surface 的版本漂移必须先修复
- status: `completed`
- mapped_ac_ids: AC-042, AC-043, AC-014
- mapped_test_ids: TEST-042, TEST-043, TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-015 — FR-015 迁移必须采用 trace-scorecard 或等价一致性回归
- status: `completed`
- mapped_ac_ids: AC-038, AC-031, AC-039, AC-056
- mapped_test_ids: TEST-038, TEST-031, TEST-039, TEST-056
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-016 — FR-016 support surface 必须能够解释“为什么推荐这条 route”
- status: `completed`
- mapped_ac_ids: AC-045
- mapped_test_ids: TEST-045
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-017 — FR-017 本特性不得破坏 `v1.4.0` 已冻结的五层架构
- status: `planned`
- mapped_ac_ids: AC-058
- mapped_test_ids: TEST-058
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis

### ITASK-018 — FR-018 prototype 在本 feature 中必须被条件触发并补入正式 requirement 链
- status: `completed`
- mapped_ac_ids: AC-049, AC-010, AC-016, AC-019, AC-022, AC-027, AC-028, AC-030, AC-032, AC-034, AC-035, AC-036, AC-037, AC-040, AC-041, AC-044, AC-046, AC-047, AC-048, AC-051, AC-053, AC-057, AC-059, AC-060
- mapped_test_ids: TEST-049, TEST-010, TEST-016, TEST-019, TEST-022, TEST-027, TEST-028, TEST-030, TEST-032, TEST-034, TEST-035, TEST-036, TEST-037, TEST-040, TEST-041, TEST-044, TEST-046, TEST-047, TEST-048, TEST-051, TEST-053, TEST-057, TEST-059, TEST-060
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: skill_surface_state, thin | thickened | governed | stable, python_responsibility_state, overloaded | split_read_write | reduced | minimal_guardrail, learning_state, latent | readable | injected | audited, modeling_state, implicit | diagram_aware | semantic_aware | gate_consumed, prd / user-story / test-case, branch-flow / state-machine / decision-priority / state axis
