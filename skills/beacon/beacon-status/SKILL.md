---
name: beacon-status
description: Use when the user wants a board, current stage snapshot, or overall lifecycle state for a Beacon feature through Beacon's current visibility surface.
---

# Beacon Status

This skill routes status inspection through Beacon's `status` surface.

The public command stays on Beacon's current visibility surface and uses the shared read model for lifecycle state and layered verdict projection.

## Use for

- current board view
- current stage snapshot
- lifecycle progress overview
- quick state checks without changing delivery truth
- revision-aware frozen/reopened/re-frozen inspection
- supplement jump visibility for `user-story` and `test-case`
- acceptance kit layered verdict visibility

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
