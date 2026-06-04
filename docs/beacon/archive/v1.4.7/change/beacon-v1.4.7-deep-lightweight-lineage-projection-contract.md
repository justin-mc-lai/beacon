# Change: beacon-v1.4.7-deep-lightweight-lineage-projection-contract

**Version**: `v1.4.7`
**Status**: `implemented-and-verified`
**Generated**: `2026-05-16`
**Track**: `deep-support-surface + trace-on-promotion + lightweight-lineage`

## Why This Change Exists

`deep` already analyzes frozen requirement truth and derives routeable findings, risk, and test deltas. A naive lineage design would require every deep discovery to carry exact `US / AC / TC` parent IDs. CEO review challenged that direction because it would increase human maintenance cost and pollute `deep` as a low-friction support surface.

This change enters the revised design:

> Use trace-on-promotion instead of trace-on-discovery.

During discovery, `deep` keeps lightweight source-bound and machine-inferred lineage. Strong canonical trace is required only when a finding is adopted into `test-case`, `change/refreeze`, or formal promotion.

When the accepted route is `change/refreeze`, human-facing route guidance should point to `beacon-change-refreeze`, which delegates to the existing `beacon change ... --refreeze-chain` transaction.

## Delta

- add a layered lineage model for deep artifacts
- keep L0/L1 lineage non-blocking and low-friction
- require stronger trace only at adoption/promotion boundaries
- prevent `deep` from becoming a truth source or new stage
- make release and QA gates trust only canonical promoted trace

## Layered Lineage Model

1. `L0 source-bound`
   - bind deep output to file-level frozen truth refs
   - no manual `US / AC / TC` maintenance
2. `L1 machine-inferred`
   - machine may infer candidate `story_id / AC / TC`
   - inferred refs must carry confidence and `inferred=true`
3. `L2 adoption-required`
   - when a finding enters current closure, the receiving truth surface must strengthen trace
   - this occurs in `test-case` or `change/refreeze`, not in `deep`
4. `L3 canonical-trace`
   - only promoted PRD/user-story/test-case material becomes canonical trace
   - release and QA gates trust L3, not L0/L1

## Implementation Status

This change has been implemented and verified through the `deep` artifact lineage projection contract.

The delivered package defines:

- deep artifact lineage schema
- route rules for L0/L1/L2/L3
- non-blocking behavior for missing inferred IDs
- adoption/promotion rules that require trace strengthening
- gate rules that prevent L0/L1 from being mistaken for canonical truth

## Out Of Scope

- automatic deep execution
- automatic truth writeback
- automatic scenario promotion
- requiring humans to fill `US / AC / TC` IDs during discovery
- treating inferred lineage as release-grade evidence

## Traceability

- `skills/beacon/beacon-deep/SKILL.md`
- `beacon/utils/deep_loop.py`
- `beacon/utils/automation_runtime.py`
- `docs/beacon/archive/v1.4.7/prd/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- `docs/brainstorms/2026-05-16-beacon-brainstorm-基于-ceo-review-对-deep-traceable-scenario-lineage-的挑战-过度要求-us-ac-tc-级-lineage-会提高人.md`
