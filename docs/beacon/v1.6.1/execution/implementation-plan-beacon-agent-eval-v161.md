# Beacon Implementation Plan

- plan_id: `plan-beacon-agent-eval-v161-r3`
- feature: `beacon-agent-eval-v161`
- version: `v1.6.1`
- revision_id: `R3`
- baseline_hash: `sha256:b7d4ed19a7a31629eb448182c258e54572e145ae943051926645553f96406bdb`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.1-beacon-agent-eval-v161-R3`
- delivery_baseline_source_hash: `sha256:3b93d943eb68285421eedc632c44ef90cdae7a7e9077db30623223485fb23f32`
- plan_hash: `sha256:665e81dc2ff0647c273f0372cf099b49894ed207a1536be9c1efbf6aacc88259`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.1/features/beacon-agent-eval-v161/truth.md`
- prd: `docs/beacon/v1.6.1/features/beacon-agent-eval-v161/truth.md`
- test_case: `docs/beacon/v1.6.1/features/beacon-agent-eval-v161/tests.md`
- truth: `docs/beacon/v1.6.1/features/beacon-agent-eval-v161/truth.md`
- tests: `docs/beacon/v1.6.1/features/beacon-agent-eval-v161/tests.md`
- tasks: `docs/beacon/v1.6.1/features/beacon-agent-eval-v161/tasks.md`
- evidence: `docs/beacon/v1.6.1/features/beacon-agent-eval-v161/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.1/features/beacon-agent-eval-v161`
- revision_delta: `docs/beacon/v1.6.1/.machine/execution/revision-delta-beacon-agent-eval-v161.json`
- ac_matrix: `docs/beacon/v1.6.1/.machine/qa/beacon-agent-eval-v161.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.6.1/.machine/qa/beacon-agent-eval-v161.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.6.1/.machine/qa/beacon-agent-eval-v161.qa9-matrix.json`
- research_projection: `docs/beacon/v1.6.1/.machine/user-story/beacon-agent-eval-v161.json`
- architecture_blueprint: `docs/beacon/v1.6.1/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-agent-eval-v161" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.1`
- run_command: `beacon implement team-run "beacon-agent-eval-v161" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.1`
- dev_run_command: `beacon implement dev-run "beacon-agent-eval-v161" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.1`
- qa_team_command: `beacon qa team-run "beacon-agent-eval-v161" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.1`
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
- git_workflow_ref: `docs/beacon/v1.6.1/.machine/execution/git-workflow-beacon-agent-eval-v161.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.1/research/beacon-agent-eval-v161.md`
- source_artifact: `docs/beacon/v1.6.1/.machine/user-story/beacon-agent-eval-v161.json`
- section_count: `0`

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.6.1/.machine/execution/revision-delta-beacon-agent-eval-v161.json`

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
