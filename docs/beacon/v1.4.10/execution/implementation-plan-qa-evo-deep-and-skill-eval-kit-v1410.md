# Beacon Implementation Plan

- plan_id: `plan-qa-evo-deep-and-skill-eval-kit-v1410-r4`
- feature: `qa-evo-deep-and-skill-eval-kit-v1410`
- version: `v1.4.10`
- revision_id: `R4`
- baseline_hash: `sha256:11964177ae6f35febbd97f8809910c28f7ccc4ce94e1f8a491795974373ce536`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.10-qa-evo-deep-and-skill-eval-kit-v1410-R4`
- delivery_baseline_source_hash: `sha256:4dd31bd93e3edc3a3457763e17f3cdffebd6b6a8afd273582efca8b053a12446`
- plan_hash: `sha256:a4649734f8562d971da415d239f8986fc43439c2518fd34ee1feb29749ae1620`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md`
- prd: `docs/beacon/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md`
- test_case: `docs/beacon/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md`
- revision_delta: `docs/beacon/v1.4.10/.machine/execution/revision-delta-qa-evo-deep-and-skill-eval-kit-v1410.json`
- ac_matrix: `docs/beacon/v1.4.10/.machine/qa/qa-evo-deep-and-skill-eval-kit-v1410.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.10/.machine/qa/qa-evo-deep-and-skill-eval-kit-v1410.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.10/.machine/qa/qa-evo-deep-and-skill-eval-kit-v1410.qa9-matrix.json`
- research_projection: `docs/beacon/v1.4.10/.machine/user-story/qa-evo-deep-and-skill-eval-kit-v1410.json`
- architecture_blueprint: `docs/beacon/v1.4.10/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "qa-evo-deep-and-skill-eval-kit-v1410" --project-root . --version v1.4.10`
- run_command: `beacon implement team-run "qa-evo-deep-and-skill-eval-kit-v1410" --project . --version v1.4.10`
- dev_run_command: `beacon implement dev-run "qa-evo-deep-and-skill-eval-kit-v1410" --project . --version v1.4.10`
- qa_team_command: `beacon qa team-run "qa-evo-deep-and-skill-eval-kit-v1410" --project . --version v1.4.10`
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
- git_workflow_ref: `docs/beacon/v1.4.10/.machine/execution/git-workflow-qa-evo-deep-and-skill-eval-kit-v1410.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

## Research Projection
- present: `True`
- source: `research:docs/beacon/v1.4.10/research/qa-evo-deep-and-skill-eval-kit-v1410.md`
- source_artifact: `docs/beacon/v1.4.10/.machine/user-story/qa-evo-deep-and-skill-eval-kit-v1410.json`
- section_count: `1`
- decision_priority: Markdown requirement truth wins over QA deep output and skill eval evidence. / QA evo-deep produces routeable findings, not release pass verdicts. / QA round memory is advisory influence and must be separated from current evidence.

## Revision Delta
- revision_id: `R4`
- source_revision_id: `R3`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.4.10/.machine/execution/revision-delta-qa-evo-deep-and-skill-eval-kit-v1410.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-QAED-001, TC-QAED-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-QAED-001, TC-QAED-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-007, AC-004, AC-003
- mapped_test_ids: TC-SKEV-003, TC-QAED-004, TC-QAED-003
- mapped_scenario_ids: SC-003, SC-004, SC-007
- mapped_qa_case_ids: TC-QAED-003, TC-QAED-004, TC-SKEV-003
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-008, AC-005, AC-009
- mapped_test_ids: TC-SKEV-004, TC-SKEV-001, TC-QAED-005
- mapped_scenario_ids: SC-005, SC-008, SC-009
- mapped_qa_case_ids: TC-SKEV-001, TC-SKEV-004, TC-QAED-005
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-SKEV-002
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-SKEV-002
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

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
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

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
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

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
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

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
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary

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
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary
