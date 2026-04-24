---
name: beacon-status
description: Use when the user wants a board, current stage snapshot, or overall lifecycle state for a Beacon feature through Beacon's current v1.3.7 runtime surface.
---

# Beacon Status

This skill routes status inspection through Beacon's `status` surface.

The public command stays on the `v1.3.7` runtime line while `v1.3.7` defines the shared read model for lifecycle visibility and delivery state.

## Use for

- current board view
- current stage snapshot
- lifecycle progress overview
- quick state checks without changing delivery truth
- revision-aware frozen/reopened/re-frozen inspection

## Operator rule

Prefer:

- `beacon status ...`
- or `bash skills/beacon/scripts/run_beacon.sh status ...`

Use status for visibility, not as a substitute for PRD, story, QA, or release decisions.
When status shows a frozen feature that now needs scope adjustment, pair it with `beacon-change`.
