# Beacon Implementation Plan

- plan_id: `plan-project-lifecycle-hook-skill-toolkit-contract-r4`
- feature: `project-lifecycle-hook-skill-toolkit-contract`
- version: `v1.4.10`
- revision_id: `R4`
- baseline_hash: `sha256:42b6cece42819287c2f0cb7447f7af330e19410907b4e1a5f55d3dcdd56145c8`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.10-project-lifecycle-hook-skill-toolkit-contract-R4`
- delivery_baseline_source_hash: `sha256:db82c333b26b743f1bd6cbc96c23e291088bd1113ae73b8838fb4a9bad8cbb77`
- plan_hash: `sha256:e28dac042b8750b6839f0733d53d07d817c9953302a04cc05bb06675d837293a`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.10/user-story/project-lifecycle-hook-skill-toolkit-contract.md`
- prd: `docs/beacon/archive/v1.4.10/prd/project-lifecycle-hook-skill-toolkit-contract.md`
- test_case: `docs/beacon/archive/v1.4.10/qa/test-cases/project-lifecycle-hook-skill-toolkit-contract.md`
- revision_delta: `docs/beacon/archive/v1.4.10/.machine/execution/revision-delta-project-lifecycle-hook-skill-toolkit-contract.json`
- ac_matrix: `docs/beacon/archive/v1.4.10/.machine/qa/project-lifecycle-hook-skill-toolkit-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.10/.machine/qa/project-lifecycle-hook-skill-toolkit-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.10/.machine/qa/project-lifecycle-hook-skill-toolkit-contract.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.10/.machine/user-story/project-lifecycle-hook-skill-toolkit-contract.json`
- architecture_blueprint: `docs/beacon/archive/v1.4.10/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "project-lifecycle-hook-skill-toolkit-contract" --project-root . --version v1.4.10`
- run_command: `beacon implement team-run "project-lifecycle-hook-skill-toolkit-contract" --project . --version v1.4.10`
- dev_run_command: `beacon implement dev-run "project-lifecycle-hook-skill-toolkit-contract" --project . --version v1.4.10`
- qa_team_command: `beacon qa team-run "project-lifecycle-hook-skill-toolkit-contract" --project . --version v1.4.10`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.10`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.4.10/.machine/execution/git-workflow-project-lifecycle-hook-skill-toolkit-contract.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.10/research/project-lifecycle-hook-skill-toolkit-contract.md`
- source_artifact: `docs/beacon/archive/v1.4.10/.machine/user-story/project-lifecycle-hook-skill-toolkit-contract.json`
- section_count: `1`
- decision_priority: Hook 是 project-level extension，不是 version-level feature artifact。 / Hook contract 固定在 `docs/beacon/hooks/<hook-id>.md`。 / Hook 必须绑定有限 hook code，不允许任意时机隐式触发。

## Revision Delta
- revision_id: `R4`
- source_revision_id: `R3`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.10/.machine/execution/revision-delta-project-lifecycle-hook-skill-toolkit-contract.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-HOOK-001, TC-HOOK-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-HOOK-001, TC-HOOK-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-HOOK-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-HOOK-004
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-HOOK-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-HOOK-003
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-HOOK-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-HOOK-005
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-005 — FR-005 AC-004
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-HOOK-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-HOOK-006
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-006 — FR-006 AC-005
- status: `completed`
- mapped_ac_ids: AC-009, AC-007
- mapped_test_ids: TC-HOOK-009, TC-HOOK-007
- mapped_scenario_ids: SC-007, SC-009
- mapped_qa_case_ids: TC-HOOK-007, TC-HOOK-009
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-007 — FR-007 AC-006
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TC-HOOK-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: TC-HOOK-008
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-008 — FR-008 AC-007
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-009 — FR-009 AC-008
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary

### ITASK-010 — FR-010 AC-009
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: hook_contract_state, hook_admission_state, trigger_policy_state, hook_run_state, hook_evidence_state, failure_route_state, truth_authority_boundary
