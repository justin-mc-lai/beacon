---
name: using-beacon
description: Use when Beacon should become the primary workflow router in Codex or Claude for requirements, implementation, QA, release readiness, or next-step guidance. Route the user into Beacon's minimal v1.3.1 6+3 surface instead of exposing the full CLI catalog.
---

# Using Beacon

Use Beacon as a minimal human-facing workflow pack.

## Public routing targets

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`

## Routing rules

1. Requirement clarification, spec writing, missing points, or ambiguous scope:
   use `beacon-prd`
2. User stories, acceptance criteria, or story-level scope:
   use `beacon-user-story`
3. Test and acceptance coverage design:
   use `beacon-test-case`
4. Implementation handoff or execution:
   use `beacon-implement`
5. Verification, acceptance, new findings, or release confidence:
   use `beacon-qa` or `beacon-release`
6. Blocked / lost / next-step questions:
   use `beacon-help`, `beacon-status`, or `beacon-doctor`

## Boundary

Do not treat these as public human entrypoints unless the user explicitly asks for internals:

- `brainstorm`
- `team`
- `implement-team`
- `qa-team`
- learning / auto research lanes
