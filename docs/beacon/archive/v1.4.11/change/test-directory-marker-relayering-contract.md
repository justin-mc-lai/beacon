# Change: Test Directory / Marker Re-Layering Contract

**Feature**: `test-directory-marker-relayering-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## 1. Change Reason

v1.4.11 has already retired or bounded several legacy surfaces. The remaining risk is that tests keep legacy behavior alive as if it were current behavior.

This change freezes Phase 10: test directory and marker re-layering.

## 2. Accepted Change

Freeze a requirement package that requires Beacon to:

1. Register deterministic pytest markers for current, projection, compatibility, historical, migration, and deprecated test roles.
2. Classify v1.4.11 retirement tests with those markers.
3. Require compatibility tests to bind to compatibility registry entries.
4. Ensure current contract tests do not require legacy fallback as default behavior.
5. Ensure historical fixture tests cannot satisfy current closure.
6. Ensure migration tests expose migration evidence when the feature requires it.
7. Ensure deprecated command/API tests do not promote deprecated surfaces into default current routes.
8. Provide marker validation and a CI-readable summary.
9. Avoid large directory moves unless explicitly justified later.
10. Preserve all runtime behavior outside the test marker governance slice.

## 3. Scope

### In Scope

- `pyproject.toml` pytest marker registration.
- Marker classification for v1.4.11 tests.
- Marker validation helper/test.
- Compatibility registry binding checks for compat tests.
- CI-readable marker summary or validation payload.
- Tests proving current/compat/historical/migration/deprecated semantics are separate.

### Out Of Scope

- No prototype/design behavior change.
- No browser deterministic command behavior change.
- No memory or intent runtime behavior change.
- No QA or PRD mirror policy change.
- No implement package behavior change.
- No command removal.
- No release verdict change by itself.
- No broad test directory move in this feature.

## 4. Source Evidence

- Research: `docs/beacon/archive/v1.4.11/research/test-directory-marker-relayering-contract.md`
- Legacy reduction plan: `docs/beacon/archive/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- Pytest marker registry: `pyproject.toml`
- Compatibility registry: `beacon/compatibility/registry.py`
- v1.4.11 tests: `tests/test_v1411_*.py`

## 5. Route Decision

This change accepts Phase 10 from the v1.4.11 legacy burden reduction plan.

It is intentionally test-governance-only:

```text
authority / compat / QA-PRD / implement / prototype-design / browser / memory-intent
  -> test marker relayering
  -> release check
```

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and freeze complete.

## 6. Freeze Deliverables

- `docs/beacon/archive/v1.4.11/research/test-directory-marker-relayering-contract.md`
- `docs/beacon/archive/v1.4.11/change/test-directory-marker-relayering-contract.md`
- `docs/beacon/archive/v1.4.11/prd/test-directory-marker-relayering-contract.md`
- `docs/beacon/archive/v1.4.11/user-story/test-directory-marker-relayering-contract.md`
- `docs/beacon/archive/v1.4.11/qa/test-cases/test-directory-marker-relayering-contract.md`

## 7. Boundary

This feature freezes requirement truth for test marker and test classification governance only.

