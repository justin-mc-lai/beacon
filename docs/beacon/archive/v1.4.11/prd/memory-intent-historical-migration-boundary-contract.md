# PRD: Memory / Intent Historical Migration Boundary Contract

**Feature**: `memory-intent-historical-migration-boundary-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Overview

This feature freezes Phase 9 of the v1.4.11 legacy burden reduction plan.

Beacon must preserve historical memory and intent compatibility without letting legacy projections and legacy router semantics keep shaping the current runtime path by default.

## 1. Problem

Memory and intent still carry historical behavior into the current runtime:

- Memory can migrate old files into `memory-v1`, but current writes can continue updating old projection files.
- Intent routing keeps old public APIs callable, but compatibility routing is not clearly separated from current boundary-aware routing.

This creates avoidable weight and audit ambiguity. Current behavior should be current by default; legacy behavior should be explicit compatibility behavior.

## 2. Goals

- AC-001: Old memory rows remain importable into current `memory-v1`.
- AC-002: First legacy memory migration writes an auditable migration transaction.
- AC-003: `memory-v1` is treated as the current memory projection after migration.
- AC-004: Current memory writes do not write legacy memory projection files by default.
- AC-005: Legacy memory projection writes require explicit compatibility mode or explicit migration/export command.
- AC-006: Legacy intent router usage is marked as compatibility routing.
- AC-007: Old intent APIs remain callable through explicit compatibility admission.
- AC-008: Current intent routing uses boundary-aware current routing and does not claim legacy router output as current route evidence.
- AC-009: Memory behavior is bound to compatibility registry entry `memory-legacy-projection`.
- AC-010: Intent behavior is bound to compatibility registry entry `intent-legacy-router`.
- AC-011: Tests prove this slice does not change prototype/design, browser, QA/PRD mirror, implement package, command removal, release, or test marker behavior.

## 3. Design Principles

### 3.1 Current path stays current

Current memory writes target current memory projection. Current intent routing uses current route semantics.

### 3.2 Compatibility remains explicit

Legacy memory projection writes and legacy intent routing remain possible, but only as compatibility behavior with evidence.

### 3.3 Migration must be auditable

Importing historical memory is allowed, but the first migration must produce a transaction that explains what moved and why.

### 3.4 Scope stays narrow

This feature is not the prototype/design rebuild, browser deterministic command rename, QA/PRD mirror policy, implement package migration, command removal, release verdict, or test marker relayering feature.

## 4. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Memory utilities must preserve the ability to import older memory rows into current `memory-v1`. |
| FR-002 | AC-002 | The first legacy memory migration must write a migration transaction with source files, imported counts, and compatibility id. |
| FR-003 | AC-003 | After migration, `memory-v1` must be the current memory projection used by current memory APIs. |
| FR-004 | AC-004 | Current memory writes must not update legacy projection files unless compatibility mode is explicit. |
| FR-005 | AC-005 | Legacy projection writes must require explicit compatibility mode or explicit migration/export command. |
| FR-006 | AC-006 | Legacy intent router usage must emit compatibility classification or evidence. |
| FR-007 | AC-007 | Existing legacy intent API entrypoints must remain callable through explicit compatibility admission. |
| FR-008 | AC-008 | Current intent routing must expose current route evidence separate from legacy compatibility route evidence. |
| FR-009 | AC-009 | Memory migration behavior must bind to `memory-legacy-projection`. |
| FR-010 | AC-010 | Intent compatibility behavior must bind to `intent-legacy-router`. |
| FR-011 | AC-011 | Regression tests must prove unrelated surfaces stay unchanged. |

## 5. Required Compatibility Binding

This feature must bind to registry entries:

- `memory-legacy-projection`
- `intent-legacy-router`

The registry entries remain compatibility governance. They do not become lifecycle stages, truth sources, or gate sources.

## 6. Evidence Contract

Memory migration evidence must expose at least:

- `migration_transaction_id`
- `compat_id=memory-legacy-projection`
- `source_files`
- `imported_count`
- `skipped_count`
- `current_projection=memory-v1`
- `legacy_projection_written`
- `compat_mode`

Intent compatibility evidence must expose at least:

- `compat_id=intent-legacy-router`
- `route_kind=compat_router` or equivalent
- `current_route_claimed=false`
- `current_router_available`
- `recommended_current_route`

The field names may be adapted to local conventions, but tests must prove the semantic distinction.

## 7. Success Metrics

- Old memory rows can still be imported.
- First migration is auditable.
- Current memory writes no longer silently update legacy projection files.
- Explicit compat mode can still write legacy projections.
- Old intent API remains callable under compatibility admission.
- Current intent route evidence is separate from legacy compatibility route evidence.
- Compatibility registry bindings are present.
- No unrelated prototype/design/browser/QA/PRD/implement/release/test-marker behavior changes.

## 8. Non Goals

- No prototype or design behavior change.
- No browser deterministic command behavior change.
- No QA legacy mirror behavior change.
- No PRD legacy mirror behavior change.
- No implement package behavior change.
- No command removal.
- No release verdict change by itself.
- No test marker relayering.

