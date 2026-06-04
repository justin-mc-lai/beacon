# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure-r1`
- feature: `beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure`
- version: `v1.4.0`
- revision_id: `R1`
- baseline_hash: `sha256:ba8780fc4d25840fc772463a8107ad083651c9f61a1460d8f5ff50dbe050e910`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.0-beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure-R1`
- delivery_baseline_source_hash: `sha256:19079fd10c3d9e6669f797d8c72ef639b050af6015e999e547556ec7d1da93c9`
- plan_hash: `sha256:2a4abe0747fa982058b5d4d8572ef607010dbe955a1ea11537e96f346a94df3e`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- prd: `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- test_case: `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- ac_matrix: `docs/beacon/archive/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/archive/v1.4.0/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure" --project-root . --version v1.4.0`
- run_command: `beacon implement team-run "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure" --project . --version v1.4.0`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure" --project . --version v1.4.0`
- qa_team_command: `beacon qa team-run "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure" --project . --version v1.4.0`
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
- git_workflow_ref: `docs/beacon/archive/v1.4.0/.machine/execution/git-workflow-beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

## Tasks

### ITASK-001 — FR-001 Optional Support Surface
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-033, TC-034, TC-035, TC-036, TC-037, TC-038, TC-039, TC-040, TC-041, TC-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-001, TC-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-002 — FR-002 One-Click Requirement Draft Package
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-003
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-003 — FR-003 Safe-by-Default Execution
- status: `completed`
- mapped_ac_ids: AC-010, AC-011
- mapped_test_ids: TEST-010, TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-004 — FR-004 Atomic and Recoverable Write
- status: `completed`
- mapped_ac_ids: AC-014, AC-004
- mapped_test_ids: TEST-014, TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-005 — FR-005 Bootstrap Output Status Contract
- status: `completed`
- mapped_ac_ids: AC-005, AC-017, AC-018
- mapped_test_ids: TEST-005, TEST-017, TEST-018
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-006 — FR-006 Traceability Contract
- status: `completed`
- mapped_ac_ids: AC-022, AC-007
- mapped_test_ids: TEST-022, TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-007 — FR-007 Quality and Consistency Gate
- status: `completed`
- mapped_ac_ids: AC-012, AC-026, AC-009, AC-013
- mapped_test_ids: TEST-012, TEST-026, TEST-009, TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-008 — FR-008 Human-Readable Next-Step Guidance
- status: `completed`
- mapped_ac_ids: AC-024, AC-031, AC-008
- mapped_test_ids: TEST-024, TEST-031, TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-009 — FR-009 No Reverse Truth Drift
- status: `completed`
- mapped_ac_ids: AC-028
- mapped_test_ids: TEST-028
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion

### ITASK-010 — FR-010 v1.4.0 Format Alignment
- status: `completed`
- mapped_ac_ids: AC-023, AC-006, AC-015, AC-016, AC-019, AC-020, AC-021, AC-025, AC-027, AC-029, AC-030, AC-032
- mapped_test_ids: TEST-023, TEST-006, TEST-015, TEST-016, TEST-019, TEST-020, TEST-021, TEST-025, TEST-027, TEST-029, TEST-030, TEST-032
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, bootstrap_state, draft_generated | review_required | supplement_required | drift_repair_required | freeze_ready | implementation_pending, draft_generated, review_required, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, needs_truth_review, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | freeze_promotion, canonical_compile, reverse_derive, repair_route, freeze_promotion
