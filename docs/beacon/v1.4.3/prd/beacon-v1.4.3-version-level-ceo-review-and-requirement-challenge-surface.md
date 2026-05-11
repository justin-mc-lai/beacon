# PRD: Beacon v1.4.3 Version-Level CEO Review and Requirement Challenge Surface

**Feature**: `beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface`  
**Version**: `v1.4.3`  
**Date**: `2026-05-11`  
**Status**: `freeze-ready`  
**Track**: `human-surface + requirement-challenge + scope-governance`  
**Scenario**: `version-level-problem-reframing + scope-judgment + truth-safe-routing`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.4.3/SUMMARY.md`
- Execution index: `docs/beacon/v1.4.3/execution/index.md`
- Umbrella PRD: `docs/beacon/v1.4.3/prd/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
- User story: `docs/beacon/v1.4.3/user-story/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md`
- Test cases: `docs/beacon/v1.4.3/qa/test-cases/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md`

## 1. 问题

### 1.1 当前断层

Beacon 当前缺少一个公开的人类面，去在版本级或大 feature 级对 requirement package 做前置挑战。`brainstorm` 能分析和收敛，但不等于：

- CEO / founder 级问题重构
- scope challenge
- `expand / hold / reduce / reframe`
- 对承诺面是否值得推进的上位审视

### 1.2 风险

- 错误问题定义可能在冻结后才被发现。
- scope 不合理时，只能通过 `change` 被动返工，缺少前置 challenge 面。
- 用户无法用公开心智清楚地区分 brainstorming 和 founder-grade challenge。

## 2. 目标

### 2.1 主要目标

- 定义 `beacon-ceo-review` 作为 support/review surface。
- 在不扩张主生命周期的前提下，对版本级 PRD / story / case 进行前置 challenge。
- 把接受后的变化安全路由回 canonical truth surfaces。

### 2.2 非目标

- 不让 `ceo-review` 直接冻结 truth。
- 不把 `ceo-review` 变成新的主命令阶段。

## 3. 设计原则

### 3.1 Strategic Challenge Without Truth Bypass

- 允许强 challenge，但不允许绕过 `prd / change / user-story / test-case`。

### 3.2 Scope Judgment Must Be Explicit

- `expand / hold / reduce / reframe` 必须显式输出，而不是隐式建议。

### 3.3 Human Surface, Not Persona Theater

- `ceo-review` 是公开决策心智面，不是角色扮演套壳。

## 4. 范围

### In scope

- version-level / major-feature requirement challenge
- strategic scope judgment
- wrong-problem / wrong-scope / wrong-promise surfacing
- truth-safe route recommendation

### Out of scope

- 直接改写冻结 PRD
- 代替 `brainstorm` 做普通发散
- 代替 `change` 执行真实 truth 变更

## 5. 功能需求

- FR-001: Beacon must define `beacon-ceo-review` as a host-visible support/review surface.
- FR-002: `ceo-review` must support explicit outputs: `expand`, `hold`, `reduce`, `reframe`.
- FR-003: `ceo-review` must operate at version-level or major-feature level rather than only implementation-local scope.
- FR-004: `ceo-review` must route accepted changes back to `prd / change / user-story / test-case` rather than freezing truth directly.
- FR-005: `ceo-review` must expose why the current proposal may be the wrong problem, wrong scope, or wrong promised surface even if downstream docs are internally coherent.

## 6. 边界 / 分层 / 恢复策略

### 6.1 边界

- `ceo-review` 只做 challenge 和 route recommendation。
- freeze truth 仍归 canonical truth surfaces 所有。

### 6.2 分层

- `problem signal -> ceo-review -> prd/change/user-story/test-case`

### 6.3 恢复策略

- 若 challenge 发现问题定义错误，回路由到 `beacon change` 或上游 PRD refinement。
- 若 scope judgement 与冻结 truth 冲突，冻结 truth 优先，并显式要求变更。

## 7. 状态轴 / 图示真相

- `ceo_review_state`: `not_requested -> challenged -> strategic_judgment_emitted -> routed`
- `requirement_challenge_state`: `unquestioned -> expanded_or_held_or_reduced_or_reframed -> routed_back_to_truth`

- `branch-flow`
  - `problem signal -> ceo-review -> change when truth must reopen`
  - `problem signal -> ceo-review -> implement path unchanged when hold`
- `decision-priority`
  - `frozen truth > route safety > ceo-review recommendation`
  - `wrong-problem detection > local downstream coherence`
- `state-machine`
  - `ceo_review_state: not_requested -> challenged -> strategic_judgment_emitted -> routed`
  - `requirement_challenge_state: unquestioned -> expanded_or_held_or_reduced_or_reframed -> routed_back_to_truth`

## 风险与缓解

- 风险：`ceo-review` 被误解为可以越过 canonical truth surface 直接改需求。
  - 缓解：所有接受后的动作只给出 route recommendation，真实改动仍回到 `change / prd / user-story / test-case`。
- 风险：用户把它当作普通 brainstorming，导致 scope judgment 不显式。
  - 缓解：输出中固定要求 `expand / hold / reduce / reframe` 之一。

## 8. 验收标准

| AC ID | Description |
| --- | --- |
| AC-001 | `beacon-ceo-review` exists as support/review surface rather than lifecycle stage. |
| AC-002 | `ceo-review` supports `expand / hold / reduce / reframe` outputs. |
| AC-003 | `ceo-review` operates at version-level or major-feature level. |
| AC-004 | accepted review outputs route back through canonical truth surfaces. |
| AC-005 | the surface can explain requirement-direction challenge without freezing truth directly. |
