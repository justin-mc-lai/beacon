# Change: beacon-v1.4.5-docs-architecture-and-machine-truth-minimization

**Version**: `v1.4.5`  
**Status**: `planned`  
**Generated**: `2026-05-12`

## Why This Change Exists

Beacon's docs tree has grown version by version without a strong semantic contract. Support surfaces now frequently dual-write human and machine artifacts even when the human artifact is only a shallow projection of machine truth.

## Delta

- freeze a clearer version-level docs structure contract
- distinguish `truth`, `guidance`, `delivery`, `evidence`, and `.machine`
- suppress paired human/machine artifacts when they add no new semantics
- define `.machine` as a projection layer with optional human companions

## Freeze Intent

This change freezes the new docs architecture semantics and artifact minimization policy. It does not require bulk migration of all historical version trees.

## Traceability

- `docs/beacon/archive/v1.4.5/prd/beacon-v1.4.5-docs-architecture-and-machine-truth-minimization.md`
- `docs/beacon/archive/v1.4.5/user-story/beacon-v1.4.5-docs-architecture-and-machine-truth-minimization.md`
- `docs/beacon/archive/v1.4.5/qa/test-cases/beacon-v1.4.5-docs-architecture-and-machine-truth-minimization.md`
