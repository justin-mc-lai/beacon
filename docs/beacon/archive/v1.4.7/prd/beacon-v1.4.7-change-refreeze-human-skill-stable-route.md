# PRD: Beacon v1.4.7 change refreeze human skill stable route

**Feature**: `beacon-v1.4.7-change-refreeze-human-skill-stable-route`
**Version**: `v1.4.7`
**Date**: `2026-05-16`
**Status**: `freeze-ready`
**Track**: `human-change-surface + stable-skill-routing`
**Scenario**: `operator_needs_a_stable_natural_language_route_for_change_refreeze`

## Context

- Global boundary source:
  - `docs/beacon/global-boundaries.md`
- Upstream feature:
  - `docs/beacon/archive/v1.4.7/prd/beacon-v1.4.7-change-refreeze-one-shot-requirement-closure.md`
- Brainstorm source:
  - `docs/brainstorms/2026-05-16-beacon-brainstorm-v1.4.7-change-一键冻结是否应该暴露为新的稳定可命中的人类面子-skill-而不是只作为-beacon-change-内的-refreeze-cha.md`
- Current implementation route:
  - `beacon change ... --refreeze-chain`

## 1. Overview

Beacon already has a governed one-shot refreeze route under `beacon change ... --refreeze-chain`. That is sufficient as a CLI mechanism, but not sufficient as a stable human-facing skill route.

This feature adds a narrow skill surface:

```text
beacon-change-refreeze
```

The skill is a route constitution and operator entrypoint for change refreeze. It must point to the existing `beacon change ... --refreeze-chain` behavior and must not create a second implementation path.

## 2. Problem

Human operators are unlikely to reliably discover or recall `--refreeze-chain` when they say:

- change 一键冻结
- change 后重新冻结
- refreeze change
- 一键闭环冻结
- deep adoption needs change/refreeze

If all of these route only to the broad `beacon-change` skill, the agent still has to infer whether the user wants reopen, change-intake, or refreeze closure. That makes a high-risk fail-closed operation less stable than it should be.

## 3. Goals

1. Add a stable, named human skill route for one-shot change refreeze.
2. Keep `beacon-change-refreeze` under the change family and out of the primary lifecycle chain.
3. Make the skill explicitly delegate execution to `beacon change ... --refreeze-chain`.
4. State that the skill is non-stage, non-truth, and non-gate.
5. Ensure deep/change route guidance can point to the stable skill name.

## 4. Non-Goals

- no new primary lifecycle stage
- no new CLI command requirement
- no second refreeze implementation
- no direct PRD, user-story, or test-case writer
- no implementation, QA, or release execution
- no canonical truth ownership inside the skill

## 5. Design Principles

### 5.1 Stable human route, single machine route

The human route can be a new skill. The machine route remains the existing refreeze transaction path.

### 5.2 Skill as boundary, not workflow expansion

`beacon-change-refreeze` must make the operation easier to invoke without expanding Beacon's main chain.

### 5.3 Deep adoption should have a named target

When `deep` finds an adoption-required requirement or acceptance delta, it should be able to explain the route as `beacon-change-refreeze` instead of only exposing a CLI flag.

## 6. Functional Requirements

### FR-001 Skill package

Beacon must add:

- `skills/beacon/beacon-change-refreeze/SKILL.md`
- `.agents/skills/beacon-change-refreeze/SKILL.md`

### FR-002 Route declaration

The skill must clearly declare:

- `beacon change ... --refreeze-chain`
- `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze`

### FR-003 Boundary declaration

The skill must explicitly state that it is:

- not a lifecycle stage
- not a truth source
- not a gate source
- not an implementation, QA, or release executor

### FR-004 Discoverability

The skill metadata and body must allow stable matching for:

- change 一键冻结
- change refreeze
- 重新冻结
- refreeze-chain
- post-freeze requirement closure

### FR-005 Route integration

Change and deep-facing documentation must be able to route users to `beacon-change-refreeze` when the intent is accepted post-freeze refreeze closure.

## 7. Acceptance Standard

This feature is accepted only if Beacon can prove the new skill improves human route stability while preserving the existing refreeze transaction as the only machine execution path.
