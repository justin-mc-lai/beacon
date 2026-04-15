---
name: beacon-prd
description: Use when the user wants to draft, refine, clarify, or review a product requirements document through Beacon's minimal v1.3.2 human surface. Keep brainstorm embedded inside the PRD loop rather than sending the user to a standalone brainstorm stage unless explicitly requested.
---

# Beacon PRD

This skill routes requirement work through Beacon's `prd` surface.

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

Keep the human on the `prd -> user-story` path. Do not expand the visible workflow unless the user explicitly asks for deeper internal lanes.
