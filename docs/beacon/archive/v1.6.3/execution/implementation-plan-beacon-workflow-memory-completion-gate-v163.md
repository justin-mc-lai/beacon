# Beacon Implementation Plan

- plan_id: `plan-beacon-workflow-memory-completion-gate-v163-r1`
- feature: `beacon-workflow-memory-completion-gate-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:e5bf0214b93e20207845430f5e9e8edc0c92d4d10dd774598b6e975a21b820bd`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-workflow-memory-completion-gate-v163-R1`
- delivery_baseline_source_hash: `sha256:f239fd946b7cce2fbacba97a9c81fa08e4882ba04a1316e52eac399afe4ba852`
- plan_hash: `sha256:b1fc5e524e00562fef9f895a53df12c0f6c8eefe7cf25459273128a65196fc20`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/truth.md`
- prd: `docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/truth.md`
- test_case: `docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/tests.md`
- truth: `docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/truth.md`
- tests: `docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/tests.md`
- tasks: `docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/tasks.md`
- evidence: `docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163`
- ac_matrix: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-workflow-memory-completion-gate-v163.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-workflow-memory-completion-gate-v163.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-workflow-memory-completion-gate-v163.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-workflow-memory-completion-gate-v163.json`
- architecture_blueprint: `docs/beacon/archive/v1.6.3/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-workflow-memory-completion-gate-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-workflow-memory-completion-gate-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-workflow-memory-completion-gate-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-workflow-memory-completion-gate-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.3`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.6.3/.machine/execution/git-workflow-beacon-workflow-memory-completion-gate-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.3/research/beacon-workflow-memory-completion-gate-v163.md`
- source_artifact: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-workflow-memory-completion-gate-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 `target_run_id=None`（无 run）→ `status: warn / blocked: False`，reason_c...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-WM-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-WM-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 run 存在但无 transaction record → `status: fail / blocked: True`，reason_c...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-WM-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-WM-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 有 run 无 transaction 时 gate check release 对应 issue `blocked: True`（**M...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-WM-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-WM-003
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 真无 run 的 fresh project 不因本修复误 block release gate（**Must**）
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-WM-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-WM-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 `failed_transaction`→fail、`drift`→fail、ok→pass 语义不变（**Must**）
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-WM-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-WM-005
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 `beacon status` 的 `memory_transaction` 在无 run vs 有 run 无 transaction...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-WM-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-WM-006
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 有 run 且 transaction ok 时仍 `status: pass / blocked: False`（**Must**）
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-WM-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: TC-WM-007
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
