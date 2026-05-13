---
name: beacon-help
description: Use when the user asks what Beacon should do next, is blocked in the Beacon lifecycle, or needs stage-aware guidance through Beacon's current guidance surface.
---

# Beacon Help

This skill routes next-step guidance through Beacon's `help` surface.

The public command stays on Beacon's current guidance surface and uses the shared read model for next-step routing.

`Beacon Acceptance Kit v1` is part of the guidance surface. When present, help should show:

- layered verdict
- failed layers
- jump back to `user-story` / `test-case`
- shared proof chain status for `real-project-validation`

## Use for

- "what next?"
- "where am I in Beacon?"
- blocked workflow progression
- stage-aware resume guidance
- frozen feature change-loop guidance
- requirement gap, supplement, and re-freeze routing

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
