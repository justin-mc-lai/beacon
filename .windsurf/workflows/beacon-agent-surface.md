---
description: Beacon v1.6.3 agent skill surface and routing
---
<!-- BEACON:AGENT_SURFACE:START -->
<!-- BEACON:VERSION:v1.6.3 -->
<!-- BEACON:DOCS_VERSION:v1.6.3 -->
# Beacon Windsurf Agent Surface

Use this workflow to discover and route to project-local Beacon skills.

1. Prefer project-local Beacon skills under `.windsurf/skills/`.
2. Use `beacon <subcommand>` as the stable local execution surface.
3. Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.
4. Refresh with `beacon doctor setup-agent-surface --project-root . --agent windsurf`.
5. Verify with `beacon doctor verify-agent-surface --project-root . --agent windsurf --strict`.

## Installed Beacon Skills

- `beacon-eval-agent`
- `beacon-eval-qa`
- `beacon-eval-qa-deep`
- `beacon-eval-real-project`
- `beacon-eval-release`
- `beacon-gen-change`
- `beacon-gen-design`
- `beacon-gen-design-explore`
- `beacon-gen-design-init`
- `beacon-gen-design-polish`
- `beacon-gen-design-system`
- `beacon-gen-implement`
- `beacon-gen-prototype`
- `beacon-gen-refreeze`
- `beacon-gen-truth`
- `beacon-gen-truth-init`
- `beacon-gov-archive`
- `beacon-gov-automation`
- `beacon-gov-branch`
- `beacon-gov-debug`
- `beacon-gov-doctor`
- `beacon-gov-extract`
- `beacon-gov-help`
- `beacon-gov-hooks`
- `beacon-gov-learn`
- `beacon-gov-library`
- `beacon-gov-lighthouse`
- `beacon-gov-metadata`
- `beacon-gov-router`
- `beacon-gov-status`
- `beacon-pln-brainstorm`
- `beacon-pln-friction`
- `beacon-pln-program`
- `beacon-pln-program-auto`
- `beacon-pln-program-interactive`
- `beacon-pln-review`
- `beacon-pln-source`
<!-- BEACON:AGENT_SURFACE:END -->










