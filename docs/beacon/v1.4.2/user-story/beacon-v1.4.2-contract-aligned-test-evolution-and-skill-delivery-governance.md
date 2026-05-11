# User Story: Beacon v1.4.2 Contract-Aligned Test Evolution and Skill Delivery Governance

**Feature**: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`  
**Version**: `v1.4.2`  
**Revision**: `R2`  
**Status**: `frozen`

## Story

**As a** Beacon maintainer,  
**I want** Beacon self-iteration tests to be classified by contract lane, and browser-capable QA to be admitted by real session/runner truth,  
**So that** implementation, QA, skill delivery, and release gates can distinguish current feature blockers from generated-surface drift, compatibility obligations, legacy snapshots, and protected-surface auth/runtime blockers without promoting the planning line to runtime.

## Acceptance Criteria

- [ ] AC-001 Test Contract Index exposes identity, truth refs, runtime/docs lines, lane membership, AC/TC/test/evidence mapping, status, and reason codes.
- [ ] AC-002 Canonical lanes include feature release-facing, current runtime contract, generated surface sync, compatibility contract, legacy snapshot, and browser runtime admission.
- [ ] AC-003 Release-facing tests without AC/TC/evidence mapping are blocked unless classified as generated-surface contract checks.
- [ ] AC-004 Doctor support surface builds and verifies test contract index without adding a public lifecycle stage.
- [ ] AC-005 QA lane execution preserves AC order, evidence pack, coverage current/gap, continue decision, blocker stop, repair handoff, help resume, and backfill.
- [ ] AC-006 Release scorecard and strict gate consume lane status and block missing, stale, failed, or unclassified release-facing evidence.
- [ ] AC-007 Generated skill, metadata, command, context, and agent surfaces are lane-classified and block delivery when drift affects truth or routing.
- [ ] AC-008 Historical snapshot failures route to legacy snapshot or test evolution backlog unless promoted to active compatibility contract.
- [ ] AC-009 Beacon skills instruct agents to use contract-lane verification and avoid unclassified full-suite release claims.
- [ ] AC-010 Deep test deltas route through test-case or supplemental QA; deep remains support-only and does not execute QA.
- [ ] AC-011 Freezing v1.4.2 requirement materials does not change current runtime release line, docs default line, or package version.
- [ ] AC-012 Test contract governance blockers include reason codes and repair or resume routes through existing support surfaces.
- [ ] AC-013 Protected browser surfaces require session/runner admission before execution and prefer attached-session paths before bare Playwright.
- [ ] AC-014 Browser-capable QA closure requires authentic browser evidence; transcript-only placeholder artifacts are insufficient.
- [ ] AC-015 Protected-surface runner priority is represented as `web-access -> attached agent-browser -> playwright attach/CDP -> bare Playwright`.
- [ ] AC-016 Missing session bridge on protected live surfaces yields `skip` or `blocked` reasoned outcomes rather than false product failures.
- [ ] AC-017 QA writes reusable runner/admission learning notes with reason, fallback, next preferred runner, and expiry semantics.
- [ ] AC-018 Browser-runtime admission and browser evidence obligations participate in lane/status reasoning alongside AC/TC/evidence mapping.

## Traceability

- PRD: `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- Test cases: `docs/beacon/v1.4.2/qa/test-cases/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- AC matrix: `docs/beacon/v1.4.2/.machine/qa/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.ac-test-matrix.json`

## Boundary Notes

- `v1.4.2` remains `planning_only`.
- Runtime/package/docs-default/current-runtime release line remain `v1.4.0`.
- Test Contract Index is a machine projection, not a new lifecycle stage or second truth root.
- Browser-runtime admission and runner-learning notes are governance/evidence projections, not standalone completion truth.
