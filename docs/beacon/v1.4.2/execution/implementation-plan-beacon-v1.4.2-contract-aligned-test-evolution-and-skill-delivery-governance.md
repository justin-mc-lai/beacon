# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance-r1`
- feature: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`
- version: `v1.4.2`
- revision_id: `R1`
- baseline_hash: `sha256:16349dc50c33a9342a9a8b292fa2db9ff48a6c8c260def944f6882c716c9ca84`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.2-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance-R1`
- delivery_baseline_source_hash: `sha256:2b0aef1aa2d1afe9cc8ab7ead11c33af3070cf636a4aedbd8ce0fce833f4aae5`
- plan_hash: `sha256:4ecf47f26ddb7841285aa4dc22a6702372b493dfe61a19575f1168eb7bdae337`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.2/user-story/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- prd: `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- test_case: `docs/beacon/v1.4.2/qa/test-cases/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- ac_matrix: `docs/beacon/v1.4.2/.machine/qa/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.2/.machine/qa/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.2/.machine/qa/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/v1.4.2/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance" --project-root . --version v1.4.2`
- run_command: `beacon implement team-run "beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance" --project . --version v1.4.2`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance" --project . --version v1.4.2`
- qa_team_command: `beacon qa team-run "beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance" --project . --version v1.4.2`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.2`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.4.2/.machine/execution/git-workflow-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

## Tasks

### ITASK-001 — FR-001 : Beacon must define a Test Contract Index containing identity, truth refs, runtime/docs line, lane membership, AC/TC/test/evidence mapping, status, and reason codes.
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-US001-001, TC-013, TC-014, TC-015, TC-016, TC-017, TC-018, TC-019, TC-020, TC-021
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-US001-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-002 — FR-002 : Beacon must verify release-facing lane classification and block unsafe unclassified failures.
- status: `completed`
- mapped_ac_ids: AC-002, AC-006
- mapped_test_ids: TC-US002-001, TC-US006-001
- mapped_scenario_ids: SC-002, SC-006
- mapped_qa_case_ids: TC-US002-001, TC-US006-001
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-003 — FR-003 : Beacon must require release-facing tests to map to AC/TC and evidence or declare an explicit generated-surface contract reason.
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-US003-001
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-US003-001
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-004 — FR-004 : Doctor support commands must own build/verify behavior for the test contract index.
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-US004-001
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-US004-001
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-005 — FR-005 : QA must preserve AC order, evidence pack, coverage current/gap, continue decision, repair handoff, help resume, and next-round backfill.
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-US005-001
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-US005-001
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-006 — FR-006 : Release scorecard and strict gate must consume lane status and expose reason codes.
- status: `completed`
- mapped_ac_ids: AC-009, AC-012, AC-007
- mapped_test_ids: TC-US009-001, TC-US012-001, TC-US007-001
- mapped_scenario_ids: SC-007, SC-009, SC-012
- mapped_qa_case_ids: TC-US007-001, TC-US009-001, TC-US012-001
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-007 — FR-007 : Beacon skill surfaces must guide agents to classify tests by lane.
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TC-US008-001
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: TC-US008-001
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-008 — FR-008 : Deep-derived test deltas must route to test-case or supplemental QA.
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TC-US010-001
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: TC-US010-001
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-009 — FR-009 : Planning-line safety must preserve runtime/package/docs-current version truth.
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TC-US011-001
- mapped_scenario_ids: SC-011
- mapped_qa_case_ids: TC-US011-001
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-010 — FR-001: Test Contract Index
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-011 — FR-002: Lane Verification
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-012 — FR-003: AC/TC/Test Mapping
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-013 — FR-004: Doctor Ownership
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-014 — FR-005: QA Consumption
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-015 — FR-006: Release Consumption
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-016 — FR-007: Skill Delivery Governance
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-017 — FR-008: Deep Delta Adoption
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking

### ITASK-018 — FR-009: Planning Line Safety
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: contract_lane, truth_binding, evidence_status, surface_sync, release_blocking
