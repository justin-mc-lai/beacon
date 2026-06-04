# Beacon Revision Delta

- feature: `implement-mode-frozen-truth-requirement-contract`
- version: `v1.4.11`
- revision_id: `R2`
- source_revision_id: `R1`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `1`
- added_requirement_count: `10`

## Removed Requirement Surfaces
- `AC-001` Acceptance criteria TBD

## Added Requirement Surfaces
- `AC-007` Each AC coverage row includes evidence or a blocking note.
- `AC-005` The prompt requires an AC coverage matrix before QA handoff.
- `AC-006` The AC coverage matrix records each AC as `pass`, `partial`, or `blocked`.
- `AC-001` The default implement task prompt includes existing root-level `DESIGN.md` as project-level design truth.
- `AC-008` Simple, team, and ralph remain implement modes under `beacon-implement`; no new public implement mode skill is introduced.
- `AC-003` Missing `DESIGN.md` or `PRODUCT.md` does not block prompt generation.
- `AC-002` The default implement task prompt includes existing root-level `PRODUCT.md` as project-level product truth.
- `AC-009` Tests cover project truth injection and AC coverage matrix wording.
- `AC-010` This change stays anchored to `build_default_task_prompt`; team-worker injection and ralph baseline hash enforcement are not included.
- `AC-004` The prompt distinguishes project-level product/design truth from frozen PRD/user-story/test-case requirement truth.
