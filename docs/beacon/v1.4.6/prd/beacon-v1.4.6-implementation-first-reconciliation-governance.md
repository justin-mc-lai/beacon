# PRD: Beacon v1.4.6 implementation-first reconciliation governance

**Feature**: `beacon-v1.4.6-implementation-first-reconciliation-governance`  
**Version**: `v1.4.6`  
**Date**: `2026-05-14`  
**Status**: `freeze-ready`  
**Track**: `anti-drift-recovery + change-governance`  
**Scenario**: `execution_outpaces_frozen_truth_and_must_be_honestly_reconciled`

## Context

- Version summary: `docs/beacon/v1.4.6/SUMMARY.md`
- Anti-drift baseline:
  - `docs/beacon/v1.4.6/prd/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- Existing change router:
  - `skills/beacon/beacon-change/SKILL.md`
- Existing implement boundary:
  - `skills/beacon/beacon-implement/SKILL.md`
- Product tension:
  - Beacon requires truth-first delivery.
  - Real work can still produce a failure mode where implementation lands before frozen truth is refreshed.
  - If Beacon only allows post-hoc writeback without explicit recovery semantics, it preserves final docs shape but loses delivery provenance.

## 1. Overview

Beacon needs an explicit recovery contract for implementation-first drift so reconciliation remains honest, routes back through `beacon-change`, and preserves provenance instead of pretending post-hoc truth was truth-first delivery.

## 1. 问题

Beacon 已明确不接受：

- “代码先做，后面再补 truth”
- “先修代码，最后再补文档”

但当前系统还缺少一个最小、诚实、可治理的恢复策略，来处理已经发生的 truth drift。

没有这层恢复治理时，团队会自然滑向两种坏结果：

- 把 post-hoc writeback 假装成 pre-implement truth
- 用 support surface、toolkit、implementation artifact 反向定义 requirement truth

这会直接破坏 Beacon 的原始交付真相：

- requirement truth must lead execution
- support surfaces are not truth sources
- implementation progress is not completion truth

## 2. 目标

1. 为 Beacon 定义一种最小的 truth recovery 机制，处理 implementation 已先于 truth 落地的场景
2. 保持 `beacon-change` 仍是唯一正式 truth reopen surface
3. 保留 drift 历史，不允许用事后回填抹平真实因果顺序
4. 要求受影响的 QA / release-facing proof 在 truth 补齐后重新投影或重新验证

## 2. Scope

### In scope

- define implementation-first reconciliation as recovery semantics
- freeze the reconciliation artifact contract
- require reprojection/revalidation of affected QA and release-facing proof
- keep `beacon-change` as the only formal truth recovery route

### Out of scope

- add a new public lifecycle stage
- allow support surfaces or implementation artifacts to redefine requirement truth
- auto-accept truth drift without formal change/recovery governance

## 3. 设计原则

### 3.1 这是 recovery governance，不是常规交付路径

`implementation-first reconciliation` 只能用于承认并恢复已经发生的 truth drift。

它不是鼓励先实现后补 truth 的正常模式。

### 3.2 不新增主生命周期 stage

该能力必须挂在 `beacon-change` 之下。

不允许：

- 新增一级 lifecycle stage
- 新增平行 truth surface
- 新增 support surface 来替代 `change`

### 3.3 必须保留 provenance，而不是只保留最终文档状态

恢复完成后，Beacon 不只需要“文档已经补齐”，还必须保留：

- 哪些实现先发生
- 当时缺哪些 truth
- 为什么会先实现
- 哪些 artifacts 先落地
- 哪些 proof 后续被重新投影

### 3.4 重新收口到 truth-first，而不是给 post-hoc writeback 开绿灯

该机制的目标是恢复 Beacon 的 truth-first 模型，而不是合法化 truth-last。

## 4. 范围

### In scope

- 定义 implementation-first reconciliation 的治理语义
- 明确它必须通过 `beacon-change` 路由
- 定义最小 reconciliation artifact contract
- 定义受影响 QA / release proof 的重新投影要求

### Out of scope

- 新增公开一级主命令
- 新增新的 support surface
- 自动根据实现反写 PRD / user-story / test-case 内容
- 自动推断 drift 是否可接受而跳过 formal change

## 5. 功能需求

### FR-001 Beacon 必须定义 implementation-first reconciliation 为异常恢复语义

该语义必须明确表示：

- truth drift 已经发生
- 当前动作是恢复，不是普通 writeback
- 后续需要 re-freeze

### FR-002 Reconciliation 必须通过 `beacon-change` 路由

Beacon 不得新增并鼓励使用新的一级 public stage 处理该问题。

正式 route 必须仍为：

- `beacon-change`

### FR-003 Beacon 必须冻结 reconciliation artifact contract

至少包含：

- feature / version
- drift_detected_at 或 equivalent recovery timestamp
- implementation_artifacts
- missing_truth_surfaces
- recovery_reason
- truth_surfaces_backfilled
- re_freeze_status
- reprojection_targets

### FR-004 补 truth 后必须重新收口受影响 proof

若 reconciliation 影响 acceptance、coverage、scope、promise、release claim，则 Beacon 必须要求重新投影或重跑相关 proof。

至少显式列出：

- `user-story`
- `qa/test-cases`
- QA proof
- release-facing proof

### FR-005 Beacon 不得把 reconciliation 伪装成正常 truth-first 交付

在 human-facing 和 machine-facing contract 中，都必须能看出：

- this feature required recovery
- post-hoc writeback did occur
- the final state should not erase the drift history

## 6. 验收标准

| AC ID | 说明 |
| --- | --- |
| AC-001 | Beacon defines implementation-first reconciliation as recovery semantics rather than a normal delivery mode |
| AC-002 | implementation-first reconciliation routes through `beacon-change` instead of a new public stage |
| AC-003 | Beacon freezes a minimal reconciliation artifact contract |
| AC-004 | affected truth and proof surfaces must be reprojected or revalidated after reconciliation |
| AC-005 | Beacon preserves drift provenance instead of treating post-hoc writeback as if it were pre-implementation truth |
