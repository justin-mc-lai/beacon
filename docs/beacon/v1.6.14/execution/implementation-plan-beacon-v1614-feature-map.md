# Beacon Implementation Plan

- plan_id: `plan-beacon-v1614-feature-map-r1`
- feature: `beacon-v1614-feature-map`
- version: `v1.6.14`
- revision_id: `R1`
- baseline_hash: `sha256:4c8558f56643c6634ecab127a4056aff75d98378ab3ff094eac57c7db114befe`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.14-beacon-v1614-feature-map-R1`
- delivery_baseline_source_hash: `sha256:1fce734a358c250e3b6683299d8eec9091617f246059d5b0e21a88489b1b7519`
- plan_hash: `sha256:f5fb5a5435c21b54e5b0b9695803332752244392c5e7cb088b59f77aee862555`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md`
- prd: `docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md`
- test_case: `docs/beacon/v1.6.14/features/beacon-v1614-feature-map/tests.md`
- truth: `docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md`
- tests: `docs/beacon/v1.6.14/features/beacon-v1614-feature-map/tests.md`
- tasks: `docs/beacon/v1.6.14/features/beacon-v1614-feature-map/tasks.md`
- evidence: `docs/beacon/v1.6.14/features/beacon-v1614-feature-map/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.14/features/beacon-v1614-feature-map`
- story_scenario_map: `docs/beacon/v1.6.14/.machine/qa/beacon-v1614-feature-map.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.14/.machine/user-story/beacon-v1614-feature-map.json`
- architecture_blueprint: `docs/beacon/v1.6.14/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1614-feature-map" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- run_command: `beacon implement team-run "beacon-v1614-feature-map" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- dev_run_command: `beacon implement dev-run "beacon-v1614-feature-map" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- qa_team_command: `beacon qa team-run "beacon-v1614-feature-map" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.14/beacon-v1614-feature-map`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.14/.machine/execution/git-workflow-beacon-v1614-feature-map.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.14/research/beacon-v1614-feature-map.md`
- source_artifact: `docs/beacon/v1.6.14/.machine/user-story/beacon-v1614-feature-map.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: 每个 feature 有 `feature-map.md` 骨架：entry_points + verification_commands... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-001.json`
- status: `planned`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Implement AC-002: 复现路由：map 含 `reproduce[]`（symptom_hint → 定位 steps），模糊 bug 描述可路由到对应 ent... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-002.json`
- status: `planned`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Implement AC-003: agent 自验证：map 的 verification 命令可被 agent 执行（复用 code2truth 资产），输出可观测信号供断言。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-003.json`
- status: `planned`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Implement AC-004: 单向投影：map 引用 truth（AC），不反向改 truth；不新增命令面；AC 变化时 map 漂移可检测。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-004.json`
- status: `planned`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004, TC-ILLEGAL
- mapped_scenario_ids: SC-004, SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/QA-MATRIX.json`
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
