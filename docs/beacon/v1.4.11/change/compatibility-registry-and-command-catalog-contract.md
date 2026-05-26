# Change: Compatibility Registry and Command Catalog Contract

**Feature**: `compatibility-registry-and-command-catalog-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Change Reason

v1.4.11 Phase 0 and Phase 1 already established authority vocabulary and generated a baseline inventory of known legacy, fallback, and compatibility surfaces.

The next low-risk slice is to turn that inventory into a governed compatibility registry and to make the command catalog explicitly layered.

This change does not retire compatibility behavior. It only makes compatibility visible, typed, testable, and auditable before later behavior-changing cleanup.

## 2. Accepted Change

Freeze a requirement package that requires Beacon to:

1. Define a compatibility registry contract for known legacy, fallback, compatibility, deprecated, and historical surfaces.
2. Register the baseline inventory surfaces from v1.4.11 Phase 0.
3. Validate registry shape, required fields, known surface coverage, and command alias coverage.
4. Classify command catalog entries as current, support, advanced, labs, compatibility, deprecated, or internal.
5. Preserve current public command behavior while preventing hidden, unregistered compatibility paths from being added silently.

## 3. Scope

### In Scope

- Compatibility registry schema and validation contract.
- Registry entries for known inventory rows:
  - command catalog compat and deprecated aliases.
  - CLI factory hidden compatibility registrations.
  - implement legacy CLI loader.
  - QA legacy auto-test status mirror.
  - PRD legacy machine mirror.
  - prototype legacy wireframe source.
  - browser fallback command naming.
  - memory legacy projection migration.
  - intent legacy router facade.
- Command catalog layer contract:
  - `current`
  - `support`
  - `advanced`
  - `labs`
  - `compat`
  - `deprecated`
  - `internal`
- Tests that fail when a known compat/fallback/legacy surface is missing registry coverage.
- Tests that fail when compat or deprecated commands are recommended as the default mainline next route.

### Out Of Scope

- No removal of compat commands such as `think`, `workflow`, `auto-test`, `verify`, `gate`, `work`, `prompt`, or `save`.
- No QA legacy mirror behavior change.
- No PRD legacy mirror behavior change.
- No implement package migration or `_implement_legacy_cli` removal.
- No prototype legacy inspector split.
- No browser fallback runtime rename.
- No memory or intent behavior change.
- No compatibility registry as a new human-facing lifecycle stage.

## 4. Source Evidence

- Research: `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- Action plan: `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- Baseline inventory: `docs/beacon/v1.4.11/execution/legacy-burden-baseline-inventory.md`
- Baseline inventory JSON: `docs/beacon/v1.4.11/.machine/execution/legacy-burden-baseline-inventory.json`

## 5. Route Decision

This change accepts Phase 2 and the low-risk validation part of Phase 3 from the v1.4.11 legacy burden reduction plan.

It is intentionally registration-first:

```text
inventory -> registry -> catalog validation -> later behavior policy
```

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and freeze complete.

## 6. Freeze Deliverables

- `docs/beacon/v1.4.11/change/compatibility-registry-and-command-catalog-contract.md`
- `docs/beacon/v1.4.11/prd/compatibility-registry-and-command-catalog-contract.md`
- `docs/beacon/v1.4.11/user-story/compatibility-registry-and-command-catalog-contract.md`
- `docs/beacon/v1.4.11/qa/test-cases/compatibility-registry-and-command-catalog-contract.md`

## 7. Boundary

This feature freezes requirement truth for compatibility registry and command catalog validation only.

It does not execute implementation, QA, release, compatibility behavior retirement, legacy mirror policy change, or command removal.
