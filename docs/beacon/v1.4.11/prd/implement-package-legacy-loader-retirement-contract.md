# PRD: Implement Package Legacy Loader Retirement Contract

**Feature**: `implement-package-legacy-loader-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Overview

This feature freezes the v1.4.11 implement package migration slice.

Beacon must remove the hidden dynamic loader that imports sibling `beacon/commands/implement.py` as `_implement_legacy_cli`, while preserving the public `beacon implement ...` command experience.

The feature is internal-structure cleanup. It must not remove public implement capability.

## 1. Problem

`beacon.commands.implement` is now a package with extracted helper modules, but `beacon/commands/implement/__init__.py` still dynamically loads sibling `beacon/commands/implement.py`.

That means:

- implement ownership is split between package modules and a sibling legacy file.
- tests may still depend on `_legacy_cli`.
- code maps and static audits see a hidden dynamic import path.
- future implement cleanup cannot tell which surface is current.

The user-facing command can remain stable without keeping this dynamic loader.

## 2. Goals

- AC-001: `beacon implement` remains the public implementation entrypoint.
- AC-002: Public implement subcommands still route after the package migration.
- AC-003: The package-owned implement surface exports the Typer app without dynamic sibling loading.
- AC-004: `_load_legacy_cli_module` is removed from current source.
- AC-005: `_implement_legacy_cli` dynamic module loading is removed from current source.
- AC-006: Tests no longer import or assert `_legacy_cli`.
- AC-007: The retirement is bound to the compatibility registry entry `implement-legacy-cli-loader`.
- AC-008: This slice does not change QA, PRD, prototype, browser, memory, intent, or command alias behavior.

## 3. Design Principles

### 3.1 Public UX stable

Users should keep calling:

```text
beacon implement ...
```

No public implement command should disappear as part of this slice.

### 3.2 Package owns current behavior

The package directory `beacon/commands/implement/` must own the current implement entrypoint.

### 3.3 No hidden dynamic bridge

The current code must not load sibling `implement.py` under an internal module name.

### 3.4 Tests use public contracts

Tests must verify public CLI or helper APIs, not `_legacy_cli` internals.

## 4. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | `beacon implement --help` must remain routeable. |
| FR-002 | AC-002 | Main public implement subcommands must remain visible and callable. |
| FR-003 | AC-003 | `beacon.commands.implement.app` must come from package-owned current code. |
| FR-004 | AC-003 | `run_implement_stage` or equivalent public helper must remain importable if still used by callers. |
| FR-005 | AC-004 | Current source must not define `_load_legacy_cli_module`. |
| FR-006 | AC-005 | Current source must not register `beacon.commands._implement_legacy_cli`. |
| FR-007 | AC-006 | Tests must not import, monkeypatch, or assert `_legacy_cli`. |
| FR-008 | AC-007 | Compatibility registry must retain `implement-legacy-cli-loader` with this feature as retirement route. |
| FR-009 | AC-008 | Regression tests must prove no unrelated QA, PRD, prototype, browser, memory, intent, or command alias behavior is retired. |

## 5. Required Command Coverage

The implementation must verify at least these public surfaces:

- `beacon implement --help`
- `beacon implement list-runners --help`
- `beacon implement import-evidence --help`
- `beacon implement run --help`
- `beacon implement plan --help`
- `beacon implement status --help`
- `beacon implement check-branch --help`
- `beacon implement sync-git-workflow --help`

If additional public implement subcommands exist, they should remain visible unless a separate frozen change removes them.

## 6. Runtime Behavior Contract

Default behavior:

```text
beacon.main
  -> implement package app
  -> package-owned command handlers
```

Forbidden behavior:

```text
implement package
  -> importlib load sibling beacon/commands/implement.py
  -> module name beacon.commands._implement_legacy_cli
```

## 7. Success Metrics

- Public implement command help works.
- Public implement subcommands remain discoverable.
- Static scan finds no `_load_legacy_cli_module`.
- Static scan finds no `_implement_legacy_cli`.
- Static scan finds no tests depending on `_legacy_cli`.
- Registry binding for `implement-legacy-cli-loader` remains present.
- No unrelated legacy behavior is retired.

## 8. Diagram Truth Layer

### 8.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 8.2 State Axes

- `implement_entrypoint`: `package_app`, `legacy_dynamic_loader_removed`
- `public_cli_state`: `routeable`, `missing`, `behavior_changed`
- `test_contract_state`: `public_api_bound`, `legacy_internal_bound`
- `migration_scope`: `implement_only`, `unrelated_surface_change`

### 8.3 Branch Flow

```text
beacon implement command request
  -> package app exists
    -> route public command
  -> package app missing
    -> fail implementation entrypoint check
  -> legacy dynamic loader present
    -> fail static scan
  -> public command removed
    -> fail CLI smoke
```

### 8.4 State Machine

```text
legacy_loader_registered
  -> package_app_required
  -> package_app_exported
  -> legacy_loader_removed
  -> public_cli_verified
```

Terminal states:

- `public_cli_verified`: package-owned app routes public implement commands.
- `static_scan_blocked`: legacy loader names remain in current source or tests.
- `scope_drift_blocked`: unrelated surface behavior changed in this slice.

### 8.5 Decision Priority

```text
public implement UX
  > package-owned current entrypoint
  > compatibility registry traceability
  > internal cleanup convenience
  > legacy sibling loader retention
```

The legacy sibling loader cannot outrank current package ownership once public command stability is proven.

## 9. Non Goals

- No QA legacy mirror policy changes.
- No PRD legacy mirror policy changes.
- No prototype legacy inspector split.
- No browser fallback rename.
- No memory migration policy change.
- No intent router policy change.
- No command alias removal.
- No new lifecycle stage.
