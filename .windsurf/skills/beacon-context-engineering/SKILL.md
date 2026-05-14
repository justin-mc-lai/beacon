---
name: beacon-context-engineering
description: Use when the user needs Beacon to strengthen execution or review by restructuring context, extracting the minimum working truth, and reducing context drift without rewriting canonical requirement truth.
---

# Beacon Context Engineering

## Overview

This is a support surface for context shaping.

Its job is to improve how work is framed and consumed before or during implementation, QA, or review. It is not a truth source, not a gate source, and not a new lifecycle stage.

## When to Use

- implementation context feels bloated, noisy, or contradictory
- frozen truth exists but the working set is unclear
- too many irrelevant artifacts are competing for attention
- the user needs a smaller, clearer execution context before `beacon-implement` or `beacon-qa`

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen `prd`, `user-story`, `test-case`, or `.machine/`
- if accepted scope or acceptance must change, route to `beacon-change`

## Workflow / Decision Loop

- identify the smallest working context that still preserves frozen truth
- separate canonical truth, active evidence, and low-value noise
- propose the minimum context pack needed for the next mainline surface
- if context confusion hides a real truth gap, route back to `beacon-change`, `beacon-user-story`, or `beacon-test-case`

## Common Rationalizations

- “上下文乱一点没关系，模型自己会补。” -> 不允许；噪声会降低决策质量
- “把 context engineering 的结论直接当 requirement 改掉。” -> 不允许；它只整理上下文，不写 truth
- “只是做上下文收缩，不需要说明保留了哪些 truth。” -> 不允许；working set 必须可解释

## Red Flags

- working context 丢掉了仍然有效的 frozen truth
- context 收缩后，执行面不知道 acceptance 从哪来
- support 输出停留在泛泛建议，没有明确下一跳

## Verification

- working context 能明确说明保留了哪些 canonical truth 和 active evidence
- 缩减后的上下文更利于后续 `implement`、`qa` 或 `review`
- 如果识别到 truth gap，会显式 route back，而不是假装可以直接继续

## Evidence Produced

- context pack recommendation
- keep / discard rationale
- next-surface recommendation

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- may block premature execution by exposing unresolved truth drift or missing evidence anchors

## Examples

- 适用例：
  - “材料很多，但真正和这轮实现有关的上下文不清楚，先帮我收缩 working set。”
  - “我不想改需求，只想把执行前必须记住的 truth、evidence、风险边界理顺。”
- 不适用例：
  - “我要正式改冻结 scope。” -> 应去 `beacon-change`
  - “我现在要代码实现或正式验收。” -> 应去 `beacon-implement` 或 `beacon-qa`

## Cold-start anchors

- `context-engineering` 解决的是上下文质量，不是 truth 写回。
- 它的价值是缩短有效 working set，而不是制造新的文档层。
- 如果整理上下文时发现正式承诺面要改，必须回主链。
