# Change: beacon-v1.4.3-governed-learning-recall-and-route-explainability

**Version**: `v1.4.3`  
**Status**: `planned`  
**Generated**: `2026-05-11`

## Why This Change Exists

Beacon already has a learning plane, but learning does not yet reliably enter each relevant skill as a default decision input. That leaves learning stored but not operationalized.

## Delta

- add a host-visible `beacon-learn` governance surface
- require default governed learning injection for core decision surfaces
- expose learning influence, confidence, and staleness to operators
- define stale/conflicting learning downgrade, flag, and prune behavior
- require `help / status / ask / deep` to explain route and learning influence

## Freeze Intent

This change freezes learning-governance expectations and route explainability requirements. It does not implement retrieval ranking, pruning jobs, or UI presentation yet.

## Traceability

- `docs/beacon/v1.4.3/prd/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`
- `docs/beacon/v1.4.3/user-story/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`
- `docs/beacon/v1.4.3/qa/test-cases/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md`
