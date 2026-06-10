# Beacon Implementation Plan

- plan_id: `plan-beacon-loop-goal-closed-loop-orchestrator-r3`
- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- revision_id: `R3`
- baseline_hash: `sha256:909af515dbe441d54288fb4f0b4463a2166a3a04cdfe195d0d624dee89d26bc4`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.0-beacon-loop-goal-closed-loop-orchestrator-R3`
- delivery_baseline_source_hash: `sha256:af9b498aa256d3f85777fe013ff0c39a65e140b3c7616047e92c89b51a0ac7eb`
- plan_hash: `sha256:a7cbab848f1d9d14aec11f3e6e1c97bd54388f52eebfa41dfc6f24e07f5ffcd7`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- prd: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- test_case: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md`
- truth: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- tests: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md`
- tasks: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tasks.md`
- evidence: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator`
- revision_delta: `docs/beacon/v1.6.0/.machine/execution/revision-delta-beacon-loop-goal-closed-loop-orchestrator.json`
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

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.6.0/.machine/execution/revision-delta-beacon-loop-goal-closed-loop-orchestrator.json`

## Tasks

### ITASK-001 — TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。
- status: `completed`
- mapped_ac_ids: AC-004, AC-008, AC-021, AC-010, AC-029, AC-009
- mapped_test_ids: TC-034, TEST-008, TC-040, TEST-010, TEST-029, TEST-009
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-006, SC-007
- mapped_qa_case_ids: TC-034, TC-040
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
- status: `planned`
- mapped_ac_ids: AC-013, AC-022, AC-016, AC-019, AC-025
- mapped_test_ids: TEST-013, TC-040, TC-022, TC-041
- mapped_scenario_ids: SC-001, SC-004, SC-005, SC-006, SC-007, SC-008
- mapped_qa_case_ids: TC-040, TC-022, TC-041
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。
- status: `planned`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-040
- mapped_scenario_ids: SC-001, SC-004, SC-006, SC-007
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
- status: `planned`
- mapped_ac_ids: AC-014
- mapped_test_ids: TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。
- status: `planned`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TEST-001, TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — TASK-047 CLI：`--strict-interrupt`（opt-in）、`--ack-intent-drift`；`--ask-on` deprecated。
- status: `planned`
- mapped_ac_ids: AC-024
- mapped_test_ids: TEST-024
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — TASK-048 测试 TC-031..TC-033、TC-038 骨架。
- status: `planned`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — TASK-049 实现 `truth_gap_scan`：resolve + review parity 缺口合成。
- status: `planned`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — TASK-050 实现 `truth_fill` 子链编排器，记录 `truth-promotion.json`（beacon gen-* CLI 序列）。
- status: `planned`
- mapped_ac_ids: AC-026
- mapped_test_ids: TEST-026
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — TASK-051 实现 `truth_freeze_gate`：frozen 前 block `implement_loop`（AC-035）。
- status: `planned`
- mapped_ac_ids: AC-028, AC-015, AC-017, AC-018, AC-020, AC-023, AC-027
- mapped_test_ids: TEST-028, TEST-015, TEST-017, TEST-018, TEST-020, TEST-023, TEST-027
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — TASK-052 `execute-only` 模式：强制 `--feature` + resolve pass。
- status: `planned`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — TASK-053 测试 TC-034、TC-035、TC-038b。
- status: `planned`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — TASK-054 `--mode delivery` 自动链：import-evidence → beacon qa → beacon release（subprocess + JSON 解析）。
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-021 — TASK-061 实现 AC-041：review lane 真并行（`execution_mode=parallel_subagent_review`）。
- status: `planned`
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
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-023 — TASK-063 `beacon qa run` + release gate 正式验收本 feature（R1 AC-031..039）。
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-022
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-024 — TASK-064 实现 LLM intent tie-break adapter + `intent-tiebreak.json` 落盘（AC-040）。
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-023
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-025 — TASK-065 默认 green-light：`orchestrator` 移除 ambiguous→`user_decision_pending`；hard stop 白名单。
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-024
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-026 — TASK-066 CLI：`--strict-interrupt` opt-in；deprecate `--auto-decide deferrals` 作为 ambiguous 门控。
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
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
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-038
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
