# Research Closure: Test Directory / Marker Re-Layering Contract

**Feature**: `test-directory-marker-relayering-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## 1. Purpose

This research closure promotes Phase 10 of the v1.4.11 legacy burden reduction plan into requirement truth.

The slice covers test directory and marker governance only:

- make current behavior tests distinguishable from compatibility tests.
- make projection integrity tests distinguishable from runtime behavior tests.
- make historical fixtures and migration tests explicit.
- require compatibility tests to bind to compatibility registry entries.
- prevent legacy behavior from being reintroduced as current contract through unmarked tests.

This feature must not change prototype/design, browser, memory, intent, QA/PRD mirror, implement package, command catalog behavior, or release verdict semantics.

## 2. Current Problem

Beacon has now split several legacy surfaces:

- prototype legacy wireframes became migration input after the design/prototype rebuild.
- browser fallback command naming became deterministic command evidence.
- memory and intent legacy paths became explicit compatibility/migration behavior.
- QA and PRD legacy mirrors no longer define current truth by default.

But tests can still blur those boundaries. A test that asserts legacy fallback behavior without a marker can accidentally make that legacy behavior look like a current regression contract.

The problem is not missing coverage. The problem is unclear coverage ownership.

## 3. Target Test Layer Model

The target marker model is:

```text
current_contract
  -> current default behavior only
  -> cannot require legacy fallback as current closure

projection_integrity
  -> machine projection, transaction, acceptance envelope, and mirror consistency
  -> does not claim human truth authority by itself

compat_contract
  -> explicit compatibility behavior
  -> must bind to compatibility registry entry

historical_fixture
  -> old artifact remains readable/inspectable
  -> cannot satisfy current closure

migration
  -> old artifact/data moves into current projection through auditable migration
  -> must expose evidence or transaction when required

deprecated
  -> old command/API remains callable during retirement window
  -> cannot appear in default current route
```

## 4. State Machine

```text
test_unclassified
  -> marker_required
  -> marker_applied
  -> marker_validation_passed
  -> qa_matrix_readable
```

Blocked transitions:

- `compat_behavior_test -> current_contract`: blocked because compatibility behavior must stay explicit.
- `historical_fixture_test -> current_closure`: blocked because historical fixtures are not current truth.
- `migration_test -> no_transaction_when_required`: blocked because migration must be auditable.
- `deprecated_command_test -> default_surface_promotion`: blocked because deprecated behavior cannot become current route.

## 5. Decision Priority

When test classification conflicts, use this priority:

1. Current behavior must be easy to identify and run.
2. Compatibility behavior must remain covered before retirement.
3. Historical fixtures must remain useful without becoming current closure.
4. Migration behavior must be auditable.
5. Projection integrity must stay separate from human truth authority.
6. Marker governance must be lightweight and deterministic.
7. Do not move large test directories unless marker classification proves insufficient.

## 6. Source Architecture Notes

Source-backed inputs:

- `pyproject.toml`: current pytest marker registry.
- `tests/test_v1411_*.py`: v1.4.11 compatibility and retirement feature tests.
- `beacon/compatibility/registry.py`: compatibility registry entries required by compat tests.
- `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`: Phase 10 plan.
- `docs/beacon/v1.4.11/execution/legacy-burden-baseline-inventory.md`: baseline compatibility surfaces.

## 7. Closure Decision

Freeze a test marker relayering requirement package.

The correct implementation route is marker-first:

```text
register markers
classify v1.4.11 tests
add marker validation
bind compat tests to registry
avoid broad file moves
```

Do not include runtime behavior changes, command removal, release verdict changes, or large directory moves in this slice.

## 8. Projection Truth Binding

### 8.1 prd_refs

- `docs/beacon/v1.4.11/prd/test-directory-marker-relayering-contract.md`

### 8.2 user_story_refs

- `docs/beacon/v1.4.11/user-story/test-directory-marker-relayering-contract.md`

### 8.3 test_case_refs

- `docs/beacon/v1.4.11/qa/test-cases/test-directory-marker-relayering-contract.md`

### 8.4 coverage_notes

- AC-001 through AC-002 cover pytest marker registration and deterministic v1.4.11 test classification.
- AC-003 through AC-008 cover current, projection, compatibility, historical, migration, and deprecated test role separation.
- AC-009 through AC-010 cover marker validation output and no runtime behavior changes.

### 8.5 out_of_scope_notes

- Prototype/design rebuild is already handled by `beacon-design-product-prototype-rebuild-contract`.
- Browser deterministic command naming is already handled by `browser-fallback-deterministic-command-contract`.
- Memory and intent migration boundaries are already handled by `memory-intent-historical-migration-boundary-contract`.
- Command removal and release verdict changes are out of scope.

## 9. Recommended Next Route

```text
beacon-change-refreeze
  -> beacon-implement
  -> beacon-qa
```

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-05-27T01:51:38.042089+00:00`
- deep_artifact_root: `docs/beacon/v1.4.11/deep/test-directory-marker-relayering-contract`
- machine_artifact_root: `docs/beacon/v1.4.11/.machine/deep/test-directory-marker-relayering-contract`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/v1.4.11/.machine/deep/test-directory-marker-relayering-contract/release-supplement.json`
- adoption_status: `route_only`
