# Release Checklist: v1.6.4

**Version**: v1.6.4  
**Created**: 2026-07-02 14:46  
**Updated**: 2026-07-06 18:45  
**Status**: **GO** (R5 patch applied)

---

## Pre-Release Checks

- [x] All tests passing (unit 28/28 incl. R5 — `run-20260706T171931359390`)
- [x] Code coverage >= 80% (feature scorecard 4/4)
- [x] No critical bugs open (R5 friction queue cleared)
- [x] Security scan completed (inherited from v1.6.4 core)
- [x] Performance benchmarks passed (N/A — governance patch)
- [x] Documentation updated (release notes + research)

## Build

- [x] Build successful
- [x] No linting errors
- [x] Type checks passing

## Deployment

- [x] Staging deployment successful (Beacon CLI install from `main`)
- [x] Smoke tests passed (SidePilot admit fixtures)
- [x] Database migrations tested (N/A)

## Release

- [x] Production deployment (runtime line v1.6.4 on `main`)
- [x] Health checks passing (`beacon release check`, `verify-version-surfaces --strict`)
- [x] Rollback plan ready (revert `107b0907`/`1bce6bf4`)

## Change Documents

- [x] Version change document generated: `docs/beacon/v1.6.4/change/v1.6.4.md`
- [x] Version change machine payload generated: `docs/beacon/v1.6.4/.machine/change/v1.6.4.json`
- [x] Release reviewer confirmed included feature packages match intended scope
- [x] R5 patch documented in `docs/beacon/v1.6.4/release/v1.6.4.md`

---

## Notes

- **2026-07-02**: Initial v1.6.4 GO — 5 QA features (`9d3ddd92`).
- **2026-07-06**: R5 program-level workspace admission merged into v1.6.4 runtime line; SidePilot delivery-repo admit unblocked.
