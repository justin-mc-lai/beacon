# User Story: Beacon Design / Product / Prototype Rebuild Contract

**Feature**: `beacon-design-product-prototype-rebuild-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Story

As a Beacon maintainer, I want Beacon to own a basic, auditable product/design truth and prototype adapter capability, so that accepted UI/UX facts cannot be lost outside Beacon truth and later implementation, QA, or release cannot accidentally follow stale design requirements.

## Ordered Sub-Contracts

This is one feature with five ordered sub-contracts:

1. `beacon-design-product-truth-contract`
2. `beacon-design-component-system-contract`
3. `accepted-ui-ux-truth-writeback-gate-contract`
4. `beacon-prototype-adapter-rebuild-contract`
5. `beacon-design-subskill-contract`

## Acceptance Criteria

| AC ID | Sub-Contract | Theme | Description |
| --- | --- | --- | --- |
| AC-001 | product truth | project truth | Beacon defines `PRODUCT.md` and `DESIGN.md` participation for product/design truth. |
| AC-002 | product truth | version style | Beacon defines version-wide design style truth under `docs/beacon/<version>/design/style.md`. |
| AC-003 | product truth | projection boundary | `.machine/design` is projection/evidence only, not design truth. |
| AC-004 | component system | design command | `beacon design` supports component-system planning/validation beyond Design Thinking templates. |
| AC-005 | component system | design axes | Design output covers page, component, state, interaction, accessibility, and responsive axes. |
| AC-006 | component system | source-bound libraries | Component library choices are explicit, source-bound, and auditable. |
| AC-007 | UI/UX writeback | accepted ledger | Accepted UI/UX result ledger records accepted design facts and affected truth refs. |
| AC-008 | UI/UX writeback | implement block | Implement blocks with `accepted_ui_ux_truth_gap` when accepted design facts are unbound. |
| AC-009 | UI/UX writeback | QA block | QA blocks instead of producing pass/fail against stale UI truth. |
| AC-010 | UI/UX writeback | release block | Release treats unbound accepted UI/UX facts as a P0 blocker. |
| AC-011 | prototype rebuild | adapter default | `beacon prototype` defaults to accepted design truth adapter behavior for v1.4.11+. |
| AC-012 | prototype rebuild | explicit legacy | Legacy wireframe inspection is available only through explicit include-legacy / compat behavior. |
| AC-013 | prototype rebuild | legacy status rename | `legacy_source_only` is retired in favor of `migration_input_present`. |
| AC-014 | prototype rebuild | legacy not closure | Legacy wireframe source cannot satisfy current prototype gate or accepted UI/UX truth writeback. |
| AC-015 | design skill | route surface | `$beacon:beacon-design` exists as a support-only child skill and exposes stable routes: `explore`, `system`, `review`, `polish`, `extract`, `library`, and `bootstrap`. |
| AC-016 | design skill | vibe-to-ui parity | `beacon-design-explore` and `beacon-design-extract` preserve `vibe-to-ui` exploration and reference/screenshot extraction capability. |
| AC-017 | design skill | ui-ux-pro-max parity | `beacon-design-system` preserves `ui-ux-pro-max` design-system, component, token, state, responsive, accessibility, and stack-aware baseline capability. |
| AC-018 | design skill | impeccable parity | `beacon-design-review` and `beacon-design-polish` preserve `impeccable` UX review, hardening, and ship-readiness polish capability. |
| AC-019 | design skill | reference-only library | `beacon-design-library` uses `awesome-design-md` as reference-only design pattern source, not execution skill or truth source. |
| AC-020 | design skill | bootstrap boundary | `beacon-design-bootstrap` validates installed upstream skills, mirrored source trees, or bootstrap route availability without becoming truth/gate/lifecycle/release authority. |

## Non Goals

- This story does not rename browser fallback behavior.
- This story does not change memory migration behavior.
- This story does not change intent router behavior.
- This story does not relayer test markers.
- This story does not embed all of `ui-ux-dev` implementation internals.
- This story does not treat upstream design skills as Beacon truth sources.
- This story does not treat `awesome-design-md` as an execution skill.
- This story does not make design support a new lifecycle stage.
- This story does not let AI output directly overwrite truth.

## Boundary

Design style is version-wide. It is not a feature-local `docs/beacon/<version>/design/product.md` artifact.

This story freezes the full design capability rebuild requirement. It does not implement, QA, or release it.
