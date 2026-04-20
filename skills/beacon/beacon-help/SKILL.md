---
name: beacon-help
description: Use when the user asks what Beacon should do next, is blocked in the Beacon lifecycle, or needs stage-aware guidance through the minimal v1.3.3 human surface.
---

# Beacon Help

This skill routes next-step guidance through Beacon's `help` surface.

## Use for

- "what next?"
- "where am I in Beacon?"
- blocked workflow progression
- stage-aware resume guidance
- frozen feature change-loop guidance

## Operator rule

Prefer:

- `beacon help ...`
- or `bash skills/beacon/scripts/run_beacon.sh help ...`

Use `beacon-help` before exposing low-level machine lanes or asking the user to reason about Beacon internals.
When the user is changing a frozen feature, prefer routing to `beacon-change` rather than explaining hidden `reopen/freeze` mechanics directly.
