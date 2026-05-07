# Release Checklist: v1.4.0

**Version**: v1.4.0
**Created**: 2026-05-07 03:48
**Status**: Feature Closure Complete / Release Pending

---

## Pre-Release Checks

- [ ] All tests passing
- [ ] Code coverage >= 80%
- [ ] No critical bugs open
- [ ] Security scan completed
- [ ] Performance benchmarks passed
- [x] Documentation updated

## Build

- [ ] Build successful
- [ ] No linting errors
- [ ] Type checks passing

## Deployment

- [ ] Staging deployment successful
- [ ] Smoke tests passed
- [ ] Database migrations tested

## Release

- [ ] Production deployment
- [ ] Health checks passing
- [ ] Rollback plan ready

## Change Documents

- [x] Version change document generated: `docs/beacon/v1.4.0/change/v1.4.0.md`
- [x] Version change machine payload generated: `docs/beacon/v1.4.0/.machine/change/v1.4.0.json`
- [ ] Release reviewer confirmed included feature packages match intended scope

---

## Notes

- 截至 `2026-05-07`，`v1.4.0` 并行三条正式需求都已完成实现、QA 和 formal acceptance：
  - `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
  - `beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure`
  - `beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration`
- 三条 feature 的 `artifact-update-obligations` 已全部收口为 `open_count=0`
- 三条 feature 的 `Beacon Acceptance Kit v1` 均为 `Contract Pass`
- 当前不勾选版本级 release 项，是因为 release scorecard 仍未到 `release_ready`
- 当前版本级阻断不在 feature 验收，而在 release governance / gate 收口
