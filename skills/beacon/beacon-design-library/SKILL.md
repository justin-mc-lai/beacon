---
name: beacon-design-library
description: Use when the user wants Beacon-owned support-only design reference lookup through the deterministic `beacon design route library` contract.
---

# Beacon Design Library

## Overview

This is a host-visible child skill for the Beacon design `library` route.

It preserves `awesome-design-md` as a reference-only source for curated patterns and adaptation notes. It is not an execution skill and not Beacon truth.

## When to Use

- curated design reference lookup
- pattern example comparison
- adaptation guidance
- component or layout inspiration

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- reference-only
- support-only design library lookup
- does not replace `beacon-design`
- does not treat `awesome-design-md` as an execution skill

## Workflow / Decision Loop

- run or reason against `beacon design route library "<feature>" --project . --version auto --json`
- produce reference notes and adaptation candidates
- keep source references separate from accepted project truth
- route accepted prototype input to `beacon prototype adapt`
- route promise-changing facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Verification

- route payload reports `route=beacon-design-library`, `intent=library`, and `upstream=awesome-design-md`
- route payload marks `reference_only=true`, `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- accepted design facts have a truth-binding route before implementation

## Operator Rule

Prefer:

```bash
beacon design route library "<feature>" --project . --version auto --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```
