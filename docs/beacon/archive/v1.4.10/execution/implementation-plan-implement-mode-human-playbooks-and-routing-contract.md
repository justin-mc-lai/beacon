# Beacon Implementation Plan

- plan_id: `plan-implement-mode-human-playbooks-and-routing-contract-r3`
- feature: `implement-mode-human-playbooks-and-routing-contract`
- version: `v1.4.10`
- revision_id: `R3`
- baseline_hash: `sha256:800acefc5870b88f09e8896423cf259f248e72f6ddcf5cc090e93442c3039684`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.10-implement-mode-human-playbooks-and-routing-contract-R3`
- delivery_baseline_source_hash: `sha256:81f87d294c24eb3048483aeeee86862fb52cf498afae8c6f4b7d180399c70f01`
- plan_hash: `sha256:151b6ae8c79beda3258a420074cd348f586da5e39ecf6e9d3f83d1f24ce64e7f`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.10/user-story/implement-mode-human-playbooks-and-routing-contract.md`
- prd: `docs/beacon/archive/v1.4.10/prd/implement-mode-human-playbooks-and-routing-contract.md`
- test_case: `docs/beacon/archive/v1.4.10/qa/test-cases/implement-mode-human-playbooks-and-routing-contract.md`
- revision_delta: `docs/beacon/archive/v1.4.10/.machine/execution/revision-delta-implement-mode-human-playbooks-and-routing-contract.json`
- ac_matrix: `docs/beacon/archive/v1.4.10/.machine/qa/implement-mode-human-playbooks-and-routing-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.10/.machine/qa/implement-mode-human-playbooks-and-routing-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.10/.machine/qa/implement-mode-human-playbooks-and-routing-contract.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.10/.machine/user-story/implement-mode-human-playbooks-and-routing-contract.json`
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
- plan_command: `beacon implement team-plan "implement-mode-human-playbooks-and-routing-contract" --project-root . --version v1.4.10`
- run_command: `beacon implement team-run "implement-mode-human-playbooks-and-routing-contract" --project . --version v1.4.10`
- dev_run_command: `beacon implement dev-run "implement-mode-human-playbooks-and-routing-contract" --project . --version v1.4.10`
- qa_team_command: `beacon qa team-run "implement-mode-human-playbooks-and-routing-contract" --project . --version v1.4.10`
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
- git_workflow_ref: `docs/beacon/archive/v1.4.10/.machine/execution/git-workflow-implement-mode-human-playbooks-and-routing-contract.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.10/research/implement-mode-human-playbooks-and-routing-contract.md`
- source_artifact: `docs/beacon/archive/v1.4.10/.machine/user-story/implement-mode-human-playbooks-and-routing-contract.json`
- section_count: `1`
- decision_priority: `beacon-implement` remains the only public implementation skill. / Mode playbooks explain execution shape; they do not create public lifecycle stages. / Help/status recommendations must include the reason and canonical command.

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.10/.machine/execution/revision-delta-implement-mode-human-playbooks-and-routing-contract.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-IMPL-MODE-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-IMPL-MODE-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-002, AC-003
- mapped_test_ids: TC-IMPL-MODE-002, TC-IMPL-MODE-003
- mapped_scenario_ids: SC-002, SC-003
- mapped_qa_case_ids: TC-IMPL-MODE-002, TC-IMPL-MODE-003
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-006, AC-007, AC-004
- mapped_test_ids: TC-IMPL-MODE-006, TC-IMPL-MODE-007, TC-IMPL-MODE-004
- mapped_scenario_ids: SC-004, SC-006, SC-007
- mapped_qa_case_ids: TC-IMPL-MODE-004, TC-IMPL-MODE-006, TC-IMPL-MODE-007
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TC-IMPL-MODE-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: TC-IMPL-MODE-008
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-IMPL-MODE-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-IMPL-MODE-005
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary

### ITASK-006 — FR-006 AC-006
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary

### ITASK-007 — FR-007 AC-007
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary

### ITASK-008 — FR-008 AC-008
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implement_request_state, mode_resolution_state, mode_admission_state, implementation_evidence_state, ralph_closure_route_state, truth_authority_boundary
