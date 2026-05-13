---
name: beacon-status
description: Use when the user wants a board, current stage snapshot, or overall lifecycle state for a Beacon feature through Beacon's current visibility surface.
---

# Beacon Status

## Overview

This skill routes status inspection through Beacon's `status` support surface.

It provides lifecycle/read-model visibility without changing requirement truth or execution state by itself.

## When to Use

- current board view
- current stage snapshot
- lifecycle progress overview
- quick state checks without changing delivery truth
- revision-aware frozen/reopened/re-frozen inspection
- supplement jump visibility for `user-story` and `test-case`
- acceptance kit layered verdict visibility

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not substitute for PRD, QA, or release decisions

## Workflow / Decision Loop

- inspect lifecycle state and layered verdict projections
- show where the feature is, what is blocked, and which route is implied next
- pair with `beacon-change` when frozen features need scope adjustment

## Common Rationalizations

- “status 看着差不多，就算通过。” -> 不允许；status 不是 verdict
- “有 board 了，就不需要 requirement/gate surface 了。” -> 不允许；status 只读
- “revision 乱了，status 直接帮我改。” -> 不允许；状态修复要回 `doctor` 或 truth surface

## Red Flags

- board/snapshot 被当成正式 acceptance 或 release 结论
- 生命周期状态和下一跳完全脱节
- 状态展示掩盖了 frozen/reopened 差异

## Verification

- current stage, blockers, and next-step visibility are explicit
- frozen/reopened/re-frozen state remains distinguishable
- no status payload is mistaken for formal truth mutation

## Evidence Produced

- board/snapshot projection
- lifecycle and layered-verdict visibility

## State Updated

- none by default
- read-model visibility only

## Gate Impact

- no direct gate verdict
- can prevent misrouting by revealing missing closure or blocker state

## Operator rule

Prefer:

- `beacon status ...`
- or `beacon status ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh status ...`)

Use status for visibility, not as a substitute for PRD, story, QA, or release decisions.
When status shows a frozen feature that now needs scope adjustment, pair it with `beacon-change`.

## Examples

- 适用例：
  - “我想看这条 feature 现在在哪个阶段、卡在哪里。”
  - “先给我一个 board / snapshot，不要改任何 truth。”
- 不适用例：
  - “我要正式判断 release readiness 或改 requirement truth。” -> 应去对应主链 surface
