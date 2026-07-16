# Change: Version Truth Archive Lineage

- version: `v1.5.2`
- feature: `version-truth-archive-lineage`
- status: `accepted`
- reason: Promote brainstorm research on MD-only version truth catalog, physical archive plane, lineage/inventory, and global-boundaries §4.1 into frozen requirement truth.

## Summary

Beacon self-development accumulates ~49 version truth trees under `docs/beacon/v*`. Operators need a default **3-version active delivery plane**, historical lookup under `docs/beacon/archive/<version>/`, cross-version feature lineage, and AC-level capability inventory — without JSON-first catalog authority or a new lifecycle stage.

This change freezes the requirement to introduce **`docs/beacon/governance/version-truth-catalog.md`** as the sole commit source for version-level truth placement, one-time **bootstrap relocate** for non-active trees, generated **`docs/beacon/archive/INDEX.md`**, extended **`beacon archive`** commands (`catalog`, `lineage`, `inventory`), and **global-boundaries §4.1** on the MD-only catalog + archive plane.

## Upstream Research (support evidence)

- `docs/beacon/archive/v1.5.2/research/version-truth-archive-lineage.md`
- `docs/beacon/archive/v1.5.2/source-architecture/version-truth-archive-lineage.md`

## Related Shipped Work

- `markdown-only-project-version-governance` — governance MD canonical (branch/topology)
- `project-governance-projection-lifecycle` — governance projection hash + archive contract lifecycle

## Scope

- In: version-truth-catalog MD, catalog plan/apply/bootstrap, archive relocate, INDEX generation, drift verify, resolver active default, feature discovery via `features/*/truth.md`, lineage/inventory commands, skill Examples A–F, global-boundaries §4.1.
- Out: deleting archived trees; auto-archiving without `--confirm`; JSON-first catalog; standing `governance/lineage/*.md` forest; slug alias MD (deferred C5).

## Locked Closure (brainstorm)

| Item | Decision |
|------|----------|
| C1 `docs/beacon/research/` | Stay at repo root; catalog lists as support root, not a version |
| C3 link rewrite on bootstrap | Bounded rewrite in moved trees + known cross-version indexes only |
| C5 slug aliases | Defer dedicated alias file; lineage uses directory + `parent_feature` when present |

## Boundary

- Requirement truth lives in `features/version-truth-archive-lineage/*.md` only after refreeze completes.
- Physical directory moves and catalog commits happen in **implementation**, not in this change transaction.
- Implementation, QA, and release follow after freeze.
