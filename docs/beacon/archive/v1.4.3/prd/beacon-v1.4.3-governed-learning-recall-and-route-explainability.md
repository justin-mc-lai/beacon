# PRD: Beacon v1.4.3 Governed Learning Recall and Route Explainability

**Feature**: `beacon-v1.4.3-governed-learning-recall-and-route-explainability`  
**Version**: `v1.4.3`  
**Date**: `2026-05-11`  
**Status**: `freeze-ready`  
**Track**: `learning-plane + explainability + support-surface`  
**Scenario**: `default-learning-injection + visible-route-explanation`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.4.3/SUMMARY.md`
- Execution index: `docs/beacon/archive/v1.4.3/execution/index.md`
- Umbrella PRD: `docs/beacon/archive/v1.4.3/prd/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
- User story: `docs/beacon/archive/v1.4.3/user-story/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`
- Test cases: `docs/beacon/archive/v1.4.3/qa/test-cases/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`

## 1. 问题

### 1.1 当前断层

Beacon 已有 learning plane kernel，但：

- 不会系统性进入每个 skill 的默认消费路径
- 用户看不到 learning 是否被用、为什么被用、是否过期
- `help / status / ask / deep` 还不能稳定解释 learning 对 route 和判断的影响

### 1.2 风险

- learning 存在但不消费，导致同类错误重复发生。
- learning 被消费但不可见，会削弱 evidence-first 与 operator trust。
- stale / conflicting learning 若不降级，可能污染 route recommendation。

## 2. 目标

### 2.1 主要目标

- 定义 `beacon-learn` 作为 learning governance surface。
- 把 learning recall、staleness/conflict handling、route explainability 正式接入默认 decision surfaces。
- 让操作员看到 learning 对当前建议的影响范围和可信度。

### 2.2 非目标

- 不让 learning 单独决定 gate / release verdict。
- 不把 learn surface 变成第二真相源。

## 3. 设计原则

### 3.1 Learning Is Input, Not Truth

- learning 提供 hint、warning、prior pattern，不直接定义最终真相。

### 3.2 Progressive Disclosure

- learning 默认接入决策，但只展示与当前路由真正相关的部分。

### 3.3 Auditability Over Magic

- 必须能看见 learning 来源、状态、冲突与降级结果。

## 4. 范围

### In scope

- governed learning recall
- stale/conflict downgrade and prune signals
- route explainability in `help / status / ask / deep`
- prior-learning visibility in support surfaces

### Out of scope

- 自动改写冻结 truth
- 用 learning 取代 QA 或 release gate
- 无边界的全量记忆展示

## 5. 功能需求

- FR-001: Beacon must define `beacon-learn` as a host-visible learning governance surface.
- FR-002: Core decision surfaces must support default governed learning injection through progressive disclosure.
- FR-003: When learning is applied, the operator must see which learning influenced the route or judgment and its confidence/staleness state.
- FR-004: Stale or conflicting learning must be downgraded, flagged, or pruned rather than silently reused.
- FR-005: `help / status / ask / deep` must explain route recommendation, evidence gaps, and learning influence in human-readable form.

## 6. 边界 / 分层 / 恢复策略

### 6.1 边界

- learn surface 负责 visibility / audit / governance，不负责 freeze 或 gate verdict。

### 6.2 分层

- `learning record -> governed recall -> route explanation -> operator-visible caution`

### 6.3 恢复策略

- stale/conflicting learning 命中时，降级为 caution 或 prune candidate。
- 若 learning 与冻结 truth 冲突，冻结 truth 优先并要求显式说明。

## 7. 状态轴 / 图示真相

- `learning_state`: `latent -> recalled -> disclosed -> audited -> pruned_or_retained`
- `route_explainability_state`: `implicit -> visible -> reasoned -> evidence_first`

- `branch-flow`
  - `decision request -> governed recall -> route explanation -> next surface`
  - `decision request -> stale/conflict warning -> downgraded influence -> next surface`
- `decision-priority`
  - `frozen truth > gate truth > route safety > learning hints`
  - `visible reasoning > hidden heuristic reuse`
- `state-machine`
  - `learning_state: latent -> recalled -> disclosed -> audited -> pruned_or_retained`
  - `route_explainability_state: implicit -> visible -> reasoned -> evidence_first`

## 风险与缓解

- 风险：stale 或 conflicting learning 被静默复用，污染 route recommendation。
  - 缓解：默认降级为 caution，并在 learn surface 中标出 prune candidate。
- 风险：learning 已参与决策，但操作员看不到其来源和权重。
  - 缓解：在 `help / status / ask / deep` 中显示 learning influence、staleness 和 reason code。

## 8. 验收标准

| AC ID | Description |
| --- | --- |
| AC-001 | `beacon-learn` exists as visible learning governance surface. |
| AC-002 | core decision surfaces support default governed learning injection. |
| AC-003 | operators can see which learning influenced current route/judgment and its confidence/staleness. |
| AC-004 | stale/conflicting learning is downgraded, flagged, or pruned. |
| AC-005 | `help / status / ask / deep` explain route, evidence gap, and learning influence. |
