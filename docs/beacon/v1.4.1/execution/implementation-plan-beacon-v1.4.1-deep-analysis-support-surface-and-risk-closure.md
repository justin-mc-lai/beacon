# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure-r1`
- feature: `beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure`
- version: `v1.4.1`
- revision_id: `R1`
- baseline_hash: `sha256:07f472341b96368b0d9a9760860c748b0e892650d0c7a182ff8db8fbfbf2e24a`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.1-beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure-R1`
- delivery_baseline_source_hash: `sha256:ee32e221030f4f79468b5f45d0f81eee17d6b0bd8c71e6c3a10f5c92f73fcf0a`
- plan_hash: `sha256:689a0c134d17d4594478787d5d9429144c2c600966654b34ca324166b54b08a9`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.1/user-story/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- prd: `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- test_case: `docs/beacon/v1.4.1/qa/test-cases/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- ac_matrix: `docs/beacon/v1.4.1/.machine/qa/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.1/.machine/qa/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.1/.machine/qa/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/v1.4.1/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.4.1`
- run_command: `beacon implement team-run "beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.1`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.1`
- qa_team_command: `beacon qa team-run "beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure" --project /Users/apple/Developer/Personal/products/beacon --version v1.4.1`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.1`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.4.1/.machine/execution/git-workflow-beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

## Tasks

### ITASK-001 — FR-001 Deep artifact contract
- status: `completed`
- mapped_ac_ids: AC-010, AC-001, AC-002
- mapped_test_ids: TC-US004-001, TC-US001-001, TC-029, TC-030, TC-031, TC-032, TC-033, TC-034, TC-035, TC-036, TC-037, TC-US001-002
- mapped_scenario_ids: SC-001, SC-002, SC-014
- mapped_qa_case_ids: TC-US001-001, TC-US001-002, TC-US004-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-002 — FR-002 Trigger and skip contract
- status: `completed`
- mapped_ac_ids: AC-005, AC-003
- mapped_test_ids: TC-US002-002, TC-US001-003
- mapped_scenario_ids: SC-003, SC-005, SC-006, SC-007, SC-008, SC-009
- mapped_qa_case_ids: TC-US001-003, TC-US002-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-003 — FR-003 Delta-first contract
- status: `completed`
- mapped_ac_ids: AC-017
- mapped_test_ids: TC-US006-001
- mapped_scenario_ids: SC-021
- mapped_qa_case_ids: TC-US006-001
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-004 — FR-004 Truth governance contract
- status: `completed`
- mapped_ac_ids: AC-023
- mapped_test_ids: TC-US008-001
- mapped_scenario_ids: SC-027
- mapped_qa_case_ids: TC-US008-001
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-005 — FR-005 Release supplement contract
- status: `completed`
- mapped_ac_ids: AC-020
- mapped_test_ids: TC-US007-001
- mapped_scenario_ids: SC-024
- mapped_qa_case_ids: TC-US007-001
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-006 — FR-006 Deep loop orchestration contract
- status: `completed`
- mapped_ac_ids: AC-007, AC-006
- mapped_test_ids: TC-US003-001, TC-US002-003
- mapped_scenario_ids: SC-010, SC-011
- mapped_qa_case_ids: TC-US002-003, TC-US003-001
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-007 — FR-007 One-pass convergence contract
- status: `completed`
- mapped_ac_ids: AC-008, AC-009
- mapped_test_ids: TC-US003-002, TC-US003-003
- mapped_scenario_ids: SC-012, SC-013
- mapped_qa_case_ids: TC-US003-002, TC-US003-003
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-008 — FR-008 Cross-stage delta routing contract
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TC-US005-001
- mapped_scenario_ids: SC-017
- mapped_qa_case_ids: TC-US005-001
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-009 — FR-009 Human support skill contract
- status: `completed`
- mapped_ac_ids: AC-018, AC-026, AC-027, AC-011, AC-012
- mapped_test_ids: TC-US006-002, TC-US009-001, TC-US009-002, TC-US004-002, TC-US004-003
- mapped_scenario_ids: SC-015, SC-016, SC-022, SC-030, SC-031
- mapped_qa_case_ids: TC-US004-002, TC-US004-003, TC-US006-002, TC-US009-001, TC-US009-002
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending

### ITASK-010 — FR-010 Deep QA-preflight contract
- status: `completed`
- mapped_ac_ids: AC-019, AC-014, AC-004, AC-015, AC-016, AC-021, AC-022, AC-024, AC-025, AC-028
- mapped_test_ids: TC-US006-003, TC-US005-002, TC-US002-001, TC-US005-003, TC-US005-004, TC-US007-002, TC-US007-003, TC-US008-002, TC-US008-003, TC-US009-003
- mapped_scenario_ids: SC-004, SC-018, SC-019, SC-020, SC-023, SC-025, SC-026, SC-028, SC-029, SC-032
- mapped_qa_case_ids: TC-US002-001, TC-US005-002, TC-US005-003, TC-US005-004, TC-US006-003, TC-US007-002, TC-US007-003, TC-US008-002, TC-US008-003, TC-US009-003
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: deep_loop_state, not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed, not_started, scanning, modeling, challenging, deriving_delta, routing, verifying, closed, finding_state, candidate | classified | routed | closed | waived | backlog | rejected, candidate, classified, routed, waived, backlog, rejected, delta_state, proposed | accepted | attached_to_test_case | executed_by_qa | closed, proposed, accepted, attached_to_test_case, executed_by_qa, risk_state, open | release_blocking | waived | accepted_backlog | closed, open, release_blocking, accepted_backlog, requirement_package_state, prd_only | three_piece_complete | frozen | implement_pending, prd_only, three_piece_complete, frozen, implement_pending
