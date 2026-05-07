# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.0-branch-governance-human-surface-and-implement-gate-r1`
- feature: `beacon-v1.4.0-branch-governance-human-surface-and-implement-gate`
- version: `v1.4.0`
- revision_id: `R1`
- baseline_hash: `sha256:40b86cbd37b90026f98a640f4366b7e908555017f5875f18bac154498932d136`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.0-beacon-v1.4.0-branch-governance-human-surface-and-implement-gate-R1`
- delivery_baseline_source_hash: `sha256:9e8702074a9dc7e86ccf1076605a17810f4509443bdb8e0fa02a5220993d8406`
- plan_hash: `sha256:d4f1bc30b385670f3071f719fd1947f581fa7595bbfe6423b6fa0f160648aec0`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
- prd: `docs/beacon/v1.4.0/prd/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
- test_case: `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
- ac_matrix: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.qa9-matrix.json`
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
- plan_command: `beacon implement team-plan "beacon-v1.4.0-branch-governance-human-surface-and-implement-gate" --project-root . --version v1.4.0`
- run_command: `beacon implement team-run "beacon-v1.4.0-branch-governance-human-surface-and-implement-gate" --project . --version v1.4.0`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.0-branch-governance-human-surface-and-implement-gate" --project . --version v1.4.0`
- qa_team_command: `beacon qa team-run "beacon-v1.4.0-branch-governance-human-surface-and-implement-gate" --project . --version v1.4.0`
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
- git_workflow_ref: `docs/beacon/v1.4.0/.machine/execution/git-workflow-beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

## Tasks

### ITASK-001 — FR-001 新能力必须采用 toolkit 并排命名，而不是新主命令
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-033, TC-034, TC-035, TC-036, TC-037, TC-038, TC-039, TC-040, TC-041
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-002 — FR-002 人类面必须展示清楚的 branch 流程图
- status: `completed`
- mapped_ac_ids: AC-002, AC-010, AC-025, AC-029
- mapped_test_ids: TC-002, TEST-010, TEST-025, TEST-029
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-003 — FR-003 人类面必须有足够清楚的 git 管理摘要
- status: `completed`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-004 — FR-004 必须支持默认 workflow 与本次定制 workflow
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-005 — FR-005 metadata/profile 必须沉淀 branch governance 最小模板字段
- status: `completed`
- mapped_ac_ids: AC-020, AC-019
- mapped_test_ids: TEST-020, TEST-019
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-006 — FR-006 `implement` 必须在进入执行前强制消费 branch governance contract
- status: `completed`
- mapped_ac_ids: AC-022, AC-021
- mapped_test_ids: TEST-022, TEST-021
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-007 — FR-007 合规条件满足时，必须支持直接切换到规范 branch / worktree
- status: `completed`
- mapped_ac_ids: AC-011, AC-026, AC-007
- mapped_test_ids: TEST-011, TEST-026, TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-008 — FR-008 merge direction policy 必须正式化，并能阻断非法路径
- status: `completed`
- mapped_ac_ids: AC-008, AC-030, AC-031, AC-003, AC-015, AC-017, AC-018
- mapped_test_ids: TEST-008, TEST-030, TEST-031, TC-003, TEST-015, TEST-017, TEST-018
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-003
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-009 — FR-009 evidence contract 必须可见且可校验
- status: `completed`
- mapped_ac_ids: AC-023
- mapped_test_ids: TEST-023
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete

### ITASK-010 — FR-010 关键不合规状态必须 fail-closed
- status: `completed`
- mapped_ac_ids: AC-028, AC-009, AC-005, AC-006, AC-013, AC-014, AC-016, AC-024, AC-027, AC-032
- mapped_test_ids: TEST-028, TEST-009, TEST-005, TEST-006, TEST-013, TEST-014, TEST-016, TEST-024, TEST-027, TEST-032
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_state, missing | resolved | verified | blocked | switch_ready, workspace_state, unresolved | wrong_branch | wrong_worktree | compliant, execution_state, preflight_pending | blocked | switched | implement_ready, evidence_state, missing | partial | complete
