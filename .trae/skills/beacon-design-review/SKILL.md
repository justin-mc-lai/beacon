---
name: beacon-design-review
description: Use when the user wants Beacon to challenge UI/UX direction and decide whether a feature should enter formal prototype freeze.
---

# Beacon Design Review

## Overview

This is a host-visible support/review surface for UI/UX direction challenge.

It separates design judgment from prototype freeze and routes outcomes back to `prototype`, `change`, `user-story`, `test-case`, or `implement` as needed.

## When to Use

- hierarchy review
- state clarity review
- interaction coherence review
- prototype entry decision

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not replace `beacon-prototype`
- does not act as final UI authority

## Workflow / Decision Loop

- challenge hierarchy, state clarity, and interaction coherence
- decide whether prototype entry is ready, not required, or revision is needed
- route to `beacon-prototype`, `beacon-change`, `beacon-user-story`, `beacon-test-case`, or `beacon-implement`
- leave the formal freeze to downstream truth or prototype surfaces

## Common Rationalizations

- “design review 过了，就算 prototype freeze 了。” -> 不允许；它只做 entry judgment
- “只是交互小问题，不用回 requirement surface。” -> 不允许；如果影响 acceptance/behavior 就要回主链
- “视觉方向结论不需要 evidence 或 route。” -> 不允许；support result 必须有下一跳

## Red Flags

- UI/UX verdict 没有明确 prototype/change/implement route
- 设计 review 被当成最终 UI authority
- 支持面输出没有说明它影响的是 design、truth 还是 execution

## Verification

- prototype entry judgment clear and auditable
- mismatch between design and requirement truth routes back correctly
- no silent promotion from review verdict to frozen prototype truth

## Evidence Produced

- support-surface transaction
- design verdict and issue summary
- route decision and writeback targets when needed

## State Updated

- design-review transaction state

## Gate Impact

- no direct release gate verdict
- may block prototype or implementation entry until design mismatch is resolved

## Operator rule

Prefer:

```bash
beacon review design "<feature>" --project . --version auto --json
```

If the result clears prototype entry, route to `beacon-prototype`.
If the result exposes design or requirement mismatch, route to `beacon change run ...`, `beacon-user-story`, or `beacon-test-case`.

## Examples

- 适用例：
  - “这个 UI/UX 方向是不是足够清楚，可以进入 prototype freeze。”
  - “我想先 challenge 一下层级、状态和交互一致性。”
- 不适用例：
  - “我要正式生成 prototype bundle。” -> 应去 `beacon-prototype`
