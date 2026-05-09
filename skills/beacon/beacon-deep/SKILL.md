---
name: beacon-deep
description: Use when Beacon should run deep analysis as a support surface for complex business risk, test-delta derivation, cross-stage routing, and release supplement closure without adding a new lifecycle stage.
---

# Beacon Deep

This skill routes deep analysis work through Beacon's `deep` support surface.

`deep` is not a primary lifecycle stage. It analyzes frozen requirement truth, derives routeable findings and test deltas, and writes release-facing supplement evidence. Canonical requirement changes still go through existing Beacon surfaces.

## Use for

- high-risk trigger and low-risk skip decisions
- state-machine, fact-source, invariant, and consistency-chain analysis
- deep test delta derivation before QA
- structural QA feedback review when P0/P1/P2 defects expose modeling gaps
- release supplement evidence for deep closure, waiver, backlog, or skip decisions

## Operator rule

Prefer:

- `beacon deep run ...`
- optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh deep run ...`

Keep toolkit internals hidden behind `beacon-deep` unless the user explicitly asks for implementation details.

## Inputs Contract

- `project-root`
- `version`
- `feature`
- frozen `prd / user-story / test-case`
- optional user intent snapshot
- optional explicit skip reason
- optional QA feedback and severity for structural reopen decisions

## Decision Protocol

- Continue in `deep` only as a support analysis loop.
- Route requirement gaps to `change/refreeze`.
- Route acceptance gaps to `test-case`.
- Route implementation gaps to `implement`.
- Route QA evidence gaps to supplemental `qa`.
- Route release risks to closure, waiver, or accepted backlog decision.
- Do not rewrite frozen PRD, user-story, or test-case truth directly.

## Artifact Contract

`beacon deep run` writes:

- deep analysis report
- state machine report
- deep test delta
- risk register
- deep loop trace
- deep closure brief
- optional skip evidence

## Backstop CLI

- `beacon deep run ...`
- `beacon deep status ...`
- `beacon deep report ...`
- `beacon test-case ...` for accepted test deltas
- `beacon change ...` when frozen truth must reopen
- `beacon qa ...` after adopted deltas require execution evidence
- `beacon release ...` after deep closure or skip evidence is ready
