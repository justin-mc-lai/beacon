---
name: beacon-doubt-review
description: Use when the user wants Beacon to challenge self-rationalized plans, surface evidence gaps, and apply doubt-driven review before implementation, QA, or release continues.
---

# Beacon Doubt Review

## Overview

This is a support surface for adversarial doubt.

It is designed to challenge plans or conclusions that may already be self-consistent but not yet well-proven. It does not replace truth surfaces, QA, or release gates.

## When to Use

- a plan feels too smooth and may be self-rationalized
- the user wants explicit evidence-gap challenge before continuing
- implementation or review claims need a harder skeptical pass
- the next step is unclear because confidence is high but proof is thin

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen truth directly
- if accepted scope, promise, or acceptance must change, route to `beacon-change`

## Workflow / Decision Loop

- identify the strongest current claim and the weakest current proof
- search for contradictions, missing evidence, and false certainty
- separate supported conclusions from convenient narratives
- route the result back to `beacon-change`, `beacon-implement`, `beacon-qa`, or `beacon-release` as appropriate

## Common Rationalizations

- “看起来能讲通，就不用继续质疑了。” -> 不允许；可讲通不等于已证实
- “doubt review 只是补充意见，不需要明确下一跳。” -> 不允许；挑战必须回路由
- “既然发现问题，就直接在这里改掉正式 truth。” -> 不允许；support 只 challenge，不直接写 truth

## Red Flags

- 输出只有态度，没有具体疑点或证据缺口
- 明明发现 drift，却没有 route back
- 用怀疑姿态代替正式 QA 或 release gate

## Verification

- challenge 输出至少指出 claim、evidence gap、risk 或 contradiction 之一
- 若问题影响冻结承诺面，会显式回 `beacon-change`
- 若问题只是执行或验证质量问题，会回 `beacon-implement` 或 `beacon-qa`

## Evidence Produced

- doubt register
- contradiction or gap summary
- route recommendation with confidence caveat

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- can stop blind continuation by exposing weak proof or self-rationalized claims

## Examples

- 适用例：
  - “我怀疑这版方案已经开始自我合理化了，帮我做一轮逆向挑战。”
  - “实现看起来差不多，但我不信证据够，先做一轮 doubt review。”
- 不适用例：
  - “我要正式确认 release 放行。” -> 应去 `beacon-release`
  - “我要正式改冻结需求。” -> 应去 `beacon-change`

## Cold-start anchors

- `doubt-review` 的职责是拆穿自洽幻觉，不是制造额外流程。
- 它要把怀疑转成明确的 evidence gap 和下一跳。
- 发现问题后要回主链，不要把 support 面当终点。
