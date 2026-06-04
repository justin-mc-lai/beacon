# Release Checklist: v1.4.7

**Version**: v1.4.7
**Created**: 2026-05-14
**Updated**: 2026-05-16
**Status**: Pass for runtime release

---

## Pre-Release Checks

- [x] Requirement package frozen for accepted slices
- [x] Accepted-slice implementation completed
- [x] Targeted QA regression passing
- [x] Runtime-release acceptance summary written and refreshed after support-surface and runtime-facing automation verification
- [x] Release reviewer confirmed this is a runtime-promotion verdict
- [x] Real-project proof refreshed against `shopxo_canada` feature closure

## Build

- [x] Skill contract validation passing
- [x] Host-pack compatibility relevant to this slice passing
- [x] Support-surface regression relevant to this slice passing
- [x] Release-facing materials generated for `v1.4.7`
- [x] Runtime-facing automation verification linked into planning-line release materials

## Deployment

- [x] Runtime cutover requested and completed
- [x] Docs-default cutover requested and completed
- [x] Version-truth promotion performed

## Release

- [x] Formal runtime-release verdict written
- [x] Runtime-release checklist completed
- [x] QA evidence linked from release notes
- [x] Promotion decision explicitly recorded as approved
- [x] Runtime/default docs line explicitly updated
- [x] Latest real-project proof linked into release materials

## Change Documents

- [x] Version change document generated: `docs/beacon/archive/v1.4.7/change/v1.4.7.md`
- [x] Feature change document generated: `docs/beacon/archive/v1.4.7/change/beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces.md`
- [x] Feature change document generated: `docs/beacon/archive/v1.4.7/change/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
- [x] Feature change document generated: `docs/beacon/archive/v1.4.7/change/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- [x] Feature change document generated: `docs/beacon/archive/v1.4.7/change/beacon-v1.4.7-change-refreeze-one-shot-requirement-closure.md`
- [x] Feature change document generated: `docs/beacon/archive/v1.4.7/change/beacon-v1.4.7-change-refreeze-human-skill-stable-route.md`
- [x] Feature change document generated: `docs/beacon/archive/v1.4.7/change/beacon-v1.4.7-deep-lightweight-lineage-projection-contract.md`
- [x] Stable `beacon-change-refreeze` human route verified
- [x] Deep lightweight lineage projection verified
- [x] v1.4.7 plus automation regression package passing: `96 passed`
- [x] QA acceptance summary generated: `docs/beacon/archive/v1.4.7/qa/acceptance-summary.md`
- [x] Release notes generated: `docs/beacon/archive/v1.4.7/release/v1.4.7.md`
- [x] Promotion decision material generated: `docs/beacon/archive/v1.4.7/release/runtime-promotion-decision.md`
- [x] Real-project proof generated: `docs/beacon/archive/v1.4.7/release/shopxo-canada-real-project-proof-2026-05-16.md`

---

## Promotion Decision

- `v1.4.7` runtime release candidate: approved
- runtime/default docs promotion: approved
- active default line remains: `v1.4.7`

## Notes

- `v1.4.7` has passed runtime-promotion QA for the accepted support-surface slices and the accepted runtime-facing automation slices.
- `v1.4.7` now also has a repaired and passing real-project feature proof on `shopxo_canada` for `admin-merchandising-analytics`.
- This line is release-ready as the active Beacon runtime/docs line for the six listed feature packages, even though broader roadmap slices remain open.
- The accepted automation slices are included only as bounded runtime contracts; they do not imply approval of full autonomous closure-loop behavior.
- Local/global CLI and managed runtime context should now align to `v1.4.7`.
