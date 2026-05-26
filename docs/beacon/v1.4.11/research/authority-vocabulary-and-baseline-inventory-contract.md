# Research Closure: Authority Vocabulary and Baseline Inventory Contract

**Feature**: `authority-vocabulary-and-baseline-inventory-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Purpose

This research closure promotes the low-risk first slice of the v1.4.11 legacy burden reduction plan into requirement truth.

The slice covers:

- Phase 0: baseline inventory before behavior changes.
- Phase 1: authority vocabulary cleanup for Markdown truth, machine projection, runtime evidence, and compatibility mirrors.

It intentionally excludes behavior-changing retirement work for QA legacy mirror, PRD legacy mirror, implement legacy loader, prototype legacy source, browser fallback, memory migration, and intent router fallback.

## 2. Architecture

The low-risk slice introduces a small authority vocabulary contract and an inventory artifact contract.

The architecture is:

```text
Markdown requirement truth
  -> deterministic projection / read model
  -> runtime evidence
  -> status / help / report wording
  -> baseline inventory for later compatibility registry work
```

The authority vocabulary must classify artifacts by role:

- `truth`
- `projection`
- `evidence`
- `runtime_state`
- `compat_mirror`
- `historical_fixture`

The baseline inventory must capture existing legacy, fallback, and compatibility surfaces without changing their runtime behavior.

Source-backed input comes from:

- `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- `.understand-anything/knowledge-graph.json`
- `.understand-anything/graph-build-report.json`

## 3. Business Flow

The operator flow is:

```text
research finding accepted
  -> freeze low-risk authority/inventory requirement
  -> implement inventory and vocabulary tooling
  -> QA verifies wording, inventory schema, and no behavior change
  -> later features consume inventory to build compatibility registry and retirement policies
```

The important business rule is that inventory is not cleanup. Inventory is the pre-change audit layer.

This prevents accidental removal of compatibility behavior before Beacon has evidence about:

- source file
- symbol or function
- current behavior
- risk
- proposed phase
- proposed owner
- required test evidence

## 4. State Machine

```text
research_input
  -> refreeze_input
  -> frozen_requirement
  -> implementation_inventory_generated
  -> qa_verified
  -> downstream_registry_ready
```

Allowed transitions:

- `research_input -> refreeze_input`: accepted by v1.4.11 scope decision.
- `refreeze_input -> frozen_requirement`: PRD, user-story, test-case, clarity, and freeze are complete.
- `frozen_requirement -> implementation_inventory_generated`: implementation produces markdown and JSON inventory.
- `implementation_inventory_generated -> qa_verified`: tests verify schema, forbidden wording, and no behavior change.
- `qa_verified -> downstream_registry_ready`: later v1.4.11 slices may begin compatibility registry work.

Blocked transitions:

- `research_input -> implementation`: blocked because requirement truth is not frozen.
- `frozen_requirement -> behavior_retirement`: blocked because this slice does not retire behavior.
- `inventory_generated -> release_ready`: blocked unless QA and release evidence close normally.

## 5. Decision Priority

When decisions conflict, use this priority:

1. Preserve Beacon QA, release, evidence, projection, git, metadata, and version gates.
2. Preserve existing user-visible behavior during this slice.
3. Correct authority vocabulary where it incorrectly describes machine artifacts as requirement truth.
4. Generate auditable inventory before any compatibility retirement.
5. Route any behavior-changing retirement into later frozen features.

## 6. Source Architecture Notes

Code-map-backed hotspots:

- `beacon/artifact-language-policy.json`: low-risk wording source.
- `beacon/utils/artifact_language.py`: low-risk default wording and renderer source.
- `beacon/command_catalog.py`: central command classification, later registry input.
- `beacon/cli_factory.py`: command registration and hidden compatibility surface.
- `beacon/commands/implement/__init__.py`: implement legacy loader, inventory only in this slice.
- `beacon/utils/qa_runtime.py`: QA canonical and legacy mirror behavior, inventory only in this slice.
- `beacon/utils/material_audit.py`: PRD legacy mirror and drift classification, inventory only in this slice.
- `beacon/utils/prototype_utils.py`: prototype legacy source behavior, inventory only in this slice.
- `beacon/adapters/browser_runner_common.py`: browser fallback evidence wording, inventory only in this slice.
- `beacon/utils/memory.py`: legacy memory migration behavior, inventory only in this slice.
- `beacon/utils/intent_router.py`: legacy intent router behavior, inventory only in this slice.

## 7. Closure Decision

Freeze the low-risk Phase 0 and Phase 1 requirement package first.

Do not include Phase 2 or later behavior-changing work in this frozen slice.

## 8. Projection Truth Binding

### 8.1 prd_refs

- `docs/beacon/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md`

### 8.2 user_story_refs

- `docs/beacon/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md`

### 8.3 test_case_refs

- `docs/beacon/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md`

### 8.4 coverage_notes

- AC-001 through AC-004 cover authority vocabulary and Markdown/projection boundaries.
- AC-005 and AC-006 cover baseline inventory artifacts and schema.
- AC-007 covers the no-behavior-retirement boundary.
- AC-008 covers regression guards for forbidden wording and hotspot coverage.

### 8.5 out_of_scope_notes

- Compatibility registry is out of scope.
- QA and PRD legacy mirror behavior changes are out of scope.
- Implement legacy loader migration is out of scope.
- Prototype, browser, memory, and intent compatibility behavior changes are out of scope.

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-05-26T11:18:32.532312+00:00`
- deep_artifact_root: `docs/beacon/v1.4.11/deep/authority-vocabulary-and-baseline-inventory-contract`
- machine_artifact_root: `docs/beacon/v1.4.11/.machine/deep/authority-vocabulary-and-baseline-inventory-contract`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/v1.4.11/.machine/deep/authority-vocabulary-and-baseline-inventory-contract/release-supplement.json`
- adoption_status: `route_only`
