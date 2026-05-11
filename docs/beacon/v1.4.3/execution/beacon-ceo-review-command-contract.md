# Beacon CEO Review Command Contract

## Scope

- command surface: `beacon-ceo-review`
- feature: `beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface`
- status: `implementation-spec-ready`

## Intent

Provide a founder/CEO-grade requirement challenge surface for version-level or major-feature-level problem reframing and scope judgment without creating a second truth source.

## Invocation Contract

### Supported entry shapes

```text
beacon ceo-review "<version-or-feature>"
beacon ceo-review "<version-or-feature>" --focus problem
beacon ceo-review "<version-or-feature>" --focus scope
beacon ceo-review "<version-or-feature>" --focus promise
```

## Required Inputs

- target version or feature slug
- bound truth refs:
  - PRD
  - user-story
  - test-case
- review focus:
  - `problem`
  - `scope`
  - `promise`
  - `full`

## Optional Inputs

- explicit operator concern
- business constraint note
- prior learning refs
- prior brainstorm or deep refs

## Output Contract

The surface must always emit:

- `decision`
  - `expand`
  - `hold`
  - `reduce`
  - `reframe`
- `why_now`
- `evidence_used`
- `challenge_summary`
- `risk_if_ignored`
- `route_decision`
- `writeback_targets`
- `blocked_reason` or `none`

## Decision Semantics

- `expand`: current scope is too narrow to satisfy the real user or business goal
- `hold`: current scope is directionally correct and should remain stable
- `reduce`: current scope carries unjustified promise or delivery risk
- `reframe`: the requirement package is solving the wrong problem or expressing the wrong commitment

## Route Contract

Accepted decisions must route to existing truth surfaces only:

- PRD problem/goal/boundary change -> `beacon-change` then `beacon-prd`
- story acceptance or actor shift -> `beacon-user-story`
- test coverage obligation shift -> `beacon-test-case`
- multi-surface change -> `beacon-change` umbrella route

## Writeback Contract

`beacon-ceo-review` must never freeze truth directly.

It may only produce:

- proposed delta summary
- affected truth refs
- recommended next route
- reason code and operator note

Canonical writeback remains downstream in:

- `change`
- `prd`
- `user-story`
- `test-case`

## Blocked Reasons

- `truth_refs_missing`
- `review_scope_ambiguous`
- `version_level_target_missing`
- `insufficient_promise_evidence`
- `conflicting_learning_requires_operator_resolution`

## Boundary Rules

- cannot mark `freeze-ready`
- cannot mark `release-ready`
- cannot bypass `change/refreeze`
- cannot silently rewrite requirement truth
- cannot become a generic brainstorm alias

## Acceptance Hooks

- AC-001 through AC-005 for `beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface`
