# Beacon Deep Capability Upgrade Research Supplement

**Date**: `2026-05-09`  
**Target version**: `v1.4.1`  
**Status**: `research-supplement / planning-input`  
**Source project**: `slow_uni_bmtop`  
**Source research**: `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/execution/2026-05-09-beacon-deep-capability-upgrade-research.md`  
**Source feature**: `friend-match`  

## 1. Research Import Summary

The source research came from a real BMTOP `friend-match / v1.0.0` QA closure loop.

The feature passed MVP acceptance after fixing a P2 issue, but the issue exposed a deeper Beacon capability gap:

> Beacon can validate known requirements, but complex business features also need structured discovery of hidden state machines, cross-module closure, data-source consistency, idempotency, illegal transitions, and long-term regression risk.

The source conclusion recommended a `beacon-deep` capability.

This supplement accepts the research direction but adjusts the product boundary for Beacon `v1.4.1`:

- `deep` should not become a new mandatory lifecycle stage.
- `deep` should be a support surface and gate supplement.
- `deep` should generate analysis, test delta, risk, and closure artifacts.
- `deep` should not directly rewrite frozen truth.

## 2. Key Evidence From Friend-Match

The source QA covered:

- creating a match
- adding participants
- generating matchups
- fast scoring
- leaderboard display
- joining a match
- score entry convergence
- match detail
- one-game ranking correctness
- user information and participation statistics
- guest post-match real-name binding

Final source verdict:

- primary acceptance path passed
- API regression covered US-010 / US-011
- P2 issue found and fixed
- final status: `passed-after-fix`

The important learning is not the bug itself. The important learning is the category of bug:

```text
score fact source
-> derived ranking fields
-> match detail response
-> personal statistics
-> post-match guest binding attribution
```

This category is cross-surface and stateful. It is easy to miss when test cases are only organized by individual user stories.

## 3. Capability Gap

Current Beacon capability is strong enough for MVP Gate:

- PRD truth
- user-story acceptance criteria
- test-case matrix
- QA progress
- acceptance brief
- evidence capture
- defect closure

The gap is deeper:

- missing mandatory state-machine extraction for high-risk features
- missing fact-source and derived-field modeling
- missing cross-page / cross-API consistency chain modeling
- missing illegal transition matrix
- missing idempotency and repeated-action analysis
- missing explicit release risk register produced from deep analysis

## 4. Product Boundary Adjustment

The source research proposed this conceptual path:

```text
prd
-> user-story
-> deep
-> test-case
-> qa
-> deep review
-> release
```

For Beacon `v1.4.1`, this must be adjusted to preserve global boundaries:

```text
prd
-> user-story
-> test-case
-> implement
-> qa
-> release
```

with optional support loops:

```text
prd/user-story/test-case/qa/release
-> deep analyze
-> deep delta
-> change/refreeze or supplemental qa when accepted
```

`deep` is therefore a support capability, not a new main stage.

## 5. Required Deep Analysis Dimensions

High-risk features should be inspected across these dimensions:

- role model
- entity model
- state machines
- allowed transition matrix
- forbidden transition matrix
- event and API trigger map
- fact-source vs derived-field map
- cross-surface consistency chain
- idempotency and repeated-action behavior
- ordering constraints
- migration and historical-data attribution
- permission and actor boundary
- release risk classification

## 6. First Validation Sample

`friend-match` remains a strong validation sample because it includes:

- organizer, participant, guest, and bound-real-user roles
- match lifecycle state
- participant identity state
- scoring state
- invite/join state
- leaderboard and statistics consistency
- guest binding historical attribution
- old-system takeover and migration constraints

The sample should inform Beacon `v1.4.1` without becoming Beacon-specific canonical truth.

## 7. Recommended v1.4.1 Design Move

The first `v1.4.1` requirement should define:

1. a deep analysis support surface
2. artifact contracts for analysis/state/test-delta/risk/closure
3. trigger rules and skip reasons
4. release gate supplement semantics
5. change/refreeze integration for accepted requirement deltas
6. non-goals that prevent scope creep and QA duplication

## 8. Research Decision

Adopt:

- deep analysis as a formal support capability
- state-machine and data-consistency modeling as required high-risk dimensions
- test-case delta generation as the main implementation output
- risk register and closure brief as release-facing artifacts

Reject or defer:

- making `deep` a mandatory lifecycle stage
- letting `deep` directly rewrite frozen truth
- requiring deep for low-risk static features
- making deep execute tests in the first iteration

## 9. Traceability Into v1.4.1 PRD

This supplement feeds:

- `docs/beacon/archive/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`

The PRD should be treated as the normative next-version requirement statement. This research supplement remains evidence and rationale.
