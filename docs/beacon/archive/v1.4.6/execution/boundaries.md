# Beacon v1.4.6 Execution Boundaries

## Status

- version: `v1.4.6`
- status: `current_runtime_release`
- runtime line: `v1.4.6` is the current runtime/default docs line
- implementation line: `v1.4.6` is complete and promoted

## Main Lifecycle Boundary

`v1.4.6` does not add or rename a public lifecycle stage.

The main lifecycle remains:

```text
prd
-> user-story
-> test-case
-> implement
-> qa
-> release
```

## Skill Contract Boundary

`v1.4.6` strengthens host-visible skill contracts, but it does not turn skills into rigid operation scripts.

The enforced public contract is:

```text
strategy philosophy
-> minimum complete tools
-> necessary facts
-> explicit boundary / verification / gate semantics
```

The line must not:

- prescribe step-by-step execution playbooks for strong models by default
- let support surfaces invent requirement truth
- let presentation polish masquerade as release evidence

## Support-Surface Boundary

The following remain support surfaces rather than new truth or gate owners:

- `beacon-brainstorm`
- `beacon-deep`
- `beacon-ceo-review`
- `beacon-design-review`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`

These surfaces may challenge, explain, route, and expose consequence.
They may not:

- freeze requirement truth
- grant release readiness on their own
- create a parallel delivery lifecycle

## Truth Boundary

Canonical truth for this line remains:

- `docs/beacon/global-boundaries.md`
- `docs/beacon/archive/v1.4.6/prd/`
- `docs/beacon/archive/v1.4.6/user-story/`
- `docs/beacon/archive/v1.4.6/qa/test-cases/`
- `docs/beacon/archive/v1.4.6/change/`

`.machine` remains a projection and audit layer.
It can enforce drift detection, but it does not become an independent source of product truth.

## Enforcement Boundary

`v1.4.6` adds machine-checkable anti-drift enforcement for:

- missing required skill anatomy
- support-surface authority overreach
- high-risk challenge outputs without route / evidence / state / gate binding

This enforcement is intentionally narrow:

- it blocks contract regression
- it does not replace human requirement judgment
- it does not auto-promote a release line

## Implementation Boundary

The frozen implementation-facing subfeature for this line is:

- `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`

This subfeature stays inside Beacon's existing truth, QA, and release governance, and cannot bypass version-surface promotion just because implementation and tests are green.
