# Beacon v1.6.7 — Unified Topology + Intent-Aware Loop Goal

## Scope

v1.6.7 delivers unified git topology and loop-goal intent continuation (program `beacon-unified-topology-loop-goal-v167`):

- Slice B: `GitScopeGraph` + `topology_gate` (`beacon-git-scope-graph-v167`)
- Slice A: loop-goal R7 intent continuation + dual runtime (`beacon-loop-goal-v166`)

Promotion ref: `friction:2e306f7acea7`.

## Status

- **delivery**: `feature-ready` (topology/loop-goal) + **Product Goal Domain Delivery GO**
- **program**: `docs/beacon/v1.6.7/programs/beacon-unified-topology-loop-goal-v167/`
- **program (product-goal)**: `docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/` → **release-ready**

## Features

| Order | Feature slug | Revision | QA | Release |
|-------|--------------|----------|-----|---------|
| B | `beacon-git-scope-graph-v167` | R1 | pass | feature-ready |
| A | `beacon-loop-goal-v166` | R7 | pass | feature-ready |

## Program: Product Goal + Domain Delivery

- **program**: `docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/`
- **status**: **delivered / release-ready (GO, human-confirmed)**
- **intent**: Goal spans full lifecycle; domain FSM hard gates; kill empty-castle greens
- **public entry**: `$beacon-goal` / `beacon goal run` only (`beacon-loop-goal` = support discovery)
- **release evidence**:
  - `docs/beacon/v1.6.7/release/product-goal-domain-delivery-v167-go.md`
  - `docs/beacon/v1.6.7/release/checklist-v1.6.7.md`
  - `beacon release check v1.6.7` → pass / `release_ready=true`

| Priority | Feature | Status |
|----------|---------|--------|
| P0 | beacon-domain-fsm-authority-v167 | qa-pass / release-ready |
| P0 | beacon-golden-commerce-fixture-v167 | qa-pass / release-ready |
| P0 | beacon-domain-fsm-qa-gate-v167 | qa-pass / release-ready |
| P1 | beacon-product-goal-runtime-v167 | qa-pass / release-ready |
| P1 | beacon-ui-design-ship-gate-v167 | qa-pass / release-ready |
| P2 | beacon-loop-discover-goal-finish-v167 | qa-pass / release-ready |
| P2 | beacon-ralph-implement-boundary-v167 | qa-pass / release-ready |

