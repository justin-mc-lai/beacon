---
name: beacon-design-review
description: Use when the user wants Beacon-owned support-only UX review through the deterministic `beacon design route review` contract while preserving Beacon truth binding.
---

# Beacon Design Review

## Overview

This is a host-visible child skill for the Beacon design `review` route.

It preserves the `impeccable` review capability while keeping review output as support evidence until accepted facts are bound back to Beacon truth.

## When to Use

- hierarchy review
- copy and flow friction review
- missing state review
- accessibility review
- UX finding prioritization

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- support-only design review
- does not replace `beacon-design`
- does not replace `beacon-prototype`
- does not treat `impeccable` output as Beacon truth

## Workflow / Decision Loop

- run or reason against `beacon design route review "<feature>" --project . --version auto --json`
- produce prioritized UX findings and candidate design truth deltas
- route accepted prototype input to `beacon prototype adapt`
- route promise-changing facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Common Rationalizations

- “review output is accepted, so it is truth.” -> Not allowed; accepted facts still need Beacon truth binding.
- “Small UX findings do not need requirement routing.” -> Not allowed when they change product promise, behavior, AC, or QA coverage.
- “Review pass means release pass.” -> Not allowed; this is not a gate or release verdict.

## Red Flags

- review output copied into implementation without truth refs
- UX findings change acceptance behavior but skip change/refreeze
- review is treated as final UI authority

## Verification

- route payload reports `route=beacon-design-review`, `intent=review`, and `upstream=impeccable`
- route payload marks `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- accepted design facts have a truth-binding route before implementation

## Evidence Produced

- route contract payload
- UX finding summary
- accepted design fact candidates
- route decision and writeback targets

## State Updated

- no lifecycle state directly
- optional support/read model evidence only

## Gate Impact

- no direct release gate verdict
- may block downstream implementation only when accepted design facts remain unbound

## Operator rule

Prefer:

```bash
beacon design route review "<feature>" --project . --version auto --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```

## Examples

- 适用例：
  - “这个界面做一次 UX review，看看层级、状态、文案和可访问性问题。”
  - “我想让 Beacon review UI，但不要把 review 直接当 truth。”
- 不适用例：
  - “我要正式生成 prototype bundle。” -> 应去 `beacon-prototype`
