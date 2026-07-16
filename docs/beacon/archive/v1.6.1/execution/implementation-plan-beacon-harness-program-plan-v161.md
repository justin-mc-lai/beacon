# Beacon Implementation Plan

- plan_id: `plan-beacon-harness-program-plan-v161-r2`
- feature: `beacon-harness-program-plan-v161`
- version: `v1.6.1`
- revision_id: `R2`
- baseline_hash: `sha256:18bbd908a8395b2a13baef2b2d5fe3e593f6976331c79ba3467767d7f22b8aa5`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.1-beacon-harness-program-plan-v161-R2`
- delivery_baseline_source_hash: `sha256:bf743b997217a643c175b59053322241f752812a2de753f538d11b7216ebffe3`
- plan_hash: `sha256:3b71994aed9c31df1fb22c7010aac5e99ce448d1af123410cbe8392213551caa`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md`
- prd: `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md`
- test_case: `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/tests.md`
- truth: `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md`
- tests: `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/tests.md`
- tasks: `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/tasks.md`
- evidence: `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161`
- revision_delta: `docs/beacon/archive/v1.6.1/.machine/execution/revision-delta-beacon-harness-program-plan-v161.json`
- ac_matrix: `docs/beacon/archive/v1.6.1/.machine/qa/beacon-harness-program-plan-v161.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.6.1/.machine/qa/beacon-harness-program-plan-v161.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.6.1/.machine/qa/beacon-harness-program-plan-v161.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.6.1/.machine/user-story/beacon-harness-program-plan-v161.json`
- architecture_blueprint: `docs/beacon/archive/v1.6.1/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-harness-program-plan-v161" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.1`
- run_command: `beacon implement team-run "beacon-harness-program-plan-v161" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.1`
- dev_run_command: `beacon implement dev-run "beacon-harness-program-plan-v161" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.1`
- qa_team_command: `beacon qa team-run "beacon-harness-program-plan-v161" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.1`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `pre-main`
- branch_prefix: `pre-main/`
- base_branch: `pre-main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.6.1/.machine/execution/git-workflow-beacon-harness-program-plan-v161.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.1/research/beacon-harness-program-plan-v161.md`
- source_artifact: `docs/beacon/archive/v1.6.1/.machine/user-story/beacon-harness-program-plan-v161.json`
- section_count: `0`

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `True`
- revision_delta_ref: `docs/beacon/archive/v1.6.1/.machine/execution/revision-delta-beacon-harness-program-plan-v161.json`

## Tasks

### ITASK-001 — AC-001 Acceptance criteria TBD
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — Cleanup superseded surfaces from R1
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: -
- reference_only_services: -
- target_modules: -
- diagram_review_gates: -
- required_cleanup: `True`
- source_revision_id: `R1`
- revision_delta_ref: `docs/beacon/archive/v1.6.1/.machine/execution/revision-delta-beacon-harness-program-plan-v161.json`
- cleanup_surface_labels: AC-001: Acceptance criteria TBD
