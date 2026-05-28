# PRD: Design Project Truth Initialization Contract

**Feature**: `design-project-truth-initialization-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Overview

Beacon design has a project-level truth contract, but the CLI cannot initialize the project-level files declared by that contract.

This feature adds an explicit, safe, auditable initialization path for `PRODUCT.md` and `DESIGN.md`.

## 1. Problem

`beacon design contract` reports:

```text
PRODUCT.md
DESIGN.md
docs/beacon/<version>/design/style.md
docs/beacon/<version>/design/component-system.md
docs/beacon/<version>/design/interaction-contract.md
docs/beacon/<version>/design/state-matrix.md
```

But `beacon design truth --write` only creates the version-wide files.

This means the CLI contract and write behavior are not fully aligned.

## 2. Goals

- AC-001: `beacon design truth --write` keeps existing default behavior and writes only version-wide design surfaces.
- AC-002: `beacon design truth --write --include-project-truth` creates missing root-level `PRODUCT.md`.
- AC-003: `beacon design truth --write --include-project-truth` creates missing root-level `DESIGN.md`.
- AC-004: Existing `PRODUCT.md` and `DESIGN.md` are not overwritten unless `--force` is provided.
- AC-005: With `--force`, existing project-level truth files may be overwritten and JSON output reports `overwritten`.
- AC-006: JSON output reports per-path status: `written`, `exists`, or `overwritten`.
- AC-007: Generated `PRODUCT.md` explains that it is project-level product truth.
- AC-008: Generated `DESIGN.md` explains that it is project-level design truth.
- AC-009: `.machine/design/design-contract.projection.json` remains projection-only.
- AC-010: Accepted design facts still require truth binding, prototype adapter binding, or change/refreeze before implementation.

## 3. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Preserve default version-wide-only write behavior for `beacon design truth --write`. |
| FR-002 | AC-002 | Add `--include-project-truth` to `beacon design truth`. |
| FR-003 | AC-002, AC-003 | Create missing `PRODUCT.md` and `DESIGN.md` when `--write --include-project-truth` is used. |
| FR-004 | AC-004 | Do not overwrite existing project-level truth files without `--force`. |
| FR-005 | AC-005 | Overwrite existing project-level truth files only when `--force` is explicit. |
| FR-006 | AC-006 | Return auditable JSON write status for all design truth paths touched or skipped. |
| FR-007 | AC-007 | Provide a product truth starter template for `PRODUCT.md`. |
| FR-008 | AC-008 | Provide a design truth starter template for `DESIGN.md`. |
| FR-009 | AC-009 | Keep machine design output projection-only. |
| FR-010 | AC-010 | Keep design support outputs out of implementation until bound through Beacon truth routes. |

## Scope

### In Scope

- `beacon design truth` CLI option parsing.
- `write_version_design_contracts` write behavior.
- Explicit `--include-project-truth` initialization of missing root-level `PRODUCT.md` and `DESIGN.md`.
- Default no-overwrite protection for project-level truth files.
- Explicit `--force` overwrite behavior for project-level truth files.
- Auditable JSON write statuses for project-level and version-wide design truth paths.
- Starter templates for project-level product and design truth.
- Regression tests for default, include, force, template, projection, and support boundary behavior.

### Out Of Scope

- No automatic promotion of design support output into truth.
- No new design lifecycle stage.
- No release gate verdict change.
- No prototype adapter behavior change.
- No mandatory project truth initialization for non-UI features.
- No historical product/design content migration.

## 5. Command Contract

Default behavior:

```bash
beacon design truth --project . --version v1.4.11 --write --json
```

Creates or preserves:

```text
docs/beacon/v1.4.11/design/style.md
docs/beacon/v1.4.11/design/component-system.md
docs/beacon/v1.4.11/design/interaction-contract.md
docs/beacon/v1.4.11/design/state-matrix.md
docs/beacon/v1.4.11/.machine/design/design-contract.projection.json
```

Project truth initialization:

```bash
beacon design truth --project . --version v1.4.11 --write --include-project-truth --json
```

Also creates missing:

```text
PRODUCT.md
DESIGN.md
```

Force overwrite:

```bash
beacon design truth --project . --version v1.4.11 --write --include-project-truth --force --json
```

May overwrite existing `PRODUCT.md` and `DESIGN.md`.

## 6. Template Requirements

`PRODUCT.md` must include sections for:

- product purpose,
- target users,
- core product promises,
- non-goals,
- truth update policy.

`DESIGN.md` must include sections for:

- design principles,
- component system baseline,
- interaction principles,
- UI state coverage,
- accessibility and responsive baseline,
- truth update policy.

## 7. Non Goals

- No automatic design-result-to-truth promotion.
- No direct mutation from `beacon-design-*` support output.
- No new lifecycle stage.
- No release gate change.
- No project-level truth requirement for all features.
- No migration of historical product/design docs.

## 8. Success Metrics

- Default write behavior remains backward-compatible.
- Explicit include creates `PRODUCT.md` and `DESIGN.md` when missing.
- Existing files are protected by default.
- Force behavior is explicit and auditable.
- Tests verify JSON write statuses and projection-only machine output.
