---
name: beacon-design-bootstrap
description: Use when the user wants Beacon-owned support-only upstream design capability admission checks through the deterministic `beacon design route bootstrap` contract.
---

# Beacon Design Bootstrap

## Overview

This is a host-visible child skill for the Beacon design `bootstrap` route.

It checks installed skill, mirrored source tree, or bootstrap route availability for upstream design capabilities. It is capability-admission-only.

## When to Use

- verify upstream design skills are installed
- verify mirrored open-source design sources exist
- inspect bootstrap route availability
- diagnose missing design capability prerequisites

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- capability-admission-only
- support-only bootstrap check
- does not replace `beacon-design`
- does not prove design quality or release readiness

## Workflow / Decision Loop

- run or reason against `beacon design route bootstrap "<feature>" --project . --version auto --json`
- use `beacon design bootstrap --project . --version auto --json` for capability admission details
- report installed, mirrored, or bootstrap availability only
- route accepted prototype input to `beacon prototype adapt`
- route promise-changing facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Verification

- route payload reports `route=beacon-design-bootstrap`, `intent=bootstrap`, and `upstream=upstream-compatibility`
- route payload marks `capability_admission_only=true`, `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- bootstrap payload marks `release_verdict=false`

## Operator Rule

Prefer:

```bash
beacon design route bootstrap "<feature>" --project . --version auto --json
beacon design bootstrap --project . --version auto --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```
