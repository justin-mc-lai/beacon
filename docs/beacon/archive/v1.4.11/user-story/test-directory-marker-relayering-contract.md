# User Story: Test Directory / Marker Re-Layering Contract

**Feature**: `test-directory-marker-relayering-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Story

As a Beacon maintainer, I want tests to clearly say whether they protect current behavior, compatibility behavior, historical fixture readability, migration behavior, deprecated callability, or projection integrity, so future refactors do not accidentally preserve legacy behavior as current truth.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | marker registry | Pytest markers exist for `current_contract`, `projection_integrity`, `compat_contract`, `historical_fixture`, `migration`, and `deprecated`. |
| AC-002 | test classification | v1.4.11 retirement tests are classified with at least one deterministic marker. |
| AC-003 | current boundary | Current contract tests do not assert legacy fallback as default current behavior. |
| AC-004 | compat registry binding | Compatibility tests bind to a compatibility registry id when they test registered compatibility behavior. |
| AC-005 | historical boundary | Historical fixture tests cannot be used as current closure evidence. |
| AC-006 | migration evidence | Migration tests expose required migration evidence or transaction assertions. |
| AC-007 | deprecated boundary | Deprecated command/API tests prove callability only and do not promote default current routes. |
| AC-008 | projection boundary | Projection integrity tests are separate from human truth authority tests. |
| AC-009 | validation output | Marker validation produces a deterministic, CI-readable result. |
| AC-010 | no runtime change | This feature does not move broad test directories or change runtime behavior. |

## Test Story Map

| Test ID | Covers | Scenario |
| --- | --- | --- |
| TEST-001 | AC-001 | Marker registry contains all six marker names. |
| TEST-002 | AC-002 | v1.4.11 retirement test modules are marked. |
| TEST-003 | AC-003 | Current contract tests do not include legacy-default patterns. |
| TEST-004 | AC-004 | Compat tests reference registered compatibility ids. |
| TEST-005 | AC-005 | Historical fixture tests include non-current closure semantics. |
| TEST-006 | AC-006 | Migration tests assert transaction or evidence behavior. |
| TEST-007 | AC-007 | Deprecated tests do not make deprecated routes default. |
| TEST-008 | AC-008 | Projection tests are separately marked. |
| TEST-009 | AC-009 | Marker validator returns deterministic pass/block payload. |
| TEST-010 | AC-010 | Runtime behavior surfaces remain out of scope. |

