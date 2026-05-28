---
name: beacon-design-explore
description: Use when the user wants Beacon-owned support-only UI direction exploration through the deterministic `beacon design route explore` contract.
---

# Beacon Design Explore

## Overview

This is a host-visible child skill for the Beacon design `explore` route.

It preserves the `vibe-to-ui` exploration capability while keeping output as design direction candidates until accepted facts are bound back to Beacon truth.

## When to Use

- UI direction exploration
- concept direction comparison
- information hierarchy sketching
- layout model exploration
- interaction model candidates

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- support-only design exploration
- does not replace `beacon-design`
- does not treat `vibe-to-ui` output as Beacon truth

## Workflow / Decision Loop

- run or reason against `beacon design route explore "<feature>" --project . --version auto --json`
- produce concept directions, hierarchy options, layout models, and interaction candidates
- route accepted prototype input to `beacon prototype adapt`
- route promise-changing facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Verification

- route payload reports `route=beacon-design-explore`, `intent=explore`, and `upstream=vibe-to-ui`
- route payload marks `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- accepted design facts have a truth-binding route before implementation

## Operator Rule

Prefer:

```bash
beacon design route explore "<feature>" --project . --version auto --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```
