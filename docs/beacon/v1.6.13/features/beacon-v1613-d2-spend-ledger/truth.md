---
slug: beacon-v1613-d2-spend-ledger
version: v1.6.13
status: frozen
language: zh
domain_required: true
ux_required: false
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
package_maturity: filled
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.13/features/beacon-v1613-d2-spend-ledger/truth.md
  user_story: docs/beacon/v1.6.13/features/beacon-v1613-d2-spend-ledger/truth.md
  test_case: docs/beacon/v1.6.13/features/beacon-v1613-d2-spend-ledger/tests.md
---

# Requirement Truth: beacon-v1613-d2-spend-ledger (v1.6.13)

## 人话

给长任务加一个**记账本**。每个长任务（goal）有一份"预算账本"，规则很简单：

- **真正干完活才算钱**：只有"交付了东西、而且被验证通过"的回合，才在账本上记一笔
- **没干活不扣**：预检、试跑、静默跳过都不记
- **不能重复扣**：同一个回合因为网络中断重放，不会记两笔
- **钱花光就停**：预算用完后任务停下来，而不是空转烧时间

这样你跑一个长任务，随时能回答"它花了多少次机会、还剩多少、为什么停"。

- 能做：goal 状态里持久化账本；按上述规则记账；预算耗尽时用现有 `halt_budget` 停止
- 不能做：不把 dry-run/预检当消费；不破坏现有"未验证 writeback 不许扣"的规矩（那是基础）
- 怎样算完：账本能持久化、幂等、只对已验证交付扣费、花光即停，且有测试证明

## User Intent

在 v1.6.12 已有的回合预算（`beacon/utils/goal_budget.py`，LoopX 蒸馏）之上，把"回合数上限"升级为真正的 spend 账本：持久化、只对 validated writeback 扣一次、幂等重放、quiet skip 不扣、配额耗尽 halt。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
truth_review_gate: required
fill_depth: filled
intent_source: beacon-v1613-planning-source-audit-2026-08-27 D2
loopx_anchor: oss-sync/automation/autoresearch/loopx quota/spend_commit.ts + slot_accounting.py
```

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-001 | D2：持久化 spend ledger | must | AC-001 | covered |
| INT-002 | 只对 validated writeback 扣一次 | must | AC-002 | covered |
| INT-003 | quiet skip/dry-run 不扣 | must | AC-003 | covered |
| INT-004 | spend 幂等（CAS 重放不重扣） | must | AC-004 | covered |
| INT-005 | 配额耗尽 halt_budget | must | AC-005 | covered |
| INT-006 | 交接预算回归保留 | should | AC-006 | covered |
| INT-007 | 按 goal 占空比配额（loopx slot 账本） | should | AC-005 | deferred-to-next |

## 用户旅程

1. 触发：goal run 驱动长任务（program driver / goal agent driver）
2. 关键操作：每个回合走 choose→deliver→validate→writeback→spend；只有 validate+writeback 通过才 spend
3. 结果：状态文件里能看到账本（已花/剩余/每笔来源）；花光 → `halt_budget` 停止并给原因
4. 异常：网络中断重放回合不重复扣费；预检/静默跳过不扣费

## First principles

- 系统边界：只计入"已验证交付"，不计入尝试
- 不可变：未验证 writeback 不得 spend（v1.6.12 AC-004 保留）
- 可推翻假设：按占空比配额（slot 账本）为 should，若复杂度高可下放下一迭代

## Domain Model

| Entity | Key fields | Notes |
|--------|------------|-------|
| SpendLedger | goal_id, entries[], spent, quota_limit | 持久化到 goal run state |
| SpendEntry | index, source, spent_at, writeback_ref, digest | 每笔消费记录 |
| QuotaAccount | window_hours, slot_minutes, used_slots | 占空比配额（should，可下放） |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | goal run 状态含持久化 `spend_ledger`（已花回合数、每笔 SpendEntry 的 index/source/spent_at/writeback_ref），可跨进程读取。 |
| AC-002 | spend 仅在 validated writeback 之后发生一次（保留 `spend_guard`：writeback 未验证 → `spend_without_writeback`，不 spend）。 |
| AC-003 | quiet skip / dry-run / preflight 不 spend（`spend_ledger` 计数不变）。 |
| AC-004 | spend 幂等：同一 index 重放不重复扣（CAS on index digest，conflict 即拒绝）。 |
| AC-005 | 配额（`max_drive_turns`/quota_limit）耗尽 → 状态 `halt_budget` + reason_code `program_drive_budget_exhausted`，不继续驱动。 |
| AC-006 | 交接文本预算（handoff budget：16 行 / 1800 字符）保留且仍生效（回归）。 |

## Domain FSM Order

| State | From | Guard |
|-------|------|-------|
| deliver | choose | budget_ok |
| validate | deliver | outcome_valid |
| writeback | validate | valid |
| spend | writeback | durably_saved |
| next_choose | spend | index_cas_ok |
| halt_budget | any | quota_zero |

## Illegal transitions

- writeback(未验证) → spend（spend_without_writeback）
- spend 重放 → 重复扣（幂等违反）
- quiet skip → spend（空转消费）
- quota 耗尽后继续驱动（超预算运行）

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| choose | pick_step | budget_ok | deliver | — |
| deliver | produced | outcome_valid | validate | — |
| validate | verified | valid | writeback | — |
| writeback | durably_saved | persisted | spend | record_entry |
| spend | committed | index_cas_ok | next_choose | spend_once |
| any | budget_exhausted | quota_zero | halt_budget | stop |

**终态：** halt_budget（预算耗尽）或 done（完成）

### invalid / illegal

- writeback(未验证) → spend（illegal：spend_without_writeback）
- spend 重放 → 重复扣（illegal：幂等违反）
- quiet skip → spend（illegal：空转消费）
- quota 耗尽后继续驱动（illegal：超预算运行）

## Non-goals

- 不做跨 goal 共享配额池（多 goal 独立账本）
- 不把 spend 接成计费/货币系统（仅回合机会计数）
- 不改变 release 人类 gate

## Freeze readiness

- [x] Intent Matrix must 无 missing
- [x] 用户旅程非「待补」占位
- [x] First principles / Domain Model 已具体化
- [x] 业务 FSM 五元组 + illegal
- [x] 每 AC ≥ 1 TC（Command+Assertion）+ exec-layer TC
- [x] tasks 均有 ac= + evidence= 绑定
- [x] package_maturity: filled
- [x] `beacon truth review` pass 后再 freeze

### Gap vs gold (订单支付示例)

- 对照：`docs/beacon/v1.6.13/features/truth-gold-order-pay-v1610/truth.md`
- 对照：`skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md`

## Source Excerpt

```markdown
beacon-v1613-d2-spend-ledger
现有基础：beacon/utils/goal_budget.py（TURN_STEPS、spend_guard、handoff budget）
LoopX 锚定：oss-sync/automation/autoresearch/loopx loopx/control_plane/quota/spend_commit.ts（CAS 幂等）、slot_accounting.py:708-726（quiet skip 不扣）、turn_transaction_contract.json（spend 时序）
```
