---
name: beacon-user-story
description: Use when the user wants to derive, refine, review, or freeze user stories and acceptance criteria from a Beacon PRD through the minimal v1.3.2 human surface.
---

# Beacon User Story

This skill routes story work through Beacon's `user-story` surface.

## Use for

- story drafting
- acceptance criteria refinement
- story boundary clarification
- readiness checks before test-case or freeze

## Operator rule

Prefer:

- `beacon user-story ...`
- or `bash skills/beacon/scripts/run_beacon.sh user-story ...`

Keep the human on the `user-story -> test-case` path. Treat internal critique and research as background machine support, not public stages.
