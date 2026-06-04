# Beacon Implementation Plan

- plan_id: `plan-beacon-design-human-subskills-closure-contract-r3`
- feature: `beacon-design-human-subskills-closure-contract`
- version: `v1.4.11`
- revision_id: `R3`
- baseline_hash: `sha256:fa3ad06374e85aac1bf14b5da2013a7767bbb4e3a27a60d65326a8c9e96e886c`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.11-beacon-design-human-subskills-closure-contract-R3`
- delivery_baseline_source_hash: `sha256:669dcb0e36c57182404009c2fdc380f68dd2efcedc3ac6575b24567d343aae2f`
- plan_hash: `sha256:d6cce9a3ed4e6b175c09f9274bd280517f7eb7d90ae252e637812652e2c95d63`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.11/user-story/beacon-design-human-subskills-closure-contract.md`
- prd: `docs/beacon/archive/v1.4.11/prd/beacon-design-human-subskills-closure-contract.md`
- test_case: `docs/beacon/archive/v1.4.11/qa/test-cases/beacon-design-human-subskills-closure-contract.md`
- revision_delta: `docs/beacon/archive/v1.4.11/.machine/execution/revision-delta-beacon-design-human-subskills-closure-contract.json`
- ac_matrix: `docs/beacon/archive/v1.4.11/.machine/qa/beacon-design-human-subskills-closure-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.11/.machine/qa/beacon-design-human-subskills-closure-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.11/.machine/qa/beacon-design-human-subskills-closure-contract.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.11/.machine/user-story/beacon-design-human-subskills-closure-contract.json`
- architecture_blueprint: `docs/beacon/archive/v1.4.11/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-design-human-subskills-closure-contract" --project-root . --version v1.4.11`
- run_command: `beacon implement team-run "beacon-design-human-subskills-closure-contract" --project . --version v1.4.11`
- dev_run_command: `beacon implement dev-run "beacon-design-human-subskills-closure-contract" --project . --version v1.4.11`
- qa_team_command: `beacon qa team-run "beacon-design-human-subskills-closure-contract" --project . --version v1.4.11`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.11`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.4.11/.machine/execution/git-workflow-beacon-design-human-subskills-closure-contract.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: beacon design route simplify, beacon-design-simplify/skill.md
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: beacon design route simplify, beacon-design-simplify/skill.md

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.11/research/beacon-design-human-subskills-closure-contract.md`
- source_artifact: `docs/beacon/archive/v1.4.11/.machine/user-story/beacon-design-human-subskills-closure-contract.json`
- section_count: `0`

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.11/.machine/execution/revision-delta-beacon-design-human-subskills-closure-contract.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-DESIGN-SKILL-001, TC-DESIGN-SKILL-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-DESIGN-SKILL-001, TC-DESIGN-SKILL-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-003, AC-012, AC-016, AC-004, AC-010, AC-005, AC-006, AC-007, AC-008, AC-011
- mapped_test_ids: TC-DESIGN-SKILL-003, TC-DESIGN-SKILL-012, TEST-016, TC-DESIGN-SKILL-004, TC-DESIGN-SKILL-010, TC-DESIGN-SKILL-005, TC-DESIGN-SKILL-006, TC-DESIGN-SKILL-007, TC-DESIGN-SKILL-008, TC-DESIGN-SKILL-011
- mapped_scenario_ids: SC-003, SC-004, SC-005, SC-006, SC-007, SC-008, SC-010, SC-011, SC-012
- mapped_qa_case_ids: TC-DESIGN-SKILL-003, TC-DESIGN-SKILL-004, TC-DESIGN-SKILL-005, TC-DESIGN-SKILL-006, TC-DESIGN-SKILL-007, TC-DESIGN-SKILL-008, TC-DESIGN-SKILL-010, TC-DESIGN-SKILL-011, TC-DESIGN-SKILL-012
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-013, AC-017, AC-009, AC-015
- mapped_test_ids: TEST-013, TEST-017, TC-DESIGN-SKILL-009, TEST-015
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-DESIGN-SKILL-009
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-004 — FR-004 AC-004
- status: `planned`
- mapped_ac_ids: AC-014
- mapped_test_ids: TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-005 — FR-005 AC-005
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-006 — FR-006 AC-006
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-007 — FR-007 AC-007
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-008 — FR-008 AC-008
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-009 — FR-009 AC-009
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-010 — FR-010 AC-010
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-011 — FR-011 AC-011
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-012 — FR-012 AC-012
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-013 — FR-001 AC-001
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-014 — FR-002 AC-002
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-015 — FR-003 AC-003
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-016 — FR-004 AC-004
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-017 — FR-005 AC-005
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-018 — FR-006 AC-006
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-019 — FR-007 AC-007
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-018
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-020 — FR-008 AC-008
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-021 — FR-009 AC-009
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-020
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-022 — FR-010 AC-010
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-023 — FR-011 AC-011
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-022
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-024 — FR-012 AC-012
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-023
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-025 — FR-013 AC-013
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-024
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-026 — FR-014 AC-014
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-025
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-027 — FR-015 AC-015
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-026
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-028 — FR-016 AC-016
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-027
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md

### ITASK-029 — FR-017 AC-017
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-028
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: beacon design route simplify, beacon-design-simplify/skill.md
