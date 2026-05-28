# Research Closure: Design Project Truth Initialization Contract

**Feature candidate**: `design-project-truth-initialization-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`  
**Source surfaces**:

- `docs/beacon/v1.4.11/research/beacon-design-product-prototype-rebuild-contract.md`
- `docs/beacon/v1.4.11/research/beacon-design-human-subskills-closure-contract.md`
- `docs/brainstorms/2026-05-27-beacon-brainstorm-分析-beacon-design-子-skill-设计是否合理-当前有-beacon-design-入口和-explore-extract-system-rev.md`

## 1. Conclusion

Beacon v1.4.11 design now has stable support routes and host-visible `beacon-design-*` subskills.

The remaining gap is narrower:

```text
The design truth contract declares PRODUCT.md and DESIGN.md as project-level truth,
but `beacon design truth --write` initializes only version-wide design files.
```

This is confusing and incomplete. Operators can see that project-level product/design truth is part of the contract, but the CLI cannot safely initialize those files.

The right fix is not to silently create or overwrite project truth by default. The right fix is to add an explicit, auditable project-truth initialization option.

## 2. Plain-Language Problem

Beacon design can now help decide:

- what the product is trying to promise,
- what the UI should feel like,
- what components and states should exist,
- how accepted UI/UX facts should flow into implementation.

But when the operator asks Beacon to initialize design truth, Beacon only creates:

```text
docs/beacon/<version>/design/style.md
docs/beacon/<version>/design/component-system.md
docs/beacon/<version>/design/interaction-contract.md
docs/beacon/<version>/design/state-matrix.md
```

It does not create:

```text
PRODUCT.md
DESIGN.md
```

So the design contract says one thing, while the write command does another.

## 3. Design Judgment

Keeping `PRODUCT.md` and `DESIGN.md` out of the default write path is reasonable because they are project-level truth, not version-local drafts.

However, operators need a deterministic way to initialize them when they are missing.

The intended behavior should be:

```text
default --write:
  create version-wide design truth drafts only

--write --include-project-truth:
  also create missing PRODUCT.md and DESIGN.md

--force:
  may overwrite existing generated surfaces when explicitly requested
```

This keeps project truth safe while making the truth initialization path complete.

## 4. Scope Recommendation

Freeze a small feature:

```text
design-project-truth-initialization-contract
```

It should add a deterministic and auditable path for project-level product/design truth initialization.

## 5. Required Behavior

The feature should require:

1. `beacon design truth --write` keeps existing behavior and initializes only version-wide design surfaces.
2. `beacon design truth --write --include-project-truth` creates missing `PRODUCT.md` and `DESIGN.md`.
3. Existing `PRODUCT.md` and `DESIGN.md` are not overwritten unless `--force` is provided.
4. JSON output reports `written`, `exists`, or `overwritten` per path.
5. The generated `PRODUCT.md` template explains project-level product truth.
6. The generated `DESIGN.md` template explains project-level design truth.
7. `.machine/design/design-contract.projection.json` remains projection-only.
8. Accepted design facts still require Beacon truth binding, prototype adapter binding, or change/refreeze before implementation.

## 6. Non Goals

- Do not promote `beacon-design-*` output into truth automatically.
- Do not make design a new lifecycle stage.
- Do not make `.machine/design` the source of truth.
- Do not require every project to have `PRODUCT.md` / `DESIGN.md` before all non-UI work.
- Do not change release verdict logic in this feature.

## 7. Next Route

This finding changes the frozen design truth initialization contract, so it must enter:

```text
beacon-change-refreeze -> implement -> qa
```
