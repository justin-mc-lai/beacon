# Beacon Implementation Plan

- plan_id: `plan-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance-r1`
- feature: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- version: `v1.3.11`
- revision_id: `R1`
- baseline_hash: `sha256:99d77761f3248af5df3d18418b90fe04fcb27855fccf394d6e18f89cb740dc3c`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.11-beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance-R1`
- delivery_baseline_source_hash: `sha256:261c27861deb0e3356c691bb270583d9a837037189ff5f6dd5f74ca7b7e9b3f6`
- plan_hash: `sha256:e5bd7e2fc43634e4ad0a524dd7d0d818cfd2363e06ee6b81b10735f26f475b86`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.11/user-story/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- prd: `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- test_case: `docs/beacon/v1.3.11/qa/test-cases/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
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

## Tasks

### ITASK-001 — FR-001 Beacon 必须定义统一的 work item 模型
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-002, TC-018, TC-019
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004
- mapped_qa_case_ids: TC-001, TC-002, TC-018, TC-019
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-002 — FR-002 Beacon 必须定义统一的 run 模型
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004, TC-021
- mapped_scenario_ids: SC-007, SC-008
- mapped_qa_case_ids: TC-004, TC-021
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-003 — FR-003 Beacon 必须提供统一 run scheduler
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-017
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-017
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved

### ITASK-004 — FR-004 Beacon 必须提供 run 级 workspace isolation
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
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
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
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
- mapped_ac_ids: AC-003, AC-008, AC-016, AC-017
- mapped_test_ids: TC-003, TEST-008, TEST-016, TEST-017, TC-020
- mapped_scenario_ids: SC-005, SC-006
- mapped_qa_case_ids: TC-003, TC-020
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: runtime_item_axis, team_task, ralph_step, real_project_validation_case, implement_delivery, qa_repair, release_closure, run_status_axis, queued, running, retry_waiting, blocked, handoff_required, completed, cancelled, workspace_axis, isolated_workspace, shared_workspace_blocked, recovery_axis, retry_path_explicit, repair_resume_explicit, human_intervention_explicit, delivery_bridge_axis, truth_read_only, runtime_bridge_only, release_gate_preserved
