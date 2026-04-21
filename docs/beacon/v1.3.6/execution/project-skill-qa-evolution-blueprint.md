# Beacon v1.3.6 Project-Skill QA Evolution Blueprint

## Purpose

This blueprint explains how project-local skills, Beacon's host-visible skill pack, and QA evidence evolve together on the `v1.3.6` runtime line.

## Current Contract

- Human-facing routing stays on the minimal `prd -> user-story -> test-case -> prototype -> implement -> qa -> release` chain.
- `skills/beacon/` is the canonical packaged host skill surface for Codex and Claude.
- Project-local helpers may participate during implementation and QA, but they remain subordinate to Beacon's delivery contract and release gate.

## Skill Layering

1. Beacon public host skills
   - `using-beacon`
   - `beacon-prd`
   - `beacon-user-story`
   - `beacon-test-case`
   - `beacon-implement`
   - `beacon-qa`
   - `beacon-release`
   - `beacon-help`
   - `beacon-status`
   - `beacon-doctor`
2. Optional supplemental skills
   - bootstrap, lighthouse, memory/friction evolution, real-project validation
3. Project-local implementation helpers
   - allowed only as internal execution support
   - never replace Beacon's public routing surface

## QA Evolution Rules

- QA evidence must remain traceable to the current `v1.3.6` requirement materials.
- `qa` refreshes the active spec fingerprint and writes canonical status for release/gate checks.
- Project-local QA helpers can provide browser or environment evidence, but Beacon owns the final pass/block decision.
- If docs, execution evidence, or fingerprints drift, the correct response is repair plus rerun, not manual waiver.

## Release Alignment

- Root docs, packaged skills, and `docs/beacon/v1.3.6/` must agree on the active runtime line.
- Change documents under `docs/beacon/v1.3.6/change/` and `.machine/change/` are required release memory evidence.
- `gate check release` and `release scorecard` are the final truth surfaces for ship readiness.

## Reading Order

1. `docs/beacon/v1.3.6/SUMMARY.md`
2. `docs/beacon/v1.3.6/execution/index.md`
3. `docs/beacon/v1.3.6/execution/architecture-blueprint.md`
4. `docs/beacon/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`
5. `docs/beacon/v1.3.6/release/v1.3.6.md`
