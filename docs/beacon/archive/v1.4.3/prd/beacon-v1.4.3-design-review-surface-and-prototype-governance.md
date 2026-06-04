# PRD: Beacon v1.4.3 Design Review Surface and Prototype Governance

**Feature**: `beacon-v1.4.3-design-review-surface-and-prototype-governance`  
**Version**: `v1.4.3`  
**Date**: `2026-05-11`  
**Status**: `freeze-ready`  
**Track**: `design-decision + prototype-governance + ux-handoff`  
**Scenario**: `design-review-before-prototype + prototype-de-overloading`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.4.3/SUMMARY.md`
- Execution index: `docs/beacon/archive/v1.4.3/execution/index.md`
- Umbrella PRD: `docs/beacon/archive/v1.4.3/prd/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
- User story: `docs/beacon/archive/v1.4.3/user-story/beacon-v1.4.3-design-review-surface-and-prototype-governance.md`
- Test cases: `docs/beacon/archive/v1.4.3/qa/test-cases/beacon-v1.4.3-design-review-surface-and-prototype-governance.md`

## 1. 问题

### 1.1 当前断层

Beacon 当前 `prototype` 在实践中容易从 requirement-driven freeze 滑向：

- 设计方向决策
- UI/UX 交付物语义
- 产品承诺面承接

这说明 design challenge 与 prototype freeze 没有被清晰分层。

### 1.2 风险

- 原型语义会被直接传递到 UI/UX 交付物，导致视觉和交互决策没有独立 challenge 面。
- `implement` 可能把 prototype 当作最终设计批准，绕过 design-quality 讨论。
- 一旦 prototype 被过载，需求冻结、设计判断、交接物料会混成单层。

## 2. 目标

### 2.1 主要目标

- 定义 `beacon-design-review` 作为 UI/UX 决策 challenge surface。
- 把 `prototype` 收缩回 formal freeze / handoff contract。
- 在真实需要 UX/UI handoff 时，强制保持 `design-review -> prototype -> implement` 顺序。

### 2.2 非目标

- 不把 `design-review` 变成新的 lifecycle stage。
- 不让 `prototype` 升级成视觉定稿器或最终设计裁决面。

## 3. 设计原则

### 3.1 Design Challenge First

- 设计方向挑战必须先于 prototype 冻结发生。

### 3.2 Prototype Is Handoff, Not Final Approval

- `prototype` 只负责 handoff packaging，不负责设计最终判断。

### 3.3 Truth Boundary

- `design-review` 提供挑战和建议，但不能直接改写冻结 truth。

## 4. 范围

### In scope

- `beacon-design-review` surface
- hierarchy / state / interaction coherence review
- prototype conditional trigger judgment
- prototype de-overloading rules

### Out of scope

- 自动 UI 生成
- 视觉高保真产出系统
- 用 prototype 替代 PRD / user-story / test-case

## 5. 功能需求

- FR-001: Beacon must define `beacon-design-review` as a support/review surface for UI/UX decision challenge.
- FR-002: `design-review` must evaluate page hierarchy, state clarity, interaction coherence, and UX evidence sufficiency.
- FR-003: `prototype` must be explicitly re-scoped as conditional formal freeze/handoff.
- FR-004: `prototype` must no longer default into product-strategy challenge, design final approval, or direct UI deliverable authority.
- FR-005: `design-review` and `prototype` must be layered so design direction challenge precedes formal handoff freeze.

## 6. 边界 / 分层 / 恢复策略

### 6.1 边界

- `design-review` 是 support/review surface，不是 truth surface。
- `prototype` 只在 UX/UI handoff 真正存在时触发。

### 6.2 分层

- `prd / user-story / test-case truth -> design-review -> prototype_when_triggered -> implement`

### 6.3 恢复策略

- 若 design evidence 不足，路由回 `beacon review design` 或上游 truth refinement。
- 若 prototype 被错误当作 final approval，必须回退到 `design-review` 修正判断。

## 7. 状态轴 / 图示真相

- `design_review_state`: `not_requested -> challenged -> sufficient_for_direction -> routed`
- `prototype_governance_state`: `not_needed -> condition_triggered -> frozen_for_handoff -> consumed_by_implement`

- `branch-flow`
  - `truth ready -> design-review -> prototype_when_triggered -> implement`
  - `truth ready -> design-review -> implement when prototype is not required`
- `decision-priority`
  - `frozen truth > design-review outcome > prototype packaging`
  - `design direction challenge > deliverable-semantic convenience`
- `state-machine`
  - `prototype_governance_state: not_needed -> condition_triggered -> frozen_for_handoff -> consumed_by_implement`
  - `design_review_state: not_requested -> challenged -> sufficient_for_direction -> routed`

## 风险与缓解

- 风险：`prototype` 再次被用作设计最终裁决，导致 design-review 失去独立价值。
  - 缓解：保持 `design-review` 的显式推荐路由，并在 prototype 触发时只允许 handoff 语义。
- 风险：没有真实 UI 证据时仍强行进入 prototype。
  - 缓解：在 `design-review` 中先判定 `prototype_required`，不满足则直接路由实现或上游 refinement。

## 8. 验收标准

| AC ID | Description |
| --- | --- |
| AC-001 | `beacon-design-review` exists as support/review surface. |
| AC-002 | the surface can evaluate hierarchy, state clarity, interaction coherence, and UX evidence sufficiency. |
| AC-003 | `prototype` is re-scoped as conditional freeze/handoff. |
| AC-004 | `prototype` is explicitly prevented from defaulting into design-final-approval semantics. |
| AC-005 | `design-review` and `prototype` are layered rather than collapsed. |
