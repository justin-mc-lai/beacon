# Beacon Implementation Plan

- plan_id: `plan-beacon-v1616-failure-mode-expansion-r1`
- feature: `beacon-v1616-failure-mode-expansion`
- version: `v1.6.16`
- revision_id: `R1`
- baseline_hash: `sha256:1c158d9e1edf0e5442aa26813c4b9024e5b23b863e6cd3ea8888058c29fa1fb9`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.16-beacon-v1616-failure-mode-expansion-R1`
- delivery_baseline_source_hash: `sha256:8fd562f8d67ece7974d7e7e80dbdf8a8d1aed756fce2c25564b685c0e3476dc9`
- plan_hash: `sha256:6b817b35df59f0ad7d45871e8c706a75712d792e223de4c9733b229acadbdca3`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/truth.md`
- prd: `docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/truth.md`
- test_case: `docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/tests.md`
- truth: `docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/truth.md`
- tests: `docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/tests.md`
- tasks: `docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/tasks.md`
- evidence: `docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion`
- ac_matrix: `docs/beacon/v1.6.16/.machine/qa/beacon-v1616-failure-mode-expansion.ac-test-matrix.json`
- research_projection: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-failure-mode-expansion.json`
- architecture_blueprint: `docs/beacon/v1.6.16/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1616-failure-mode-expansion" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- run_command: `beacon implement team-run "beacon-v1616-failure-mode-expansion" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- dev_run_command: `beacon implement dev-run "beacon-v1616-failure-mode-expansion" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- qa_team_command: `beacon qa team-run "beacon-v1616-failure-mode-expansion" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.16/beacon-v1616-failure-mode-expansion`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.16/.machine/execution/git-workflow-beacon-v1616-failure-mode-expansion.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.16/research/beacon-v1616-failure-mode-expansion.md`
- source_artifact: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-failure-mode-expansion.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: cataloged 阶段：失败模式目录条目 ≥ 20（从 5 扩到 20+）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-001.json`
- status: `planned`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Implement AC-002: verified 阶段：每条条目带 source_ref（v1.6.13-15 真实失败记录）（来自 v1.6.13-15 真实失败记录）... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-002.json`
- status: `planned`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002, TC-ILLEGAL
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Implement AC-003: authored 阶段：每条含完整 rubric（症状/判定/通过/拦截）：症状 / 判定规则 / 通过标准 / 拦截标准。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-003.json`
- status: `planned`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Implement AC-004: cataloged→审查：目录可作为对抗式审查翻车点输入（QA/release 前）。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-004.json`
- status: `planned`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/GATES.json`
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/QA-MATRIX.json`
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
