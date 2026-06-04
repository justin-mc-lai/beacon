# Beacon Implementation Plan

- plan_id: `plan-qa-evidence-attribution-layer-r4`
- feature: `qa-evidence-attribution-layer`
- version: `v1.4.10`
- revision_id: `R4`
- baseline_hash: `sha256:21f4ffd5a11e2c7f83ada424d6632f7483c28d499072036802494bc0afd0b1f3`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.10-qa-evidence-attribution-layer-R4`
- delivery_baseline_source_hash: `sha256:0b3bf838df04930e2f60ae1930bc04c11874ae4bb6c9b957a19ca6cfeaef2d49`
- plan_hash: `sha256:fe5d0a2141b7054f2e0cb53b22eefaa667af6fcbb9956f25cd5bc78a3b80cdde`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.10/user-story/qa-evidence-attribution-layer.md`
- prd: `docs/beacon/archive/v1.4.10/prd/qa-evidence-attribution-layer.md`
- test_case: `docs/beacon/archive/v1.4.10/qa/test-cases/qa-evidence-attribution-layer.md`
- revision_delta: `docs/beacon/archive/v1.4.10/.machine/execution/revision-delta-qa-evidence-attribution-layer.json`
- ac_matrix: `docs/beacon/archive/v1.4.10/.machine/qa/qa-evidence-attribution-layer.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.10/.machine/qa/qa-evidence-attribution-layer.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.10/.machine/qa/qa-evidence-attribution-layer.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.10/.machine/user-story/qa-evidence-attribution-layer.json`
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
- plan_command: `beacon implement team-plan "qa-evidence-attribution-layer" --project-root . --version v1.4.10`
- run_command: `beacon implement team-run "qa-evidence-attribution-layer" --project . --version v1.4.10`
- dev_run_command: `beacon implement dev-run "qa-evidence-attribution-layer" --project . --version v1.4.10`
- qa_team_command: `beacon qa team-run "qa-evidence-attribution-layer" --project . --version v1.4.10`
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
- git_workflow_ref: `docs/beacon/archive/v1.4.10/.machine/execution/git-workflow-qa-evidence-attribution-layer.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.10/research/qa-evidence-attribution-layer.md`
- source_artifact: `docs/beacon/archive/v1.4.10/.machine/user-story/qa-evidence-attribution-layer.json`
- section_count: `3`
- architecture: `truth_drift`: requirement truth must reopen through `beacon-change`. / `implementation_gap`: implementation must route to `beacon-implement`. / `coverage_gap`: acceptance coverage must route to `beacon-test-case`.
- state_machine: `source_evidence_missing`: AC or evidence refs are missing. / `runner_admission_blocked`: runner never reached AC evaluation. / `authority_boundary_violation`: attribution claims truth or verdict authority.
- decision_priority: Authority boundary violation blocks first. / Proven `truth_drift` routes to `beacon-change`. / Proven `coverage_gap` routes to `beacon-test-case`.

## Revision Delta
- revision_id: `R4`
- source_revision_id: `R3`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.10/.machine/execution/revision-delta-qa-evidence-attribution-layer.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-QA-ATTR-001, TC-QA-ATTR-002, TC-QA-ATTR-003
- mapped_scenario_ids: SC-001, SC-002, SC-003
- mapped_qa_case_ids: TC-QA-ATTR-001, TC-QA-ATTR-002, TC-QA-ATTR-003
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-004, AC-007, AC-005
- mapped_test_ids: TC-QA-ATTR-005, TC-QA-ATTR-008, TC-QA-ATTR-006
- mapped_scenario_ids: SC-005, SC-006, SC-008
- mapped_qa_case_ids: TC-QA-ATTR-005, TC-QA-ATTR-006, TC-QA-ATTR-008
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state

### ITASK-003 — FR-003 AC-002
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-QA-ATTR-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-QA-ATTR-004
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state

### ITASK-004 — FR-004 AC-003
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-QA-ATTR-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: TC-QA-ATTR-007
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state

### ITASK-005 — FR-005 AC-004
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state

### ITASK-006 — FR-006 AC-005
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state

### ITASK-007 — FR-007 AC-006
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state

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
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state
