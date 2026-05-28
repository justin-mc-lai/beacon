---
name: beacon-design-polish
description: Use when the user wants Beacon-owned support-only UI ship-readiness polish through the deterministic `beacon design route polish` contract.
---

# Beacon Design Polish

## Overview

This is a host-visible child skill for the Beacon design `polish` route.

It preserves the `impeccable` polish capability for spacing, alignment, feedback detail, trust detail, and microcopy cleanup.

## When to Use

- ship-readiness polish
- spacing and alignment cleanup
- feedback state detail
- trust and confidence details
- microcopy cleanup

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- support-only design polish
- does not replace `beacon-design`
- does not treat `impeccable` output as Beacon truth

## Workflow / Decision Loop

- run or reason against `beacon design route polish "<feature>" --project . --version auto --json`
- produce polish findings and candidate cleanup deltas
- route accepted prototype input to `beacon prototype adapt`
- route promise-changing facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Verification

- route payload reports `route=beacon-design-polish`, `intent=polish`, and `upstream=impeccable`
- route payload marks `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- accepted design facts have a truth-binding route before implementation

## Operator Rule

Prefer:

```bash
beacon design route polish "<feature>" --project . --version auto --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```
