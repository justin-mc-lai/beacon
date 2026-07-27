---
schema: beacon-program-manifest-v1
program_slug: beacon-plan-goal-task-closure-v1611
version: v1.6.11
status: program_frozen
revision_id: D2
language: zh
scope_mode: full_parity
lake_or_ocean: 海
baseline_commit: 30b9adffc8ec5442a7691a88faf64a251d97b98f
truth_canonical_branch: main
human_scope_ack: accepted
scope_ack_ref: user-confirmation-2026-07-27
---

# Program: Beacon Plan/Goal Task Closure

## Program 意图

用户只需口头给出大目标，Beacon 就能基于当前主分支与冻结 Truth 把意图拆全，生成可执行任务图，持续报告每条路径进度；发现偏差或注水时暂停并请求人工决定，取消/替换后继续执行下一个 ready task，直到可证明整体收敛。

## 基线绑定

| Kind | Ref |
|------|-----|
| main commit | `30b9adffc8ec5442a7691a88faf64a251d97b98f` |
| runtime | `v1.6.10` |
| docs target | `v1.6.11` |
| Plan implementation | `beacon/commands/planner_review.py`, `beacon/utils/planner_review_runtime.py`, `beacon/utils/intent_decomposition.py`, `beacon/utils/plan_artifact.py` |
| Goal implementation | `beacon/utils/product_goal_runtime.py`, `beacon/utils/program_plan_state.py` |
| package authority | `beacon/utils/feature_package.py`, `beacon/utils/truth_review_gate.py` |
| prior truth | `docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` |
| prior Goal/Plan truth | `docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md` |
| subagent truth | `docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md` |
| worktree admission truth | `docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md` |
| lifecycle trace truth | `docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md` |
| truth authority | `docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` |
| research | `docs/beacon/v1.6.9/research/goal-closed-loop-program-parallel-subagent-pln.md` |
| competitor registry | `docs/beacon/research/beacon-competitor-registry.md` |

## Lakes

| Lake | Feature | Outcome |
|------|---------|---------|
| L0 | `contract-baseline-convergence-v1611` | 收敛上下文与合同测试基线 |
| L1 | `brownfield-context-resolver-v1611` | 解析 commit/Truth/code/tests/Change 基线 |
| L2 | `intent-completeness-engine-v1611` | 递归拆全意图、旅程、异常、状态与非目标 |
| L3 | `change-impact-state-diff-v1611` | 生成五表面 Before→After 与 FSM diff |
| L4 | `atomic-task-graph-compiler-v1611` | 编译原子任务 DAG |
| L5 | `task-progress-ledger-v1611` | 任务/路径级进度反馈账本 |
| L6 | `drift-padding-review-gate-v1611` | 偏差与注水人工门禁 |
| L7 | `cancel-replan-next-ready-v1611` | 取消、替代、重排、next-ready |
| L8 | `convergence-verifier-v1611` | 六层闭环与 Goal 完成判定 |

## 依赖

```text
L0 → L1 → L2 → L3 → L4
                    ├→ L5 ─┐
                    └→ L6 → L7 ─┤
                                 └→ L8
```

## Program 状态

当前：`program_frozen`。

合法主链：

```text
program_intent_captured
→ plan_mode_selected
→ program_inventory
→ program_reviewed
→ feature_graph_ack
→ lakes_truth_in_progress
→ lakes_frozen
→ program_frozen
→ program_delivery
```

冻结要求：

- 九个湖 package validation 与 Truth Review Gate 全部通过。
- feature graph 结构有效且用户确认 scope。
- 不存在 must missing、悬空状态、无 TC 的 AC、无 evidence 绑定的 task。
- 用户已确认范围与跨能力继承；只有九湖全部通过机器门并冻结后，才允许 Program freeze。

## 已确认决策

| Decision | Accepted value | Decision ref |
|----------|----------------|--------------|
| L0–L8 范围与依赖图 | 接受本 manifest 与 feature graph | user-confirmation-2026-07-27 |
| drift/padding mandatory kinds | intent drift、scope drift、orphan、duplicate、padding、evidence mismatch | user-confirmation-2026-07-27 |
| 取消 required dependency | 必须 replacement，否则 block path | user-confirmation-2026-07-27 |
| Goal completion owner | 仅 Goal owner 可在 verifier pass 后完成 | user-confirmation-2026-07-27 |
| 子代理继承 | intent-on、诚实 fallback、不可 freeze/release/complete Goal | user-confirmation-2026-07-27 |
| worktree 继承 | direct/goal/team/ralph 共享真实 worktree admission | user-confirmation-2026-07-27 |
| 生命周期继承 | 内部状态映射回 1+6，并绑定 `agent_trace.v1` | user-confirmation-2026-07-27 |
| no-compat | 旧 shape fail-closed，只允许重新 plan/change/review/freeze | user-confirmation-2026-07-27 |

## Alignment Surface

本 revision 必须闭环：GoalRun 合同、任务 DAG、子代理 delegation、共享 worktree admission、任务/路径进度、偏差人工门、取消重排、1+6 lifecycle trace、no-compat 前向迁移和六层收敛验证。

不允许把内部 TaskRun、drift gate、progress ledger 暴露成新的公共 lifecycle stage。

## Phased Backlog

| Phase | Scope | Decision |
|-------|-------|----------|
| R1 | L0–L8 全部 requirement truth、继承合同、状态机和 planned TC | accepted |
| Implement | runtime compiler/ledger/gate/scheduler/verifier 与已有 Goal/admission/trace 集成 | downstream implement |
| QA | 真实 Git worktree、subagent fallback、no-compat、取消重排、Goal closure E2E | downstream qa |
| Release | runtime promotion 与 catalog active-window 收敛 | deferred to release |

## Deferral Ledger

| Deferral ID | Capability | User decision | Impact |
|-------------|------------|---------------|--------|
| D-PGTC-001 | v1.6.11 runtime/package version promotion | accepted defer | truth 可冻结，不能声称 runtime 已发布 |
| D-PGTC-002 | catalog 默认 active window=3 的历史治理债 | accepted defer to release | freeze 前目录册必须一致；release 前收敛政策 |

## Beacon 原生能力继承合同

### 子代理

- 默认单线程；仅 intent-on 时启用 host subagent。
- TaskNode 声明 `execution_mode`、`required_role`、`delegation_reason`、输入与输出 evidence contract。
- 无 host runtime 时降级为 `single_process_multi_reviewer`，不得宣称 parallel。
- 子代理不得修改 Goal 终态、freeze Truth、签署 QA/release verdict。

### Git worktree

- Truth/change/freeze/refreeze 只在 governance `truth_canonical=main`。
- direct/goal/team/ralph 在第一次实现写入前消费同一个 shared admission。
- branch-only、soft skip、mkdir-only、empty gitlink、hook installed 均不能授权写入。
- worktree 必须 merge/reconcile main 上冻结的 truth revision；refreeze 后旧 admission 与 ready set stale。

### 1+6 生命周期与 trace

| Internal capability | Public harness |
|---------------------|----------------|
| L0–L3 baseline/intent/diff | plan → truth |
| L4 task graph | frozen truth 派生的 implement input |
| L5 progress | goal/implement 内部账本 |
| L6 drift gate | goal/implement 内部 human gate |
| L7 cancel/replan | goal 内部调度 |
| L8 convergence | qa evidence + Goal verifier |

关键出口复用 Goal `run_id` 并写 `agent_trace.v1`；append 失败不得静默成功。

### 不向下兼容与前向迁移

- 旧 package、旧 Goal ledger、无 `ac=`/`evidence=` task 一律 fail-closed。
- reason code 指向 `package_shape_upgrade_required` 或等价 no-compat 阻断。
- 唯一升级路径：`plan → truth/change → Truth Review Gate → freeze new revision`。
- 旧冻结 Truth 只读保留；有效语义通过 `parent_truth` / `inherited_contracts` 在 v1.6.11 新 shape 中重新声明，不增加 legacy reader 或 compatibility adapter。

## 竞品借鉴边界

- Spec-Kit：借鉴 specify→plan→tasks→analyze→implement→converge 与依赖任务表达。
- Matt Pocock Skills：借鉴小步、清晰完成标准与快速反馈。
- ECC：借鉴 checkpoint、loop status、context monitoring。
- 外部项目仅作研究输入；Beacon 的 truth、gate 与状态机仍由本 Program 定义。
