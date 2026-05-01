# Beacon Implementation Plan

- plan_id: `plan-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance-r2`
- feature: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- version: `v1.3.11`
- revision_id: `R2`
- baseline_hash: `sha256:fe24402c6ec7e16ad21e8732b43c805bc57a174583faccf7e62fc72bd3232e9c`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.11-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance-R2`
- delivery_baseline_source_hash: `sha256:f7acadffa038bb23b595f6864c57adf4ebe2c2aae8324944cb808d6318110675`
- plan_hash: `sha256:ba468a98741653f77b0d4ef661b8b0a1b11eff928086d55f754dd2f5076aab7c`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.11/user-story/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- prd: `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- test_case: `docs/beacon/v1.3.11/qa/test-cases/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- revision_delta: `docs/beacon/v1.3.11/.machine/execution/revision-delta-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.json`
- ac_matrix: `docs/beacon/v1.3.11/.machine/qa/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.11/.machine/qa/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.11/.machine/qa/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/v1.3.11/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance" --project-root . --version v1.3.11`
- run_command: `beacon implement team-run "beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance" --project . --version v1.3.11`
- dev_run_command: `beacon implement dev-run "beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance" --project . --version v1.3.11`
- qa_team_command: `beacon qa team-run "beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance" --project . --version v1.3.11`
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
- git_workflow_ref: `docs/beacon/v1.3.11/.machine/execution/git-workflow-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.3.11/.machine/execution/revision-delta-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.json`

## Tasks

### ITASK-001 — FR-001 Beacon 必须定义统一的 work item 模型
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-002, TC-024, TC-025
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004
- mapped_qa_case_ids: TC-001, TC-002, TC-024, TC-025
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-002 — FR-002 Beacon 必须定义统一的 run 模型
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004, TC-027
- mapped_scenario_ids: SC-007, SC-008
- mapped_qa_case_ids: TC-004, TC-027
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-003 — FR-003 Beacon 必须提供统一 run scheduler
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-021
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-021
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-004 — FR-004 Beacon 必须提供 run 级 workspace isolation
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-022
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: TC-022
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-005 — FR-005 Beacon 必须提供 worker runtime 生命周期记录
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-006 — FR-006 Beacon 必须提供 retry / reconciliation 机制
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-023
- mapped_scenario_ids: SC-011
- mapped_qa_case_ids: TC-023
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-007 — FR-007 Beacon 必须提供 runtime board
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-008 — FR-008 Beacon 必须提供 delivery closure bridge
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-009 — FR-009 `team` 必须优先接入 orchestration runtime
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-010 — FR-010 `ralph` 必须作为 controller 而不是直接执行器接入
- status: `completed`
- mapped_ac_ids: AC-014
- mapped_test_ids: TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-011 — FR-011 `real-project-validation` 必须接入 run 级隔离
- status: `completed`
- mapped_ac_ids: AC-015, AC-012
- mapped_test_ids: TEST-015, TEST-012
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-012 — FR-012 orchestration runtime 不得反向写 requirement truth
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003, TC-026
- mapped_scenario_ids: SC-005, SC-006
- mapped_qa_case_ids: TC-003, TC-026
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-013 — FR-013 同版本多个 feature package 的 execution blueprint 投影必须可并存
- status: `completed`
- mapped_ac_ids: AC-017, AC-018
- mapped_test_ids: TEST-017, TEST-018
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-014 — FR-014 Beacon 必须提供版本内 feature implementation order 分析
- status: `completed`
- mapped_ac_ids: AC-019, AC-008, AC-016, AC-020, AC-021, AC-022, AC-023
- mapped_test_ids: TEST-019, TEST-008, TEST-016, TEST-020, TEST-021, TEST-022, TEST-023
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved
