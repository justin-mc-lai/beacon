# User Story: Beacon v1.4.7 automation support-review, truth-refreeze, and promotion contract

**Feature**: `beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract`  
**Version**: `v1.4.7`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon maintainer, automation operator, or real-project owner,  
**I want** automation runtime to distinguish support-review, truth pressure, scenario-discovery class, and promotion-proof strength,  
**So that** repeated closure work can continue boundedly without mistaking structural uncertainty for implementation work, and without letting runtime silently mutate frozen truth.

## Acceptance Criteria

- AC-001 Beacon can emit `next_route=support_review` with explicit executor and reason metadata when QA or automation determines that repeated structural failure needs a support surface rather than immediate implement retry.
- AC-002 Beacon can record bounded `deep` outcomes that distinguish implementation-only findings, truth-pressure findings, and repeat-cap exhaustion.
- AC-003 Beacon can route support-review outcomes to `implement`, `change_refreeze`, or `human`, without inventing a new primary lifecycle stage.
- AC-004 Beacon can record `truth_recompiled_pending=true` plus explicit downstream target surfaces that must be regenerated before implement resumes.
- AC-005 Beacon blocks `implement` when automation runtime says support review is still required, truth refreeze is required, or truth recompile is still pending.
- AC-006 Beacon can classify scenario discovery into `closure_supplement` and `promotion_candidate`, with explicit `requirement_meaning_delta` and `requires_truth_reopen` flags.
- AC-007 Beacon routes `closure_supplement` or requirement-meaning delta into `change_refreeze`, but keeps pure `promotion_candidate` findings in a non-canonical sink without blocking current closure by default.
- AC-008 Beacon projects promotion-grade proof hooks from current evidence, including acceptance-kit presence, all-layer pass state, real-project proof presence, and missing proof hooks.
- AC-009 Beacon keeps all new automation runtime behavior inside the support plane: classify, route, explain, and block are allowed; canonical truth mutation and autonomous refreeze are not.

## Actor Semantics

1. QA round executor
   - may decide the next step is no longer direct implement retry
   - can emit `support_review` route intent
2. Support-review executor
   - can be `deep` or another support surface
   - may conclude:
     - implementation-only defect
     - requirement meaning pressure
     - repeat cap exhausted
3. Truth owner / change-refreeze owner
   - remains human-governed
   - owns canonical truth updates and downstream recompilation
4. Implement executor
   - may continue only after support/truth barriers are cleared
5. Release / promotion owner
   - uses proof hooks as evidence input
   - does not treat proof hooks as release verdict replacement

## Round Semantics

- QA round may create a support-review detour without expanding the lifecycle
- support-review outcome does not increment closure truth by itself; it only narrows the next safe route
- truth refreeze and downstream recompilation are separate from support-review outcome
- promotion candidates may accumulate across rounds, but remain non-canonical until a governed `change` accepts them

## Boundary Notes

- `support_review` is a route target, not a new stage
- `deep` is a bounded support executor, not an autonomous truth owner
- `truth_recompiled_pending` is a hard barrier, not a soft reminder
- promotion proof hooks strengthen routing judgment, but do not define release truth
