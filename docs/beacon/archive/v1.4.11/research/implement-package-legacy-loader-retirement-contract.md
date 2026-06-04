# Research Closure: Implement Package Legacy Loader Retirement Contract

**Feature**: `implement-package-legacy-loader-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Purpose

This research closure promotes Phase 6 of the v1.4.11 legacy burden reduction plan into requirement truth.

The slice covers implement package migration only:

- remove the hidden `_implement_legacy_cli` dynamic sibling-loader.
- keep the public `beacon implement ...` command surface stable.
- move required CLI exports into the package-owned implement surface.
- update tests so current contracts use public app/helper APIs instead of `_legacy_cli`.

This feature depends on the prior compatibility registry and mirror-policy slices. It removes an internal migration bridge, not a user-facing capability.

## 2. Architecture

The target architecture is:

```text
beacon.main
  -> beacon.commands.implement package
  -> package-owned Typer app / command modules
  -> adapter, git, ralph, team, evidence, preflight helpers
```

The current architecture still contains a dynamic bridge:

```text
beacon.commands.implement.__init__
  -> import sibling beacon/commands/implement.py
  -> register as beacon.commands._implement_legacy_cli
  -> re-export app and run_implement_stage
```

The migration must remove that bridge while preserving the public CLI contract.

## 3. Business Flow

The operator flow must remain:

```text
frozen requirement truth
  -> beacon implement ...
  -> implementation evidence
  -> beacon qa
```

The maintainer flow changes internally:

```text
legacy sibling CLI loader present
  -> freeze package migration requirement
  -> move or expose required commands through package modules
  -> remove dynamic sibling loader
  -> prove public implement commands still route
```

This feature answers:

- which implement entrypoint is current.
- which public commands must remain callable.
- which internal loader must disappear.
- how tests prove the package owns implement behavior.

It does not change implement's user-facing lifecycle role.

## 4. State Machine

```text
legacy_loader_registered
  -> package_cli_required
  -> package_cli_exported
  -> legacy_loader_removed
  -> public_implement_surface_verified
```

Allowed transitions:

- `legacy_loader_registered -> package_cli_required`: accepted by v1.4.11 Phase 6 scope decision.
- `package_cli_required -> package_cli_exported`: implementation moves or exposes CLI commands through package modules.
- `package_cli_exported -> legacy_loader_removed`: `_load_legacy_cli_module` and `_implement_legacy_cli` dynamic import are removed.
- `legacy_loader_removed -> public_implement_surface_verified`: CLI smoke tests and static scans pass.

Blocked transitions:

- `legacy_loader_registered -> public_command_removal`: blocked because public implement UX must remain stable.
- `package_cli_exported -> QA_or_PRD_policy_change`: blocked because QA and PRD mirror policies are separate completed slices.
- `legacy_loader_removed -> prototype_browser_memory_intent_change`: blocked because those are later features.
- `public_implement_surface_verified -> release_ready`: blocked unless implementation, QA, and release evidence close normally.

## 5. Decision Priority

When decisions conflict, use this priority:

1. Preserve `beacon implement` as the only public implementation entrypoint.
2. Preserve existing public implement subcommands and route semantics.
3. Prefer package-owned modules over dynamic sibling loading.
4. Tests must use public app/helper APIs, not `_legacy_cli`.
5. Static scan must fail if `_implement_legacy_cli` or `_load_legacy_cli_module` returns.
6. Do not expand this slice into QA, PRD, prototype, browser, memory, intent, or command alias behavior.

## 6. Source Architecture Notes

Source-backed inputs:

- `beacon/commands/implement/__init__.py`: current dynamic loader and package exports.
- `beacon/commands/implement.py`: sibling CLI module currently loaded under `_implement_legacy_cli`.
- `beacon/commands/implement/adapter.py`: adapter integration.
- `beacon/commands/implement/git.py`: git workflow helpers.
- `beacon/commands/implement/ralph.py`: Ralph runtime helpers.
- `beacon/commands/implement/team.py`: team mode helpers.
- `tests/test_v147_automation_support_review_and_promotion_contract.py`: known test coupling to `_legacy_cli`.
- `docs/beacon/archive/v1.4.11/execution/legacy-burden-baseline-inventory.md`: baseline inventory row `implement-legacy-cli-loader`.
- `beacon/compatibility/registry.py`: registry entry `implement-legacy-cli-loader`.

## 7. Closure Decision

Freeze the implement package legacy loader retirement requirement package.

This package must require package-owned implement CLI exports, removal of dynamic sibling loading, and public CLI smoke evidence.

Do not include QA legacy mirror policy, PRD legacy mirror policy, prototype legacy inspector split, browser fallback rename, memory migration changes, intent router changes, command removal, or compatibility registry as a new lifecycle stage.

## 8. Projection Truth Binding

### 8.1 prd_refs

- `docs/beacon/archive/v1.4.11/prd/implement-package-legacy-loader-retirement-contract.md`

### 8.2 user_story_refs

- `docs/beacon/archive/v1.4.11/user-story/implement-package-legacy-loader-retirement-contract.md`

### 8.3 test_case_refs

- `docs/beacon/archive/v1.4.11/qa/test-cases/implement-package-legacy-loader-retirement-contract.md`

### 8.4 coverage_notes

- AC-001 through AC-003 cover public implement CLI stability and package-owned entrypoint behavior.
- AC-004 through AC-006 cover removal of dynamic sibling loading and test coupling.
- AC-007 covers compatibility registry binding.
- AC-008 covers no unrelated retirement.

### 8.5 out_of_scope_notes

- QA and PRD legacy mirror policies are out of scope.
- Prototype, browser, memory, and intent behavior changes are out of scope.
- Compat command removal is out of scope.
- Release verdict changes are out of scope.
