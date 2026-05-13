# Release Checklist: v1.4.6

**Version**: v1.4.6  
**Created**: 2026-05-13 11:30  
**Updated**: 2026-05-13 22:24  
**Status**: Pass

---

## Pre-Release Checks

- [x] Requirement package frozen and clarity pass
- [x] Feature implementation completed
- [x] Targeted QA regression passing
- [x] Wider release reviewer regression completed
- [x] Candidate release verdict approved
- [ ] Runtime/default docs promotion approved

## Build

- [x] Skill contract validation passing
- [x] Support-surface regression passing
- [x] Release governance regression passing
- [x] Release-facing evidence artifacts regenerated on `v1.4.6`

## Deployment

- [x] Install/sync plan confirmed for agent surfaces
- [x] Runtime release-line candidate cutover prepared
- [ ] Active runtime/default docs line switched

## Release

- [x] Formal release verdict written
- [x] `beacon release check v1.4.6` fully passing
- [x] Release scorecard ready
- [ ] Version truth updated if runtime promotion is approved
- [ ] Runtime/default docs line promoted
- [x] Rollback/readiness note confirmed

## Change Documents

- [x] Version change document generated: `docs/beacon/v1.4.6/change/v1.4.6.md`
- [x] Version change machine payload generated: `docs/beacon/v1.4.6/.machine/change/v1.4.6.json`
- [x] Release reviewer confirmed included feature packages match intended scope

---

## Promotion Decision

- `v1.4.6` release candidate: approved
- runtime/default docs promotion: deferred
- active default line remains: `v1.4.5`

## Notes

- `v1.4.6` release closure is complete; the remaining open item is only whether to promote package/runtime/docs default surfaces.
- local/global CLI can be refreshed to the current editable source without changing `version-truth`.
