# PRD: Beacon v1.4.7 change refreeze one-shot requirement closure

**Feature**: `beacon-v1.4.7-change-refreeze-one-shot-requirement-closure`
**Version**: `v1.4.7`
**Date**: `2026-05-16`
**Status**: `freeze-ready`
**Track**: `human-change-surface + governed-refreeze-orchestration`
**Scenario**: `operator_needs_a_low-friction_way_to_recompile_frozen_requirement_truth_after_change`

## Context

- Global boundary source:
  - `docs/beacon/global-boundaries.md`
- Change surface:
  - `skills/beacon/beacon-change/SKILL.md`
  - `beacon/commands/change.py`
- Current route evidence:
  - `beacon change "<feature>" --project . --version v1.4.7 --reason "<reason>" --json`

## 1. Overview

Beacon already treats `change` as the governed route for frozen truth updates. The current human surface correctly refuses to bypass the main requirement chain, but it still leaves operators to manually drive each downstream truth surface.

This feature proposes a bounded one-shot closure helper:

```text
change
-> prd
-> user-story
-> test-case
-> requirement_clarity
-> freeze
```

The helper is a convenience orchestrator over existing truth surfaces. It does not become a new lifecycle stage and does not own implementation, QA, or release.

## 2. Problem

When a post-freeze change is accepted, Beacon needs the operator to refresh the whole affected requirement package. Today the system can recommend the ladder, but the operator still has to coordinate the surfaces manually.

This creates three risks:

1. Partial refreeze: PRD changes but user-story or test-case stays stale.
2. Drift-by-convenience: implementation resumes after a change route without the whole truth package being recompiled.
3. Operator burden: the human must remember the exact chain and failure semantics.

## 3. Goals

1. Provide a human-facing one-shot refreeze route for accepted post-freeze changes.
2. Keep `prd / user-story / test-case / requirement_clarity / freeze` as the actual truth chain.
3. Emit an auditable transaction envelope for every one-shot refreeze attempt.
4. Fail closed if any required downstream surface cannot be refreshed or verified.
5. Return a clear next route after refreeze: `implement`, `qa`, `release`, or `human`.

## 4. Non-Goals

- no new primary lifecycle stage
- no direct implementation execution
- no QA or release gate bypass
- no silent truth mutation
- no requirement generation without operator-visible diff/summary

## 5. Design Principles

### 5.1 One-shot means one governed closure attempt, not blind automation

The helper may coordinate the chain, but each surface must remain recognizable in the transaction.

### 5.2 Truth surfaces stay authoritative

`change` can orchestrate. It cannot replace `prd`, `user-story`, `test-case`, `requirement_clarity`, or `freeze`.

### 5.3 Partial completion is blocked state

If PRD refresh passes but user-story or test-case refresh fails, the feature must remain blocked for stale truth.

### 5.4 Human readability is part of the product

The output must state:

- what changed
- which surfaces were refreshed
- which surfaces failed or were skipped
- whether refreeze is complete
- which route is safe next

## 6. Functional Requirements

### FR-001 One-shot refreeze entry

Beacon must expose a human-facing route that can start a governed one-shot refreeze for an accepted change intent.

Acceptable implementation shapes:

- `beacon change ... --refreeze-chain`
- `beacon change refreeze ...`
- a support subskill such as `beacon-change-refreeze`

### FR-002 Chain coverage

The one-shot route must explicitly cover:

- `change`
- `prd`
- `user-story`
- `test-case`
- `requirement_clarity`
- `freeze`

### FR-003 Transaction envelope

Every run must emit a machine-readable transaction envelope with:

- `feature`
- `version`
- `change_reason`
- `touched_surfaces`
- `surface_statuses`
- `truth_revision_before`
- `truth_revision_after`
- `refreeze_status`
- `next_route`
- `blocked_reason`

### FR-004 Fail-closed partial refresh

If any required surface fails to refresh or verify, the transaction must mark `refreeze_status=blocked` and must not route to `implement`, `qa`, or `release`.

### FR-005 Operator-visible summary

The human output must summarize the chain state without requiring the operator to inspect every artifact manually.

### FR-006 No lifecycle expansion

The feature must preserve `change` as a support/revision route and must not create a new primary lifecycle stage.

## 7. Acceptance Standard

This feature is accepted only if Beacon can prove that a one-shot refreeze improves operator closure without weakening the canonical truth chain or hiding partial failure.
