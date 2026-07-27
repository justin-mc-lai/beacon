---
schema: beacon-program-manifest-v1
program_slug: beacon-plan-goal-task-closure-v1611
version: v1.6.11
status: program_frozen
change_round: D3
revision_id: R2
previous_revision: R1
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

当前：`program_frozen`（D3/R2 requirement truth）。

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
- Program freeze 必须验证当前四文件 hash、package-validation、Truth Review、human ack、promotion receipt 与 PAC trace，不能只信 status 字符串。

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
| CLI scaffold | CLI 只确定性创建当前四文件骨架与协议元数据，不负责虚构领域语义 | user-confirmation-2026-07-27 |
| Host Agent (skill-authored fill) full fill | Host Agent（skill-authored fill）必须填充完整 package 领域对象，不能只润色 L0 或一句一 AC | user-confirmation-2026-07-27 |
| write authority | LLM 返回结构化 response；CLI 校验后事务化 patch 与确定性投影 | user-confirmation-2026-07-27 |
| semantic compile migration | 复用旧 PRD/User Story host-response/bridge 语义能力，但不恢复旧 shape canonical 写入 | user-confirmation-2026-07-27 |

## Alignment Surface

本 revision 必须闭环：GoalRun 合同、任务 DAG、子代理 delegation、共享 worktree admission、任务/路径进度、偏差人工门、取消重排、1+6 lifecycle trace、no-compat 前向迁移和六层收敛验证。

不允许把内部 TaskRun、drift gate、progress ledger 暴露成新的公共 lifecycle stage。

## Phased Backlog

| Phase | Scope | Decision |
|-------|-------|----------|
| R1 | L0–L8 初版 requirement truth、继承合同、状态机和 planned TC | superseded by D3/R2 |
| R2 | CLI scaffold + Host Agent (skill-authored fill) full-package fill、结构化事务、恢复 FSM、authenticated Program freeze | accepted |
| Implement | runtime compiler/ledger/gate/scheduler/verifier 与已有 Goal/admission/trace 集成 | downstream implement |
| QA | 真实 Git worktree、subagent fallback、no-compat、取消重排、Goal closure E2E | downstream qa |
| Release | runtime promotion 与 catalog active-window 收敛 | deferred to release |

## Deferral Ledger

| Deferral ID | Capability | User decision | Impact |
|-------------|------------|---------------|--------|
| D-PGTC-001 | v1.6.11 runtime/package version promotion | accepted defer | truth 可冻结，不能声称 runtime 已发布 |
| D-PGTC-002 | catalog 默认 active window=3 的历史治理债 | accepted defer to release | freeze 前目录册必须一致；release 前收敛政策 |

> D-PGTC-002 不能作为伪冻结豁免；若 catalog active plane 在 Program freeze 时仍漂移，Program 保持 blocked，等待独立治理决定。

## D3 Full-Package Fill 主链

```text
GoalUtteranceCaptured
→ VersionAndContextResolved
→ DeterministicScaffoldMaterialized
→ HostAgentFillRequested
→ StructuredFillProduced
→ FillPatchSchemaValidated
→ CanonicalTruthPatched
→ TestsTasksEvidenceRegenerated
→ PackageValidationPassed
→ TruthReviewPassed
→ AwaitingHumanAck
→ Frozen
```

### 合同与 authority

| Contract | Authority rule |
|----------|----------------|
| `truth-fill-request.v1` | CLI 绑定 utterance、版本、ContextEnvelope、R2/base hashes、semantic compiler/host transport/Humanizer/PAC refs |
| `truth-fill-response.v1` | Host Agent（skill-authored fill）返回结构化领域对象和 projection inputs，不返回可自由覆盖的 canonical Markdown |
| `truth-fill-transaction.v1` | CLI 校验 schema、hash、引用和 allowed paths，原子 patch 后再生成 tests/tasks/evidence |
| `truth-human-ack.v1` | 人工确认 finding disposition 与最终 R2 hash set，freeze 不得自行代签 |

旧 `prd`/`user-story` semantic compiler 的 host-response、command-bridge 与 provider transport 是可复用输入；当前唯一 requirement authority 仍为：

```text
features/<slug>/{truth,tests,tasks,evidence}.md
```

禁止恢复平行旧 shape，禁止 LLM 直接写四文件，禁止 scaffold/规则模板冒充 full fill。

## Program PAC Trace Matrix

| PAC | Lake | AC | TC | Task/Evidence | Revision proof |
|-----|------|----|----|---------------|----------------|
| PAC-001 | L0/L1 | AC-BAS-002, AC-CTX-001 | TC-BAS-002, TC-CTX-001 | generated R2 tasks/evidence | R2 + final hash |
| PAC-002 | L2 | AC-INT-001..007 | TC-INT-001..007 | generated R2 tasks/evidence | R2 + final hash |
| PAC-003 | L3 | AC-DIF-001..007 | TC-DIF-001..007 | generated R2 tasks/evidence | R2 + final hash |
| PAC-004/005 | L4/L6 | AC-DAG-001..010, AC-REV-001/007 | TC-DAG-001..010, TC-REV-001/007 | generated R2 tasks/evidence | R2 + final hash |
| PAC-006 | L5 | AC-LED-001..007 | TC-LED-001..007 | generated R2 tasks/evidence | R2 + final hash |
| PAC-007 | L6 | AC-REV-001..007 | TC-REV-001..007 | generated R2 tasks/evidence | R2 + final hash |
| PAC-008 | L7 | AC-RPL-001..009 | TC-RPL-001..009 | generated R2 tasks/evidence | R2 + final hash |
| PAC-009/010 | L0/L8 | AC-BAS-004/009, AC-CNV-001..010 | TC-BAS-004/009, TC-CNV-001..010 | generated R2 tasks/evidence | R2 + final hash |
| PAC-011/012 | L4/L7 | AC-DAG-006..008, AC-RPL-006/007 | TC-DAG-006..008, TC-RPL-006/007 | generated R2 tasks/evidence | R2 + final hash |
| PAC-013/014 | L5/L8 | AC-LED-005..007, AC-CNV-004/006/007 | mapped TC rows | generated R2 tasks/evidence | R2 + final hash |
| PAC-015 | L0/L1 | AC-BAS-005/006/008, AC-CTX-005 | mapped TC rows | generated R2 tasks/evidence | R2 + final hash |
| PAC-016 | L0 | AC-BAS-007 | TC-BAS-007 | generated R2 tasks/evidence | R2 + final hash |
| PAC-017 | L1/L2 | AC-CTX-007/008, AC-INT-006/007 | mapped TC rows | generated R2 tasks/evidence | R2 + final hash |
| PAC-018 | L0/L1/L4 | AC-BAS-008, AC-CTX-007, AC-DAG-010 | mapped TC rows | generated R2 tasks/evidence | R2 + final hash |
| PAC-019 | L3/L4 | AC-DIF-006/007, AC-DAG-009 | mapped TC rows | generated R2 tasks/evidence | R2 + final hash |
| PAC-020 | L5/L6/L7 | AC-LED-007, AC-REV-007, AC-RPL-008/009 | mapped TC rows | generated R2 tasks/evidence | R2 + final hash |
| PAC-021 | L8 | AC-CNV-008/009/010 | TC-CNV-008/009/010 | generated R2 tasks/evidence | R2 + final hash |

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
