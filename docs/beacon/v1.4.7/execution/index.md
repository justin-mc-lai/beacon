# Execution Index (v1.4.7)

## Human Primary Surface

- `boundaries.md`
- `architecture-blueprint.md`
- `human-skill-reference.md`
- `project-skill-qa-evolution-blueprint.md`
- release-facing execution notes under this version line

## Machine Secondary Surface

- `docs/beacon/v1.4.7/.machine/execution/`

## Notes

- `execution/` remains Markdown-first for host operators.
- `.beacon/` remains runtime internal state only.
- `v1.4.7` promotes the meta-protocol and bounded automation slices into the active runtime/docs line, but keeps the lifecycle compact.

## Runtime Focus

- main `beacon` skill is now a thinner host-level meta-protocol
- horizontal engineering support skills are host-visible but remain support-only
- bounded automation runtime remains fail-closed around truth barriers, queue safety, and promotion-proof semantics
