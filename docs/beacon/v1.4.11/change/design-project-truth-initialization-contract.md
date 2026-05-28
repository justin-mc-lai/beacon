# Change: Design Project Truth Initialization Contract

**Feature**: `design-project-truth-initialization-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## 1. Change Reason

v1.4.11 design contract declares `PRODUCT.md` and `DESIGN.md` as project-level truth:

```text
PRODUCT.md -> project-level product truth
DESIGN.md  -> project-level design truth
```

But `beacon design truth --write` currently initializes only version-wide design files under:

```text
docs/beacon/<version>/design/
```

This leaves a contract gap. Operators can see project-level truth paths in the design contract, but Beacon cannot safely create those surfaces.

## 2. Accepted Change

Freeze a small requirement delta:

1. Keep current `beacon design truth --write` behavior for version-wide design drafts.
2. Add an explicit `--include-project-truth` option.
3. When used with `--write`, the option creates missing root-level `PRODUCT.md` and `DESIGN.md`.
4. Existing project-level truth files are not overwritten unless `--force` is also provided.
5. JSON output must show per-path write status.
6. Machine design projection remains projection-only and never becomes truth authority.

## 3. Scope

### In Scope

- `beacon design truth` command contract.
- `write_version_design_contracts` behavior.
- Root-level `PRODUCT.md` / `DESIGN.md` initialization templates.
- Auditable JSON write reporting.
- Regression tests for default, explicit include, and force behavior.
- Documentation describing project-level truth initialization.

### Out Of Scope

- No automatic promotion of design subskill output into truth.
- No content migration from existing PRD / DESIGN / PRODUCT files.
- No release verdict change.
- No new lifecycle stage.
- No prototype adapter behavior change.
- No requirement that every non-UI feature must initialize project design truth.

## 4. Source Evidence

- Research: `docs/beacon/v1.4.11/research/design-project-truth-initialization-contract.md`
- Brainstorm: `docs/brainstorms/2026-05-27-beacon-brainstorm-分析-beacon-design-子-skill-设计是否合理-当前有-beacon-design-入口和-explore-extract-system-rev.md`
- Existing design contract: `beacon design contract "<feature>" --project . --version v1.4.11 --json`
- Existing design truth command: `beacon design truth --project . --version v1.4.11 --write --json`

## 5. Route Decision

This is a post-design-surface correction for v1.4.11.

It should go through normal requirement refreeze before implementation because it changes a CLI contract and the write behavior of Beacon-managed truth surfaces.

## 6. Freeze Deliverables

- `docs/beacon/v1.4.11/research/design-project-truth-initialization-contract.md`
- `docs/beacon/v1.4.11/change/design-project-truth-initialization-contract.md`
- `docs/beacon/v1.4.11/prd/design-project-truth-initialization-contract.md`
- `docs/beacon/v1.4.11/user-story/design-project-truth-initialization-contract.md`
- `docs/beacon/v1.4.11/qa/test-cases/design-project-truth-initialization-contract.md`

## 7. Boundary

This feature freezes the requirement contract for explicit project-level design/product truth initialization only.
