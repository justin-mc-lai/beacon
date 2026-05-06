---
name: beacon-prd
description: Use when the user wants to draft, refine, clarify, or review a product requirements document through Beacon's current v1.3.9 runtime surface. Keep brainstorm embedded inside the PRD loop rather than sending the user to a standalone brainstorm stage unless explicitly requested.
---

# Beacon PRD

This skill routes requirement work through Beacon's `prd` surface.

The public command stays on the `v1.3.9` runtime line while `v1.3.12` defines the host-native semantic compile target for requirement deepening and human-loop closure.

## Use for

- PRD drafting
- requirement clarification
- missing points / open questions
- business ambiguity closure
- freeze-readiness before story generation

## Operator rule

Prefer Beacon's PRD surface first:

- `beacon prd ...`
- or `bash skills/beacon/scripts/run_beacon.sh prd ...`

Keep the human on the `prd -> user-story -> test-case` closure path. Use brainstorm only as a read-only gap sidecar when the PRD needs deeper convergence, and route frozen changes through `beacon-change`.
