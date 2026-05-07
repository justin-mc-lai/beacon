# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration-r1`
- feature: `beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration`
- version: `v1.4.0`
- revision_id: `R1`
- baseline_hash: `sha256:1174849126ad499d60f21c90e5a035c7366f34a544e753abb831e0cc9bfb642d`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.0-beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration-R1`
- delivery_baseline_source_hash: `sha256:108cfb84612b60249a8d6b133707d82e04d05e3d760f0902d3f5d0ae40a598b8`
- plan_hash: `sha256:b421b695904489acdb09ea4d4e8afd7962b9f0f1fdd5c408807b19aa713059a6`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- prd: `docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- test_case: `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- ac_matrix: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.qa9-matrix.json`
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
- plan_command: `beacon implement team-plan "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration" --project-root . --version v1.4.0`
- run_command: `beacon implement team-run "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration" --project . --version v1.4.0`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration" --project . --version v1.4.0`
- qa_team_command: `beacon qa team-run "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration" --project . --version v1.4.0`
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
- git_workflow_ref: `docs/beacon/v1.4.0/.machine/execution/git-workflow-beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

## Tasks

### ITASK-001 — FR-001 Package State Detection
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001, TC-029, TC-030, TC-031, TC-032, TC-033, TC-034, TC-035, TC-036, TC-037
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-002 — FR-002 Missing-Layer Compile Orchestration
- status: `completed`
- mapped_ac_ids: AC-005, AC-002, AC-022
- mapped_test_ids: TEST-005, TC-002, TEST-022
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-003 — FR-003 Canonical Compile Order
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-004 — FR-004 Reverse-Derived Truth Labeling
- status: `completed`
- mapped_ac_ids: AC-027, AC-009
- mapped_test_ids: TEST-027, TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-005 — FR-005 Drift Digest and Repair Routing
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-006 — FR-006 Closure Analyzer
- status: `completed`
- mapped_ac_ids: AC-017
- mapped_test_ids: TEST-017
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-007 — FR-007 Conditional Promotion
- status: `completed`
- mapped_ac_ids: AC-019
- mapped_test_ids: TEST-019
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-008 — FR-008 Unified Human Output
- status: `completed`
- mapped_ac_ids: AC-012, AC-004
- mapped_test_ids: TEST-012, TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-004
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-009 — FR-009 Optional Support Surface Boundary
- status: `completed`
- mapped_ac_ids: AC-025
- mapped_test_ids: TEST-025
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion

### ITASK-010 — FR-010 Reuse Existing Truth Tree
- status: `completed`
- mapped_ac_ids: AC-003, AC-010, AC-011, AC-007, AC-008, AC-014, AC-015, AC-016, AC-018, AC-020, AC-021, AC-023, AC-024, AC-026, AC-028
- mapped_test_ids: TC-003, TEST-010, TEST-011, TEST-007, TEST-008, TEST-014, TEST-015, TEST-016, TEST-018, TEST-020, TEST-021, TEST-023, TEST-024, TEST-026, TEST-028
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-003
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: package_state, empty | prd_only | user_story_only | test_case_only | prd_user_story | prd_test_case | user_story_test_case | full_consistent | full_inconsistent, empty, prd_only, user_story_only, test_case_only, prd_user_story, prd_test_case, user_story_test_case, full_consistent, full_inconsistent, closure_state, package_detected | missing_layer_routed | reverse_derived_truth | needs_truth_review | supplement_required | drift_repair_required | freeze_ready | implementation_pending, package_detected, missing_layer_routed, reverse_derived_truth, needs_truth_review, supplement_required, drift_repair_required, freeze_ready, implementation_pending, truth_origin_state, native_truth | derived_from_downstream | needs_truth_review, native_truth, derived_from_downstream, decision_state, accepted | rejected | deferred, accepted, rejected, deferred, routing_state, canonical_compile | reverse_derive | repair_route | conditional_promotion, canonical_compile, reverse_derive, repair_route, conditional_promotion
