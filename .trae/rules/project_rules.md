<!-- BEACON:AGENT_SURFACE:START -->
<!-- BEACON:VERSION:v1.4.0 -->
<!-- BEACON:DOCS_VERSION:v1.4.0 -->
# Beacon Trae Project Rules

- Prefer project-local Beacon skills under `.trae/skills/`.
- Prefer `beacon <subcommand>` as the stable execution entry.
- Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.
- If skill materialization drifts, run `beacon doctor setup-agent-surface --project-root . --agent trae`.
- Verify Trae skill availability with `beacon doctor verify-agent-surface --project-root . --agent trae --strict`.
<!-- BEACON:AGENT_SURFACE:END -->

