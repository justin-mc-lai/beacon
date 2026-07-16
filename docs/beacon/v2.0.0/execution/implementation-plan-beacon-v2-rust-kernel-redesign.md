# Beacon Implementation Plan

- plan_id: `plan-beacon-v2-rust-kernel-redesign-r20`
- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- revision_id: `R20`
- baseline_hash: `sha256:dddc94f66eddbaf800013f22b0b4b55d1c5e3be26b9e8c5ef368da3b2973c8cb`
- delivery_baseline_id: `impl-delivery-baseline-v2.0.0-beacon-v2-rust-kernel-redesign-R20`
- delivery_baseline_source_hash: `sha256:8cd15fef4541a2946864e1eda5bec4a4c551dffa085f7c1677e64dc890dbb63b`
- plan_hash: `sha256:1e37da95a21fbbf09530eb8919b56c6c401a50cb66556ff0b91ace6fdcc41e87`
- status: `blocked`

## Source Refs
- user_story: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md`
- prd: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md`
- test_case: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md`
- truth: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md`
- tests: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md`
- tasks: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tasks.md`
- evidence: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/evidence.md`
- source_of_truth_root: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign`
- revision_delta: `docs/beacon/v2.0.0/.machine/execution/revision-delta-beacon-v2-rust-kernel-redesign.json`
- research_projection: `docs/beacon/v2.0.0/.machine/user-story/beacon-v2-rust-kernel-redesign.json`
- architecture_blueprint: `docs/beacon/v2.0.0/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v2-rust-kernel-redesign" --project-root /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v2.0.0/beacon-v2-rust-kernel-redesign --version v2.0.0`
- run_command: `beacon implement team-run "beacon-v2-rust-kernel-redesign" --project /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v2.0.0/beacon-v2-rust-kernel-redesign --version v2.0.0`
- dev_run_command: `beacon implement dev-run "beacon-v2-rust-kernel-redesign" --project /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v2.0.0/beacon-v2-rust-kernel-redesign --version v2.0.0`
- qa_team_command: `beacon qa team-run "beacon-v2-rust-kernel-redesign" --project /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v2.0.0/beacon-v2-rust-kernel-redesign --version v2.0.0`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v2.0.0/beacon-v2-rust-kernel-redesign`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v2.0.0/.machine/execution/git-workflow-beacon-v2-rust-kernel-redesign.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v2.0.0/research/beacon-v2-rust-kernel-redesign.md`
- source_artifact: `docs/beacon/v2.0.0/.machine/user-story/beacon-v2-rust-kernel-redesign.json`
- section_count: `0`

## Revision Delta
- revision_id: `R20`
- source_revision_id: `R19`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v2.0.0/.machine/execution/revision-delta-beacon-v2-rust-kernel-redesign.json`

## Tasks

### ITASK-001 — AC-001 Agent 写代码→跑 Eval→发现问题→修→再测，自动闭环
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 人看实现→修正 Spec→重新实现；人注入 AI 不知道的上下文
- status: `blocked`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 show [--json]`（机器级多项目）。
- status: `blocked`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 clean preflight；branch 模式 P2；**worktree 全模式 P3（AC-099）**
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 acp:*>` CLI 直接选 agent 跑长任务编码落地；agent 选择映射到对应 AgentBackend；loop 在 CLI...
- status: `blocked`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 p95 < 100ms 本地
- status: `blocked`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 p95 < 50ms
- status: `blocked`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — AC-008 p95 < 200ms
- status: `blocked`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — AC-009 p95 < 50ms
- status: `blocked`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — AC-010 p95 < 10ms
- status: `blocked`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — AC-011 < 60s 典型 fixture
- status: `blocked`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — AC-012 < 100ms 不含 agent
- status: `blocked`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — AC-013 软上限 500MB
- status: `blocked`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — AC-014 beacon-loop / v1 CLI 并行
- status: `blocked`
- mapped_ac_ids: AC-014
- mapped_test_ids: TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-015 — AC-015 迁移为可选对照，不强迫退役 v1
- status: `blocked`
- mapped_ac_ids: AC-015
- mapped_test_ids: TEST-015
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-016 — AC-016 结构性消除
- status: `blocked`
- mapped_ac_ids: AC-016
- mapped_test_ids: TEST-016
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-017 — AC-017 三层+Spine+projection rebuild
- status: `blocked`
- mapped_ac_ids: AC-017
- mapped_test_ids: TEST-017
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-018 — AC-018 workspace
- status: `blocked`
- mapped_ac_ids: AC-018
- mapped_test_ids: TEST-018
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-019 — AC-019 双 FSM+benchmark
- status: `blocked`
- mapped_ac_ids: AC-019
- mapped_test_ids: TEST-019
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-018
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-020 — AC-020 六能力 surface + legacy removal + progressive disclosure + BranchContext...
- status: `blocked`
- mapped_ac_ids: AC-020
- mapped_test_ids: TEST-020
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-021 — AC-021 九表+DAO
- status: `blocked`
- mapped_ac_ids: AC-021
- mapped_test_ids: TEST-021
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-020
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-022 — AC-022 P0–P6
- status: `blocked`
- mapped_ac_ids: AC-022
- mapped_test_ids: TEST-022
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-023 — AC-023 可执行缓解
- status: `blocked`
- mapped_ac_ids: AC-023
- mapped_test_ids: TEST-023
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-022
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-024 — AC-024 evaluator 裁决
- status: `blocked`
- mapped_ac_ids: AC-024
- mapped_test_ids: TEST-024
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-023
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-025 — AC-025 TIG + planner multi-agent + doctor 路由
- status: `blocked`
- mapped_ac_ids: AC-025
- mapped_test_ids: TEST-025
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-024
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-026 — AC-026 beacon-rs scaffold 已完成
- status: `blocked`
- mapped_ac_ids: AC-026
- mapped_test_ids: TEST-026
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-025
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-027 — AC-027 用户拒绝延期
- status: `blocked`
- mapped_ac_ids: AC-027
- mapped_test_ids: TEST-027
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-026
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-028 — AC-028 v1/v2 skill+CLI 语言分叉，需合并互不影响
- status: `blocked`
- mapped_ac_ids: AC-028
- mapped_test_ids: TEST-028
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-027
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-029 — AC-029 落地稳依赖可测 skill 资产
- status: `blocked`
- mapped_ac_ids: AC-029
- mapped_test_ids: TEST-029
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-028
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-030 — AC-030 禁止 Darwin 式自动改 SKILL.md
- status: `blocked`
- mapped_ac_ids: AC-030
- mapped_test_ids: TEST-030
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-029
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-031 — AC-031 planner review 选项 A：AC-042–046 真集成；Diagram Truth Layer；AC 重编号至 098；禁止...
- status: `blocked`
- mapped_ac_ids: AC-031
- mapped_test_ids: TEST-031
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-030
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-032 — AC-032 R6 refreeze：六 public skill 渐进式披露 contract；内部保留 branch governance / do...
- status: `blocked`
- mapped_ac_ids: AC-032
- mapped_test_ids: TEST-032
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-031
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-033 — AC-033 R7 refreeze：TraceSpine.v1 / TraceContext.v1 成为 run authority；loop/imp...
- status: `blocked`
- mapped_ac_ids: AC-033
- mapped_test_ids: TEST-033
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-032
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-034 — AC-034 R8 refreeze：将 canonical truth author/refreeze/commit -> feature workt...
- status: `completed`
- mapped_ac_ids: AC-034
- mapped_test_ids: TEST-034
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-033
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-035 — AC-035 ，后者是 L1 MD / L2 SQLite / L3 Blob**）：
- status: `blocked`
- mapped_ac_ids: AC-035
- mapped_test_ids: TEST-035
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-034
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-036 — AC-036 （stop-when maker≠checker）→ v2 AC-105
- status: `blocked`
- mapped_ac_ids: AC-036
- mapped_test_ids: TEST-036
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-035
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-037 — AC-037 **）
- status: `blocked`
- mapped_ac_ids: AC-037
- mapped_test_ids: TEST-037
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-036
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-038 — AC-038 ）
- status: `blocked`
- mapped_ac_ids: AC-038
- mapped_test_ids: TEST-038
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-037
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-039 — AC-039 ..114）
- status: `blocked`
- mapped_ac_ids: AC-039
- mapped_test_ids: TEST-039
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-038
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-040 — AC-040 ..116）
- status: `blocked`
- mapped_ac_ids: AC-040
- mapped_test_ids: TEST-040
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-039
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-041 — AC-041 ..123）
- status: `blocked`
- mapped_ac_ids: AC-041
- mapped_test_ids: TEST-041
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-040
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-042 — AC-042 **：v2 core closure **不包含** `beacon-python` / PyO3 / v1 Python runtime...
- status: `completed`
- mapped_ac_ids: AC-042
- mapped_test_ids: TEST-042
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-041
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-043 — AC-043 **：`~/.beacon/beacon.db` 不得存储可编辑的需求正文；只可存 metadata、FSM、gate、artifact 指针。
- status: `blocked`
- mapped_ac_ids: AC-043
- mapped_test_ids: TEST-043
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-042
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-044 — AC-044 **：`.beacon/qa/*.json`、`.beacon/gate-report.json` 等 v1 投影在 v2 为 **非权威...
- status: `blocked`
- mapped_ac_ids: AC-044
- mapped_test_ids: TEST-044
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-043
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-045 — AC-045 **：**禁止** `<project>/.beacon/beacon.db` 作为运行态权威（v2 明确否决 per-project DB）。
- status: `blocked`
- mapped_ac_ids: AC-045
- mapped_test_ids: TEST-045
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-044
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-046 — AC-046 **：**禁止** `<project>/.beacon/loop/ledger/loop-runs.db` 作为 v2 权威；v1.6...
- status: `blocked`
- mapped_ac_ids: AC-046
- mapped_test_ids: TEST-046
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-045
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-047 — AC-047 **：Blob 文件变更时 `artifact_refs` 必须更新 `content_hash`；hash 不匹配时 Spine 标记...
- status: `blocked`
- mapped_ac_ids: AC-047
- mapped_test_ids: TEST-047
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-046
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-048 — AC-048 **：`beacon doctor projection rebuild` 须能从已注册 `project_root` 的 MD + bl...
- status: `blocked`
- mapped_ac_ids: AC-048
- mapped_test_ids: TEST-048
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-047
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-049 — AC-049 存储原则（Plan §2.5）
- status: `blocked`
- mapped_ac_ids: AC-049
- mapped_test_ids: TEST-049
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-048
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-050 — AC-050 **：每次 gate 评估写入 `gate_results`（pass/fail/blocked + reason_codes JSON）。
- status: `blocked`
- mapped_ac_ids: AC-050
- mapped_test_ids: TEST-050
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-049
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-051 — AC-051 **：每次 run 启动写入 `runs`；checkpoint 写入 `checkpoints`。
- status: `blocked`
- mapped_ac_ids: AC-051
- mapped_test_ids: TEST-051
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-050
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-052 — AC-052 **：Spine 查询 **DB-first**；blob 仅当 `artifact_refs` 存在且 hash 有效时拼接。
- status: `blocked`
- mapped_ac_ids: AC-052
- mapped_test_ids: TEST-052
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-051
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-053 — AC-053 **：v1 JSON 运行态只允许 **export/import 迁移**，不得与 DB 双写竞争权威。
- status: `blocked`
- mapped_ac_ids: AC-053
- mapped_test_ids: TEST-053
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-052
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-054 — AC-054 Operator Spine API（Plan §2.5）
- status: `blocked`
- mapped_ac_ids: AC-054
- mapped_test_ids: TEST-054
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-053
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-055 — AC-055 **：必须实现 `beacon spine list [--project PATH] [--status STATUS] [--json]`。
- status: `blocked`
- mapped_ac_ids: AC-055
- mapped_test_ids: TEST-055
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-054
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-056 — AC-056 **：必须实现 `beacon spine artifacts <run-id> [--json]`。
- status: `blocked`
- mapped_ac_ids: AC-056
- mapped_test_ids: TEST-056
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-055
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-057 — AC-057 **：必须实现 `beacon spine gate <feature> [--version vX] [--json]`。
- status: `blocked`
- mapped_ac_ids: AC-057
- mapped_test_ids: TEST-057
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-056
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-058 — AC-058 **：crate 依赖方向：`cli -> {gate, orchestrator, store, core}`；`store -> co...
- status: `blocked`
- mapped_ac_ids: AC-058
- mapped_test_ids: TEST-058
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-057
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-059 — AC-059 **：v2.0.0 **不交付** `beacon-proto`/gRPC（**D-V2-001 accepted defer**）；CL...
- status: `blocked`
- mapped_ac_ids: AC-059
- mapped_test_ids: TEST-059
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-058
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-060 — AC-060 **：单文件模块超过 500 行须拆分或 ADR 说明例外（对齐 D-02）。
- status: `blocked`
- mapped_ac_ids: AC-060
- mapped_test_ids: TEST-060
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-059
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-061 — AC-061 **：阶段转换表显式编码；非法转换返回 typed error + reason_code。
- status: `blocked`
- mapped_ac_ids: AC-061
- mapped_test_ids: TEST-061
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-060
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-062 — AC-062 **：`Blocked` 必须携带 `reason_codes: Vec<String>` 与可选 `blocking_gate`。
- status: `blocked`
- mapped_ac_ids: AC-062
- mapped_test_ids: TEST-062
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-061
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-063 — AC-063 **：`Skipped` 仅允许带 `user_accepted_deferral_id` 或 deferral ledger 引用。
- status: `blocked`
- mapped_ac_ids: AC-063
- mapped_test_ids: TEST-063
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-062
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-064 — AC-064 **：`Crashed` / `TimedOut` / `Interrupted` 须写入 `lifecycle_events` 且可触发...
- status: `blocked`
- mapped_ac_ids: AC-064
- mapped_test_ids: TEST-064
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-063
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-065 — AC-065 **：Delivery 运行时 12 状态在 `beacon-core` 定义并与 `runs.status` CHECK 一致。
- status: `blocked`
- mapped_ac_ids: AC-065
- mapped_test_ids: TEST-065
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-064
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-066 — AC-066 **：plan 主链节点转换须写入 `lifecycle_events`（可审计，非仅内存）。
- status: `blocked`
- mapped_ac_ids: AC-066
- mapped_test_ids: TEST-066
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-065
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-067 — AC-067 **：`Paused` / `Stopping` / `Stopped` 与 v1 beacon-loop graceful+force...
- status: `blocked`
- mapped_ac_ids: AC-067
- mapped_test_ids: TEST-067
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-066
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-068 — AC-068 **：`Repairing` 须持久化 repair payload 到 `artifact_refs`。
- status: `blocked`
- mapped_ac_ids: AC-068
- mapped_test_ids: TEST-068
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-067
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-069 — AC-069 **：`AwaitingQa` 仅在 `import-evidence` 成功后可进入。
- status: `blocked`
- mapped_ac_ids: AC-069
- mapped_test_ids: TEST-069
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-068
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-070 — AC-070 **：`Closed` 仅 release gate pass 或用户显式 archive；orchestrator **不得**自设 C...
- status: `blocked`
- mapped_ac_ids: AC-070
- mapped_test_ids: TEST-070
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-069
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-071 — AC-071 **：`EvidenceChain` 含 `manifest_hash`、`signature_chain`、`artifact_refs...
- status: `blocked`
- mapped_ac_ids: AC-071
- mapped_test_ids: TEST-071
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-070
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-072 — AC-072 **：import 断链 fail-closed → `EVIDENCE_CHAIN_BROKEN`。
- status: `blocked`
- mapped_ac_ids: AC-072
- mapped_test_ids: TEST-072
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-071
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-073 — AC-073 **：v1 `.beacon/evidence-signature-chain.json` 可迁移为 v2 记录。
- status: `blocked`
- mapped_ac_ids: AC-073
- mapped_test_ids: TEST-073
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-072
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-074 — AC-074 **：启动前 `truth-map resolve`；blocked → exit != 0 + 推荐 `beacon-gen-change`。
- status: `blocked`
- mapped_ac_ids: AC-074
- mapped_test_ids: TEST-074
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-073
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-075 — AC-075 **（P2）：`SubprocessBackend` 完成 1 次真 integration iteration（可控测试 harness...
- status: `blocked`
- mapped_ac_ids: AC-075
- mapped_test_ids: TEST-075
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-074
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-076 — AC-076 **（P3）：`AcpBackend`（CLI `acp:<target>`）完成 1 次真 integration iteration；...
- status: `blocked`
- mapped_ac_ids: AC-076
- mapped_test_ids: TEST-076
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-075
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-077 — AC-077 **：checkpoint resume 后 iteration 递增；notes 注入写入 `lifecycle_events`（可审计）。
- status: `blocked`
- mapped_ac_ids: AC-077
- mapped_test_ids: TEST-077
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-076
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-078 — AC-078 **：`stop_when` 移植 v1 `stop-when-gate`（含 gate pass 早停）。
- status: `blocked`
- mapped_ac_ids: AC-078
- mapped_test_ids: TEST-078
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-077
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-079 — AC-079 **：orchestrator **禁止**输出 QA pass / release ready / feature complete v...
- status: `blocked`
- mapped_ac_ids: AC-079
- mapped_test_ids: TEST-079
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-078
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-080 — AC-080 **：Phase Controller 四阶段写入 `runs.metadata_json`；phase 转换写 `lifecycle_e...
- status: `blocked`
- mapped_ac_ids: AC-080
- mapped_test_ids: TEST-080
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-079
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-081 — AC-081 **（P3）：Developer Feedback Loop 人注入 checkpoint——`beacon-v2 run --feedb...
- status: `blocked`
- mapped_ac_ids: AC-081
- mapped_test_ids: TEST-081
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-080
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-082 — AC-082 **（P3）：Loop Engineering 三层 Loop 可观测——spine snapshot 含 `loop_layer` 字段...
- status: `blocked`
- mapped_ac_ids: AC-082
- mapped_test_ids: TEST-082
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-081
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-083 — AC-083 **：双轨运行时选择必须 **显式**（例如独立 `beacon-v2` 二进制，或 `beacon --runtime v2` / 等价...
- status: `blocked`
- mapped_ac_ids: AC-083
- mapped_test_ids: TEST-083
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-082
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-084 — AC-084 **：`BEACON_STORE_PATH` 测试隔离；生产默认 `~/.beacon/beacon.db`。
- status: `blocked`
- mapped_ac_ids: AC-084
- mapped_test_ids: TEST-084
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-083
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-085 — AC-085 **：在 **v2 runtime 路径内**，任何把 v1 Python/legacy skill 当执行后端的请求必须 fail-cl...
- status: `blocked`
- mapped_ac_ids: AC-085
- mapped_test_ids: TEST-085
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-084
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-086 — AC-086 **：`beacon harness list --version v2.0.0 --json`（或等价 CLI）只返回六个一等能力及其...
- status: `blocked`
- mapped_ac_ids: AC-086
- mapped_test_ids: TEST-086
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-085
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-087 — AC-087 **：spine/projects/workflow/truth-map/implement/qa/release/run 子命令可解析且...
- status: `blocked`
- mapped_ac_ids: AC-087
- mapped_test_ids: TEST-087
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-086
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-088 — AC-088 **：spine/projects/run 支持 `--json` 且 schema 可校验。
- status: `blocked`
- mapped_ac_ids: AC-088
- mapped_test_ids: TEST-088
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-087
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-089 — AC-089 **：v1 reason_codes 对齐：`gate_results.reason_codes_json` 失败样例须含 documen...
- status: `blocked`
- mapped_ac_ids: AC-089
- mapped_test_ids: TEST-089
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-088
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-090 — AC-090 **：`project_versions`（id, project_id, version, docs_root, is_current）
- status: `blocked`
- mapped_ac_ids: AC-090
- mapped_test_ids: TEST-090
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-089
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-091 — AC-091 **：`feature_packages`（id, project_version_id, slug, truth_path, tests...
- status: `blocked`
- mapped_ac_ids: AC-091
- mapped_test_ids: TEST-091
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-090
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-092 — AC-092 **：`feature_lifecycle`（feature_id, stage, status, reason_codes_json,...
- status: `blocked`
- mapped_ac_ids: AC-092
- mapped_test_ids: TEST-092
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-091
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-093 — AC-093 **：`lifecycle_events`（id, feature_id, run_id, event_type, payload_jso...
- status: `blocked`
- mapped_ac_ids: AC-093
- mapped_test_ids: TEST-093
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-092
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-094 — AC-094 **：`gate_results`（id, feature_id, gate_type, verdict, reason_codes_js...
- status: `blocked`
- mapped_ac_ids: AC-094
- mapped_test_ids: TEST-094
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-093
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-095 — AC-095 **：`artifact_refs`（id, run_id, kind, abs_path, content_hash, size_byt...
- status: `blocked`
- mapped_ac_ids: AC-095
- mapped_test_ids: TEST-095
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-094
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-096 — AC-096 **：`checkpoints`（id, run_id, iteration, state_json, created_at）
- status: `blocked`
- mapped_ac_ids: AC-096
- mapped_test_ids: TEST-096
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-095
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-097 — AC-097 **：`beacon-store` 提供 ProjectDao, FeatureDao, RunDao, GateDao, Artifac...
- status: `blocked`
- mapped_ac_ids: AC-097
- mapped_test_ids: TEST-097
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-096
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-098 — AC-098 **：migration `v1_runtime_ledger`：自 `~/.beacon/runtime-ledger/runtime-...
- status: `blocked`
- mapped_ac_ids: AC-098
- mapped_test_ids: TEST-098
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-097
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-099 — AC-099 **：migration `v1_loop_ledger`：扫描各项目 `loop-runs.db` 一次性导入。
- status: `blocked`
- mapped_ac_ids: AC-099
- mapped_test_ids: TEST-099
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-098
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-100 — AC-100 **：migration `v1_qa_projection`：可选历史只读导入。
- status: `blocked`
- mapped_ac_ids: AC-100
- mapped_test_ids: TEST-100
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-099
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-101 — AC-101 **：schema `user_version` 管理；降级禁止。
- status: `blocked`
- mapped_ac_ids: AC-101
- mapped_test_ids: TEST-101
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-100
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-102 — AC-102 **：`SpineDao::snapshot` 联查 lifecycle + run + gate + artifacts。
- status: `blocked`
- mapped_ac_ids: AC-102
- mapped_test_ids: TEST-102
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-101
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-103 — AC-103 **：`list` 支持 lifecycle/run status 过滤。
- status: `blocked`
- mapped_ac_ids: AC-103
- mapped_test_ids: TEST-103
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-102
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-104 — AC-104 **：`artifact_refs.abs_path` 必须绝对路径。
- status: `completed`
- mapped_ac_ids: AC-104
- mapped_test_ids: TEST-104
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-103
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-105 — AC-105 **：migration 前自动备份 runtime-ledger 与既有 DB。
- status: `completed`
- mapped_ac_ids: AC-105
- mapped_test_ids: TEST-105
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-104
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-106 — AC-106 **：双写期 **单一写者**；双向同时写须测试失败。
- status: `completed`
- mapped_ac_ids: AC-106
- mapped_test_ids: TEST-106
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-105
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-107 — AC-107 **：v2 harness surface / cross-track isolation 回归失败 → `beacon-gov-doct...
- status: `completed`
- mapped_ac_ids: AC-107
- mapped_test_ids: TEST-107
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-106
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-108 — AC-108 **：v2 benchmark 相对 baseline 回退 >10% 阻断 **v2 P6 成熟度出口**；不授权、不要求关停 v1 轨。
- status: `completed`
- mapped_ac_ids: AC-108
- mapped_test_ids: TEST-108
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-107
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-109 — AC-109 **：全量 AC closure 由 evaluator 裁决；generator/implementer 不得自证 release re...
- status: `completed`
- mapped_ac_ids: AC-109
- mapped_test_ids: TEST-109
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-108
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-110 — AC-110 **：frozen package 权威高于 plan；plan 变更须 promote。
- status: `completed`
- mapped_ac_ids: AC-110
- mapped_test_ids: TEST-110
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-109
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-111 — AC-111 **（P3）：`beacon doctor verify-truth-integrity` 在 v2 路由到 Rust gate；`--m...
- status: `completed`
- mapped_ac_ids: AC-111
- mapped_test_ids: TEST-111
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-110
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-112 — AC-112 **：v1 Python / Node / v1 skill 面 **不进入 v2 core closure 的验收依赖**；它们作为 *...
- status: `completed`
- mapped_ac_ids: AC-112
- mapped_test_ids: TEST-112
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-111
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-113 — AC-113 **：每轮 plan/truth/review/brainstorm 必须保存 prompt snapshot hash，并标记 acce...
- status: `completed`
- mapped_ac_ids: AC-113
- mapped_test_ids: TEST-113
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-112
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-114 — AC-114 **：intent confidence 低、强意图冲突、scope 未确认或 deferral 未拍板时，truth freeze fa...
- status: `completed`
- mapped_ac_ids: AC-114
- mapped_test_ids: TEST-114
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-113
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-115 — AC-115 **：loop 启动必须读取 `decision_packet.v1`；缺失、过期或引用未接受 prompt snapshot 时不得进入...
- status: `completed`
- mapped_ac_ids: AC-115
- mapped_test_ids: TEST-115
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-114
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-116 — AC-116 **：implement admission 必须同时验证 truth_frozen、decision_packet_current、de...
- status: `completed`
- mapped_ac_ids: AC-116
- mapped_test_ids: TEST-116
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-115
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-117 — AC-117 **：stagnation detector 基于 agent trace 确定性识别 repeat_failure / repeat_l...
- status: `completed`
- mapped_ac_ids: AC-117
- mapped_test_ids: TEST-117
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-116
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-118 — AC-118 **：remediation sandbox 在 governed worktree 内执行 overlay/eval/rollback；...
- status: `completed`
- mapped_ac_ids: AC-118
- mapped_test_ids: TEST-118
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-117
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-119 — AC-119 **：loop guardrails 包含 pattern registry、failure catalog、token budget、r...
- status: `completed`
- mapped_ac_ids: AC-119
- mapped_test_ids: TEST-119
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-118
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-120 — AC-120 **：qa-evidence 必须产出 confidence_chain 与 truth-derived business FSM cov...
- status: `completed`
- mapped_ac_ids: AC-120
- mapped_test_ids: TEST-120
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-119
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-121 — AC-121 **：QA defect 必须形成 defect -> fix -> regression evidence chain；缺段 `repa...
- status: `completed`
- mapped_ac_ids: AC-121
- mapped_test_ids: TEST-121
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-120
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-122 — AC-122 **：closure evidence 必须包含可执行行为验证、至少一个有效断言、AC/TC 绑定 artifact 与运行佐证；纯静态...
- status: `completed`
- mapped_ac_ids: AC-122
- mapped_test_ids: TEST-122
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-121
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-123 — AC-123 **：release human gate 是不变量；`auto_decide=true` 不得触发 release gate 通过。
- status: `completed`
- mapped_ac_ids: AC-123
- mapped_test_ids: TEST-123
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-122
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-124 — AC-124 **：skill loader 必须采用 progressive disclosure；默认只加载 public `SKILL.md`，按...
- status: `completed`
- mapped_ac_ids: AC-124
- mapped_test_ids: TEST-124
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-123
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-125 — AC-125 **：六个 public skill 都必须提供 route examples；示例覆盖 `truth review -> decisio...
- status: `completed`
- mapped_ac_ids: AC-125
- mapped_test_ids: TEST-125
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-124
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-126 — AC-126 **：`BranchContext.v1` 是所有写入/agent/evidence/release harness 的共同输入，字段至少...
- status: `completed`
- mapped_ac_ids: AC-126
- mapped_test_ids: TEST-126
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-125
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-127 — AC-127 **：branch/workspace governance 是 hard gate；任何 generator/implement/qa-...
- status: `completed`
- mapped_ac_ids: AC-127
- mapped_test_ids: TEST-127
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-126
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-128 — AC-128 **：Harness boundary 以 reason_code enforce：planner/truth 不实现，implement...
- status: `completed`
- mapped_ac_ids: AC-128
- mapped_test_ids: TEST-128
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-127
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-129 — AC-129 **：`loop start` 必须创建 `TraceContext.v1` 并绑定 BranchContext、decision_pac...
- status: `completed`
- mapped_ac_ids: AC-129
- mapped_test_ids: TEST-129
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-128
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-130 — AC-130 **：`implement` / `qa-evidence` / `release` 必须验证 trace completeness；tr...
- status: `completed`
- mapped_ac_ids: AC-130
- mapped_test_ids: TEST-130
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-129
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-131 — AC-131 **：`stagnation-report.v1` 必须引用 trace event range、reason_code、failure...
- status: `completed`
- mapped_ac_ids: AC-131
- mapped_test_ids: TEST-131
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-130
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-132 — AC-132 **：`remediation-report.v1` 必须引用 stagnation report、overlay/eval/rollba...
- status: `completed`
- mapped_ac_ids: AC-132
- mapped_test_ids: TEST-132
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-131
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-133 — AC-133 **：truth/change/refreeze 只能在 `truth_canonical_branch`（默认 main，缺失时 mas...
- status: `completed`
- mapped_ac_ids: AC-133
- mapped_test_ids: TEST-133
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-132
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-134 — AC-134 **：refreeze transaction 必须拒绝 reason-only / machine-only 变化；revision i...
- status: `completed`
- mapped_ac_ids: AC-134
- mapped_test_ids: TEST-134
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-133
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-135 — AC-135 **：canonical refreeze 只有在 canonical branch 提交后才成为可消费 baseline；未提交 ref...
- status: `completed`
- mapped_ac_ids: AC-135
- mapped_test_ids: TEST-135
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-134
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-136 — AC-136 **：feature worktree 中发现 stale feature-local refreeze/projection dirty...
- status: `completed`
- mapped_ac_ids: AC-136
- mapped_test_ids: TEST-136
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-135
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-137 — AC-137 **：feature/dev branch 进入 implement 前必须包含 canonical `truth_baseline_co...
- status: `completed`
- mapped_ac_ids: AC-137
- mapped_test_ids: TEST-137
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-136
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-138 — AC-138 **：标准流 admission evidence bundle 必须包含 truth-map verify、verify-materia...
- status: `completed`
- mapped_ac_ids: AC-138
- mapped_test_ids: TEST-138
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-137
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-139 — AC-139 **：标准流必须可 idempotent resume；已对齐步骤重复执行时返回 `up_to_date` / `pass`，不得因重复执...
- status: `completed`
- mapped_ac_ids: AC-139
- mapped_test_ids: TEST-139
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-138
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-140 — AC-140 **：标准执行流通过六 public skill 的 progressive examples 暴露，不得新增第七个 public ski...
- status: `completed`
- mapped_ac_ids: AC-140
- mapped_test_ids: TEST-140
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-139
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-141 — AC-141 **：Beacon 产品策略为长期双轨：`track_v1`（Python CLI + v1 skill 面）与 `track_v2`（R...
- status: `completed`
- mapped_ac_ids: AC-141
- mapped_test_ids: TEST-141
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-140
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-142 — AC-142 **：双轨隔离契约——代码树、CLI 入口、skill 根、docs version tree、CI job 必须可分轨合并；同一 PR...
- status: `completed`
- mapped_ac_ids: AC-142
- mapped_test_ids: TEST-142
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-141
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-143 — AC-143 **：运行时选择必须显式（对齐 AC-060）；禁止 v2 路径执行 v1 backend，禁止 v1 路径把请求静默升级为 v2 并改写...
- status: `completed`
- mapped_ac_ids: AC-143
- mapped_test_ids: TEST-143
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-142
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-144 — AC-144 **：迁移/导入工具可以只读对照另一轨状态，但不得在双写期成为第二写者（延续 AC-093 单写者原则，按轨分别强制）。
- status: `completed`
- mapped_ac_ids: AC-144
- mapped_test_ids: TEST-144
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-143
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-145 — AC-145 **：统一评分必须包含 **结构质量**（SKILL.md/package/HARD GATE/progressive 合规，对齐 ski...
- status: `completed`
- mapped_ac_ids: AC-145
- mapped_test_ids: TEST-145
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-144
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-146 — AC-146 **：skill 评分产物权威为 `runtime_evidence_only`；**不得**替代 `qa-evidence` forma...
- status: `completed`
- mapped_ac_ids: AC-146
- mapped_test_ids: TEST-146
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-145
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-147 — AC-147 **：评分执行者与被评 skill 的「修改建议作者」在流程上必须可分离（独立评分会话或独立 grader）；禁止同一无审计步骤既改 sk...
- status: `completed`
- mapped_ac_ids: AC-147
- mapped_test_ids: TEST-147
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-146
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-148 — AC-148 **：v1 `beacon eval` 既有 scorecard 维度可映射进统一 schema，但发布门必须以统一 schema 的稳定...
- status: `completed`
- mapped_ac_ids: AC-148
- mapped_test_ids: TEST-148
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-147
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
