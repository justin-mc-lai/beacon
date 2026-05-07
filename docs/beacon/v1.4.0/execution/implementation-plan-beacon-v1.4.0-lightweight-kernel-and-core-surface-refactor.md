# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor-r1`
- feature: `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
- version: `v1.4.0`
- revision_id: `R1`
- baseline_hash: `sha256:108a84b476801b9c7623ccae84d77f8e887bad1fc89b9c966b67025a82a0aaad`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.0-beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor-R1`
- delivery_baseline_source_hash: `sha256:68eeacb4d25735b1564e8387ba4cb0182eacaabd84b620b0980370c841d699e4`
- plan_hash: `sha256:0fa507431826cf686b2511cde370ad28dd6cfed677c10b607ae92f3f3a0f99f3`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- prd: `docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- test_case: `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- ac_matrix: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.qa9-matrix.json`
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
- plan_command: `beacon implement team-plan "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor" --project-root . --version v1.4.0`
- run_command: `beacon implement team-run "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor" --project . --version v1.4.0`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor" --project . --version v1.4.0`
- qa_team_command: `beacon qa team-run "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor" --project . --version v1.4.0`
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
- git_workflow_ref: `docs/beacon/v1.4.0/.machine/execution/git-workflow-beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

## Tasks

### ITASK-001 — FR-001 Beacon 必须冻结一套正式的 v2 轻量内核分层
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-060, TC-061, TC-062, TC-063, TC-064, TC-065, TC-066, TC-067, TC-068, TC-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-001, TC-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-002 — FR-002 Beacon 必须正式定义 minimal machine contract
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-058
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-058
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-003 — FR-003 machine contract 必须由 markdown 单向编译得出
- status: `completed`
- mapped_ac_ids: AC-003, AC-004
- mapped_test_ids: TC-003, TC-004
- mapped_scenario_ids: SC-003, SC-004
- mapped_qa_case_ids: TC-003, TC-004
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-004 — FR-004 Beacon 必须重新定义事务性双写为“canonical 驱动的单向投影”
- status: `completed`
- mapped_ac_ids: AC-007, AC-005
- mapped_test_ids: TC-059, TC-057
- mapped_scenario_ids: SC-005, SC-007
- mapped_qa_case_ids: TC-057, TC-059
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-005 — FR-005 基础 code gate 基座能力必须完整保留
- status: `completed`
- mapped_ac_ids: AC-028
- mapped_test_ids: TEST-028
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-006 — FR-006 `implement` 与 `qa` 仍必须是唯一执行入口
- status: `completed`
- mapped_ac_ids: AC-019, AC-018
- mapped_test_ids: TEST-019, TEST-018
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-007 — FR-007 Host-LLM Kernel 必须保留并减耦
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-008 — FR-008 Learning Plane Kernel 必须保留 typed contract，而不是被删掉
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-009 — FR-009 Metadata / Topology Kernel 必须继续作为工程运行底座
- status: `completed`
- mapped_ac_ids: AC-009, AC-025
- mapped_test_ids: TEST-009, TEST-025
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-010 — FR-010 Memory / Workflow Memory Kernel 必须保留统一 envelope
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-011 — FR-011 Archive / Support Surface 必须保留，但不再膨胀为主路径复杂度
- status: `completed`
- mapped_ac_ids: AC-056, AC-051, AC-011, AC-012
- mapped_test_ids: TEST-056, TEST-051, TEST-011, TEST-012
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-012 — FR-012 Brainstorm 必须作为只读收敛层被正式保留
- status: `completed`
- mapped_ac_ids: AC-045, AC-054
- mapped_test_ids: TEST-045, TEST-054
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-013 — FR-013 Brainstorm 必须支持统一 route matrix，而不是继续做模板生成器
- status: `completed`
- mapped_ac_ids: AC-035
- mapped_test_ids: TEST-035
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-014 — FR-014 Beacon 必须正式分离 core commands 与 plugin/domain commands
- status: `completed`
- mapped_ac_ids: AC-014, AC-053, AC-023, AC-041, AC-050, AC-015, AC-042, AC-046, AC-057
- mapped_test_ids: TEST-014, TEST-053, TEST-023, TEST-041, TEST-050, TEST-015, TEST-042, TEST-046, TEST-057
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-015 — FR-015 Beacon 必须允许在 requirement freeze 基座上扩展更多场景，但不把扩展默认塞回 core
- status: `completed`
- mapped_ac_ids: AC-016, AC-017, AC-020, AC-021, AC-022, AC-024, AC-026
- mapped_test_ids: TEST-016, TEST-017, TEST-020, TEST-021, TEST-022, TEST-024, TEST-026
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-016 — FR-016 `doctor sync-materials` 类历史能力应向 contract compile / verify 语义收敛
- status: `completed`
- mapped_ac_ids: AC-027, AC-029, AC-030, AC-031, AC-032, AC-033, AC-034
- mapped_test_ids: TEST-027, TEST-029, TEST-030, TEST-031, TEST-032, TEST-033, TEST-034
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-017 — FR-017 Beacon 必须以“先双读、后单读”的方式迁移，避免 gate 漂移
- status: `completed`
- mapped_ac_ids: AC-036, AC-037, AC-038, AC-039, AC-040, AC-043, AC-044
- mapped_test_ids: TEST-036, TEST-037, TEST-038, TEST-039, TEST-040, TEST-043, TEST-044
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported

### ITASK-018 — FR-018 `v1.4.0` 必须保留 Python 作为主实现语言
- status: `completed`
- mapped_ac_ids: AC-047, AC-058, AC-059, AC-049, AC-048, AC-052, AC-055
- mapped_test_ids: TEST-047, TEST-058, TEST-059, TEST-049, TEST-048, TEST-052, TEST-055
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: truth_state, draft | frozen | changed | archived, draft, frozen, changed, archived, contract_state, missing | compiled | stale | blocked, missing, compiled, stale, blocked, gate_state, pass | blocked | downgrade, pass, downgrade, projection_state, not_configured | healthy | drifted | failed, not_configured, healthy, drifted, failed, brainstorm_state, brainstorm_closed | supplement_required | change_required | truth_ready, brainstorm_closed, supplement_required, change_required, truth_ready, change_state, proposed | approved | refreezing | implementing | verifying | archived, proposed, approved, refreezing, implementing, verifying, goal_state, none | active | paused | budget_limited | complete | unsupported, none, active, paused, budget_limited, complete, unsupported
