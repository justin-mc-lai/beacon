# Beacon Feature Change Document

- feature: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`
- feature_slug: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`
- version: `v1.4.2`
- status: `reopened-for-qa-scope-refresh`

## Scope
- Original scope: contract-aligned test evolution governance for Beacon v1.4.2, including Test Contract Index generation/verification, release scorecard and gate consumption, QA evidence writeback, lane-aligned tests, skill guidance, deep delta policy, and planning-line safety checks.
- Reopened scope: supplement QA-specific browser/runtime governance so protected live surfaces, attached-session admission, real browser evidence, placeholder runner boundaries, and session-backed recovery become frozen requirement truth instead of informal skill guidance.

## Added
- Test Contract Index machine projection with canonical lanes, truth refs, AC/TC/evidence mapping, lane status, planning-line safety, and repair commands.
- Doctor support commands to build and verify the Test Contract Index.
- Release scorecard and strict gate consumption of test contract governance reason codes.
- Contract-aligned v1.4.2 pytest coverage across the frozen AC matrix.
- Skill delivery guidance for contract-lane verification and unclassified full-suite claim avoidance.
- QA-specific requirement refresh for browser-native admission, session bridge truth, attached-browser/CDP-first protected-surface routing, and browser evidence authenticity.
- Explicit boundary that transcript-only placeholder adapters do not satisfy browser-capable QA completion by themselves.
- Learning-loop requirement for runner-specific skip/block reasons so Beacon avoids repeating known protected-surface failures.

## Removed / Reduced
- none

## Fixed
- Cleared stale QA rerun reason codes after successful feature-aware QA writeback so release scorecard reads current closure truth.
- Restored v1.4.2 frozen user-story truth and rebuilt derived machine story, scenario, implementation-plan, acceptance, and test contract projections.
- Preserved v1.4.2 as planning_only while runtime, docs default, current runtime release, and package version remain v1.4.0.

## Traceability Refs
- `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- `docs/beacon/v1.4.2/user-story/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- `docs/beacon/v1.4.2/qa/test-cases/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- `skills/beacon/beacon-qa/SKILL.md`
- `docs/beacon/v1.4.0/research/beacon-vs-openspec-speckit-skill-alignment.md`
- `docs/beacon/v1.4.2/.machine/testing/test-contract-index.json`
- `docs/beacon/v1.4.2/.machine/execution/implementation-plan-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.json`
- `docs/beacon/v1.4.2/.machine/execution/qa-acceptance-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.json`
- `.beacon/transactions/qa-acceptance-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.json`
- `.beacon/auto-test-status.json`
- `.beacon/coverage-summary.json`
- `.beacon/qa/features/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/scorecard.json`
