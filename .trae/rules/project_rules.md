<!-- BEACON:AGENT_SURFACE:START -->
<!-- BEACON:VERSION:v1.6.14 -->
<!-- BEACON:DOCS_VERSION:v1.6.14 -->
# Beacon Trae Project Rules

- Prefer project-local Beacon skills under `.trae/skills/`.
- Prefer `beacon <subcommand>` as the stable execution entry.
- Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.
- If skill materialization drifts, run `beacon doctor setup-agent-surface --project-root . --agent trae`.
- Verify Trae skill availability with `beacon doctor verify-agent-surface --project-root . --agent trae --strict`.

## Installed Beacon Skills

- `beacon-goal`
- `beacon-plan`
- `beacon-truth`
- `beacon-design`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
<!-- BEACON:AGENT_SURFACE:END -->











