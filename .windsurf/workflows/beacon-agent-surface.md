---
description: Beacon v1.4.5 agent skill surface and routing
---
<!-- BEACON:AGENT_SURFACE:START -->
<!-- BEACON:VERSION:v1.4.5 -->
<!-- BEACON:DOCS_VERSION:v1.4.5 -->
# Beacon Windsurf Agent Surface

Use this workflow to discover and route to project-local Beacon skills.

1. Prefer project-local Beacon skills under `.windsurf/skills/`.
2. Use `beacon <subcommand>` as the stable local execution surface.
3. Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.
4. Refresh with `beacon doctor setup-agent-surface --project-root . --agent windsurf`.
5. Verify with `beacon doctor verify-agent-surface --project-root . --agent windsurf --strict`.

## Installed Beacon Skills

- `beacon-archive`
- `beacon-brainstorm`
- `beacon-ceo-review`
- `beacon-change`
- `beacon-deep`
- `beacon-design-review`
- `beacon-doctor`
- `beacon-friction-intake`
- `beacon-help`
- `beacon-implement`
- `beacon-learn`
- `beacon-prd`
- `beacon-prd-bootstrap`
- `beacon-prototype`
- `beacon-qa`
- `beacon-real-project-validation`
- `beacon-release`
- `beacon-status`
- `beacon-test-case`
- `beacon-toolkit-branch-governance`
- `beacon-toolkit-lighthouse`
- `beacon-toolkit-metadata`
- `beacon-user-story`
- `using-beacon`
<!-- BEACON:AGENT_SURFACE:END -->




