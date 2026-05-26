# User Story: Implement Package Legacy Loader Retirement Contract

**Feature**: `implement-package-legacy-loader-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Story

As a Beacon maintainer reducing implementation-surface legacy burden, I want the implement package to own the public `beacon implement` entrypoint without dynamically loading a sibling legacy CLI module, so that implement execution stays stable for users while the source structure becomes auditable and easier to maintain.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | public entrypoint | `beacon implement` remains the public implementation entrypoint. |
| AC-002 | public subcommands | Public implement subcommands still route after the package migration. |
| AC-003 | package app ownership | The package-owned implement surface exports the Typer app without dynamic sibling loading. |
| AC-004 | loader removed | `_load_legacy_cli_module` is removed from current source. |
| AC-005 | dynamic module removed | `_implement_legacy_cli` dynamic module loading is removed from current source. |
| AC-006 | tests public API | Tests no longer import or assert `_legacy_cli`. |
| AC-007 | registry binding | The retirement is bound to compatibility registry entry `implement-legacy-cli-loader`. |
| AC-008 | no unrelated retirement | Tests prove this slice does not change QA, PRD, prototype, browser, memory, intent, or command alias behavior. |

## Non Goals

- This story does not change QA legacy mirror behavior.
- This story does not change PRD legacy mirror behavior.
- This story does not split prototype legacy inspector behavior.
- This story does not rename browser fallback behavior.
- This story does not change memory migration behavior.
- This story does not change intent routing behavior.
- This story does not remove command aliases.
- This story does not create a new lifecycle stage.
- This story does not produce QA or release verdicts.

## Boundary

This story changes implement package ownership only.

It removes an internal dynamic loader after preserving the public implement CLI contract.
