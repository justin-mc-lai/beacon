# Beacon Implementation Tasks Ledger

- feature: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`
- version: `v1.4.2`
- plan_id: `plan-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance-r1`
- revision_id: `R1`
- progress: `18/18`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/archive/v1.4.2/.machine/execution/implementation-plan-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.progress.json`
- canonical_plan_json: `docs/beacon/archive/v1.4.2/.machine/execution/implementation-plan-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` FR-001 : Beacon must define a Test Contract Index containing identity, truth refs, runtime/docs line, lane membership, AC/TC/test/evidence mapping, status, and reason codes.
  - tests=TC-US001-001,TC-013,TC-014,TC-015,TC-016,TC-017,TC-018,TC-019,TC-020,TC-021
[x] `ITASK-002` FR-002 : Beacon must verify release-facing lane classification and block unsafe unclassified failures.
  - tests=TC-US002-001,TC-US006-001 | depends_on=ITASK-001
[x] `ITASK-003` FR-003 : Beacon must require release-facing tests to map to AC/TC and evidence or declare an explicit generated-surface contract reason.
  - tests=TC-US003-001 | depends_on=ITASK-002
[x] `ITASK-004` FR-004 : Doctor support commands must own build/verify behavior for the test contract index.
  - tests=TC-US004-001 | depends_on=ITASK-003
[x] `ITASK-005` FR-005 : QA must preserve AC order, evidence pack, coverage current/gap, continue decision, repair handoff, help resume, and next-round backfill.
  - tests=TC-US005-001 | depends_on=ITASK-004
[x] `ITASK-006` FR-006 : Release scorecard and strict gate must consume lane status and expose reason codes.
  - tests=TC-US009-001,TC-US012-001,TC-US007-001 | depends_on=ITASK-005
[x] `ITASK-007` FR-007 : Beacon skill surfaces must guide agents to classify tests by lane.
  - tests=TC-US008-001 | depends_on=ITASK-006
[x] `ITASK-008` FR-008 : Deep-derived test deltas must route to test-case or supplemental QA.
  - tests=TC-US010-001 | depends_on=ITASK-007
[x] `ITASK-009` FR-009 : Planning-line safety must preserve runtime/package/docs-current version truth.
  - tests=TC-US011-001 | depends_on=ITASK-008
[x] `ITASK-010` FR-001: Test Contract Index
  - depends_on=ITASK-009
[x] `ITASK-011` FR-002: Lane Verification
  - depends_on=ITASK-010
[x] `ITASK-012` FR-003: AC/TC/Test Mapping
  - depends_on=ITASK-011
[x] `ITASK-013` FR-004: Doctor Ownership
  - depends_on=ITASK-012
[x] `ITASK-014` FR-005: QA Consumption
  - depends_on=ITASK-013
[x] `ITASK-015` FR-006: Release Consumption
  - depends_on=ITASK-014
[x] `ITASK-016` FR-007: Skill Delivery Governance
  - depends_on=ITASK-015
[x] `ITASK-017` FR-008: Deep Delta Adoption
  - depends_on=ITASK-016
[x] `ITASK-018` FR-009: Planning Line Safety
  - depends_on=ITASK-017
