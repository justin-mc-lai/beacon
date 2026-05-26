# Change: Authority Vocabulary and Baseline Inventory Contract

**Feature**: `authority-vocabulary-and-baseline-inventory-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Change Reason

v1.4.11 research found that Beacon's Markdown-first direction is correct, but the runtime and documentation still contain mixed authority vocabulary and a broad legacy/fallback/compatibility surface.

The accepted low-risk first slice is to freeze Phase 0 and Phase 1 from the legacy burden reduction plan:

- Phase 0: baseline inventory of current legacy, fallback, and compatibility surfaces.
- Phase 1: authority vocabulary cleanup so machine artifacts are described as projection, evidence, read model, runtime state, compatibility mirror, or historical fixture rather than requirement truth.

## 2. Accepted Change

Freeze a requirement package that requires Beacon to:

1. Define stable artifact authority roles.
2. Correct machine-as-truth wording in policy and human-facing output.
3. Generate a baseline inventory before behavior changes.
4. Preserve existing runtime behavior during this slice.
5. Produce deterministic tests for forbidden wording, inventory schema, and no behavior retirement.

## 3. Scope

### In Scope

- Authority vocabulary contract for truth, projection, evidence, runtime state, compatibility mirror, and historical fixture.
- Baseline inventory markdown and JSON artifact requirements.
- Static scan or deterministic inventory of known legacy/fallback/compatibility hotspots.
- Low-risk wording changes that do not alter gate behavior.
- Tests proving `.machine` is no longer described as requirement truth in current-facing wording.

### Out Of Scope

- Compatibility registry implementation.
- QA legacy mirror behavior change.
- PRD legacy mirror behavior change.
- Implement legacy loader migration.
- Prototype legacy inspector split.
- Browser fallback rename behavior.
- Memory or intent historical migration behavior change.
- Test marker relayering beyond tests required for this slice.

## 4. Source Evidence

- Research: `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- Action plan: `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- Code map: `.understand-anything/knowledge-graph.json`
- Code map report: `.understand-anything/graph-build-report.json`

## 5. Route Decision

This change accepts only the low-risk Phase 0 and Phase 1 requirement slice.

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and freeze complete.

## 6. Freeze Deliverables

- `docs/beacon/v1.4.11/change/authority-vocabulary-and-baseline-inventory-contract.md`
- `docs/beacon/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md`
- `docs/beacon/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md`
- `docs/beacon/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md`
- `docs/beacon/v1.4.11/research/authority-vocabulary-and-baseline-inventory-contract.md`
- `docs/beacon/v1.4.11/source-architecture/authority-vocabulary-and-baseline-inventory-contract.md`

## 7. Boundary

This feature freezes requirement truth for vocabulary and inventory only.

It does not execute implementation, QA, release, registry retirement, compatibility behavior changes, or legacy removal.
