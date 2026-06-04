# Change: Read-Only Support Research Write Topology Gate Contract

**Feature**: `read-only-support-research-write-topology-gate-contract`  
**Version**: `v1.4.9`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## 1. Change Reason

Beacon has a material effect registry for read-only support skills, but the write topology remains too loose. Version-bound support findings may still land in `docs/brainstorms/`, support transactions, deep directories, or ad hoc files without a single feature-level research closure point.

This creates duplicate clarification records and weakens requirement closure.

## 2. Accepted Change

Freeze a v1.4.9 topology contract for read-only support research writes:

1. Ordinary support review writes into `docs/beacon/<version>/research/<feature>.md`.
2. `beacon-deep` writes detailed artifacts into `docs/beacon/<version>/deep/<feature>/`; research only indexes the deep summary.
3. `beacon-learn` writes learning audit into `docs/beacon/<version>/learning/<feature>.md` or support transaction; research only records learning influence summary.
4. Legacy fallback to `docs/brainstorms/` is disallowed for explicit Beacon version+feature support analysis.
5. Gate and requirement clarity must fail closed when support writes violate this topology.
6. Support persistence must be preceded by a topology gate decision; unresolved routing blocks before any write and cannot use legacy fallback.

## 3. Scope

### In Scope

- Support research write topology contract.
- Ordinary support section upsert model.
- Dedicated deep artifact family preservation.
- Dedicated learning audit / transaction preservation.
- Research index summaries for deep and learning.
- Repeated clarification and cross-version lineage rules.
- Fail-closed diagnostics for invalid support write paths.
- Pre-write topology gate that selects the governed target before persistence.

### Out Of Scope

- Making support skills truth sources.
- Making support skills gate sources.
- Replacing `beacon-change` / `beacon-change-refreeze`.
- Executing implementation, QA, or release.
- Rewriting existing historical brainstorm files.

## 4. Route Decision

- This finding is accepted into v1.4.9 through `beacon-change-refreeze`.
- Runtime implementation must update support write paths and gate checks before downstream implementation can rely on the new topology.
- If a support finding changes promise, scope, or acceptance, it still routes to `beacon-change` / `beacon-change-refreeze`.

## 5. Freeze Deliverables

- `docs/beacon/archive/v1.4.9/research/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/archive/v1.4.9/source-architecture/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/archive/v1.4.9/change/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/archive/v1.4.9/prd/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/archive/v1.4.9/user-story/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/archive/v1.4.9/qa/test-cases/read-only-support-research-write-topology-gate-contract.md`

## 6. Boundary

This change refreshes requirement truth only. It does not execute implementation, QA, or release.
