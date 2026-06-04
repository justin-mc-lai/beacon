# PRD: Test Directory / Marker Re-Layering Contract

**Feature**: `test-directory-marker-relayering-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Overview

Beacon must finish v1.4.11 legacy burden reduction by making tests honest about what they protect.

Current behavior, compatibility behavior, historical fixtures, migrations, deprecated surfaces, and projection integrity must be visibly different in test metadata.

## 1. Problem

Beacon has already reduced runtime legacy burden, but tests can still blur the line:

- current tests can accidentally depend on legacy fallback behavior.
- compat tests can omit the compatibility registry id they are protecting.
- historical fixture tests can be mistaken for current closure.
- migration tests can omit auditable migration evidence.
- deprecated command tests can make deprecated routes look current.

That weakens future refactors. A future maintainer could break current behavior or preserve legacy behavior for the wrong reason.

## 2. Goals

- AC-001: Pytest markers exist for `current_contract`, `projection_integrity`, `compat_contract`, `historical_fixture`, `migration`, and `deprecated`.
- AC-002: v1.4.11 retirement tests are classified with at least one deterministic marker.
- AC-003: Current contract tests do not assert legacy fallback as default current behavior.
- AC-004: Compatibility tests bind to a compatibility registry id when they test registered compatibility behavior.
- AC-005: Historical fixture tests cannot be used as current closure evidence.
- AC-006: Migration tests expose required migration evidence or transaction assertions.
- AC-007: Deprecated command/API tests prove callability only and do not promote default current routes.
- AC-008: Projection integrity tests are separate from human truth authority tests.
- AC-009: Marker validation produces a deterministic, CI-readable result.
- AC-010: This feature does not move broad test directories or change runtime behavior.

## 3. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Register pytest markers for the six test roles. |
| FR-002 | AC-002 | Add markers to v1.4.11 retirement and compatibility tests. |
| FR-003 | AC-003 | Validate that `current_contract` tests avoid legacy-default assertions. |
| FR-004 | AC-004 | Validate that `compat_contract` tests reference registry-backed compatibility ids. |
| FR-005 | AC-005 | Validate that `historical_fixture` tests are not accepted as current closure. |
| FR-006 | AC-006 | Validate that `migration` tests assert evidence or transaction behavior. |
| FR-007 | AC-007 | Validate that `deprecated` tests do not promote deprecated commands to default current routes. |
| FR-008 | AC-008 | Keep projection tests under `projection_integrity` instead of current behavior authority. |
| FR-009 | AC-009 | Provide deterministic marker validation output suitable for CI and QA evidence. |
| FR-010 | AC-010 | Keep implementation limited to marker registration, classification, and validation. |

## 4. Marker Semantics

### `current_contract`

Current default behavior. A failure means current behavior regressed.

### `projection_integrity`

Machine projections, transaction envelopes, sync checks, and acceptance evidence. These tests do not turn projection into human truth.

### `compat_contract`

Explicit compatibility behavior. Tests must bind to a registry id when the behavior is in `beacon/compatibility/registry.py`.

### `historical_fixture`

Old artifacts remain readable or inspectable. These tests cannot satisfy current closure by themselves.

### `migration`

Old artifacts/data are imported into current projections through auditable migration behavior.

### `deprecated`

Deprecated command/API remains callable during the retirement window. These tests must not put deprecated routes into default current surfaces.

## 5. Runtime Behavior Contract

This feature must not change runtime behavior.

Allowed implementation:

```text
marker registry
test annotations
marker validation helper/test
CI-readable summary
```

Forbidden implementation:

```text
runtime default behavior change
command removal
prototype/design behavior change
browser behavior change
memory/intent behavior change
QA/PRD mirror policy change
release verdict change
broad directory move
```

## 6. Success Metrics

- Markers are registered.
- v1.4.11 retirement tests are marked.
- Marker validation passes.
- Compat tests are registry-bound.
- Current tests no longer silently protect legacy default behavior.
- Historical and migration tests remain covered without becoming current closure.

## 7. Non Goals

- No runtime refactor.
- No feature behavior change.
- No release check execution.
- No test deletion.
- No large directory reorganization.

