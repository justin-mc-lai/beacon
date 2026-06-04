# Research Closure: Compatibility Registry and Command Catalog Contract

**Feature**: `compatibility-registry-and-command-catalog-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Purpose

This research closure promotes the second low-risk slice of the v1.4.11 legacy burden reduction plan into requirement truth.

The slice covers:

- Phase 2: compatibility registry, registration-first and no behavior change.
- Low-risk part of Phase 3: command catalog validation and explicit command layering.

It intentionally excludes behavior-changing retirement work for QA legacy mirror, PRD legacy mirror, implement legacy loader, prototype legacy source, browser fallback, memory migration, and intent router fallback.

## 2. Architecture

The architecture is:

```text
v1.4.11 baseline inventory
  -> compatibility registry
  -> registry validation
  -> command catalog layer validation
  -> later explicit admission / retirement features
```

The registry is an internal governance artifact. It does not become a new lifecycle stage and does not replace the mainline:

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

Registry entries must describe compatibility surfaces with stable lifecycle metadata:

- compat id.
- surface category.
- owner.
- reason.
- introduced-before version.
- allowed version range.
- default behavior.
- current replacement.
- retirement route.
- required evidence.

Command catalog validation must classify command surfaces into:

- `current`
- `support`
- `advanced`
- `labs`
- `compat`
- `deprecated`
- `internal`

The mainline remains compact. Compat and deprecated commands may remain callable, but default guidance must not recommend them as the normal current next route.

Source-backed input comes from:

- `docs/beacon/archive/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- `docs/beacon/archive/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- `docs/beacon/archive/v1.4.11/execution/legacy-burden-baseline-inventory.md`
- `docs/beacon/archive/v1.4.11/.machine/execution/legacy-burden-baseline-inventory.json`

## 3. Business Flow

The operator and maintainer flow is:

```text
baseline inventory exists
  -> freeze compatibility registry requirement
  -> implement registry and command layer validation
  -> QA verifies schema, coverage, route discipline, and no behavior retirement
  -> later features use registry to change defaults or retire behavior
```

The important business rule is that registry is not retirement.

This feature answers:

- what compatibility surface exists.
- why it exists.
- who owns it.
- what replaces it.
- what evidence keeps it valid.
- which later feature may change it.

This feature does not answer by deleting or disabling the path.

## 4. State Machine

```text
inventory_available
  -> registry_required
  -> registry_defined
  -> catalog_layers_validated
  -> behavior_change_ready_for_later_feature
```

Allowed transitions:

- `inventory_available -> registry_required`: accepted by v1.4.11 Phase 2 scope decision.
- `registry_required -> registry_defined`: implementation creates registry schema and entries.
- `registry_defined -> catalog_layers_validated`: command catalog validation classifies current, support, advanced, labs, compat, deprecated, and internal entries.
- `catalog_layers_validated -> behavior_change_ready_for_later_feature`: QA proves registry coverage and no behavior retirement.

Blocked transitions:

- `inventory_available -> behavior_retirement`: blocked because registry coverage does not exist yet.
- `registry_defined -> command_removal`: blocked because this slice does not remove commands.
- `registry_defined -> QA_legacy_policy_change`: blocked because QA mirror retirement is a later feature.
- `registry_defined -> PRD_legacy_policy_change`: blocked because PRD mirror retirement is a later feature.
- `catalog_layers_validated -> release_ready`: blocked unless implementation, QA, and release evidence close normally.

## 5. Decision Priority

When decisions conflict, use this priority:

1. Preserve Beacon QA, release, projection, evidence, git, metadata, version, and project hook gates.
2. Preserve existing compatibility behavior during this slice.
3. Register known compatibility, fallback, legacy, deprecated, and historical surfaces before changing defaults.
4. Keep the public mainline route compact and current-facing.
5. Classify compat and deprecated command surfaces explicitly.
6. Route behavior-changing cleanup into later frozen features.

## 6. Source Architecture Notes

Code-map-backed registry inputs:

- `beacon/command_catalog.py`: `COMPAT_COMMANDS` and `DEPRECATED_COMMANDS`.
- `beacon/cli_factory.py`: hidden command registration and compatibility aliases.
- `beacon/commands/implement/__init__.py`: `_load_legacy_cli_module`.
- `beacon/utils/qa_runtime.py`: canonical QA status and legacy auto-test status mirror.
- `beacon/utils/material_audit.py`: PRD legacy mirror drift audit.
- `beacon/utils/prototype_utils.py`: legacy wireframe source status.
- `beacon/adapters/browser_runner_common.py`: fallback command evidence wording.
- `beacon/utils/memory.py`: legacy memory projection migration.
- `beacon/utils/intent_router.py`: compatibility intent facade.

The first implementation should prefer a small registry module or JSON registry plus validation helpers. It should not spread compatibility metadata across unrelated command implementations.

## 7. Closure Decision

Freeze the registration-first compatibility registry and command catalog validation requirement package.

Do not include command removal, default behavior changes, legacy mirror retirement, implement migration, browser rename, memory migration changes, or intent router behavior changes in this frozen slice.

## 8. Projection Truth Binding

### 8.1 prd_refs

- `docs/beacon/archive/v1.4.11/prd/compatibility-registry-and-command-catalog-contract.md`

### 8.2 user_story_refs

- `docs/beacon/archive/v1.4.11/user-story/compatibility-registry-and-command-catalog-contract.md`

### 8.3 test_case_refs

- `docs/beacon/archive/v1.4.11/qa/test-cases/compatibility-registry-and-command-catalog-contract.md`

### 8.4 coverage_notes

- AC-001 through AC-003 cover registry schema, inventory coverage, and lifecycle metadata.
- AC-004 covers command catalog layering.
- AC-005 and AC-008 cover no behavior retirement.
- AC-006 covers current route discipline.
- AC-007 covers fail-closed validation for unregistered compatibility surfaces.

### 8.5 out_of_scope_notes

- Command removal is out of scope.
- QA and PRD legacy mirror behavior changes are out of scope.
- Implement legacy loader migration is out of scope.
- Prototype, browser, memory, and intent compatibility behavior changes are out of scope.
- Release verdict changes are out of scope.

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-05-26T11:48:36.591783+00:00`
- deep_artifact_root: `docs/beacon/archive/v1.4.11/deep/compatibility-registry-and-command-catalog-contract`
- machine_artifact_root: `docs/beacon/archive/v1.4.11/.machine/deep/compatibility-registry-and-command-catalog-contract`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/archive/v1.4.11/.machine/deep/compatibility-registry-and-command-catalog-contract/release-supplement.json`
- adoption_status: `route_only`
