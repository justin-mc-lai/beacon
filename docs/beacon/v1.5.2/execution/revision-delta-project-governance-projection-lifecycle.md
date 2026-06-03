# Beacon Revision Delta

- feature: `project-governance-projection-lifecycle`
- version: `v1.5.2`
- revision_id: `R2`
- source_revision_id: `R1`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `1`
- added_requirement_count: `10`

## Removed Requirement Surfaces
- `AC-001` Acceptance criteria TBD

## Added Requirement Surfaces
- `AC-009` `beacon doctor metadata archive-version --version <v>` sets contract `validation_state: archived` via the same MD transaction as upsert (no JSON sink).
- `AC-010` `beacon doctor metadata prune-archived` removes archived `###` blocks from governance MD with `--dry-run` default; strict verify passes after prune.
- `AC-001` Parent feature AC-002
- `AC-008` `resolve_project_governance(version=…)` uses **active** contract for branch preflight; **archived** contracts are ignored unless `--include-archived` (doctor/inspect only).
- `AC-004` `project_metadata_current` / events store `source_hash` from governance MD frontmatter; full `payload_json` is optional diagnostic cache, not a competing write authority.
- `AC-006` No commit path may load sqlite `payload_json` to mutate governance MD; commits flow MD → sqlite projection only.
- `AC-003` `resolve_truth_map` / entrypoint inventory documents governance truth vs sqlite projection roles for operators and skills.
- `AC-002` `VERSION_GOVERNANCE_SURFACES.project_governance` remains the only truth surface (`version_governance_truth`, `is_truth=True`) for `docs/beacon/governance/project-version-governance.md`.
- `AC-005` `doctor metadata verify` (and governance verify helper) fails closed when MD `source_hash` ≠ sqlite `source_hash` or sqlite row missing while MD authoritative (`reason_code`: `governance_projection_drift`).
- `AC-007` `beacon-project-governance-v1` accepts `validation_state: active \
