# Beacon Implementation Plan

- plan_id: `plan-beacon-loop-goal-closed-loop-orchestrator-r10`
- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- revision_id: `R10`
- baseline_hash: `sha256:6d684eb1456f2a4476f8927a120ed0443f2f0e30927af031fa5b82d4f155dbbe`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.0-beacon-loop-goal-closed-loop-orchestrator-R10`
- delivery_baseline_source_hash: `sha256:58777be16c8c7586aa9d2f2c385bcad7eb2cd4c1376297cf560ad4f92a9f3b18`
- plan_hash: `sha256:9fcd54d5d347b819fcf4113f71a94197cd66f6fdb61eebd846ec9c47d57d3357`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- prd: `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- test_case: `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md`
- truth: `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- tests: `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md`
- tasks: `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tasks.md`
- evidence: `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator`
- revision_delta: `docs/beacon/archive/v1.6.0/.machine/execution/revision-delta-beacon-loop-goal-closed-loop-orchestrator.json`
- ac_matrix: `docs/beacon/archive/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.6.0/.machine/user-story/beacon-loop-goal-closed-loop-orchestrator.json`
- architecture_blueprint: `docs/beacon/archive/v1.6.0/execution/architecture-blueprint.md`

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
- git_workflow_ref: `docs/beacon/archive/v1.6.0/.machine/execution/git-workflow-beacon-loop-goal-closed-loop-orchestrator.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.0/research/beacon-loop-goal-closed-loop-orchestrator.md`
- source_artifact: `docs/beacon/archive/v1.6.0/.machine/user-story/beacon-loop-goal-closed-loop-orchestrator.json`
- section_count: `0`

## Revision Delta
- revision_id: `R10`
- source_revision_id: `R9`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.6.0/.machine/execution/revision-delta-beacon-loop-goal-closed-loop-orchestrator.json`

## Tasks

### ITASK-001 — TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。
- status: `completed`
- mapped_ac_ids: AC-044
- mapped_test_ids: TC-046
- mapped_scenario_ids: SC-023, SC-024
- mapped_qa_case_ids: TC-046
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
- status: `completed`
- mapped_ac_ids: AC-032
- mapped_test_ids: TC-032
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: TC-032
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。
- status: `completed`
- mapped_ac_ids: AC-042, AC-003
- mapped_test_ids: TC-044, TC-040
- mapped_scenario_ids: SC-001, SC-004, SC-006, SC-007, SC-020
- mapped_qa_case_ids: TC-044, TC-040
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-044 新增 `packages/beacon-loop/src/delivery/state.ts` 与 `delivery-state.json` 读写。
- status: `completed`
- mapped_ac_ids: AC-035, AC-039, AC-001, AC-038, AC-040, AC-043, AC-045
- mapped_test_ids: TC-035, TC-039, TEST-001, TC-038, TC-042, TC-045, TC-047
- mapped_scenario_ids: SC-013, SC-016, SC-017, SC-018, SC-021, SC-022, SC-025, SC-026
- mapped_qa_case_ids: TC-035, TC-038, TC-039, TC-042, TC-045, TC-047
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-045 实现 planner review subprocess 适配器，写入 `review-artifact.json`（AC-033）。
- status: `completed`
- mapped_ac_ids: AC-033
- mapped_test_ids: TC-033
- mapped_scenario_ids: SC-011
- mapped_qa_case_ids: TC-033
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。
- status: `completed`
- mapped_ac_ids: AC-002, AC-005, AC-037
- mapped_test_ids: TEST-002, TC-034, TC-037
- mapped_scenario_ids: SC-002, SC-003, SC-012, SC-015
- mapped_qa_case_ids: TC-034, TC-037
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — TASK-047 CLI：`--strict-interrupt`（opt-in）、`--ack-intent-drift`；`--ask-on` deprecated。
- status: `completed`
- mapped_ac_ids: AC-041, AC-024
- mapped_test_ids: TC-043, TEST-024
- mapped_scenario_ids: SC-019
- mapped_qa_case_ids: TC-043
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — TASK-048 测试 TC-031..TC-033、TC-038 骨架。
- status: `completed`
- mapped_ac_ids: AC-012, AC-014, AC-019
- mapped_test_ids: TEST-012, TEST-014, TC-022
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-022
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — TASK-049 实现 `truth_gap_scan`：resolve + review parity 缺口合成。
- status: `completed`
- mapped_ac_ids: AC-036, AC-025, AC-030
- mapped_test_ids: TC-036, TC-041, TEST-030
- mapped_scenario_ids: SC-008, SC-014
- mapped_qa_case_ids: TC-036, TC-041
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — TASK-050 实现 `truth_fill` 子链编排器，记录 `truth-promotion.json`（beacon gen-* CLI 序列）。
- status: `completed`
- mapped_ac_ids: AC-034
- mapped_test_ids: TC-034
- mapped_scenario_ids: SC-002, SC-003, SC-012
- mapped_qa_case_ids: TC-034
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — TASK-051 实现 `truth_freeze_gate`：frozen 前 block `implement_loop`（AC-035）。
- status: `completed`
- mapped_ac_ids: AC-016, AC-004
- mapped_test_ids: TC-040, TC-034
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-006, SC-007, SC-012
- mapped_qa_case_ids: TC-034, TC-040
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — TASK-052 `execute-only` 模式：强制 `--feature` + resolve pass。
- status: `completed`
- mapped_ac_ids: AC-027
- mapped_test_ids: TEST-027
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — TASK-053 测试 TC-034、TC-035、TC-038b。
- status: `completed`
- mapped_ac_ids: AC-015
- mapped_test_ids: TEST-015
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — TASK-054 `--mode delivery` 自动链：import-evidence → beacon qa → beacon release（subprocess + JSON 解析）。
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-015 — TASK-055 输出 payload：`closure_verdict`、`beacon_qa_verdict_ref`、`beacon_release_verdict_ref`。
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-016 — TASK-056 实现 `repair_from_qa`：qa findings 注入 notes，回灌 `implement_loop`。
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-017 — TASK-057 测试 TC-036、TC-037。
- status: `completed`
- mapped_ac_ids: AC-017, AC-018
- mapped_test_ids: TEST-017, TEST-018
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-018 — TASK-058 `resume` 扩展：恢复 `delivery-state`（含 `user_decision_pending`、`repair_from_qa`）。
- status: `completed`
- mapped_ac_ids: AC-022
- mapped_test_ids: TC-040
- mapped_scenario_ids: SC-001, SC-004, SC-006, SC-007
- mapped_qa_case_ids: TC-040
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-019 — TASK-059 非法转移 guard 与 TC-038a..d。
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-018
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-020 — TASK-060 scripted E2E `e2e-delivery-closed-loop.mjs`（AC-039 / TC-039）。
- status: `completed`
- mapped_ac_ids: AC-020
- mapped_test_ids: TEST-020
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-021 — TASK-061 实现 AC-041：review lane 真并行（`execution_mode=parallel_subagent_review`）。
- status: `completed`
- mapped_ac_ids: AC-021
- mapped_test_ids: TC-040
- mapped_scenario_ids: SC-001, SC-004, SC-006, SC-007
- mapped_qa_case_ids: TC-040
- depends_on: ITASK-020
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-022 — TASK-062 更新 `evidence.md`；parent 回归 TC-040、TC-041。
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-023 — TASK-063 `beacon qa run` + release gate 正式验收本 feature（R1 AC-031..039）。
- status: `completed`
- mapped_ac_ids: AC-031
- mapped_test_ids: TC-031
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-031
- depends_on: ITASK-022
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-024 — TASK-064 实现 LLM intent tie-break adapter + `intent-tiebreak.json` 落盘（AC-040）。
- status: `completed`
- mapped_ac_ids: AC-013, AC-023, AC-026, AC-028, AC-029
- mapped_test_ids: TEST-013, TEST-023, TEST-026, TEST-028, TEST-029
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-023
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-025 — TASK-065 默认 green-light：`orchestrator` 移除 ambiguous→`user_decision_pending`；hard stop 白名单。
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-024
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-026 — TASK-066 CLI：`--strict-interrupt` opt-in；deprecate `--auto-decide deferrals` 作为 ambiguous 门控。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-025
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-027 — TASK-067 实现 AC-042：`recommended_route` / Beacon lifecycle auto-route；无 AskUser UI。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-026
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-028 — TASK-068 测试 TC-042..TC-044；更新 deferral ledger 运行时校验（rejected D-009..011）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-027
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-029 — TASK-069 R2 implement evidence + `beacon-eval-qa` 正式验收 AC-040..042。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-028
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-030 — TASK-070 更新 agent surface / `using-beacon`：gnhf 级 launch、steer、companion 文档（AC-043）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-029
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-031 — TASK-071 `implement_loop` 改为 subprocess `beacon implement run --runner <runner>`；移除裸 `codex exec` 路径（AC-044）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-030
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-032 — TASK-072 写入 `output-schema.json`；adapter strict parse + `--output-schema`（AC-045）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-031
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-033 — TASK-073 gnhf 级 `iteration-prompt` 模板；no-op=false 语义（AC-046）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-032
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-034 — TASK-074 delivery FSM：`implement_no_op_blocked`；禁止 no-op → `qa_pending`（AC-047）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-033
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-035 — TASK-075 frozen harness worker 路由表 + `truth-promotion.json` worker 记录（AC-048）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-034
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-036 — TASK-076 `repair_from_qa` 复用 implement harness worker（AC-049）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-035
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-037 — TASK-077 parent orchestrator 回归 + doctor implement runner 检查（AC-050、AC-052）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-036
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-038 — TASK-078 真 implement runner E2E opt-in（AC-051 / TC-053）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-037
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-039 — TASK-079 测试 TC-045..TC-054；`beacon change … --refreeze-chain` 冻结 R3 truth package。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-038
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-040 — TASK-080 fork `packages/gnhf` → `packages/beacon-run`；package/bin 重命名；保留 gnhf 测试基线。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-039
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-041 — TASK-081 实现 `beacon-phase-prompt` 模块：注入 Beacon 阶段 + skill boundary digest；落盘 `beacon-phase.json`（AC-054）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-040
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-042 — TASK-082 truth phase：默认 agent iteration 路径；`--truth-bootstrap=fallback` 回退模板链（AC-055、AC-056）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-041
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-043 — TASK-083 迭代间 harness checkpoint + `truth-promotion.json` 扩展 phase 字段（AC-057）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-042
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-044 — TASK-084 `beacon-loop goal` 薄委托 `beacon-run` + deprecated 文档（AC-058）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-043
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-045 — TASK-085 Core：`beacon implement run --output-schema` 与 branch preflight doctor 消息（AC-059）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-044
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-046 — TASK-086 drill E2E `e2e-gum-drill` opt-in（AC-060 / TC-062）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-045
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-047 — TASK-087 R4 refreeze（`beacon change --refreeze-chain` complete，R3→R4）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-046
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-048 — TASK-088 Phase K implement + `beacon-eval-qa` 验收 AC-053..060。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-047
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-049 — TASK-089 `beacon-run`：`--worktree --beacon` 时 harness `projectRoot = effectiveCwd`；beacon-loop delegate 文档化（AC-061）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-048
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-050 — TASK-090 测试 TC-063：`worktree-harness-project-root`（mock harness，assert truth-promotion path）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-049
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-051 — TASK-091 `requirement_clarity`：拉丁 marker 词界 + frontmatter/path 豁免；TC-064 fixture `go-todo-crud-smoke`（AC-062）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-050
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-052 — TASK-092 `buildPhaseHarnessArgs` / phase-controller：读 target `scope_mode`；smoke truth exit 跳过 sync-materials（AC-063）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-051
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-053 — TASK-093 `beacon-phase.json`：`phase_promoted` + harness 失败日志（AC-064）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-052
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-054 — TASK-094 merge `go-todo-crud-smoke` 材料入主仓；opt-in E2E TC-067（AC-063 回归）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-053
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-055 — TASK-095 R5 refreeze（`beacon change ... --refreeze-chain`）+ `beacon-eval-qa` AC-061..064。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-054
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-056 — TASK-096 `harness-checkpoint` + `phase-controller`：`truth_freeze_gate` 序列（clarity + freeze + cutover）；smoke 跳过 sync-materials 但不跳过 freeze（AC-063/068）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-055
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-057 — TASK-097 `phase-prompt`：truth allowed 含 `beacon freeze`；generate entry frozen gate（AC-068）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-056
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-058 — TASK-098 `scope-mode`：`minimal_smoke` → smoke；`isFeatureTruthFrozen` 共享检查（AC-063）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-057
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-059 — TASK-099 测试 TC-068..TC-070 + 更新 TC-065 smoke-truth-exit 断言（AC-068）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-058
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-060 — TASK-100 R7/R8 refreeze（`beacon change ... --refreeze-chain` + cutover + `beacon freeze`）；`refreeze_status=complete`。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-059
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-061 — TASK-101 闭合 AC-069：`BEACON_RUN_E2E_GO_TODO=1` worktree+freeze E2E；回归 `go-todo-crud-smoke` 不断链。（TC-071 QA passed；live opt-in 见 `packages/beacon-run/e2e/e2e-go-todo-worktree.test.ts`）
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-060
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-062 — TASK-102 闭合 AC-070：新增 `docs/beacon/archive/v1.6.0/execution/beacon-loop-state-spine.md`；实现 `beacon-loop spine show`（或 `status --spine`）+ TC-072。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-061
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-063 — TASK-103 闭合 AC-071：`stop-when` 外部可执行 gate（harness / `--stop-check-cmd`）；`stop_when_unverified` 路径 + TC-073。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-062
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-064 — TASK-104 R10 refreeze（`beacon change ... --refreeze-chain`）；`beacon-eval-qa` v1.6.1 止血验收。（QA `run-20260612T182801183358` passed 38/38 AC、41/41 scenario；refreeze 待用户确认是否重跑）
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-063
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
