---
name: beacon-ceo-review
description: Use when the user wants a founder/CEO-grade challenge on a Beacon version or major feature before requirement truth is revised or implementation continues.
---

# Beacon CEO Review

## Overview

This is a host-visible support/review surface for version-level or major-feature challenge.

It challenges promise level, scope, and framing, then routes accepted changes back into Beacon truth surfaces. It is not itself a truth or gate surface.

## When to Use

- problem reframing
- scope challenge
- expand / hold / reduce / reframe judgment
- version-level promise review before implementation

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not freeze truth directly
- does not replace `beacon-change` or `beacon-prd`

## Workflow / Decision Loop

- bind current review to the active requirement package
- challenge problem framing, promise size, and scope direction
- return `hold`, `expand`, `reduce`, or `reframe`
- if the outcome changes accepted promise or scope, route to `beacon-change`
- if the outcome holds, route back to `beacon-implement`

## Common Rationalizations

- “CEO review 只是意见，不用绑定 requirement package。” -> 不允许；高风险挑战必须绑到 truth refs
- “结论已经很明确，可以直接当 freeze verdict。” -> 不允许；仍需回主链
- “只是版本级 review，不需要 evidence/state/gate 影响。” -> 不允许；挑战结果必须能投影回 route

## Red Flags

- review 结果没有 truth refs
- 挑战结论停留在自由文本，没有下一跳
- 把 `ceo-review` 当成正式 change writeback surface

## Verification

- 版本或 feature 级 challenge 明确绑定 requirement package
- `hold` 与 writeback 类 verdict 的 route 不混淆
- support-surface 结论能回到 `beacon-change` 或 `beacon-implement`

## Evidence Produced

- support-surface transaction
- truth refs and route decision
- operator-visible challenge summary

## State Updated

- support-surface transaction state
- latest advisory/review status projection

## Gate Impact

- no direct gate verdict
- can block blind continuation by routing accepted scope/promise changes back to `beacon-change`

## Operator rule

Prefer:

```bash
beacon review ceo "<feature>" --project . --version auto --focus full --json
```

If the result is `hold`, return to `beacon-implement`.
If the result is `expand`, `reduce`, or `reframe`, route to `beacon change run ...`.

## Examples

- 适用例：
  - “这个版本承诺是不是太大了，需要先从 CEO/产品视角挑战一下范围和 promise。”
  - “我不确定该扩、该收，还是该重构问题定义。”
- 不适用例：
  - “我已经确定要正式修改冻结 truth。” -> 应去 `beacon-change`
