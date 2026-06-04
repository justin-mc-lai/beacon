# Change: beacon-v1.4.4-pragmatic-design-baseline-and-template-governance

**Version**: `v1.4.4`  
**Status**: `planned`  
**Generated**: `2026-05-11`

## Why This Change Exists

Beacon already separated design direction challenge from prototype freeze in `v1.4.3`, but it still lacks a small, reusable default design baseline. Without that baseline, Beacon risks either producing generic UI/UX output or over-correcting by introducing a large family of design-facing skills.

## Delta

- add a restrained default anti-AI UI/UX contract
- freeze exactly 3 default templates
- bind the templates to normalized `apple` / `vercel` reference baselines
- route design quality through existing `design-review / prototype / implement / qa` surfaces
- keep external design repositories as research inputs, not runtime dependencies

## Freeze Intent

This change freezes the design baseline, template catalog, and anti-drift contract. It does not promote `v1.4.4` to runtime release, create a new public command family, or introduce an open-ended design marketplace.

## Traceability

- `docs/beacon/archive/v1.4.4/prd/beacon-v1.4.4-pragmatic-design-baseline-and-template-governance.md`
- `docs/beacon/archive/v1.4.4/user-story/beacon-v1.4.4-pragmatic-design-baseline-and-template-governance.md`
- `docs/beacon/archive/v1.4.4/qa/test-cases/beacon-v1.4.4-pragmatic-design-baseline-and-template-governance.md`
