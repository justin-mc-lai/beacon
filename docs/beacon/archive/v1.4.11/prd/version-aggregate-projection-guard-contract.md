# PRD: Version Aggregate Projection Guard Contract

**Feature**: `version-aggregate-projection-guard-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Overview

Beacon needs a deterministic guard that keeps version aggregate projection aligned with QA accepted features before release check.

The guard must live inside existing QA / release / doctor surfaces. It must not introduce a new lifecycle stage or a new mandatory human-facing command.

## 1. Problem

Feature-level QA can pass while version-level aggregate projection is stale.

When `.machine/change/<feature>.json` is missing, `release create` cannot include the feature in `change/<version>.md` or `.machine/change/<version>.json`. `release check` then blocks because the current feature is not included in version change scope.

The current behavior is fail-closed at release check, which is good, but repair is too manual and too easy to confuse with a new lifecycle step.

## 2. Goals

- AC-001: Beacon uses `version aggregate projection` wording for version change aggregation and does not call it requirement truth.
- AC-002: A QA accepted current feature has a deterministic feature change projection input or a repairable missing-projection finding.
- AC-003: `release create` rebuilds version aggregate projection from feature change projections and preserves explicit feature dependency order.
- AC-004: `release check` fails closed when the current QA accepted feature is missing from version aggregate projection.
- AC-005: `release check` passes the aggregate inclusion gate when the current QA accepted feature is included in version aggregate projection.
- AC-006: Doctor exposes repair-only projection rebuild / verify behavior for feature change projection, version aggregate projection, and test-contract-index.
- AC-007: test-contract-index refresh / verify is part of the projection repair closure when release scorecard reports stale index risk.
- AC-008: The guard does not add a new lifecycle stage, new required human-facing command, release publish action, or post-release install action.
- AC-009: Regression tests cover missing projection, repaired projection, aggregate feature count/list, dependency order, and wording boundaries.
- AC-010: Release output gives an actionable repair route when projection inclusion fails.

## 3. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Use projection/read-model wording for version aggregate outputs. |
| FR-002 | AC-002 | Detect or create feature-level change projection for QA accepted features. |
| FR-003 | AC-003 | Ensure `release create` rebuilds version aggregate projection from feature projections. |
| FR-004 | AC-003 | Preserve explicit `depends_on_features` ordering in version aggregate implementation waves. |
| FR-005 | AC-004 | Block release check when current QA accepted feature is absent from version aggregate. |
| FR-006 | AC-005 | Pass release check inclusion when current QA accepted feature is present. |
| FR-007 | AC-006 | Provide doctor repair-only command or helper for rebuilding projection artifacts. |
| FR-008 | AC-007 | Refresh and verify `docs/beacon/<version>/.machine/testing/test-contract-index.json` during repair. |
| FR-009 | AC-008 | Keep lifecycle unchanged: `change/refreeze -> implement -> qa -> release check`. |
| FR-010 | AC-009 | Add deterministic tests for projection guard behavior. |
| FR-011 | AC-010 | Include recommended repair commands in blocked release output. |

## 4. Projection Contract

The projection contract is:

```text
requirement truth:
  docs/beacon/<version>/prd/<feature>.md
  docs/beacon/<version>/user-story/<feature>.md
  docs/beacon/<version>/qa/test-cases/<feature>.md

feature release projection input:
  docs/beacon/<version>/.machine/change/<feature>.json

version aggregate projection:
  docs/beacon/<version>/change/<version>.md
  docs/beacon/<version>/.machine/change/<version>.json

release preflight index:
  docs/beacon/<version>/.machine/testing/test-contract-index.json
```

`.machine` artifacts are projection / evidence / read model, not source of requirement truth.

## 5. Non Goals

- No `aggregate-sync` lifecycle stage.
- No mandatory user-facing lifecycle command between QA and release.
- No release publish execution.
- No post-release install hook execution.
- No PRD / user-story / test-case mutation after QA acceptance.
- No promotion of machine artifacts to truth.

## 6. Success Metrics

- Missing feature projection is detected before release-ready is claimed.
- Repair path regenerates projection artifacts deterministically.
- Version change feature count and feature list include the current QA accepted feature.
- Release check status is blocked before repair and pass after repair.
- Tests prevent wording regressions that call aggregate projection truth.
