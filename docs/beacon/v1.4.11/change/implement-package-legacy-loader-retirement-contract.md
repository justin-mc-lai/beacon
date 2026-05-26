# Change: Implement Package Legacy Loader Retirement Contract

**Feature**: `implement-package-legacy-loader-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Change Reason

v1.4.11 has already registered the implement legacy CLI loader as a compatibility surface.

The next reduction slice is to remove the internal dynamic loader while preserving the public `beacon implement ...` surface.

Current code still loads sibling `beacon/commands/implement.py` through:

```text
beacon.commands.implement.__init__
  -> _load_legacy_cli_module
  -> beacon.commands._implement_legacy_cli
```

That structure makes implement ownership ambiguous and keeps tests coupled to an internal migration bridge.

## 2. Accepted Change

Freeze a requirement package that requires Beacon to:

1. Keep `beacon implement` as the public implementation entrypoint.
2. Keep public implement subcommands routeable.
3. Move required CLI exports into package-owned implement modules.
4. Remove `_load_legacy_cli_module`.
5. Remove `_implement_legacy_cli` dynamic module loading.
6. Update tests to use public app/helper APIs instead of `_legacy_cli`.
7. Bind the migration to the compatibility registry entry `implement-legacy-cli-loader`.
8. Preserve unrelated legacy, compat, QA, PRD, prototype, browser, memory, and intent behavior.

## 3. Scope

### In Scope

- `beacon/commands/implement/__init__.py` package entrypoint cleanup.
- Package-owned app export for `beacon implement`.
- Migration or direct package exposure for required implement CLI commands.
- Removal of `_load_legacy_cli_module`.
- Removal of `_implement_legacy_cli` dynamic import.
- Tests proving public implement commands still route.
- Static scan tests proving legacy loader names are absent from current source.
- Tests proving no `_legacy_cli` import/assert dependency remains.

### Out Of Scope

- No QA legacy mirror changes.
- No PRD legacy mirror changes.
- No prototype legacy inspector split.
- No browser fallback rename.
- No memory migration behavior change.
- No intent router behavior change.
- No command alias removal.
- No change to implement's lifecycle role.

## 4. Source Evidence

- Research: `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- Action plan: `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- Baseline inventory: `docs/beacon/v1.4.11/execution/legacy-burden-baseline-inventory.md`
- Compatibility registry: `beacon/compatibility/registry.py`
- Current loader: `beacon/commands/implement/__init__.py`

## 5. Route Decision

This change accepts Phase 6 from the v1.4.11 legacy burden reduction plan.

It is intentionally implement-package-only:

```text
registry -> QA/PRD mirror policy -> implement package loader retirement -> later prototype/browser/memory/intent policy
```

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and freeze complete.

## 6. Freeze Deliverables

- `docs/beacon/v1.4.11/research/implement-package-legacy-loader-retirement-contract.md`
- `docs/beacon/v1.4.11/change/implement-package-legacy-loader-retirement-contract.md`
- `docs/beacon/v1.4.11/prd/implement-package-legacy-loader-retirement-contract.md`
- `docs/beacon/v1.4.11/user-story/implement-package-legacy-loader-retirement-contract.md`
- `docs/beacon/v1.4.11/qa/test-cases/implement-package-legacy-loader-retirement-contract.md`

## 7. Boundary

This feature freezes requirement truth for implement package legacy loader retirement only.

It does not execute implementation, QA, release, QA/PRD mirror policy, prototype migration, browser rename, memory migration, intent routing changes, or command removal.
