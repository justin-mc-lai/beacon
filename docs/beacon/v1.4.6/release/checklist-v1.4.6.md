# Release Checklist: v1.4.6

**Version**: v1.4.6
**Created**: 2026-05-13 11:30
**Status**: Blocked

---

## Pre-Release Checks

- [x] Requirement package frozen and clarity pass
- [x] Feature implementation completed
- [x] Targeted QA regression passing
- [x] Wider release reviewer regression completed
- [ ] Version-surface promotion approved

## Build

- [x] Skill contract validation passing
- [x] Support-surface regression passing
- [x] Release governance regression passing
- [ ] Release-facing evidence artifacts regenerated on `v1.4.6`

## Deployment

- [ ] Install/sync plan confirmed for agent surfaces
- [ ] Runtime release-line cutover prepared

## Release

- [x] Formal release verdict written
- [ ] `beacon release check v1.4.6` fully passing
- [ ] Version truth updated if release is approved
- [ ] Runtime/default docs line promoted
- [ ] Rollback/readiness note confirmed

## Change Documents

- [x] Version change document generated: `docs/beacon/v1.4.6/change/v1.4.6.md`
- [x] Version change machine payload generated: `docs/beacon/v1.4.6/.machine/change/v1.4.6.json`
- [x] Release reviewer confirmed included feature packages match intended scope

---

## Active Blockers

- Release evidence artifacts still point at `v1.4.5`
- Acceptance projection transaction contract missing
- Release scorecard not yet ready for the `v1.4.6` feature line
- Implement prompt boundary verdict artifact missing

## Notes

- `v1.4.6` remains a release-candidate line until release-facing evidence is regenerated and version truth is explicitly promoted.
