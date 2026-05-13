---
name: beacon-help
description: Use when the user asks what Beacon should do next, is blocked in the Beacon lifecycle, or needs stage-aware guidance through Beacon's current guidance surface.
---

# Beacon Help

## Overview

This skill routes next-step guidance through Beacon's `help` support surface.

It explains where the user is in the current loop and which mainline surface should run next. It does not redefine truth or act as a release gate.

## When to Use

- "what next?"
- "where am I in Beacon?"
- blocked workflow progression
- stage-aware resume guidance
- frozen feature change-loop guidance
- requirement gap, supplement, and re-freeze routing

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not substitute for PRD, story, QA, or release decisions

## Workflow / Decision Loop

- inspect current workflow/read-model state
- explain current blockers, missing proof, or missing requirement closure
- route to `brainstorm`, `change`, `user-story`, `test-case`, `implement`, `qa`, or `release` as appropriate
- stop at guidance; do not self-author canonical truth

## Common Rationalizations

- “help 都说清楚了，就不用回主链了。” -> 不允许；它只解释和 route
- “卡住时先讲内部 lane 细节给用户。” -> 不允许；先给低摩擦 next-step guidance
- “状态有点乱，help 直接替我改掉就行。” -> 不允许；修复要去 `doctor` 或 truth surface

## Red Flags

- next-step guidance 没有明确 surface
- requirement gap 已经明确，但仍停留在泛泛建议
- 用 `help` 代替正式 `change` / `qa` / `release` 判断

## Verification

- guidance outputs current status, blocker, next step, and fallback route
- frozen-feature change scenarios route to `beacon-change`
- open gap but unchanged truth routes to read-only convergence first when appropriate

## Evidence Produced

- route recommendation
- blocked reason digest
- layered verdict summary when available

## State Updated

- none by default
- may project support/read-model state only

## Gate Impact

- no direct gate verdict
- can stop premature progression by routing back to the right mainline surface

## Operator rule

Prefer:

- `beacon help ...`
- or `beacon help ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh help ...`)

Use `beacon-help` before exposing low-level machine lanes or asking the user to reason about Beacon internals.
When the user is changing a frozen feature, prefer routing to `beacon-change` rather than explaining hidden `reopen/freeze` mechanics directly.
When a gap is still open but frozen truth is unchanged, prefer `beacon-brainstorm` for read-only convergence and then route to `beacon-user-story` or `beacon-test-case` for补料.

## Examples

- 适用例：
  - “我现在该做什么？”
  - “我被卡住了，但不知道是该回 story、test-case、qa 还是 change。”
- 不适用例：
  - “我已经明确知道要执行哪条主链动作。” -> 直接去对应 surface
