# Beacon v1.4.1 Source Architecture Index

## Purpose

This source architecture index defines the implementation reading surface for `v1.4.1` deep analysis support capability work.

`v1.4.1` is a planning-only requirement line. The current runtime source remains `v1.4.0` until version governance promotes a new runtime release line.

## Required Implementation Reading Order

1. `docs/beacon/global-boundaries.md`
2. `docs/beacon/archive/v1.4.1/SUMMARY.md`
3. `docs/beacon/archive/v1.4.1/execution/boundaries.md`
4. `docs/beacon/archive/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
5. `docs/beacon/archive/v1.4.1/user-story/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
6. `docs/beacon/archive/v1.4.1/qa/test-cases/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
7. `docs/beacon/archive/v1.4.1/research/beacon-deep-capability-upgrade-research-supplement.md`
8. `docs/beacon/archive/v1.4.1/execution/project-skill-qa-evolution-blueprint.md`

## Likely Source Areas

Implementation planning should inspect and update only the smallest necessary source areas:

- `beacon/commands/` for support command routing and gate integration
- `beacon/utils/` for artifact path, requirement parsing, state machine, risk register, and projection helpers
- `skills/beacon/` for the human-facing `beacon-deep` support skill surface and optional toolkit subskills
- `.trae/skills/` or host skill surfaces only through existing installer/sync governance, if materialized
- `tests/` for the v1.4.1 contract tests named by the frozen test-case matrix

## Source Of Truth

- Human requirement truth lives under `docs/beacon/archive/v1.4.1/**/*.md`.
- Machine surfaces under `docs/beacon/archive/v1.4.1/.machine/` and `.beacon/` are compiled projections or audit evidence.
- Source implementation must not directly treat deep findings, machine projections, or learning hints as canonical truth.

## Non-UI Handoff

This feature does not require prototype handoff before implementation because it is a CLI / skill / support toolkit / gate supplement capability rather than a user interface feature.
