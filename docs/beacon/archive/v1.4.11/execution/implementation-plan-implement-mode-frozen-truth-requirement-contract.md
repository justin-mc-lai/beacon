# Beacon Implementation Plan

- plan_id: `plan-implement-mode-frozen-truth-requirement-contract-r2`
- feature: `implement-mode-frozen-truth-requirement-contract`
- version: `v1.4.11`
- revision_id: `R2`
- baseline_hash: `sha256:2a9676d7bcd003a3b1df14f9a82e073ec5f2fd1b8f14aef2ca85bd872c021ba8`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.11-implement-mode-frozen-truth-requirement-contract-R2`
- delivery_baseline_source_hash: `sha256:8b1c718cf2b1bee08e142705be17f89309acfce451a8e7887dc30f078a5c42b7`
- plan_hash: `sha256:1c1c7879097012132d9b5374c999ce8afdeb8955faf24f78bed3bfc4620b81b8`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.11/user-story/implement-mode-frozen-truth-requirement-contract.md`
- prd: `docs/beacon/archive/v1.4.11/prd/implement-mode-frozen-truth-requirement-contract.md`
- test_case: `docs/beacon/archive/v1.4.11/qa/test-cases/implement-mode-frozen-truth-requirement-contract.md`
- revision_delta: `docs/beacon/archive/v1.4.11/.machine/execution/revision-delta-implement-mode-frozen-truth-requirement-contract.json`
- ac_matrix: `docs/beacon/archive/v1.4.11/.machine/qa/implement-mode-frozen-truth-requirement-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.11/.machine/qa/implement-mode-frozen-truth-requirement-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.11/.machine/qa/implement-mode-frozen-truth-requirement-contract.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.11/.machine/user-story/implement-mode-frozen-truth-requirement-contract.json`
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
- plan_command: `beacon implement team-plan "implement-mode-frozen-truth-requirement-contract" --project-root . --version v1.4.11`
- run_command: `beacon implement team-run "implement-mode-frozen-truth-requirement-contract" --project . --version v1.4.11`
- dev_run_command: `beacon implement dev-run "implement-mode-frozen-truth-requirement-contract" --project . --version v1.4.11`
- qa_team_command: `beacon qa team-run "implement-mode-frozen-truth-requirement-contract" --project . --version v1.4.11`
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
- git_workflow_ref: `docs/beacon/archive/v1.4.11/.machine/execution/git-workflow-implement-mode-frozen-truth-requirement-contract.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.11/research/implement-mode-frozen-truth-requirement-contract.md`
- source_artifact: `docs/beacon/archive/v1.4.11/.machine/user-story/implement-mode-frozen-truth-requirement-contract.json`
- section_count: `2`
- architecture: `build_default_task_prompt` is the correct low-risk injection point because all modes share the default task prompt. / `PRODUCT.md` and `DESIGN.md` are project-level truth inputs when present. / PRD, user-story, and test-case files remain frozen requirement truth.
- decision_priority: Global Beacon boundaries. / Frozen PRD/user-story/test-case requirement truth. / Existing project-level `PRODUCT.md` and `DESIGN.md`.

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `True`
- revision_delta_ref: `docs/beacon/archive/v1.4.11/.machine/execution/revision-delta-implement-mode-frozen-truth-requirement-contract.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-IMPL-TRUTH-001, TC-IMPL-TRUTH-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-IMPL-TRUTH-001, TC-IMPL-TRUTH-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-003, AC-006, AC-005
- mapped_test_ids: TC-IMPL-TRUTH-003, TC-IMPL-TRUTH-006, TC-IMPL-TRUTH-005
- mapped_scenario_ids: SC-003, SC-005, SC-006
- mapped_qa_case_ids: TC-IMPL-TRUTH-003, TC-IMPL-TRUTH-005, TC-IMPL-TRUTH-006
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-007, AC-004
- mapped_test_ids: TC-IMPL-TRUTH-007, TC-IMPL-TRUTH-004
- mapped_scenario_ids: SC-004, SC-007
- mapped_qa_case_ids: TC-IMPL-TRUTH-004, TC-IMPL-TRUTH-007
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TC-IMPL-TRUTH-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-IMPL-TRUTH-009
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

### ITASK-005 — FR-005 AC-005, AC-006, AC-007
- status: `completed`
- mapped_ac_ids: AC-010, AC-008
- mapped_test_ids: TC-IMPL-TRUTH-010, TC-IMPL-TRUTH-008
- mapped_scenario_ids: SC-008, SC-010
- mapped_qa_case_ids: TC-IMPL-TRUTH-008, TC-IMPL-TRUTH-010
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

### ITASK-006 — FR-006 AC-008
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

### ITASK-007 — FR-007 AC-009
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

### ITASK-008 — FR-008 AC-010
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation

### ITASK-009 — Cleanup superseded surfaces from R1
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: -
- reference_only_services: -
- target_modules: -
- diagram_review_gates: -
- required_cleanup: `True`
- source_revision_id: `R1`
- revision_delta_ref: `docs/beacon/archive/v1.4.11/.machine/execution/revision-delta-implement-mode-frozen-truth-requirement-contract.json`
- cleanup_surface_labels: AC-001: Acceptance criteria TBD
