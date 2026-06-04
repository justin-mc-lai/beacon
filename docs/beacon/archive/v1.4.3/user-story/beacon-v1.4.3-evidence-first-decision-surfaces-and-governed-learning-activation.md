# User Story: Beacon v1.4.3 Evidence-First Decision Surfaces and Governed Learning Activation

**Feature**: `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`  
**Version**: `v1.4.3`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon maintainer or advanced operator,  
**I want** Beacon to challenge requirement direction earlier, separate design decision from prototype freeze, and inject learning into default decision surfaces visibly and safely,  
**So that** Beacon becomes stronger in evidence-first quality from problem framing through UX handoff and release, instead of only after frozen truth enters implementation.

## Acceptance Criteria

- AC-001 Beacon exposes `beacon-ceo-review` as a support/review surface for version-level or major-feature requirement challenge.
- AC-002 `beacon-ceo-review` can explicitly produce `expand / hold / reduce / reframe` outputs.
- AC-003 `ceo-review` cannot freeze truth directly and must route accepted changes through existing truth surfaces.
- AC-004 Beacon exposes `beacon-design-review` as a support/review surface for UI/UX decision challenge.
- AC-005 `design-review` owns decision challenge while `prototype` remains formal freeze/handoff when triggered.
- AC-006 Beacon explicitly de-overloads `prototype` so it does not default into product strategy or design-final-approval semantics.
- AC-007 Beacon exposes `beacon-learn` as a visible learning governance surface.
- AC-008 Relevant learning can be injected by default into core decision surfaces using governed progressive disclosure.
- AC-009 Operators can see which learning influenced the current decision, route, or warning and whether it is stale or conflicting.
- AC-010 Stale or conflicting learning is downgraded, flagged, or pruned instead of silently reused.
- AC-011 `help / status / ask / deep` explain route recommendation, evidence gaps, and learning influence in human-readable form.
- AC-012 `v1.4.3` preserves minimal public surface, truth-first, and gate-first discipline while adding the new review/learning surfaces.
- AC-013 `v1.4.3` splits the umbrella line into 3 freeze-ready subfeatures whose implementation is QA-accepted and can be aggregated as umbrella acceptance evidence.

## Traceability

- PRD: `docs/beacon/archive/v1.4.3/prd/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
- Test cases: `docs/beacon/archive/v1.4.3/qa/test-cases/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`

## Boundary Notes

- `v1.4.3` is promoted to the current runtime/default docs line while preserving umbrella aggregation semantics.
- Runtime/package/docs-default/current-runtime release line remain `v1.4.0`.
- `ceo-review`, `design-review`, and `learn` are support/review surfaces, not lifecycle stages.
- learning remains advisory and cannot alone define truth, gate, or release closure.
