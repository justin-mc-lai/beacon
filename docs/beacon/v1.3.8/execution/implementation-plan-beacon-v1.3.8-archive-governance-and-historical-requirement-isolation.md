# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-r2`
- feature: `Beacon v1.3.8 archive governance and historical requirement isolation`
- version: `v1.3.8`
- revision_id: `R2`
- baseline_hash: `sha256:13f615233cc8ee664a2af6183c0028f72771f5bd25c9e21201ce6184cb499ed3`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.8-beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-R2`
- delivery_baseline_source_hash: `sha256:c67925f85ec3fff974729b80e6fa96854627a5e47542a62a887690cf4b1a89b3`
- plan_hash: `sha256:6d92c964d3474c549986c5582b4e94bbd39f558364ae7a5d6b916aec77409ed0`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- prd: `docs/beacon/v1.3.8/prd/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- test_case: `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- ac_matrix: `docs/beacon/v1.3.8/.machine/qa/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.3.8/.machine/qa/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.3.8/.machine/qa/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.qa9-matrix.json`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "Beacon v1.3.8 archive governance and historical requirement isolation" --project-root . --version v1.3.8`
- run_command: `beacon implement team-run "Beacon v1.3.8 archive governance and historical requirement isolation" --project . --version v1.3.8`
- dev_run_command: `beacon implement dev-run "Beacon v1.3.8 archive governance and historical requirement isolation" --project . --version v1.3.8`
- qa_team_command: `beacon qa team-run "Beacon v1.3.8 archive governance and historical requirement isolation" --project . --version v1.3.8`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.8`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.8/.machine/execution/git-workflow-beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: ownership, eligibility, qa, relation, visibility, status
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ownership, eligibility, qa, relation, visibility, status
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: ownership, eligibility, qa, relation, visibility, status

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-002, TC-006, TC-011, TC-007, TC-012
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, SC-007, SC-008, SC-009, SC-010, SC-011, SC-012, SC-013, SC-014, SC-015, SC-016, SC-017, SC-018, SC-019, SC-020, SC-021, SC-022, SC-023, SC-024, SC-025, SC-026, SC-027, SC-028, SC-029, SC-030
- mapped_qa_case_ids: TC-001, TC-002, TC-006, TC-007, TC-011, TC-012
- depends_on: -
- target_modules: -
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ownership, eligibility, qa, relation, visibility, status

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-004, AC-003
- mapped_test_ids: TC-004, TC-003, TC-008, TC-013, TC-009
- mapped_scenario_ids: SC-031, SC-032, SC-033, SC-034, SC-035, SC-036, SC-037, SC-038, SC-039, SC-040, SC-041, SC-042, SC-043, SC-044, SC-045, SC-046, SC-047, SC-048, SC-049, SC-050, SC-051, SC-052, SC-053, SC-054, SC-055
- mapped_qa_case_ids: TC-003, TC-004, TC-008, TC-009, TC-013
- depends_on: ITASK-001
- target_modules: -
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ownership, eligibility, qa, relation, visibility, status

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-005, TC-010
- mapped_scenario_ids: SC-056, SC-057, SC-058, SC-059, SC-060, SC-061, SC-062, SC-063, SC-064, SC-065
- mapped_qa_case_ids: TC-005, TC-010
- depends_on: ITASK-002
- target_modules: -
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ownership, eligibility, qa, relation, visibility, status

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- target_modules: -
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ownership, eligibility, qa, relation, visibility, status

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- target_modules: -
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ownership, eligibility, qa, relation, visibility, status
