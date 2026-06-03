# Change: Markdown-Only Project Version Governance

- version: `v1.5.2`
- feature: `markdown-only-project-version-governance`
- status: `accepted`
- reason: Promote v1.5.2 research on MD-only version/topology/Git governance into frozen requirement truth.

## Summary

v1.5.2 completed feature-package MD-first (AC-006) but left version/topology/Git branch governance on JSON-first `.beacon/metadata/` with optional `execution/branch-governance-*` overrides. This change freezes the requirement to use a single governance Markdown truth surface with zero governance JSON records, unified read/write via truth-map resolver, and toolkit/implement consumers aligned to that surface.

## Upstream Research (support evidence)

- `docs/beacon/v1.5.2/research/version-governance-git-branch-closure.md`
- `docs/beacon/v1.5.2/research/version-governance-md-only-convergence.md`
- `docs/beacon/v1.5.2/research/explicit-version-canonical-branch-worktree-preflight-gate.md`

## Scope

- In: governance MD path, parser contract, resolver, metadata/branch-governance toolkit write path, implement preflight consumption, migration off JSON and execution triple branch authority.
- Out: Rolo application code changes; post-merge file-content verification (separate friction/change).

## Boundary

- Requirement truth lives in `features/markdown-only-project-version-governance/*.md` only after refreeze completes.
- Implementation, QA, and release follow after freeze.
