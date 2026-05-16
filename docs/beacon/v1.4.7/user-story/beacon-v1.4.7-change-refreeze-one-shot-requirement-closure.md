# User Story: Beacon v1.4.7 change refreeze one-shot requirement closure

**Feature**: `beacon-v1.4.7-change-refreeze-one-shot-requirement-closure`
**Version**: `v1.4.7`
**Revision**: `R1`
**Status**: `frozen`

## Story

**As a** Beacon operator revising frozen requirement truth,
**I want** a governed one-shot route that can carry an accepted change through PRD, user-story, test-case, requirement clarity, and freeze,
**So that** I can recompile the full requirement package without manually coordinating every truth surface or accidentally resuming implementation against stale truth.

## Acceptance Criteria

- AC-001 Beacon exposes a human-facing one-shot refreeze route under the change family without introducing a new primary lifecycle stage.
- AC-002 The route explicitly covers `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze`.
- AC-003 The route emits a machine-readable transaction envelope with touched surfaces, per-surface statuses, before/after truth revision refs, refreeze status, next route, and blocked reason.
- AC-004 Beacon fail-closes when any required downstream truth surface cannot be refreshed or verified.
- AC-005 Beacon does not route to `implement`, `qa`, or `release` until the refreeze transaction is complete.
- AC-006 The human summary explains what changed, what was refreshed, what remains blocked, and which route is safe next.
- AC-007 The route does not execute implementation, QA, release, or autonomous truth mutation outside the existing truth surfaces.

## Actor Semantics

1. Human operator
   - submits accepted change intent
   - reviews the chain summary and blocked reasons
2. Change/refreeze helper
   - coordinates existing truth surfaces
   - records transaction state
   - does not own final release verdict
3. Truth surfaces
   - remain responsible for PRD, user-story, test-case, requirement clarity, and freeze semantics
4. Implement/QA/Release
   - may resume only after refreeze is complete

## Boundary Notes

- One-shot refreeze is a support route, not a lifecycle stage.
- Convenience orchestration must not hide partial truth drift.
- A generated draft is not frozen truth until the refreeze gate passes.
