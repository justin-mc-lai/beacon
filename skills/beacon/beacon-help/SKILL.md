---
name: beacon-help
description: Use when the user asks what Beacon should do next, is blocked in the Beacon lifecycle, or needs stage-aware guidance through Beacon's current v1.3.6 runtime surface.
---

# Beacon Help

This skill routes next-step guidance through Beacon's `help` surface.

The public command stays on the current `v1.3.6` runtime line and uses the shared read model and guidance behavior defined by the `v1.3.6` docs.

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
