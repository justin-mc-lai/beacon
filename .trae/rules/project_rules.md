<!-- BEACON:AGENT_SURFACE:START -->
<!-- BEACON:VERSION:v1.5.0 -->
<!-- BEACON:DOCS_VERSION:v1.5.0 -->
# Beacon Trae Project Rules

- Prefer project-local Beacon skills under `.trae/skills/`.
- Prefer `beacon <subcommand>` as the stable execution entry.
- Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.
- If skill materialization drifts, run `beacon doctor setup-agent-surface --project-root . --agent trae`.
- Verify Trae skill availability with `beacon doctor verify-agent-surface --project-root . --agent trae --strict`.

## Installed Beacon Skills

- `beacon-archive`
- `beacon-brainstorm`
- `beacon-ceo-review`
- `beacon-change`
- `beacon-change-refreeze`
- `beacon-context-engineering`
- `beacon-debug-recovery`
- `beacon-deep`
- `beacon-design`
- `beacon-design-bootstrap`
- `beacon-design-explore`
- `beacon-design-extract`
- `beacon-design-library`
- `beacon-design-polish`
- `beacon-design-review`
- `beacon-design-simplify`
- `beacon-design-system`
- `beacon-doctor`
- `beacon-documentation-adr`
- `beacon-doubt-review`
- `beacon-friction-intake`
- `beacon-help`
- `beacon-implement`
- `beacon-learn`
- `beacon-performance-review`
- `beacon-prd`
- `beacon-prd-bootstrap`
- `beacon-project-hooks`
- `beacon-prototype`
- `beacon-qa`
- `beacon-qa-evo-deep`
- `beacon-real-project-validation`
- `beacon-release`
- `beacon-security-review`
- `beacon-source-driven`
- `beacon-status`
- `beacon-test-case`
- `beacon-toolkit-automation`
- `beacon-toolkit-branch-governance`
- `beacon-toolkit-lighthouse`
- `beacon-toolkit-metadata`
- `beacon-user-story`
- `using-beacon`
<!-- BEACON:AGENT_SURFACE:END -->



