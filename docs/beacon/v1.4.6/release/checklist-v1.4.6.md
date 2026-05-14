# Release Checklist: v1.4.6

**Version**: v1.4.6  
**Created**: 2026-05-13 11:30  
**Updated**: 2026-05-14 00:00  
**Status**: Pass

---

## Pre-Release Checks

- [x] Requirement package frozen and clarity pass
- [x] Feature implementation completed
- [x] Targeted QA regression passing
- [x] Wider release reviewer regression completed
- [x] Candidate release verdict approved
- [x] Runtime/default docs promotion approved

## Build

- [x] Skill contract validation passing
- [x] Support-surface regression passing
- [x] Release governance regression passing
- [x] Release-facing evidence artifacts regenerated on `v1.4.6`

## Deployment

- [x] Install/sync plan confirmed for agent surfaces
- [x] Runtime release-line candidate cutover prepared
- [x] Active runtime/default docs line switched

## Release

- [x] Formal release verdict written
- [x] `beacon release check v1.4.6` fully passing
- [x] Release scorecard ready
- [x] Version truth updated after runtime promotion approval
- [x] Runtime/default docs line promoted
- [x] Rollback/readiness note confirmed

## Change Documents

- [x] Version change document generated: `docs/beacon/v1.4.6/change/v1.4.6.md`
- [x] Version change machine payload generated: `docs/beacon/v1.4.6/.machine/change/v1.4.6.json`
- [x] Automation jobs feature change payload generated: `docs/beacon/v1.4.6/.machine/change/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.json`
- [x] Automation jobs operator runbook generated: `docs/beacon/v1.4.6/execution/automation-jobs-runbook.md`
- [x] Automation scaffold bootstrap surface available:
  - `python3 -m beacon.main automation init --project-root .`
- [x] Executor capability tiering frozen into automation/docs/test surfaces
- [x] Automation queue validation and feedback loop entrypoints available:
  - `python3 -m beacon.main automation validate-queue --project-root .`
  - `python3 -m beacon.main automation summarize-qa --project-root . --json`
  - `python3 -m beacon.main automation build-summary --project-root . --job beacon-nightly-qa --layer qa`
  - `python3 -m beacon.main automation update-queue --project-root . --json`
- [x] Human-facing automation toolkit surface available:
  - `beacon-toolkit-automation`
- [x] Release reviewer confirmed included feature packages match intended scope

---

## Promotion Decision

- `v1.4.6` release candidate: approved
- runtime/default docs promotion: completed
- active default line: `v1.4.6`

## Notes

- `v1.4.6` release closure and runtime promotion are both complete.
- final release QA run: `run-20260514T002632744979`
- final acceptance-led QA run: `run-20260514T150053458785`
- final deep closure for `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance` was materialized through `beacon deep run ... --json` on `2026-05-14`
- final Ralph projection for `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance` is `stop_state=release_ready`
- local/global CLI and local agent surfaces should remain aligned to `v1.4.6` until the next accepted promotion.
