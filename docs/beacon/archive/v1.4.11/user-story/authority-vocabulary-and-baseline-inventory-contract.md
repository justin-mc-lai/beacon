# User Story: Authority Vocabulary and Baseline Inventory Contract

**Feature**: `authority-vocabulary-and-baseline-inventory-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Story

As a Beacon maintainer planning v1.4.11 legacy burden reduction, I want Beacon to define authority vocabulary and inventory legacy/fallback/compatibility surfaces before behavior changes, so that later cleanup can be audited without weakening QA, release, projection, evidence, git, metadata, or version gates.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | artifact roles | Beacon defines explicit artifact roles for truth, projection, evidence, runtime state, compatibility mirror, and historical fixture. |
| AC-002 | wording boundary | Current-facing wording does not describe `.machine` or machine-readable artifacts as requirement truth. |
| AC-003 | Markdown truth | Markdown requirement materials under `docs/beacon/<version>/` remain the current requirement truth. |
| AC-004 | projection retained | `.machine` remains available as projection, evidence, and read model. |
| AC-005 | baseline inventory | Beacon produces baseline inventory artifacts before behavior-changing cleanup. |
| AC-006 | inventory schema | Each inventory row includes source file, symbol or function, surface category, current behavior, risk, proposed owner, proposed phase, and required evidence. |
| AC-007 | no behavior retirement | This slice does not remove or change existing runtime compatibility behavior. |
| AC-008 | regression guard | Tests fail when forbidden machine-as-truth wording or missing inventory coverage is introduced. |

## Non Goals

- This story does not implement a compatibility registry.
- This story does not change QA legacy mirror behavior.
- This story does not change PRD legacy mirror behavior.
- This story does not migrate the implement legacy loader.
- This story does not split prototype legacy inspector behavior.
- This story does not rename browser fallback behavior.
- This story does not change memory or intent runtime behavior.
- This story does not produce QA or release verdicts.

## Boundary

This story is a low-risk governance prerequisite. It makes authority and legacy burden visible before later v1.4.11 features perform behavior-changing cleanup.
