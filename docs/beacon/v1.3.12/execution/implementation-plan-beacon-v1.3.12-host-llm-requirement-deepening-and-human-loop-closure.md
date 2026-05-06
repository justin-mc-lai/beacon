# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure-r1`
- feature: `beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure`
- version: `v1.3.12`
- revision_id: `R1`
- baseline_hash: `sha256:4b7b0b9bd63c8f7cf4879d07f1f7d8b107616fbf312f8f4351a2853ea086caab`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.12-beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure-R1`
- delivery_baseline_source_hash: `sha256:03d7b75ac6466dccae5988a1d441eb6fac506fb01cac525f6894e68702afe764`
- plan_hash: `sha256:95a7020f21aeb2c87755aa9e450d39a2f5d5f1dd82b3984cd3fe0b72c9fb7bfb`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.12/user-story/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- prd: `docs/beacon/v1.3.12/prd/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- test_case: `docs/beacon/v1.3.12/qa/test-cases/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- ac_matrix: `docs/beacon/v1.3.12/.machine/qa/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.12/.machine/qa/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.12/.machine/qa/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/v1.3.12/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure" --project-root . --version v1.3.12`
- run_command: `beacon implement team-run "beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure" --project . --version v1.3.12`
- dev_run_command: `beacon implement dev-run "beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure" --project . --version v1.3.12`
- qa_team_command: `beacon qa team-run "beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure" --project . --version v1.3.12`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.12`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.12/.machine/execution/git-workflow-beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

## Tasks

### ITASK-001 — FR-001 Beacon 必须为 PRD 建立 requirement deepening envelope
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-001, TC-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-002 — FR-002 `user-story` 必须从 PRD 主动发现缺失故事，而不只抽取现有 AC
- status: `completed`
- mapped_ac_ids: AC-005, AC-003
- mapped_test_ids: TEST-005, TC-003, TC-025
- mapped_scenario_ids: SC-003, SC-005
- mapped_qa_case_ids: TC-003, TC-025
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-003 — FR-003 `test-case` 必须从 PRD 与 story 主动扩展覆盖族群
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-004 — FR-004 三个 subskill 必须成为同一套补齐协议的人类面
- status: `completed`
- mapped_ac_ids: AC-004, AC-016, AC-024
- mapped_test_ids: TC-004, TEST-016, TEST-024
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-005 — FR-005 Beacon 必须为 requirement deepening 保存 gap register 与 candidate ledger
- status: `completed`
- mapped_ac_ids: AC-017
- mapped_test_ids: TEST-017
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-006 — FR-006 人类确认后的补齐必须触发正确 writeback
- status: `completed`
- mapped_ac_ids: AC-008, AC-006, AC-007
- mapped_test_ids: TEST-008, TEST-006, TEST-007, TC-026, TC-027
- mapped_scenario_ids: SC-006, SC-007
- mapped_qa_case_ids: TC-026, TC-027
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-007 — FR-007 requirement re-freeze 必须保持 anti-drift 一致性
- status: `completed`
- mapped_ac_ids: AC-019
- mapped_test_ids: TEST-019
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-008 — FR-008 host-native capability 与 downgrade 必须显式进入 requirement contract
- status: `completed`
- mapped_ac_ids: AC-013, AC-014, AC-025
- mapped_test_ids: TEST-013, TEST-014, TEST-025
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-009 — FR-009 deepening 输出必须保留拒绝与延后语义
- status: `completed`
- mapped_ac_ids: AC-015, AC-018, AC-020, AC-026
- mapped_test_ids: TEST-015, TEST-018, TEST-020, TEST-026
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback

### ITASK-010 — FR-010 delivery closure 必须能读取 requirement deepening completeness
- status: `completed`
- mapped_ac_ids: AC-021, AC-010, AC-011, AC-012, AC-022, AC-023, AC-027
- mapped_test_ids: TEST-021, TEST-010, TEST-011, TEST-012, TEST-022, TEST-023, TEST-027
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: requirement_gap_axis, unseen_role_difference, unseen_state_transition, unseen_boundary_case, unseen_exception_path, unseen_recovery_path, human_decision_axis, accepted, rejected, deferred, compile_mode_axis, host_native, provider_backed_host, rule_fallback
