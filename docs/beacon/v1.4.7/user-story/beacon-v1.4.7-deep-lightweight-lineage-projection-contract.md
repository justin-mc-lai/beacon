# User Story: Beacon v1.4.7 deep lightweight lineage projection contract

**Feature**: `beacon-v1.4.7-deep-lightweight-lineage-projection-contract`
**Version**: `v1.4.7`
**Revision**: `R1`
**Status**: `frozen`

## Story

**As a** Beacon operator using `deep` to analyze frozen requirement truth,
**I want** deep artifacts to carry lightweight, non-canonical lineage during discovery and require stronger trace only when findings are adopted or promoted,
**So that** deep remains low-friction while downstream truth surfaces can still audit and strengthen trace before refreeze, QA closure, or release.

## Acceptance Criteria

- AC-001 Deep artifacts expose a lineage projection with `lineage_mode`, `source_truth_refs`, `candidate_parent_refs`, `route_target`, `truth_impact`, and `promotion_required`.
- AC-002 L0 `source_bound` lineage is valid with file-level PRD/user-story/test-case refs and no manual `US / AC / TC` IDs.
- AC-003 L1 `machine_inferred` parent refs are optional and always marked with `confidence` plus `inferred=true`.
- AC-004 Missing exact `US / AC / TC` inferred refs does not block deep findings, risk register entries, or test deltas.
- AC-005 L2 `adoption_required` is set when a finding enters current closure through `closure_supplement`, `route_target=test-case`, `truth_impact=acceptance_delta`, or `truth_impact=requirement_meaning_delta`.
- AC-006 L2 adoption routes to `test-case` or `change/refreeze` for trace strengthening instead of writing canonical trace from deep.
- AC-007 L3 `canonical_promoted` trace can only be produced by PRD/user-story/test-case truth surfaces.
- AC-008 QA and release gates do not treat L0/L1 lineage as canonical closure truth.
- AC-009 The contract preserves `deep` as support-only: discover, explain, classify, and route are allowed; truth mutation and gate verdicts are not.

## Actor Semantics

1. Deep support executor
   - emits lightweight lineage projection
   - does not require manual parent IDs during discovery
2. Receiving truth surface
   - strengthens trace when adopting a finding
   - owns canonical promoted trace
3. QA / release gate
   - may consume L0/L1 as context
   - trusts only L3 and accepted evidence for closure
4. Human operator
   - reviews adoption/promotion decisions
   - is not forced to maintain trace details for every exploratory finding

## Boundary Notes

- `trace-on-promotion` replaces `trace-on-discovery`.
- L0/L1 are advisory projections.
- L2 is a route pressure signal.
- L3 is canonical truth.
