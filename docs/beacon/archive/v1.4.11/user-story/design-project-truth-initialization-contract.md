# User Story: Design Project Truth Initialization Contract

**Feature**: `design-project-truth-initialization-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Story

As a Beacon operator, I want `beacon design truth` to safely initialize `PRODUCT.md` and `DESIGN.md` when I explicitly ask for project-level truth, so the design contract and actual write behavior are aligned without accidentally overwriting project truth.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | backward compatibility | `beacon design truth --write` keeps writing only version-wide design surfaces by default. |
| AC-002 | product truth | `beacon design truth --write --include-project-truth` creates missing `PRODUCT.md`. |
| AC-003 | design truth | `beacon design truth --write --include-project-truth` creates missing `DESIGN.md`. |
| AC-004 | no overwrite by default | Existing `PRODUCT.md` and `DESIGN.md` are reported as `exists` and are not overwritten without `--force`. |
| AC-005 | force overwrite | With `--force`, existing project-level truth files may be overwritten and reported as `overwritten`. |
| AC-006 | auditability | JSON output reports per-path write status. |
| AC-007 | product template | Generated `PRODUCT.md` identifies itself as project-level product truth and includes required starter sections. |
| AC-008 | design template | Generated `DESIGN.md` identifies itself as project-level design truth and includes required starter sections. |
| AC-009 | projection boundary | `.machine/design/design-contract.projection.json` remains projection-only. |
| AC-010 | support boundary | Design support outputs still require Beacon truth binding before implementation. |

## Test Story Map

| Test ID | Covers | Scenario |
| --- | --- | --- |
| TEST-001 | AC-001 | Run default `--write` in a temporary project and assert no root `PRODUCT.md` / `DESIGN.md` are created. |
| TEST-002 | AC-002 | Run `--write --include-project-truth` and assert missing `PRODUCT.md` is created. |
| TEST-003 | AC-003 | Run `--write --include-project-truth` and assert missing `DESIGN.md` is created. |
| TEST-004 | AC-004 | Pre-create project truth files, run without `--force`, and assert content is unchanged. |
| TEST-005 | AC-005 | Pre-create project truth files, run with `--force`, and assert status is `overwritten`. |
| TEST-006 | AC-006 | Assert JSON output contains per-path statuses for project and version-wide truth files. |
| TEST-007 | AC-007 | Assert generated `PRODUCT.md` contains required product truth sections. |
| TEST-008 | AC-008 | Assert generated `DESIGN.md` contains required design truth sections. |
| TEST-009 | AC-009 | Assert machine design projection includes `projection_only=true`. |
| TEST-010 | AC-010 | Assert design route payload still marks support-only / non-truth / non-gate boundaries. |
