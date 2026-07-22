# Beacon v1.6.10 — Truth Authority + Humanizer + Truth Review Gate

## Scope

**Product Truth** is the computable kernel. **Plan → Truth** is the **highest-priority Mandatory Review Gate** before first freeze.

- implement / qa are derived from frozen truth only
- **Truth Review Gate (first freeze)**: Intent matrix + FSM audit + testability + Humanizer polish → then freeze
- **post-freeze**: reopen → verify-materials → refreeze; tests/tasks cascade stale
- FSM: State | Event | Guard | To | Action (+ illegal; no hanging states)
- Gold: 订单支付 + 超时关单 + 退款 + Intent×AC 矩阵
- Humanizer: oss-sync fulltext; default zh / en

## Program

`beacon-truth-authority-humanizer-v1610`

| Feature | Rev | Intent |
|---------|-----|--------|
| truth-core-authority-v1610 | **R3** | 一内核 + 三契约 + **Truth Review Gate 管线** |
| truth-gold-order-pay-v1610 | **R3** | Gold + Intent Coverage Matrix |
| truth-humanizer-runtime-v1610 | R2 | Humanizing Engine（R3 无行为变更，仅交叉引用 Gate 序） |
| trace-lifecycle-binding-v1610 | **R1** | 1+6 lifecycle → agent_trace.v1 绑定 |

## Evolution

| 框架 | 落地 |
|------|------|
| 一内核 | core R3 |
| 两引擎 | 解构(FP/FSM/Gate) + Humanizer |
| 三契约 | Freeze / Reopen+Verify / Cascade |
| **Plan→Truth 强制门** | **R3 Truth Review Gate** |

## Status

- runtime / package / docs line: **v1.6.10** (current)
- truth lakes: **frozen** — core R3 · gold R3 · humanizer R2 · **trace-lifecycle-binding R1**
- implement / gates: **closed for v1.6.10 lakes** (TRG CLI · freeze precheck · humanizer resolve · lifecycle agent_trace hooks)
- residual: stage trace fail-closed optional/env; release missing-trace soft signal (hard gate deferred INT-TRC-08)

## Locked decisions

| ID | Value |
|----|-------|
| UD-T1610-001..007 | 见 R2 |
| UD-T1610-008 | Plan→Truth = Mandatory Review Gate（首冻最高优先级） |
| UD-T1610-009 | 3-Step: Draft → Review(A/B/C+Humanizer) → Freeze |
| UD-T1610-010 | `beacon truth review`（或等价）合同化；未 pass 不得 freeze |
