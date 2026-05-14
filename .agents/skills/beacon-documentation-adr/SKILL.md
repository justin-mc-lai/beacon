---
name: beacon-documentation-adr
description: Use when the user wants Beacon to strengthen architecture or delivery clarity through documentation and ADR-style support without confusing supporting documents with canonical requirement truth.
---

# Beacon Documentation ADR

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
- if canonical promise, scope, or acceptance must change, route to `beacon-change`

## Workflow / Decision Loop

- identify which technical or architectural decision actually needs a readable rationale
- separate canonical truth from supporting explanation and ADR material
- capture the minimum decision record that improves maintenance, review, or delivery clarity
- route the result back to `beacon-change`, `beacon-implement`, `beacon-qa`, or `beacon-release` as needed

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
  - “我要正式更新冻结 requirement truth。” -> 应去 `beacon-change`
  - “我要正式给 release verdict。” -> 应去 `beacon-release`

## Cold-start anchors

- `documentation-adr` 处理的是说明层和决策可读性，不是 canonical truth 写回。
- 好的 ADR 记录的是为什么，而不是把实现再复述一遍。
- supporting docs 只在真能改善维护和判断时才应该存在。
