# Beacon Implementation Plan

- plan_id: `plan-code2truth-project-intake-r2`
- feature: `code2truth-project-intake`
- version: `v1.5.2`
- revision_id: `R2`
- baseline_hash: `sha256:0ae70798c1f77d0db999d18f8931713d19e13fdbabc359172216798fc8abd071`
- delivery_baseline_id: `impl-delivery-baseline-v1.5.2-code2truth-project-intake-R2`
- delivery_baseline_source_hash: `sha256:ee503e159c6e4d56a884ecb92821e967b26e33587bdf9ae8fc4960ce741ba2a6`
- plan_hash: `sha256:f7a009a1c246e161dcc587d0ef493a5573a2082f3a8ba380d9e40cf131b7f99a`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.5.2/features/code2truth-project-intake/truth.md`
- prd: `docs/beacon/v1.5.2/features/code2truth-project-intake/truth.md`
- test_case: `docs/beacon/v1.5.2/features/code2truth-project-intake/tests.md`
- truth: `docs/beacon/v1.5.2/features/code2truth-project-intake/truth.md`
- tests: `docs/beacon/v1.5.2/features/code2truth-project-intake/tests.md`
- tasks: `docs/beacon/v1.5.2/features/code2truth-project-intake/tasks.md`
- evidence: `docs/beacon/v1.5.2/features/code2truth-project-intake/evidence.md`
- source_of_truth_root: `docs/beacon/v1.5.2/features/code2truth-project-intake`
- revision_delta: `docs/beacon/v1.5.2/.machine/execution/revision-delta-code2truth-project-intake.json`
- story_scenario_map: `docs/beacon/v1.5.2/.machine/qa/code2truth-project-intake.story-scenario-map.json`
- research_projection: `docs/beacon/v1.5.2/.machine/user-story/code2truth-project-intake.json`
- architecture_blueprint: `docs/beacon/v1.5.2/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "code2truth-project-intake" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.5.2`
- run_command: `beacon implement team-run "code2truth-project-intake" --project /Users/apple/Developer/Personal/products/beacon --version v1.5.2`
- dev_run_command: `beacon implement dev-run "code2truth-project-intake" --project /Users/apple/Developer/Personal/products/beacon --version v1.5.2`
- qa_team_command: `beacon qa team-run "code2truth-project-intake" --project /Users/apple/Developer/Personal/products/beacon --version v1.5.2`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.5.2`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.5.2/.machine/execution/git-workflow-code2truth-project-intake.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.5.2/research/code2truth-project-intake.md`
- source_artifact: `docs/beacon/v1.5.2/.machine/user-story/code2truth-project-intake.json`
- section_count: `0`

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.5.2/.machine/execution/revision-delta-code2truth-project-intake.json`

## Tasks

### ITASK-001 — TASK-001 Define the source inventory model for code, docs, skills, tests, CLI behavior, Beacon source maps, and provider artifacts.
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Define provider authority boundaries for `qi-dev-understand-anything` / Understand-Anything and similar code-map tools.
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Define candidate truth reconstruction with source refs, confidence, and ambiguity markers.
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Require user confirmation before candidate truth can be promoted into package-authoritative truth.
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Freeze package authority through `truth-map` selected `truth.md`, `tests.md`, `tasks.md`, and `evidence.md`.
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-006 Define implement no-op/evidence-only admission when existing code satisfies frozen truth.
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — TASK-007 Define QA coverage for package truth, provider evidence, governance verify, and current behavior satisfaction.
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008, TC-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — TASK-008 Preserve fail-closed routing for ambiguous, stale, conflicting, low-confidence, or unproven behavior.
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009, TC-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — TASK-009 Support a bounded pilot on an existing project or skill pack before whole-repo adoption.
- status: `completed`
- mapped_ac_ids: AC-010, AC-007
- mapped_test_ids: TEST-010, TEST-007, TC-007, TC-010
- mapped_scenario_ids: SC-007, SC-010
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
