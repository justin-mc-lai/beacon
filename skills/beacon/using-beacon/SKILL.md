---
name: using-beacon
description: Use when Beacon should become the primary workflow router in Codex or Claude for requirements, implementation, QA, release readiness, or next-step guidance. Route the user into Beacon's minimal v1.3.3 human surface instead of exposing the full CLI catalog.
---

# Using Beacon

Use Beacon as a minimal human-facing workflow pack.

## Public routing targets

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-change`
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
4. Frozen feature scope change, requirement supplement after freeze, or re-freeze loops:
   use `beacon-change`
5. Implementation handoff or execution:
   use `beacon-implement`
6. Verification, acceptance, new findings, or release confidence:
   use `beacon-qa` or `beacon-release`
7. Blocked / lost / next-step questions:
   use `beacon-help`, `beacon-status`, or `beacon-doctor`

## Development pairing

When Beacon is routing implementation or QA for web products, it may be paired with project-local development helpers.

- For page-level UI work on sites that have development-only `page-agent` wiring, keep Beacon as the human-facing router:
  - requirements still route through `beacon-prd`
  - execution still routes through `beacon-implement`
  - verification still routes through `beacon-qa`
- `page-agent` is a development helper inside the implementation/QA loop, not a new public Beacon surface.
- For Codex/OpenAI-backed `page-agent` custom mode, prefer browser-local or preview-local credential injection over storing provider secrets in public runtime config.
- Prefer development-only or preview-only `page-agent` usage unless the user explicitly wants a broader rollout.

## Boundary

Do not treat these as public human entrypoints unless the user explicitly asks for internals:

- `brainstorm`
- `team`
- `implement-team`
- `qa-team`
- learning / auto research lanes
