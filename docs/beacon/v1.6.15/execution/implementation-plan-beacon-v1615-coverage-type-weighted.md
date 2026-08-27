# Beacon Implementation Plan

- plan_id: `plan-beacon-v1615-coverage-type-weighted-r1`
- feature: `beacon-v1615-coverage-type-weighted`
- version: `v1.6.15`
- revision_id: `R1`
- baseline_hash: `sha256:ac6c6a2fc162d7d5c9538fd5a2b993c053bd00e8244ccdda3d22c22a4cbddbed`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.15-beacon-v1615-coverage-type-weighted-R1`
- delivery_baseline_source_hash: `sha256:67c23df3b9cba490fd54552d16f7cbaa8c1ec5e9a0f10494cb3386cd11165b10`
- plan_hash: `sha256:537f330c29739f7d8adc2f71450e7e8889eef536c0eafc2f13e518ee855b1bed`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted/truth.md`
- prd: `docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted/truth.md`
- test_case: `docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted/tests.md`
- truth: `docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted/truth.md`
- tests: `docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted/tests.md`
- tasks: `docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted/tasks.md`
- evidence: `docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted`
- research_projection: `docs/beacon/v1.6.15/.machine/user-story/beacon-v1615-coverage-type-weighted.json`
- architecture_blueprint: `docs/beacon/v1.6.15/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1615-coverage-type-weighted" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.15`
- run_command: `beacon implement team-run "beacon-v1615-coverage-type-weighted" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.15`
- dev_run_command: `beacon implement dev-run "beacon-v1615-coverage-type-weighted" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.15`
- qa_team_command: `beacon qa team-run "beacon-v1615-coverage-type-weighted" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.15`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.15/beacon-v1615-coverage-type-weighted`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.15/.machine/execution/git-workflow-beacon-v1615-coverage-type-weighted.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.15/research/beacon-v1615-coverage-type-weighted.md`
- source_artifact: `docs/beacon/v1.6.15/.machine/user-story/beacon-v1615-coverage-type-weighted.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: `coverage_rate` 按类型族加权：required_families 缺一类 → 状态 assessed 时 rate < 1... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-001.json`
- status: `planned`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Implement AC-002: 非浏览器（contract/docs/unit）场景在 weighted 阶段展开类型 family（默认 happy+negative+... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-002.json`
- status: `planned`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Implement AC-003: coverage 输出在 reported 阶段列出 missing_families（缺哪类），供 QA 与自动合入门禁审计。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-003.json`
- status: `planned`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Implement AC-004: 兼容既有 lake：已通过 QA 的 lake 语义不变，仅覆盖计算方式变化（gated 判定更新），不引入新命令面。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-004.json`
- status: `planned`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/QA-MATRIX.json`
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
