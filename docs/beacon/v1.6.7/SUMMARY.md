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
| P0 | beacon-goal-durable-supervisor-v167 | qa-pass / release-ready (GO) |
| P0 | beacon-goal-agent-driver-v167 | qa-pass / release-ready (GO Path C) |
| P2 | beacon-ralph-implement-boundary-v167 | qa-pass / release-ready |

## Durable Supervisor (additive)

- **lake**: `beacon-goal-durable-supervisor-v167`
- **user locks**: opt-in `beacon goal supervise`; heartbeat **120s**; P2 memory **sqlite FTS**
- **truth**: `docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md`
- **status**: qa-pass / release-ready

## AgentDriver longrun (additive, Path C)

- **lake**: `beacon-goal-agent-driver-v167`
- **depends**: `beacon-goal-durable-supervisor-v167`
- **one-shot**: `beacon goal run "..." --longrun` attaches supervisor + starts Python Driver for **this run**
- **default**: without `--longrun`, driver stays **idle** (supervise remains opt-in)
- **truth**: `docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/truth.md`
- **v2 parity**: `beacon-v2-goal-durable-longrun`

## GoalRun main axis (UD-AXIS GO 2026-07-18)

- **lake**: `beacon-goalrun-main-axis-v167`
- **rule**: change touching promise/stage/parallel/longrun/entry/domain **must** regenerate `goalrun-main-axis.md`
- **truth**: `docs/beacon/v1.6.7/features/beacon-goalrun-main-axis-v167/truth.md`

## Truth human-readable + i18n (2026-07-18)

- **Lake**: `beacon-truth-human-readable-i18n-v167` (truth frozen R1; gate implement pending)
- **Intent**: L0 人话 + Humanizer-zh/blader norms; zh/en; freeze fail-closed `truth_human_l0_missing`
- **Axis**: mounted on `beacon-product-goal-domain-delivery-v167`
- **Norms**: `skills/beacon/references/truth-humanizer/`
