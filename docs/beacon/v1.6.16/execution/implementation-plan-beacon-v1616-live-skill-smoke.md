# Beacon Implementation Plan

- plan_id: `plan-beacon-v1616-live-skill-smoke-r1`
- feature: `beacon-v1616-live-skill-smoke`
- version: `v1.6.16`
- revision_id: `R1`
- baseline_hash: `sha256:65050f85290d5ec85d5664a10e1b23efdffe285895d29a9d5f87b7191f8e4afe`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.16-beacon-v1616-live-skill-smoke-R1`
- delivery_baseline_source_hash: `sha256:97148054e389aaba3f899ba425f65ec248c446bc381b48b0cc71505477c535f2`
- plan_hash: `sha256:8d105e6be2ad63f58cee4c20d926c72fa2193cebe7f0ae8225ceb0a9df398e25`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/truth.md`
- prd: `docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/truth.md`
- test_case: `docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/tests.md`
- truth: `docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/truth.md`
- tests: `docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/tests.md`
- tasks: `docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/tasks.md`
- evidence: `docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke`
- ac_matrix: `docs/beacon/v1.6.16/.machine/qa/beacon-v1616-live-skill-smoke.ac-test-matrix.json`
- research_projection: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-live-skill-smoke.json`
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
- plan_command: `beacon implement team-plan "beacon-v1616-live-skill-smoke" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- run_command: `beacon implement team-run "beacon-v1616-live-skill-smoke" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- dev_run_command: `beacon implement dev-run "beacon-v1616-live-skill-smoke" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- qa_team_command: `beacon qa team-run "beacon-v1616-live-skill-smoke" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.16`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.16/beacon-v1616-live-skill-smoke`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.16/.machine/execution/git-workflow-beacon-v1616-live-skill-smoke.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.16/research/beacon-v1616-live-skill-smoke.md`
- source_artifact: `docs/beacon/v1.6.16/.machine/user-story/beacon-v1616-live-skill-smoke.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: executing 阶段：eval benchmark 在 local_admitted tier 下对 37 个 skill 全量执行 ... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-001.json`
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

### ITASK-002 — TASK-002 Implement AC-002: traced→passed 后：live_skill_pass 从 1/37 提升到 ≥ 30/37（真实执行通过率）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-002.json`
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

### ITASK-003 — TASK-003 Implement AC-003: traced 阶段：每个执行过的 skill 落盘 host_behavior 执行 trace（含 status/reason_code... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-003.json`
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

### ITASK-004 — TASK-004 Implement AC-004: failed 判定：执行结果不伪造，失败 skill 标 fail + reason_code，不折算为 pass。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-004.json`
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

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/QA-MATRIX.json`
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
