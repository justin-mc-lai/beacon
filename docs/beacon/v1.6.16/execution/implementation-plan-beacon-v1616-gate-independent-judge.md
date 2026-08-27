# Beacon Implementation Plan

- plan_id: `plan-beacon-v1616-gate-independent-judge-r1`
- feature: `beacon-v1616-gate-independent-judge`
- version: `v1.6.16`
- revision_id: `R1`
- baseline_hash: `sha256:ed1f42af975e3d66603bfc22bb7ce245b225d182f783c89aa49da1b3caef05f2`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.16-beacon-v1616-gate-independent-judge-R1`
- delivery_baseline_source_hash: `sha256:67494e2cc77ec874c148bb23b386f4ff3fc89952b5c7c77308a1d0a358c669c1`
- plan_hash: `sha256:7b35a77bdbe7f40788bd39590bbdd670d6b9357bb46cddcd28505d7d32630940`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/truth.md`
- prd: `docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/truth.md`
- test_case: `docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/tests.md`
- truth: `docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/truth.md`
- tests: `docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/tests.md`
- tasks: `docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/tasks.md`
- evidence: `docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge`
- ac_matrix: `docs/beacon/v1.6.16/.machine/qa/beacon-v1616-gate-independent-judge.ac-test-matrix.json`
- research_projection: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-gate-independent-judge.json`
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
- plan_command: `beacon implement team-plan "beacon-v1616-gate-independent-judge" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- run_command: `beacon implement team-run "beacon-v1616-gate-independent-judge" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- dev_run_command: `beacon implement dev-run "beacon-v1616-gate-independent-judge" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- qa_team_command: `beacon qa team-run "beacon-v1616-gate-independent-judge" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.16/beacon-v1616-gate-independent-judge`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.16/.machine/execution/git-workflow-beacon-v1616-gate-independent-judge.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.16/research/beacon-v1616-gate-independent-judge.md`
- source_artifact: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-gate-independent-judge.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: computed 阶段：coverage_rate 等关键 gate 值可由独立脚本重算（独立于系统判定逻辑）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-001.json`
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

### ITASK-002 — TASK-002 Implement AC-002: compared 阶段：独立判定与系统判定比对：一致 → 标记可信；不一致 → 暴露偏差。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-002.json`
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

### ITASK-003 — TASK-003 Implement AC-003: flagged 阶段：偏差记录可审计（gate/系统值/独立值/diff）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-003.json`
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

### ITASK-004 — TASK-004 Implement AC-004: verified 判定：独立裁判不改变 gate 业务规则，不判 pass/fail，只核验系统值可信度。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-004.json`
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

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/QA-MATRIX.json`
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
