---
name: beacon-design-extract
description: Use when the user wants Beacon-owned support-only screenshot or reference extraction through the deterministic `beacon design route extract` contract.
---

# Beacon Design Extract

## Overview

This is a host-visible child skill for the Beacon design `extract` route.

It preserves the `vibe-to-ui` extraction capability while separating visible facts from inference and keeping output as support evidence until accepted facts are bound back to Beacon truth.

## When to Use

- screenshot structure extraction
- reference UI structure extraction
- component breakdown
- style cue extraction
- inference split for ambiguous references

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- support-only design extraction
- does not replace `beacon-design`
- does not treat `vibe-to-ui` output as Beacon truth

## Workflow / Decision Loop

- run or reason against `beacon design route extract "<feature>" --project . --version auto --json`
- separate observed structure from inferred assumptions
- produce prototype adapter input and component map candidates
- route accepted prototype input to `beacon prototype adapt`
- route promise-changing facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Verification

- route payload reports `route=beacon-design-extract`, `intent=extract`, and `upstream=vibe-to-ui`
- route payload marks `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- accepted design facts have a truth-binding route before implementation

## Operator Rule

Prefer:

```bash
beacon design route extract "<feature>" --project . --version auto --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```
