---
name: beacon-debug-recovery
description: Use when the user wants Beacon to help diagnose a blocked implementation or verification path and recover the workflow without confusing repair support with requirement or release authority.
---

# Beacon Debug Recovery

## Overview

This is a support surface for blocked-path diagnosis and recovery.

It helps identify why implementation, QA, or release is stuck, then routes the repair back to the correct surface. It does not become a hidden replacement for `change`, `implement`, `qa`, or `release`.

## When to Use

- the workflow is blocked and the user needs recovery, not just status
- implementation or QA failures are noisy and the actual repair route is unclear
- the user wants debug-focused support before returning to the mainline
- the current problem feels like mixed context, broken assumptions, or runtime confusion

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not silently repair canonical truth
- if frozen truth itself must change, route to `beacon-change`

## Workflow / Decision Loop

- identify the actual blocker family: truth drift, execution gap, verification gap, environment issue, or mixed context
- reduce the failure to the smallest actionable repair path
- separate what is broken from what is merely noisy
- route the result back to `beacon-change`, `beacon-implement`, `beacon-qa`, `beacon-release`, or `beacon-doctor`

## Common Rationalizations

- “先多试几次，说不定就好了。” -> 不允许；先找 blocker family
- “卡住就把一切都当成 doctor 问题。” -> 不允许；先分 truth / execution / qa / environment
- “debug recovery 已经看明白了，直接在这里结案。” -> 不允许；修复仍要回主链

## Red Flags

- blocker family 没分清，修复建议过宽
- 把环境/上下文噪声错当成产品结论
- 用 debug support 代替正式 QA 或 release verdict

## Verification

- 输出能明确指出 blocker family 和下一跳
- noisy symptoms 与真实 repair path 被分离
- 若卡住原因属于 truth drift，会显式 route back

## Evidence Produced

- blocker diagnosis
- repair route summary
- recovery recommendation

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- can stop blind thrashing by reducing the failure to the right repair surface

## Examples

- 适用例：
  - “这轮实现/QA 卡住了，但我不确定该回改需求、修代码，还是修环境。”
  - “我想先把失败面诊断清楚，再回主链继续。”
- 不适用例：
  - “我要正式执行 doctor 修复环境。” -> 应去 `beacon-doctor`
  - “我要正式给 release verdict。” -> 应去 `beacon-release`

## Cold-start anchors

- `debug-recovery` 的职责是分诊和回路由，不是隐藏主流程。
- 修复路径要尽量小，不要把所有异常都糊成一个大问题。
- 看明白原因之后，仍然要回正确的主链 surface 处理。
