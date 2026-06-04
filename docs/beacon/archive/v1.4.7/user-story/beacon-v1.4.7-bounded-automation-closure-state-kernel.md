# User Story: Beacon v1.4.7 bounded automation closure-state kernel

**Feature**: `beacon-v1.4.7-bounded-automation-closure-state-kernel`  
**Version**: `v1.4.7`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon maintainer, scheduled automation operator, or project owner relying on recurring QA and repair loops,  
**I want** Beacon automation to express bounded closure state, repeated repair rounds, and queue-safety semantics as formal runtime truth,  
**So that** repeated QA and implement repair can converge predictably without silently rewriting requirement truth, forking state under concurrent schedulers, or pretending to be a full autonomous lifecycle.

## Acceptance Criteria

- AC-001 Beacon defines a machine-readable closure-state envelope for feature-level bounded automation repair work, including current closure state, next route, terminal signal, round number, and previous-round reference.
- AC-002 Beacon freezes a bounded closure-state taxonomy that can at minimum distinguish `active`, `blocked`, `release_ready`, `closed`, and `human_escalation_required`.
- AC-003 Beacon freezes a bounded next-route taxonomy that can at minimum distinguish `qa`, `implement`, `release`, and `human` for the current slice, without implying that `deep/refreeze` automation is already runtime-ready.
- AC-004 Beacon defines an active issue register inheritance contract so repeated repair rounds carry only still-relevant stop reasons, accepted fixes, targeted rerun hints, and prior-round references rather than copying full artifact history.
- AC-005 Beacon makes QA exit authoritative for bounded runtime routing, so a QA round can explicitly emit `ready_for_release`, `implement_repair`, or `human_escalation` intent into the automation runtime object.
- AC-006 Beacon makes implement repair exit authoritative for bounded runtime routing, so a repair round can explicitly emit either return-to-QA intent or human-escalation intent.
- AC-007 Beacon adds queue revision semantics so automation queue mutation is guarded against stale writers and does not silently overwrite newer queue state.
- AC-008 Beacon adds feature-level execution lease semantics so only one automation worker can actively claim the same feature at one time.
- AC-009 Beacon provides operator-visible bounded runtime explanation for each round, including the current round number, closure state, terminal signal, next route, and whether human takeover is required.
- AC-010 Beacon explicitly preserves the truth boundary for this slice: automation can move repair work and state, but cannot autonomously move requirement truth, auto-promote scenario discoveries, or market itself as a full Automation Closure-Loop.

## Actor and Round Semantics

### Primary actors

1. QA round executor
   - observes verification outcome
   - writes bounded closure-state verdict
   - decides release-ready vs repair-needed vs human-escalation
2. Implement repair executor
   - consumes active issue register
   - applies one bounded repair round
   - emits next runtime intent back to QA or human
3. Automation scheduler / queue worker
   - claims feature execution lease
   - enforces queue revision and stale-writer rejection
   - does not own requirement truth
4. Human operator
   - receives escalation when bounded automation cannot safely continue
   - remains the only owner of truth-moving decisions

### Round semantics

- Round 0
  - initial QA observation
  - produces first bounded closure-state verdict and active issue register seed
- Round 1
  - first implement repair attempt after Round 0
  - must inherit the Round 0 active issue register
- Round N
  - every later round must inherit only currently active issues and the latest bounded refs
  - every round must emit one terminal signal and one next route

## Boundary Notes

- This story does not accept `deep` as a runtime-owned continuation engine.
- This story does not accept automatic `change/refreeze` execution.
- This story does not accept automation-driven requirement truth movement.
- This story does not treat local pass signals as equivalent to requirement closure or release closure.

## Freeze Narrowing

The accepted `v1.4.7` automation slice is intentionally narrowed to:

1. closure-state envelope
2. active issue register
3. authoritative QA/implement bounded routing
4. queue revision
5. feature execution lease
6. stale-writer rejection and single-flight guarantees

Anything beyond those six elements remains future roadmap or later `change`, not current acceptance truth.
