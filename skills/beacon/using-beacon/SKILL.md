---
name: using-beacon
description: Use when Beacon should become the primary workflow router in Codex or Claude for requirements, implementation, QA, release readiness, or next-step guidance. Route the user through Beacon's current v1.3.9 runtime surface instead of exposing the full CLI catalog.
---

# Using Beacon

Use Beacon as a host-native human-facing workflow pack.

The public surface follows the current `v1.3.9` runtime line.
The `v1.3.9` docs define the active host-native delivery baseline, brainstorm sidecar, archive governance, and shared delivery/read-model behavior.

## Public routing targets

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-prototype`
- `beacon-change`
- `beacon-brainstorm`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`
- `beacon-archive`

## Routing rules

1. Requirement clarification, spec writing, missing points, or ambiguous scope:
   use `beacon-prd`
2. User stories, acceptance criteria, or story-level scope:
   use `beacon-user-story`
3. Test and acceptance coverage design:
   use `beacon-test-case`
4. Requirement-driven wireframe freeze or screen-level handoff before implementation:
   use `beacon-prototype`
5. Frozen feature scope change, requirement supplement after freeze, or re-freeze loops:
   use `beacon-change`
6. Continue brainstorming, converge a requirement gap, challenge assumptions, or explore project evolution without changing truth:
   use `beacon-brainstorm`
7. Implementation handoff or execution:
   use `beacon-implement`
8. Verification, acceptance, new findings, or release confidence:
   use `beacon-qa` or `beacon-release`
9. Historical requirement isolation, archive planning, or archive state explanation:
   use `beacon-archive`
10. Blocked / lost / next-step questions:
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
