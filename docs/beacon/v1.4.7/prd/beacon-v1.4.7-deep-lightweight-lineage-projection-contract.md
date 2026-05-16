# PRD: Beacon v1.4.7 deep lightweight lineage projection contract

**Feature**: `beacon-v1.4.7-deep-lightweight-lineage-projection-contract`
**Version**: `v1.4.7`
**Date**: `2026-05-16`
**Status**: `freeze-ready`
**Track**: `deep-support-surface + trace-on-promotion + lineage-projection`
**Scenario**: `deep_needs_auditable_lineage_without_becoming_a_truth_compiler`

## Context

- Global boundary source:
  - `docs/beacon/global-boundaries.md`
- Deep support surface:
  - `skills/beacon/beacon-deep/SKILL.md`
  - `beacon/utils/deep_loop.py`
- Automation support-review baseline:
  - `docs/beacon/v1.4.7/prd/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- Brainstorm / CEO review convergence:
  - `docs/brainstorms/2026-05-16-beacon-brainstorm-分析-beacon-v1.4.7-automation-能力与现有-beacon-deep-人类面-deep-是否应围绕已冻结-prd-user-story-t.md`
  - `docs/brainstorms/2026-05-16-beacon-brainstorm-基于-ceo-review-对-deep-traceable-scenario-lineage-的挑战-过度要求-us-ac-tc-级-lineage-会提高人.md`

## 1. Overview

`deep` should remain a low-friction support surface that analyzes frozen truth, derives structural findings, and routes deltas. It should not become a parallel truth compiler.

The revised product rule is:

> trace-on-promotion, not trace-on-discovery.

Deep discovery only needs enough lineage to be auditable and routeable. Strong `US / AC / TC` trace becomes required only when the finding is adopted into canonical truth or promoted into a formal change.

## 2. Problem

The first lineage idea was too strong:

```text
Every deep scenario must carry exact parent PRD / US / AC / TC IDs.
```

That design creates hidden cost:

1. Humans must maintain trace details during exploratory analysis.
2. Deep becomes slower and heavier, reducing its support-surface value.
3. Inferred IDs may be mistaken for canonical truth.
4. Release or QA gates may over-trust non-canonical support artifacts.

## 3. Goals

1. Add auditable lineage projection to deep artifacts.
2. Keep discovery lightweight and non-blocking.
3. Distinguish source-bound, inferred, adoption-required, and canonical-promoted trace.
4. Require strong trace only when a finding enters `test-case`, `change/refreeze`, or promotion.
5. Preserve `deep` as a support surface that discovers, explains, classifies, and routes.

## 4. Non-Goals

- no automatic `deep` execution by automation
- no automatic truth writeback
- no automatic promotion to canonical requirement material
- no requirement that humans manually fill `US / AC / TC` IDs during discovery
- no release or QA gate trust in inferred L0/L1 lineage

## 5. Lineage Model

### L0 source-bound

Default mode for deep findings, risks, and test deltas.

Required fields:

- `lineage_mode=source_bound`
- `source_truth_refs`
- `route_target`
- `truth_impact`

L0 is auditable but not canonical trace.

### L1 machine-inferred

Optional machine projection from parseable requirement materials.

Required fields for inferred refs:

- `ref_type`
- `ref_id`
- `confidence`
- `inferred=true`

L1 is advisory only. Missing L1 refs must not block deep output.

### L2 adoption-required

Required when a deep finding enters current closure through:

- `closure_supplement`
- `route_target=test-case`
- `truth_impact=acceptance_delta`
- `truth_impact=requirement_meaning_delta`

L2 means the receiving truth surface must strengthen trace before refreeze or QA closure.

### L3 canonical-trace

Only PRD/user-story/test-case materials can create L3 trace.

Release and QA gates may trust L3. They must not treat L0/L1 as canonical requirement closure.

## 6. Proposed Deep Artifact Shape

```json
{
  "lineage_mode": "source_bound",
  "source_truth_refs": ["docs/beacon/v1.4.7/prd/feature.md"],
  "candidate_parent_refs": [
    {
      "ref_type": "AC",
      "ref_id": "AC-003",
      "confidence": "medium",
      "inferred": true
    }
  ],
  "route_target": "test-case",
  "truth_impact": "acceptance_delta",
  "promotion_required": false
}
```

Allowed `lineage_mode` values:

- `source_bound`
- `machine_inferred`
- `adoption_required`
- `canonical_promoted`

Allowed `truth_impact` values:

- `none`
- `acceptance_delta`
- `requirement_meaning_delta`

## 7. Functional Requirements

### FR-001 Deep artifacts must carry lightweight lineage projection

Deep findings, risks, and test deltas must include lineage fields sufficient to audit source truth and route decisions.

### FR-002 L0 must be the default discovery mode

Ordinary deep discovery must be valid with file-level `source_truth_refs` only.

### FR-003 L1 inferred refs must be explicitly non-canonical

Machine-inferred parent refs must carry `confidence` and `inferred=true`.

### FR-004 Missing `US / AC / TC` inferred refs must not block deep

Deep output remains valid when exact parent IDs cannot be inferred.

### FR-005 L2 adoption must require trace strengthening

When a finding changes current closure or routes to `test-case` / `change_refreeze`, the receiving truth surface must strengthen trace before refreeze or QA closure.

### FR-006 L3 canonical trace belongs only to truth surfaces

Only PRD, user-story, and test-case materials can produce canonical promoted trace.

### FR-007 QA and release gates must not trust L0/L1 as closure truth

L0/L1 may inform routing and prioritization, but gate closure must depend on canonical truth and accepted evidence.

### FR-008 Deep remains support-only

The lineage projection contract must not make `deep` a truth source, gate source, or new lifecycle stage.

## 8. Acceptance Standard

This feature is accepted only if Beacon gains better deep auditability without increasing human maintenance burden or weakening truth/gate boundaries.
