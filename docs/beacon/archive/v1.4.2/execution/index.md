# Beacon v1.4.2 Execution Index

## Version Line

- version: `v1.4.2`
- status: `planning_only`
- theme: `contract-aligned test evolution and skill delivery governance`
- runtime line: `v1.4.0` remains current runtime release

## Human Truth

- Summary: `docs/beacon/archive/v1.4.2/SUMMARY.md`
- PRD: `docs/beacon/archive/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- User Story: `docs/beacon/archive/v1.4.2/user-story/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- Test Cases: `docs/beacon/archive/v1.4.2/qa/test-cases/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- Architecture Blueprint: `docs/beacon/archive/v1.4.2/execution/architecture-blueprint.md`

## Execution Boundary

`v1.4.2` introduces no new required human lifecycle stage.

The main lifecycle remains:

```text
prd
-> user-story
-> test-case
-> implement
-> qa
-> release
```

The new capability is a delivery governance layer that classifies test work and skill guidance by contract lane, and that admits protected browser QA by session/runner truth before execution. It must be surfaced through existing Beacon support and lifecycle commands:

- `doctor` builds and verifies the test contract index.
- `test-case` adopts accepted test deltas into AC/TC coverage.
- `qa` executes lane-aware current-round verification and evidence capture.
- `qa` also decides whether browser-capable protected surfaces can execute via attached-session / CDP paths or must return explicit `skip/blocked`.
- `release` consumes lane status and blocks on release-facing drift.
- `deep` can derive additional test deltas, but does not execute QA or rewrite frozen truth.

## Planned Artifact Families

- `docs/beacon/<version>/.machine/testing/test-contract-index.json`
- `docs/beacon/<version>/execution/test-contract-index.md`
- `.beacon/qa/features/<feature>/lane-status.json`
- `.beacon/evidence/test-results/<feature>/<tc-id>.json`
- `.beacon/state/agent-surfaces.json`
- `docs/beacon/<version>/.machine/learning/qa/<feature-or-host>.md`

## Contract Lane Vocabulary

```text
feature_release_facing
current_runtime_contract
generated_surface_sync
compatibility_contract
legacy_snapshot
browser_runtime_admission
```

## Freeze Scope

The frozen requirement scope for `v1.4.2` is limited to defining the product contract, AC/TC matrix, command placement, evidence shape, release reason codes, browser admission semantics, and skill delivery guidance needed for contract-aligned test evolution.

It does not implement the runtime command changes.
