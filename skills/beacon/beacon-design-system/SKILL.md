---
name: beacon-design-system
description: Use when the user wants Beacon-owned support-only component system planning through the deterministic `beacon design route system` contract.
---

# Beacon Design System

## Overview

This is a host-visible child skill for the Beacon design `system` route.

It preserves the `ui-ux-pro-max` design-system capability for component, token, state, responsive, accessibility, and stack-aware baseline planning.

## When to Use

- component system planning
- design token baseline
- UI state matrix planning
- responsive behavior planning
- accessibility baseline planning
- stack-aware design guidance

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- support-only design-system planning
- does not replace `beacon-design`
- does not treat `ui-ux-pro-max` output as Beacon truth

## Workflow / Decision Loop

- run or reason against `beacon design route system "<feature>" --project . --version auto --json`
- produce component system, token, state, responsive, accessibility, and implementation baseline candidates
- route accepted prototype input to `beacon prototype adapt`
- route promise-changing facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Verification

- route payload reports `route=beacon-design-system`, `intent=system`, and `upstream=ui-ux-pro-max`
- route payload marks `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- accepted design facts have a truth-binding route before implementation

## Operator Rule

Prefer:

```bash
beacon design route system "<feature>" --project . --version auto --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```
