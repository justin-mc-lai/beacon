---
schema: beacon-change-truth-v1
version: v1.6.11
program_slug: beacon-plan-goal-task-closure-v1611
status: frozen
baseline_commit: 30b9adffc8ec5442a7691a88faf64a251d97b98f
truth_canonical_branch: main
change_reason: "D2: inherit Beacon subagent, unified worktree admission, 1+6 lifecycle trace, GoalRun ownership, no-compat forward migration"
scope_ack_ref: user-confirmation-2026-07-27
---

# Change Truth: Beacon Plan/Goal Task Closure

## 变更原因

当前 Plan/Goal 已有意图拆解、海湖划分、Truth Review、Program graph 与阶段日志，但仍不能证明“大目标被拆全并持续落地”。关键缺口是 brownfield 基线、递归原子任务 DAG、路径级进度、偏差人工门禁、取消/替代/重排，以及全局收敛证明。

## Before → After

| Surface | Before | After |
|---------|--------|-------|
| baseline | 计划可读取局部材料，但不强制绑定 commit/Truth/test baseline | 每个 Change 固定 commit、Truth revision、代码入口、测试基线与历史 Change |
| intent | 可产出海湖与 journey seed | must 意图递归落到 Journey/AC/Non-goal/Deferral，缺失即阻断 |
| change | 主要是计划文本 | 输出 promise/interface/data/FSM/test 的 Before→After diff |
| task | feature/阶段级任务 | AC/状态/代码/证据绑定的原子任务 DAG，可承载 100+ 节点 |
| progress | Goal stage log | task/path 级 attempts、feedback、blocked、cancelled、replacement、remaining |
| drift | review advisory | drift/padding 命中后强制人工决策 |
| cancel | 无完整语义 | cancelled/superseded/replacement + ready set 重算 |
| done | verifier refs 较粗 | intent/path/AC/state/task/evidence 六层收敛证明 |
| subagent | 旧 Goal/Plan 仅有关键词 gate 与 review pack | TaskNode delegation 合同、真实 execution mode、诚实 fallback、parent-only completion |
| worktree | 旧 unified admission 已冻结但未进入新任务图 | 所有 implementation TaskNode 统一绑定 service/worktree/admission/cwd/HEAD |
| lifecycle | 旧 agent_trace 已覆盖 stage，但新 L0–L8 未映射 | 内部状态映射回 1+6，复用 Goal run_id 与 `agent_trace.v1` |
| compatibility | 旧 shape 可能被误认为历史方言 | fail-closed，唯一升级路径为重新 plan/change/review/freeze |

## ChangePlan FSM

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| intent_captured | resolve_baseline | goal_present | baseline_resolving | capture goal |
| baseline_resolving | baseline_ok | refs_bound | baseline_resolved | persist baseline |
| baseline_resolving | baseline_conflict | conflict_found | awaiting_human | attach conflict |
| baseline_resolved | expand_intent | baseline_current | intent_expanding | build coverage tree |
| intent_expanding | intent_complete | must_covered | impact_mapping | seal intent set |
| impact_mapping | diff_complete | five_surfaces_mapped | state_diff_review | emit Before→After |
| state_diff_review | approve_scope | human_ack | change_draft | bind decisions |
| change_draft | submit_truth_review | package_complete | truth_review | run A–D |
| truth_review | review_pass | all_lakes_pass | refrozen | freeze revisions |
| truth_review | review_fail | findings_present | change_draft | reopen gaps |
| refrozen | compile_tasks | graph_current | task_graph_ready | emit task DAG |

终态：`task_graph_ready`。`awaiting_human` 必须通过显式人工决定返回相应上游状态。

### invalid / illegal

- `intent_captured → task_graph_ready`
- `baseline_resolving → impact_mapping` without bound baseline
- `state_diff_review → change_draft` without human scope acknowledgement
- `truth_review → refrozen` while any lake fails
- refreeze 后继续使用旧 graph revision

## TaskRun FSM

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| proposed | dependencies_ready | all_required_done | ready | enter ready set |
| ready | resolve_admission | implementation_task | admission_resolving | call shared admission |
| admission_resolving | admission_pass | real_worktree_and_truth_reconciled | running | bind cwd/HEAD and increment attempt |
| admission_resolving | admission_fail | reason_present | blocked | record reason and route |
| running | submit_evidence | output_present | evidence_pending | bind evidence |
| evidence_pending | verify_pass | assertion_pass | verified | record verifier |
| verified | close | path_consistent | done | aggregate progress |
| running | drift_detected | score_over_threshold | drift_suspected | pause execution |
| drift_suspected | request_decision | finding_complete | awaiting_human | publish choices |
| awaiting_human | continue | human_continue | running | record decision |
| awaiting_human | rewrite | human_rewrite | proposed | replace task contract |
| awaiting_human | split | human_split | superseded | create child tasks |
| awaiting_human | replace | human_replace | cancelled | link replacement |
| awaiting_human | cancel | human_cancel | cancelled | recompute ready set |
| running | execution_fail | retryable | retry_wait | record failure |
| retry_wait | retry_due | within_policy | ready | requeue |
| retry_wait | retry_exhausted | limit_hit | blocked | block path |

终态：`done`、`cancelled`、`superseded`、`blocked`。

### invalid / illegal

- `proposed → running` with unmet dependencies
- `ready → running` without shared admission for implementation task
- implementation write on main、branch-only、mkdir-only 或 unreconciled worktree
- `running → done` without evidence
- `drift_suspected → running` without human decision
- `cancelled → done`
- required dependency 被取消且无 replacement 时，下游仍进入 ready
- subagent 直接把 GoalRun 标为 complete

## 跨 Program Acceptance

| ID | Requirement | Lake |
|----|-------------|------|
| PAC-001 | Change 绑定 main commit、Truth revision、代码入口与测试基线 | L0/L1 |
| PAC-002 | 每条 must 意图落到 Journey/AC/Non-goal/approved Deferral | L2 |
| PAC-003 | 输出 promise/interface/data/FSM/test Before→After diff | L3 |
| PAC-004 | 任务图可承载 100+ 节点，但禁止按数量注水 | L4/L6 |
| PAC-005 | 每个任务绑定 intent、journey、AC、code scope、dependencies、verification、evidence | L4 |
| PAC-006 | 每条路径聚合 completed/blocked/cancelled/replacement/remaining | L5 |
| PAC-007 | drift/padding 强制进入人工选择门 | L6 |
| PAC-008 | 取消或替换后重算 ready set；必要依赖缺替代则 block | L7 |
| PAC-009 | refreeze 使旧 tasks/tests/evidence stale | L0/L8 |
| PAC-010 | Goal 完成要求全部路径与六层追溯闭环 | L8 |
| PAC-011 | TaskNode 声明子代理角色、execution mode、输入输出和 parent-only completion | L4/L6 |
| PAC-012 | direct/goal/team/ralph 共享真实 worktree admission，refreeze 后旧 admission stale | L4/L7 |
| PAC-013 | L0–L8 内部状态映射回 1+6，并在关键出口写 `agent_trace.v1` | L5/L8 |
| PAC-014 | GoalRun 持有 program/graph/truth/ready/human/admission/trace/verifier refs | L8 |
| PAC-015 | 旧 package/ledger fail-closed，不建兼容 reader，只经新 revision 重新冻结 | L0/L1 |

## Frozen Truth Lineage

| Parent truth | Inherited invariant |
|--------------|---------------------|
| `beacon-plan-goal-deep-integration-v169` | Goal host_subagent gate、stage trace、plan 不实现/不 freeze |
| `beacon-plan-host-subagent-voltpack-v1610` | intent-on、10-role pack、诚实 fallback、禁止假 parallel |
| `unified-implement-admission-v1610` | direct/goal/team/ralph shared admission + real worktree |
| `trace-lifecycle-binding-v1610` | 1+6 → `agent_trace.v1`、append fail 不静默 |
| `truth-core-authority-v1610` | Truth Review、freeze/reopen/stale/refreeze |

## Public Lifecycle Boundary

```text
goal
  → plan
  → truth
  → design (conditional)
  → implement (shared worktree admission)
  → qa (independent)
  → release (human gate)
```

Task graph、progress、drift、cancel/replan、verifier 都是内部控制机制，不新增公共 harness。

## No-compat Migration

```text
old package / old ledger detected
→ block(package_shape_upgrade_required)
→ plan re-decompose
→ truth change in current shape
→ Truth Review Gate
→ freeze new revision
```

旧冻结需求保留为 lineage/evidence；禁止通过 soft skip、legacy reader 或 compatibility adapter 继续交付。

## 非目标

- 不把“上百个任务”设成最低数量指标。
- 不允许 host hook 成为唯一强门禁。
- 本 Change 不在 truth 阶段实现代码，也不自证 QA/release。
