# Research Closure: Memory / Intent Historical Migration Boundary Contract

**Feature**: `memory-intent-historical-migration-boundary-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## 1. Purpose

This research closure promotes Phase 9 of the v1.4.11 legacy burden reduction plan into requirement truth.

The slice covers memory and intent historical migration boundaries only:

- keep older memory rows importable.
- stop current memory writes from continuously mirroring legacy projection files by default.
- record first legacy memory migration as an auditable migration transaction.
- keep older intent APIs callable only as explicit compatibility routes.
- mark legacy intent routing as compatibility routing, not current mainline routing.
- preserve prototype/design, browser deterministic command, QA/PRD mirror policy, implement package, command removal, and test marker behavior outside this slice.

The immediately previous slices already rebuilt current prototype behavior into `design-result-adapter` and renamed browser fallback command semantics to deterministic command evidence. This Phase 9 slice must not reopen those surfaces.

## 2. Current Problem

Beacon still has two historical carryovers:

1. `memory.py` can migrate legacy memory rows into `memory-v1`, but current writes also keep legacy projection files updated.
2. `intent_router.py` keeps old public router behavior callable, but current routing and legacy compatibility routing are not clearly separated in evidence or readout.

That keeps old storage and old router semantics visible in current runtime behavior. The result is not data loss, but weight: current execution continues paying for historical projection compatibility even when no operator asked for compat mode.

## 3. Target Architecture

The target model is:

```text
legacy memory files present
  -> explicit import or first v1 bootstrap
  -> migration transaction recorded
  -> memory-v1 becomes current projection
  -> legacy projection writes disabled by default

current memory write
  -> memory-v1 write
  -> no legacy projection write unless compat mode is explicit

legacy intent API used
  -> compat router admitted
  -> compat_id=intent-legacy-router evidence
  -> current route remains boundary-aware router
```

## 4. State Machine

```text
legacy_memory_present
  -> migration_admitted
  -> migration_transaction_written
  -> memory_v1_ready
  -> current_memory_write_only

current_memory_write_only
  -> compat_mode_absent
  -> legacy_projection_not_written

current_memory_write_only
  -> compat_mode_explicit
  -> legacy_projection_written_with_compat_evidence

legacy_intent_api_called
  -> compat_router_admitted
  -> intent_compat_evidence_recorded

current_intent_detected
  -> boundary_aware_router
  -> current_route_evidence_recorded
```

Blocked transitions:

- `current_memory_write_only -> silent_legacy_projection_write`: blocked because legacy projection must be explicit compat behavior.
- `legacy_intent_api_called -> current_route_claim`: blocked because legacy API usage is compatibility evidence.
- `migration_transaction_missing -> release_ready_for_migration_slice`: blocked because migration must be auditable.

## 5. Decision Priority

When decisions conflict, use this priority:

1. Preserve old memory importability.
2. Preserve old intent API callability under explicit compatibility admission.
3. Make current memory writes target `memory-v1` without default legacy projection writes.
4. Make first migration auditable through a migration transaction.
5. Make current intent routing boundary-aware and distinct from compatibility routing.
6. Do not change prototype/design, browser fallback naming, QA/PRD mirrors, implement package, command removal, or test marker relayering in this slice.

## 6. Source Architecture Notes

Source-backed inputs:

- `beacon/utils/memory.py`: memory-v1 storage, legacy row loading, legacy projection writing.
- `beacon/utils/intent_router.py`: current and compatibility intent route behavior.
- `beacon/compatibility/registry.py`: registry entries `memory-legacy-projection` and `intent-legacy-router`.
- `docs/beacon/v1.4.11/execution/legacy-burden-baseline-inventory.md`: baseline inventory rows for memory and intent surfaces.
- `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`: Phase 9 plan and boundary notes.

## 7. Closure Decision

Freeze the memory / intent historical migration boundary requirement package.

This package must require current memory and intent behavior to be clearly separated from historical compatibility behavior, while retaining explicit import and compatibility paths for old data and old APIs.

Do not include prototype/design changes, browser deterministic command changes, QA/PRD mirror changes, implement package changes, command removal, release verdict changes, or test marker relayering.

## 8. Projection Truth Binding

### 8.1 prd_refs

- `docs/beacon/v1.4.11/prd/memory-intent-historical-migration-boundary-contract.md`

### 8.2 user_story_refs

- `docs/beacon/v1.4.11/user-story/memory-intent-historical-migration-boundary-contract.md`

### 8.3 test_case_refs

- `docs/beacon/v1.4.11/qa/test-cases/memory-intent-historical-migration-boundary-contract.md`

### 8.4 coverage_notes

- AC-001 through AC-004 cover memory migration transaction and default current-only memory writes.
- AC-005 through AC-007 cover explicit compatibility mode for legacy projection and intent routing.
- AC-008 through AC-010 cover compatibility registry binding, no false current-route claims, and out-of-scope preservation.

### 8.5 out_of_scope_notes

- Prototype/design rebuild is already handled by `beacon-design-product-prototype-rebuild-contract`.
- Browser deterministic command naming is already handled by `browser-fallback-deterministic-command-contract`.
- Test marker relayering remains Phase 10.
- Release verdict changes are out of scope.

