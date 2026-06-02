# Beacon Revision Delta

- feature: `beacon-truth-map-center-and-package-cutover`
- version: `v1.5.1`
- revision_id: `R8`
- source_revision_id: `R7`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `1`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `AC-026` v1.5.1 tracks high-risk truth read/write entrypoints, including PRD/user-story/test-case/workflow/truth/gate commands, PRD bootstrap, requirement clarity/deepening, manifest, acceptance kit, packaged skills, and `.agents/skills`; each entrypoint routes through truth_center/resolver or is explicitly classified as a v1.5.1 legacy/generated/runtime exception with fail-closed or v1.5.2 cutover handling.
