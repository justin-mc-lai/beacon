# Beacon Implementation Plan

- plan_id: `plan-beacon-loop-goal-closed-loop-orchestrator-r1`
- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- revision_id: `R1`
- baseline_hash: `sha256:66327efa4cf6d3ed778dbcde241818445b311c0ff4a34ed689dbefc8ec9426c5`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.0-beacon-loop-goal-closed-loop-orchestrator-R1`
- delivery_baseline_source_hash: `sha256:9ce91309132bea6a2db4a8a6a455cb6fabca0d1559b9002be646fcfc08a80950`
- plan_hash: `sha256:b54f040ca1b6d10db45ac66f97f7fb752e4ac7944f6332bb73f9717e625f72a3`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- prd: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- test_case: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md`
- truth: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- tests: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md`
- tasks: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tasks.md`
- evidence: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator`
- ac_matrix: `docs/beacon/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.qa9-matrix.json`
- research_projection: `docs/beacon/v1.6.0/.machine/user-story/beacon-loop-goal-closed-loop-orchestrator.json`
- architecture_blueprint: `docs/beacon/v1.6.0/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-loop-goal-closed-loop-orchestrator" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.0`
- run_command: `beacon implement team-run "beacon-loop-goal-closed-loop-orchestrator" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.0`
- dev_run_command: `beacon implement dev-run "beacon-loop-goal-closed-loop-orchestrator" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.0`
- qa_team_command: `beacon qa team-run "beacon-loop-goal-closed-loop-orchestrator" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.0`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.0`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.0/.machine/execution/git-workflow-beacon-loop-goal-closed-loop-orchestrator.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.0/research/beacon-loop-goal-closed-loop-orchestrator.md`
- source_artifact: `docs/beacon/v1.6.0/.machine/user-story/beacon-loop-goal-closed-loop-orchestrator.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-034
- mapped_scenario_ids: SC-002, SC-003
- mapped_qa_case_ids: TC-034
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-040
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-040
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-044 新增 `packages/beacon-loop/src/delivery/state.ts` 与 `delivery-state.json` 读写。
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-034
- mapped_scenario_ids: SC-002, SC-003
- mapped_qa_case_ids: TC-034
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-045 实现 planner review subprocess 适配器，写入 `review-artifact.json`（AC-033）。
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TEST-001, TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — TASK-047 CLI：`--ask-on`、`--auto-decide deferrals`、`--ack-intent-drift`。
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — TASK-048 测试 TC-031..TC-033、TC-038 骨架。
- status: `completed`
- mapped_ac_ids: AC-007, AC-014
- mapped_test_ids: TEST-007, TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — TASK-049 实现 `truth_gap_scan`：resolve + review parity 缺口合成。
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — TASK-050 实现 `truth_fill` 子链编排器，记录 `truth-promotion.json`（beacon gen-* CLI 序列）。
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — TASK-051 实现 `truth_freeze_gate`：frozen 前 block `implement_loop`（AC-035）。
- status: `completed`
- mapped_ac_ids: AC-012, AC-013, AC-015
- mapped_test_ids: TEST-012, TEST-013, TEST-015
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — TASK-052 `execute-only` 模式：强制 `--feature` + resolve pass。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — TASK-053 测试 TC-034、TC-035、TC-038b。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — TASK-054 `--mode delivery` 自动链：import-evidence → beacon qa → beacon release（subprocess + JSON 解析）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-015 — TASK-055 输出 payload：`closure_verdict`、`beacon_qa_verdict_ref`、`beacon_release_verdict_ref`。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-016 — TASK-056 实现 `repair_from_qa`：qa findings 注入 notes，回灌 `implement_loop`。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-017 — TASK-057 测试 TC-036、TC-037。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-018 — TASK-058 `resume` 扩展：恢复 `delivery-state`（含 `user_decision_pending`、`repair_from_qa`）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-019 — TASK-059 非法转移 guard 与 TC-038a..d。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-018
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-020 — TASK-060 scripted E2E `e2e-delivery-closed-loop.mjs`（AC-039 / TC-039）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-021 — TASK-061 defer D-009: review lane 并行化评估与实现。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-020
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-022 — TASK-062 更新 `evidence.md`；parent 回归 TC-040、TC-041。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-023 — TASK-063 `beacon qa run` + release gate 正式验收本 feature。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-022
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
