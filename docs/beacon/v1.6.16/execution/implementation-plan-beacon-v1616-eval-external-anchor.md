# Beacon Implementation Plan

- plan_id: `plan-beacon-v1616-eval-external-anchor-r1`
- feature: `beacon-v1616-eval-external-anchor`
- version: `v1.6.16`
- revision_id: `R1`
- baseline_hash: `sha256:121dbeffd2547af679c8f1f593670ed0992bdf1b2602257c126f707b2bd0443a`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.16-beacon-v1616-eval-external-anchor-R1`
- delivery_baseline_source_hash: `sha256:f31ef3426c33953b9901cfd7720d6eacc9d2681685bb7aede24e4d701080bfd9`
- plan_hash: `sha256:3a47350203fdb6e7fda9c0598c0387a4dfd38ed10d857d94e9b9f639784de49a`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/truth.md`
- prd: `docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/truth.md`
- test_case: `docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/tests.md`
- truth: `docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/truth.md`
- tests: `docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/tests.md`
- tasks: `docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/tasks.md`
- evidence: `docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor`
- ac_matrix: `docs/beacon/v1.6.16/.machine/qa/beacon-v1616-eval-external-anchor.ac-test-matrix.json`
- research_projection: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-eval-external-anchor.json`
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
- plan_command: `beacon implement team-plan "beacon-v1616-eval-external-anchor" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- run_command: `beacon implement team-run "beacon-v1616-eval-external-anchor" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- dev_run_command: `beacon implement dev-run "beacon-v1616-eval-external-anchor" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- qa_team_command: `beacon qa team-run "beacon-v1616-eval-external-anchor" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.16/beacon-v1616-eval-external-anchor`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.16/.machine/execution/git-workflow-beacon-v1616-eval-external-anchor.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.16/research/beacon-v1616-eval-external-anchor.md`
- source_artifact: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-eval-external-anchor.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: collected 阶段：benchmark 案例集引入外部来源案例（真实失败案例/社区标准），不再全内置。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-001.json`
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

### ITASK-002 — TASK-002 Implement AC-002: verified 阶段：每个外部案例带 source_ref，伪称来源被拒（可追溯来源），伪称外部来源的案例被拒。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-002.json`
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

### ITASK-003 — TASK-003 Implement AC-003: executed 阶段：外部案例可被 benchmark 执行（prompt + expected_route 完整）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-003.json`
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

### ITASK-004 — TASK-004 Implement AC-004: registered 兼容：系统内置案例保留（回归兼容），外部案例为增量。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-004.json`
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

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/QA-MATRIX.json`
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
