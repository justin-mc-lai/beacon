# Beacon Implementation Plan

- plan_id: `plan-beacon-v1614-fsm-test-generation-r1`
- feature: `beacon-v1614-fsm-test-generation`
- version: `v1.6.14`
- revision_id: `R1`
- baseline_hash: `sha256:ec94b8da65e0a8a2f8d3d6ead017a127b3790dc5f3ce2cd073b3026efa33449b`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.14-beacon-v1614-fsm-test-generation-R1`
- delivery_baseline_source_hash: `sha256:6a2716e6571e18c473bebb4abd745858e8a8f9f8c0f5e0696655f412ae50c3e6`
- plan_hash: `sha256:1738b2fe893fb4653b6ae176f1b6bc58029a0093e39a86ee27eba307cbda59f6`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/truth.md`
- prd: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/truth.md`
- test_case: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/tests.md`
- truth: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/truth.md`
- tests: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/tests.md`
- tasks: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/tasks.md`
- evidence: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation`
- story_scenario_map: `docs/beacon/v1.6.14/.machine/qa/beacon-v1614-fsm-test-generation.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.14/.machine/user-story/beacon-v1614-fsm-test-generation.json`
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
- plan_command: `beacon implement team-plan "beacon-v1614-fsm-test-generation" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- run_command: `beacon implement team-run "beacon-v1614-fsm-test-generation" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- dev_run_command: `beacon implement dev-run "beacon-v1614-fsm-test-generation" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- qa_team_command: `beacon qa team-run "beacon-v1614-fsm-test-generation" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.14/beacon-v1614-fsm-test-generation`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.14/.machine/execution/git-workflow-beacon-v1614-fsm-test-generation.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.14/research/beacon-v1614-fsm-test-generation.md`
- source_artifact: `docs/beacon/v1.6.14/.machine/user-story/beacon-v1614-fsm-test-generation.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: 从合法 truth FSM 自动生成 legal-walk 测试用例（覆盖从 initial 到 terminal 的合法路径，可达状态全走）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-001.json`
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

### ITASK-002 — TASK-002 Implement AC-002: 生成的用例作为 exec-layer TC 进 tests.md（可执行、断言退出码）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-002.json`
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

### ITASK-003 — TASK-003 Implement AC-003: 每个到达状态生成顶点断言（vertex=验证：进入该状态即断言成功）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-003.json`
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

### ITASK-004 — TASK-004 Implement AC-004: illegal 转换路径不被生成（生成器排除 illegal，产出中无非法路径）。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-004.json`
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

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/GATES.json`
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

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/QA-MATRIX.json`
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
