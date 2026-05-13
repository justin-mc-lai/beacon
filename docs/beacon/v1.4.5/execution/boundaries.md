# Beacon v1.4.5 Execution Boundaries

## Status

- version: `v1.4.5`
- status: `current_runtime_release`
- runtime line: `v1.4.5` is the current runtime/default docs line
- implementation line: `this line is promoted and release-governed`

## Main Lifecycle Boundary

`v1.4.5` does not add a new main lifecycle stage.

The main lifecycle remains:

```text
prd
-> user-story
-> test-case
-> implement
-> qa
-> release
```

## Guidance Surface Boundary

`v1.4.5` formalizes a guidance surface family, but these remain support surfaces outside the primary lifecycle:

- `beacon-ceo-review`
- `beacon-brainstorm`
- `beacon-design-review`
- `beacon-deep`

These surfaces may challenge, explain, and route. They may not become truth authority, gate authority, or a second completion line.

## Truth Boundary

Canonical truth for this line remains:

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.5/prd/`
- `docs/beacon/v1.4.5/user-story/`
- `docs/beacon/v1.4.5/qa/test-cases/`
- `docs/beacon/v1.4.5/change/`

Neither guidance projections nor external capability sources may freeze truth directly.

## Docs Semantics Boundary

`v1.4.5` clarifies semantic layers:

- `truth`
- `guidance`
- `delivery`
- `evidence`
- `.machine`

`.machine` remains a projection layer. It is not an independent requirement source.

## External Capability Boundary

External capability sources are first-class and governed, but they stay within Beacon's existing runtime and truth boundaries.

- business-goal-first selection is allowed
- capability composition may be learned over time
- external sources may not bypass frozen requirement truth
- external sources may not redefine runtime gates

## Implementation Boundary

The frozen implementation-facing subfeatures are:

- `beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning`
- `beacon-v1.4.5-docs-architecture-and-machine-truth-minimization`
- `beacon-v1.4.5-governed-external-skill-sources-and-learning-composition`

These subfeatures now ship inside the promoted `v1.4.5` release line and remain governed by Beacon's shared runtime and release gates.
