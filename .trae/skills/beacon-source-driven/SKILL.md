---
name: beacon-source-driven
description: Use when the user wants Beacon to strengthen implementation or review by anchoring work to source truth, actual code, and evidence instead of speculative restatement or free-form reasoning.
---

# Beacon Source Driven

## Overview

This is a support surface for source-anchored execution and review.

It keeps work tied to actual source truth, code, interfaces, tests, and evidence rather than letting the workflow drift into speculative restatement. It is not itself a truth author or a release gate.

## When to Use

- implementation should stay tightly anchored to existing code or interfaces
- review should prefer actual evidence over paraphrased intent
- the user wants stronger source-driven discipline before `beacon-implement` or `beacon-qa`
- there is risk of the model inventing behavior that source materials do not support

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not redefine canonical requirement truth
- if frozen promise or acceptance must change, route to `beacon-change`

## Workflow / Decision Loop

- identify the highest-authority source material for the current task
- keep claims anchored to requirement docs, code, interfaces, tests, or runtime evidence
- challenge any reasoning that outruns available source support
- route back to truth or execution surfaces with explicit source-backed guidance

## Common Rationalizations

- “大概意思差不多，直接按常识补齐。” -> 不允许；先看 source 是否支持
- “source-driven 太慢，不如直接发挥。” -> 不允许；无锚推断更容易漂移
- “既然 source 不完整，就顺手把 acceptance 也改了。” -> 不允许；改 truth 要回 `change`

## Red Flags

- 关键结论没有 source anchor
- 代码或接口已经给出反例，但 reasoning 仍继续自洽
- 把 source-driven review 错当成 formal QA/release verdict

## Verification

- 输出能指出本轮判断依赖的主要 source
- 没有 source 支撑的推断被明确降级为假设或疑点
- 若 source 与 frozen truth 冲突，会显式 route back

## Evidence Produced

- source anchor summary
- unsupported-claim warnings
- route recommendation for execution, truth repair, or QA follow-up

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- can block blind continuation by exposing claims that outrun source support

## Examples

- 适用例：
  - “这轮实现必须强锚定现有代码和接口，不要让解释跑到 source 前面。”
  - “我想先看这条判断有没有被 requirement、代码、测试或证据真正支撑。”
- 不适用例：
  - “我要正式给 release verdict。” -> 应去 `beacon-release`
  - “我要正式补 frozen requirement truth。” -> 应去 `beacon-change`

## Cold-start anchors

- `source-driven` 的核心不是多读材料，而是提高 claims 的锚定强度。
- 它更像执行前和评审时的防漂移支持层。
- source 不足时，可以暴露风险，但不能擅自改 truth。
