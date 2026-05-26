# Beacon Implementation Plan

- plan_id: `plan-qa-browser-memory-and-skill-evolution-advisory-loop-r2`
- feature: `qa-browser-memory-and-skill-evolution-advisory-loop`
- version: `v1.4.10`
- revision_id: `R2`
- baseline_hash: `sha256:69ba2cdebe7fe6a468951d64a6f0914ed079ef41e815cb784ed7a9d8299b4673`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.10-qa-browser-memory-and-skill-evolution-advisory-loop-R2`
- delivery_baseline_source_hash: `sha256:1dd4c03286c70e00ffae1111ade73f1a713c34eeb6319089a5220dc66a78bc8c`
- plan_hash: `sha256:64d03f7e39e797fc60b225b5176606cf06f0698c144399b039965ea88661d41c`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.10/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.md`
- prd: `docs/beacon/v1.4.10/prd/qa-browser-memory-and-skill-evolution-advisory-loop.md`
- test_case: `docs/beacon/v1.4.10/qa/test-cases/qa-browser-memory-and-skill-evolution-advisory-loop.md`
- revision_delta: `docs/beacon/v1.4.10/.machine/execution/revision-delta-qa-browser-memory-and-skill-evolution-advisory-loop.json`
- ac_matrix: `docs/beacon/v1.4.10/.machine/qa/qa-browser-memory-and-skill-evolution-advisory-loop.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.10/.machine/qa/qa-browser-memory-and-skill-evolution-advisory-loop.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.10/.machine/qa/qa-browser-memory-and-skill-evolution-advisory-loop.qa9-matrix.json`
- research_projection: `docs/beacon/v1.4.10/.machine/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.json`
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
- plan_command: `beacon implement team-plan "qa-browser-memory-and-skill-evolution-advisory-loop" --project-root . --version v1.4.10`
- run_command: `beacon implement team-run "qa-browser-memory-and-skill-evolution-advisory-loop" --project . --version v1.4.10`
- dev_run_command: `beacon implement dev-run "qa-browser-memory-and-skill-evolution-advisory-loop" --project . --version v1.4.10`
- qa_team_command: `beacon qa team-run "qa-browser-memory-and-skill-evolution-advisory-loop" --project . --version v1.4.10`
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
- git_workflow_ref: `docs/beacon/v1.4.10/.machine/execution/git-workflow-qa-browser-memory-and-skill-evolution-advisory-loop.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:docs/beacon/v1.4.10/research/qa-browser-memory-and-skill-evolution-advisory-loop.md`
- source_artifact: `docs/beacon/v1.4.10/.machine/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.json`
- section_count: `0`

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.4.10/.machine/execution/revision-delta-qa-browser-memory-and-skill-evolution-advisory-loop.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-QA-MEM-001, TC-QA-MEM-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-QA-MEM-001, TC-QA-MEM-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-005, AC-011, AC-003
- mapped_test_ids: TC-QA-MEM-005, TC-QA-MEM-011, TC-QA-MEM-003
- mapped_scenario_ids: SC-003, SC-005
- mapped_qa_case_ids: TC-QA-MEM-003, TC-QA-MEM-005, TC-QA-MEM-011
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-006, AC-004
- mapped_test_ids: TC-QA-MEM-006, TC-QA-MEM-004
- mapped_scenario_ids: SC-004, SC-006
- mapped_qa_case_ids: TC-QA-MEM-004, TC-QA-MEM-006
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-007, AC-008
- mapped_test_ids: TC-QA-MEM-007, TC-QA-MEM-008
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: TC-QA-MEM-007, TC-QA-MEM-008
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: AC-010, AC-012, AC-009
- mapped_test_ids: TC-QA-MEM-010, TC-QA-MEM-012, TC-QA-MEM-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: TC-QA-MEM-009, TC-QA-MEM-010, TC-QA-MEM-012
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

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
- diagram_review_gates: -

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
- diagram_review_gates: -

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
- diagram_review_gates: -

### ITASK-009 — FR-009 AC-009
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — FR-010 AC-010
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — FR-011 AC-011
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — FR-012 AC-012
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
