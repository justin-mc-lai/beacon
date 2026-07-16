# Beacon Implementation Plan

- plan_id: `plan-beacon-git-scope-graph-v167-r1`
- feature: `beacon-git-scope-graph-v167`
- version: `v1.6.7`
- revision_id: `R1`
- baseline_hash: `sha256:fe34b05343f65800f13d31a9b86a96ab121b47d40dff4a572c4fe59916f2831c`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.7-beacon-git-scope-graph-v167-R1`
- delivery_baseline_source_hash: `sha256:c915487ff30472ac7b3e3991714df7499ec5d5e8be7cfc0b5deffdcdd9d36526`
- plan_hash: `sha256:b08f3d61da5bb7db406e0b1236de2b15b0810b6f287e0ef97f6c729dab141c54`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/truth.md`
- prd: `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/truth.md`
- test_case: `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/tests.md`
- truth: `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/truth.md`
- tests: `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/tests.md`
- tasks: `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/tasks.md`
- evidence: `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167`
- revision_delta: `docs/beacon/v1.6.7/.machine/execution/revision-delta-beacon-git-scope-graph-v167.json`
- story_scenario_map: `docs/beacon/v1.6.7/.machine/qa/beacon-git-scope-graph-v167.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.7/.machine/user-story/beacon-git-scope-graph-v167.json`
- architecture_blueprint: `docs/beacon/v1.6.7/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-git-scope-graph-v167" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.7`
- run_command: `beacon implement team-run "beacon-git-scope-graph-v167" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.7`
- dev_run_command: `beacon implement dev-run "beacon-git-scope-graph-v167" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.7`
- qa_team_command: `beacon qa team-run "beacon-git-scope-graph-v167" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.7`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.7/beacon-git-scope-graph-v167`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.7/.machine/execution/git-workflow-beacon-git-scope-graph-v167.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.7/research/beacon-git-scope-graph-v167.md`
- source_artifact: `docs/beacon/v1.6.7/.machine/user-story/beacon-git-scope-graph-v167.json`
- section_count: `0`

## Revision Delta
- revision_id: `R1`
- source_revision_id: `greenfield`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.6.7/.machine/execution/revision-delta-beacon-git-scope-graph-v167.json`

## Tasks

### ITASK-001 — TASK-001 Materialize feature package
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

### ITASK-002 — TASK-002 Validate frontmatter and acceptance criteria
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Validate checkbox ledger without gate bypass
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Validate evidence authority labels
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Run canonical implement and QA gates separately
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
