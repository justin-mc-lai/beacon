# Beacon Feature Change Document

- feature: `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
- feature_slug: `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
- version: `v1.4.0`
- status: `frozen-pending-implementation`

## Scope
- reopen frozen requirement package for Beacon self-repo version drift governance
- supplement canonical release manifest, projected version surfaces, and sync/verify doctor requirements
- re-freeze the feature package into pending implementation state

## Added
- `FR-009A` canonical release manifest as the only editable version truth source
- `FR-009B` package/runtime/docs/skill/rules version surfaces become manifest-driven projections
- `FR-009C` `beacon doctor sync-version-surfaces` / `verify-version-surfaces` governance
- `AC-105` single manifest requirement for Beacon self-repo
- `AC-106` projected version surfaces requirement
- `AC-107` sync-version-surfaces repair requirement
- `AC-108` verify-version-surfaces strict blocking requirement

## Removed / Reduced
- none

## Fixed
- Updated `docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- Updated `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- Updated `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- Updated `docs/beacon/v1.4.0/execution/revision-delta-beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- Updated `docs/beacon/v1.4.0/SUMMARY.md`

## Traceability Refs
- `docs/beacon/v1.4.0/research/beacon-openspec-speckit-comparison-and-deliverable-design.md`
- `docs/beacon/v1.4.0/research/openspec-archive-vs-beacon-version-evolution.md`
- `beacon/__init__.py`
- `beacon/version-truth.json`
- `beacon/version-semantics.json`
