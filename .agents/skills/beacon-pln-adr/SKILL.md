---
name: beacon-pln-adr
description: Beacon v1.6.0 planner skill migrated from `beacon-documentation-adr`. Use when the user wants Beacon to strengthen architecture or delivery clarity through documentation and ADR-style support without confusing supporting documents with canonical requirement truth.
---

# Beacon Planner Documentation Adr

## Overview

This is a support surface for architecture and delivery documentation clarity.

It helps capture decision rationale, tradeoffs, and operational meaning in a readable way without silently promoting support documents into canonical truth.

## When to Use

- the user needs ADR-style clarification for a technical choice
- architecture, delivery, or operational reasoning should be made more readable
- a feature is hard to maintain because decision rationale is missing
- the user wants stronger documentation support before `implement`, `qa`, or `release`

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen requirement truth by itself
- if canonical promise, scope, or acceptance must change, route to `beacon-gen-change`

## Workflow / Decision Loop

- identify which technical or architectural decision actually needs a readable rationale
- separate canonical truth from supporting explanation and ADR material
- capture the minimum decision record that improves maintenance, review, or delivery clarity
- route the result back to `beacon-gen-change`, `beacon-gen-implement`, `beacon-eval-qa`, or `beacon-eval-release` as needed

## Common Rationalizations

- “文档写清楚一点就等于 truth 也改了。” -> 不允许；说明层不自动改 canonical truth
- “ADR 只是记录，不需要讲取舍和边界。” -> 不允许；没有 tradeoff 的记录价值很低
- “支持文档多写一点总没坏处。” -> 不允许；只写真正改善决策和维护的最小必要层

## Red Flags

- supporting docs 被误当成 canonical truth
- ADR 没有明确 decision / tradeoff / consequence
- 文档化输出没有回路由或消费面

## Verification

- 输出能指出 decision、tradeoff、consequence 或 operator-facing clarification 中的至少一项
- supporting docs 与 canonical truth 的边界明确
- 若文档化发现 truth drift，会显式 route back

## Evidence Produced

- ADR or documentation recommendation
- decision / tradeoff summary
- route recommendation and consumption hint

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- can block blind continuation when unreadable or missing rationale hides real implementation or release risk

## Examples

- 适用例：
  - “这条架构决策需要补一页轻量 ADR，不然维护者看不懂为什么这么做。”
  - “功能没变，但设计取舍和后果要写清楚，避免后面误判。”
- 不适用例：
  - “我要正式更新冻结 requirement truth。” -> 应去 `beacon-gen-change`
  - “我要正式给 release verdict。” -> 应去 `beacon-eval-release`

## Cold-start anchors

- `documentation-adr` 处理的是说明层和决策可读性，不是 canonical truth 写回。
- 好的 ADR 记录的是为什么，而不是把实现再复述一遍。
- supporting docs 只在真能改善维护和判断时才应该存在。


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 planner skill。
禁止调用 implementation/generator/evaluator/release 类 skill。
禁止写代码、搭脚手架、修改 package truth、修改 `.machine/`、给 QA/release verdict。
你的唯一产出是 research/planning artifact、gap/risk 分析、湖/海判断和 route recommendation。
如需进入 truth/change/refreeze/generate/evaluate，必须停止并路由，等待用户确认。

## v1.6.0 Harness Migration

- Harness：`planner`。
- 来源迁移：`beacon-documentation-adr` -> `beacon-pln-adr`。
- 主要作用：ADR 和文档清晰度分析。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-documentation-adr` -> `beacon-pln-adr`。
- 主要作用：ADR 和文档清晰度分析。
- 默认语言：中文为主；英文只用于稳定术语、路径、命令或协议标识。

## 边界

- Planner 只产出 research/planning artifact 和 route recommendation，不写 truth、implementation、QA verdict 或 release verdict。
- Generator 只在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact，不自证完成。
- Evaluator 只产出 evidence verdict、finding、reason code 和 route recommendation，不改 truth、不修 implementation。
- Governor 只维护 context、metadata、archive、hooks、automation、status 和 diagnostic support，不成为主生命周期 stage。

## 路由

- 粗提示词先归约为 outcome、truth/source/evidence refs、湖/海、truth_gap、test_gap、implementation_risk、verification_risk 和 recommended_route。
- `docs/beacon/<version>/research/<feature-slug>.md` 是 planner `support_advisory` artifact；没有用户确认和 `promotion_ref`，不能升级为 requirement truth。
- 需要跨 harness 时，停止当前动作，输出 route recommendation，并等待用户确认。
