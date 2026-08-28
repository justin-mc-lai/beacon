# Beacon Implementation Plan

- plan_id: `plan-beacon-v1617-live-benchmark-verify-r1`
- feature: `beacon-v1617-live-benchmark-verify`
- version: `v1.6.17`
- revision_id: `R1`
- baseline_hash: `sha256:6ab08b9d15252d02ba86dfdf2ea61bca895bfffb1f3f93d0aef3870bb9f64cbf`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.17-beacon-v1617-live-benchmark-verify-R1`
- delivery_baseline_source_hash: `sha256:2df51f8a7debc5f9276dbbbd4baf6d770767f07074abfff582b48fb9a6edb71c`
- plan_hash: `sha256:2f996424c5d1d88676594c2b878de132362f6848d0718404d80bfe4056a3d5b7`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/truth.md`
- prd: `docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/truth.md`
- test_case: `docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/tests.md`
- truth: `docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/truth.md`
- tests: `docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/tests.md`
- tasks: `docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/tasks.md`
- evidence: `docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify`
- ac_matrix: `docs/beacon/v1.6.17/.machine/qa/beacon-v1617-live-benchmark-verify.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.6.17/.machine/qa/beacon-v1617-live-benchmark-verify.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.17/.machine/user-story/beacon-v1617-live-benchmark-verify.json`
- architecture_blueprint: `docs/beacon/v1.6.17/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1617-live-benchmark-verify" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.17`
- run_command: `beacon implement team-run "beacon-v1617-live-benchmark-verify" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.17`
- dev_run_command: `beacon implement dev-run "beacon-v1617-live-benchmark-verify" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.17`
- qa_team_command: `beacon qa team-run "beacon-v1617-live-benchmark-verify" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.17`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.17/beacon-v1617-live-benchmark-verify`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.17/.machine/execution/git-workflow-beacon-v1617-live-benchmark-verify.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.17/research/beacon-v1617-live-benchmark-verify.md`
- source_artifact: `docs/beacon/v1.6.17/.machine/user-story/beacon-v1617-live-benchmark-verify.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: materialized 阶段：34 个 live skill 的 prompt fixture 文件真实存在（非空、含 ROUTE: 行）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-001.json`
- status: `planned`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001
- mapped_scenario_ids: SC-001, SC-002, SC-003
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Implement AC-002: resolved 阶段：skill surface 解析修正（mode 子能力映射到主 SKILL.md）：mode 子能力（如 beac... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-002.json`
- status: `planned`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002
- mapped_scenario_ids: SC-004, SC-005, SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Implement AC-003: executing 阶段：`beacon eval scorecard --runner live --live-tier local_a... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-003.json`
- status: `planned`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003
- mapped_scenario_ids: SC-007, SC-008, SC-009
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Implement AC-004: passed 判定：live_skill_pass ≥ 30/37（真实执行），失败 skill 有真实 reason_code（不折算 ... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-004.json`
- status: `planned`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004, TC-ILLEGAL
- mapped_scenario_ids: SC-010, SC-011, SC-012, SC-013, SC-014, SC-015
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/QA-MATRIX.json`
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
