# Change: Project Governance Projection Lifecycle

- version: `v1.5.2`
- feature: `project-governance-projection-lifecycle`
- status: `accepted`
- reason: Close §4 projection gaps left after markdown-only project version governance (truth-map dual role, sqlite drift, version contract lifecycle).

## Summary

`markdown-only-project-version-governance` delivered MD-only governance authority and retired execution-triple branch merge. Follow-on work hardens **global-boundaries §4** semantics: one truth surface in truth-map, hash-bound sqlite projection, and archived version contracts without duplicating cross-version topology.

## Upstream

- Parent: `docs/beacon/archive/v1.5.2/features/markdown-only-project-version-governance/truth.md`
- Research: `docs/beacon/archive/v1.5.2/research/version-governance-md-only-convergence.md` (Phase 2 projection hash; §4.1 versionless topology)
- Canonical: `docs/beacon/global-boundaries.md` §4

## Scope

- In: truth-map surface hygiene; `doctor metadata verify` projection drift; `validation_state` + archive/prune for version contracts in governance MD.
- Out: new governance JSON authority; expanding governance MD to docs-version / skill-profile / feature-package meta; Rolo multi-repo topology changes.

## Boundary

- Requirement truth lives in `features/project-governance-projection-lifecycle/*.md` after refreeze.
- Does not reopen parent feature ACs unless a parent defect is proven.
