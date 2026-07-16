# Beacon Revision Delta

- feature: `legacy-project-v152-cutover`
- version: `v1.5.2`
- revision_id: `R5`
- source_revision_id: `R4`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `1`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `AC-010` Beacon must close the four accepted friction findings with the lowest-cognitive-load route: keep `truth-cutover` as a CLI/machine repair transaction instead of adding a new default public skill, route existing human surfaces to it, add explicit `doctor truth-source-mismatch` diagnostics and repair commands, and regression-test the `technical_review_contract` root fix plus change CLI version stability.
