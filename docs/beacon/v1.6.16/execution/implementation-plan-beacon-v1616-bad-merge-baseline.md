# Beacon Implementation Plan

- plan_id: `plan-beacon-v1616-bad-merge-baseline-r1`
- feature: `beacon-v1616-bad-merge-baseline`
- version: `v1.6.16`
- revision_id: `R1`
- baseline_hash: `sha256:f4a1c3af156216875d5cc73f4b7097a9a14fc85027055e43900b559a83ca101d`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.16-beacon-v1616-bad-merge-baseline-R1`
- delivery_baseline_source_hash: `sha256:30426a865fcc26ddc63a5b8b4c1fc0fa7eebf572933168212973c3627b07ad2a`
- plan_hash: `sha256:ca948d8ffc9023cbc98a3ee5a910887224fb2da380d467ea54ce51a6810d39a4`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/truth.md`
- prd: `docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/truth.md`
- test_case: `docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/tests.md`
- truth: `docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/truth.md`
- tests: `docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/tests.md`
- tasks: `docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/tasks.md`
- evidence: `docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline`
- ac_matrix: `docs/beacon/v1.6.16/.machine/qa/beacon-v1616-bad-merge-baseline.ac-test-matrix.json`
- research_projection: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-bad-merge-baseline.json`
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
- plan_command: `beacon implement team-plan "beacon-v1616-bad-merge-baseline" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- run_command: `beacon implement team-run "beacon-v1616-bad-merge-baseline" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- dev_run_command: `beacon implement dev-run "beacon-v1616-bad-merge-baseline" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- qa_team_command: `beacon qa team-run "beacon-v1616-bad-merge-baseline" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.16/beacon-v1616-bad-merge-baseline`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.16/.machine/execution/git-workflow-beacon-v1616-bad-merge-baseline.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.16/research/beacon-v1616-bad-merge-baseline.md`
- source_artifact: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-bad-merge-baseline.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: collected 阶段：统计 v1.6.15 以来合并到 main 的提交数及 revert 数（git 分析）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-001.json`
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

### ITASK-002 — TASK-002 Implement AC-002: computed 阶段：计算 bad-merge 率（revert 数 / 合并数，按时间窗）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-002.json`
- status: `planned`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Implement AC-003: reported 阶段：产出可对比基线报告（合并数/revert 数/比率/时间窗/置信度）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-003.json`
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

### ITASK-004 — TASK-004 Implement AC-004: warned 判定：统计不改变自动合入行为，数据不足标低置信度；数据不足时标低置信度不硬算。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-004.json`
- status: `planned`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004, TC-ILLEGAL
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/QA-MATRIX.json`
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
