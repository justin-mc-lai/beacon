# PRD: Beacon Design / Product / Prototype Rebuild Contract

**Feature**: `beacon-design-product-prototype-rebuild-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Overview

Beacon must rebuild its design, product, and prototype capability as one complete ordered feature.

The goal is not to add a cosmetic design helper. The goal is to prevent accepted UI/UX facts from being lost outside Beacon truth, while giving Beacon a built-in baseline design capability distilled from `ui-ux-dev`.

Design style must apply across the whole version. It must not be isolated in a feature-local `docs/beacon/<version>/design/product.md` file.

## 1. Problem

Current Beacon has three gaps:

- `beacon design` is only a Design Thinking template generator.
- `beacon prototype` mixes old wireframe generation, legacy inspection, and v1.4.9+ design-result adapter behavior.
- accepted UI/UX facts can exist outside Beacon truth, causing implement / QA / release to trust stale Markdown and treat accepted UI changes as drift.

`friction:cd1809c3220a` proves this is a P0 product safety issue.

## 2. Goals

This feature has twenty acceptance criteria across five ordered sub-contracts.

### 2.1 beacon-design-product-truth-contract

- AC-001: Beacon defines project-level `PRODUCT.md` and `DESIGN.md` truth participation.
- AC-002: Beacon defines version-wide design style truth under `docs/beacon/<version>/design/style.md`.
- AC-003: `.machine/design` is projection/evidence only, not design truth.

### 2.2 beacon-design-component-system-contract

- AC-004: `beacon design` can produce or validate a component-system contract for open-source UI libraries.
- AC-005: Component design output includes page, component, state, interaction, accessibility, and responsive axes.
- AC-006: Component library choices are explicit, source-bound, and auditable.

### 2.3 accepted-ui-ux-truth-writeback-gate-contract

- AC-007: Accepted UI/UX result ledger records accepted design facts and affected truth refs.
- AC-008: Implement blocks with `accepted_ui_ux_truth_gap` when accepted design facts are unbound.
- AC-009: QA blocks instead of producing pass/fail against stale UI truth.
- AC-010: Release treats unbound accepted UI/UX facts as a P0 blocker.

### 2.4 beacon-prototype-adapter-rebuild-contract

- AC-011: `beacon prototype` defaults to accepted design truth adapter behavior for v1.4.11+.
- AC-012: Legacy wireframe inspection is available only through explicit include-legacy / compat behavior.
- AC-013: `legacy_source_only` is retired in favor of `migration_input_present`.
- AC-014: Legacy wireframe source cannot satisfy current prototype gate or accepted UI/UX truth writeback.

### 2.5 beacon-design-subskill-contract

- AC-015: `$beacon:beacon-design` exists as a support-only child skill and exposes stable design intent routes: `explore`, `system`, `review`, `polish`, `extract`, `library`, and `bootstrap`.
- AC-016: `beacon-design-explore` and `beacon-design-extract` preserve `vibe-to-ui` exploration and reference/screenshot extraction capability.
- AC-017: `beacon-design-system` preserves `ui-ux-pro-max` design-system, component, token, state, responsive, accessibility, and stack-aware baseline capability.
- AC-018: `beacon-design-review` and `beacon-design-polish` preserve `impeccable` UX review, hardening, and ship-readiness polish capability.
- AC-019: `beacon-design-library` uses `awesome-design-md` as a reference-only design pattern source and never treats it as an execution skill or truth source.
- AC-020: `beacon-design-bootstrap` validates installed upstream skills, mirrored source trees, or bootstrap route availability without becoming a truth source, gate, lifecycle stage, or release verdict.

## 3. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Product/design truth discovery must include `PRODUCT.md` and `DESIGN.md`. |
| FR-002 | AC-002 | Version design style must live under `docs/beacon/<version>/design/style.md`. |
| FR-003 | AC-002 | Design style must be version-wide, not feature-local. |
| FR-004 | AC-003 | `.machine/design` artifacts must be classified as projection/evidence. |
| FR-005 | AC-004 | `beacon design` must move beyond static Design Thinking template output. |
| FR-006 | AC-005 | Design contracts must cover page, component, state, interaction, accessibility, and responsive axes. |
| FR-007 | AC-006 | Component system recommendations must name source/library candidates explicitly. |
| FR-008 | AC-007 | Accepted UI/UX facts must be recorded in an auditable ledger. |
| FR-009 | AC-008 | `beacon implement` must fail closed on unbound accepted UI/UX facts. |
| FR-010 | AC-009 | `beacon qa` must fail closed on stale UI truth. |
| FR-011 | AC-010 | `beacon release` must block unbound accepted UI/UX facts. |
| FR-012 | AC-011 | Prototype status must use current adapter binding semantics by default. |
| FR-013 | AC-012 | Legacy prototype details require explicit admission. |
| FR-014 | AC-013 | Current source and tests must stop using `legacy_source_only` as current status. |
| FR-015 | AC-014 | Release/gate logic must not count legacy wireframe source as current design closure. |
| FR-016 | AC-015 | A Beacon design child skill must be installable/discoverable and route to deterministic CLI/tooling. |
| FR-017 | AC-015 | Beacon design must expose stable support routes for `explore`, `system`, `review`, `polish`, `extract`, `library`, and `bootstrap`. |
| FR-018 | AC-016 | `explore` and `extract` routes must preserve `vibe-to-ui` capability ownership while binding accepted outputs back to Beacon truth candidates. |
| FR-019 | AC-017 | `system` route must preserve `ui-ux-pro-max` capability ownership for design systems, components, tokens, states, responsive rules, accessibility, and stack-aware guidance. |
| FR-020 | AC-018 | `review` and `polish` routes must preserve `impeccable` capability ownership while separating support-only findings from accepted truth-changing facts. |
| FR-021 | AC-019 | `library` route must use `awesome-design-md` as reference-only source and must not generate execution truth by itself. |
| FR-022 | AC-020 | `bootstrap` route must report installed/mirrored/bootstrap availability for upstream design capabilities without affecting lifecycle gates. |

## 4. Required Design Truth Paths

The feature must define these paths:

```text
PRODUCT.md
DESIGN.md
docs/beacon/<version>/design/style.md
docs/beacon/<version>/design/component-system.md
docs/beacon/<version>/design/interaction-contract.md
docs/beacon/<version>/design/state-matrix.md
docs/beacon/<version>/.machine/design/
```

Forbidden design truth shape:

```text
docs/beacon/<version>/design/product.md as the sole version design style surface
```

The version-wide design style contract must apply across the version.

## 5. Runtime Behavior Contract

Default current behavior after implementation:

```text
design needed
  -> version-wide design style + component system contract
  -> accepted design result ledger
  -> prototype adapter binding
  -> change/refreeze when requirement truth changes
  -> implement / QA / release allowed only after binding is closed
```

Forbidden behavior:

```text
accepted UI/UX facts exist
  -> no truth binding
  -> implement / QA / release continues against stale Markdown
```

## 5.1 Beacon Design Route Contract

`$beacon:beacon-design` must preserve the `ui-ux-dev` upstream capability split while adding Beacon truth binding.

| Beacon route | Upstream capability | Required behavior |
| --- | --- | --- |
| `beacon-design-explore` | `vibe-to-ui` | Produces concept directions, layout models, information hierarchy, and candidate design truth deltas. |
| `beacon-design-extract` | `vibe-to-ui` | Extracts visible page structure, component breakdown, style cues, and inferred interaction assumptions from screenshots or references. |
| `beacon-design-system` | `ui-ux-pro-max` | Produces stack-aware component, token, state, accessibility, responsive, and implementation baseline guidance. |
| `beacon-design-review` | `impeccable` | Produces prioritized UX findings across hierarchy, copy, flow friction, missing states, and accessibility. |
| `beacon-design-polish` | `impeccable` | Produces ship-readiness cleanup for spacing, alignment, feedback, state detail, trust, and microcopy. |
| `beacon-design-library` | `awesome-design-md` | Produces curated references and adaptation guidance only. It is reference-only. |
| `beacon-design-bootstrap` | upstream compatibility model | Reports installed skill, mirrored source, or bootstrap route availability only. |

All routes are support routes. Accepted design facts still require Beacon truth binding and, when they change requirement promises, `change/refreeze`.

## 6. Diagram Truth Layer

### 6.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 6.2 State Axes

- `design_truth_scope`: `project_level`, `version_wide`, `feature_local_rejected`
- `design_capability_state`: `template_only`, `component_system_contract`, `truth_bound`
- `accepted_ui_ux_state`: `none`, `accepted_unbound`, `bound`, `requires_refreeze`
- `prototype_state`: `adapter_current`, `legacy_migration_input`, `legacy_current_rejected`
- `execution_gate_state`: `allowed`, `blocked_truth_gap`, `blocked_stale_truth`
- `skill_surface_state`: `design_skill_present`, `support_only`, `not_gate`
- `design_route_state`: `explore`, `system`, `review`, `polish`, `extract`, `library`, `bootstrap`
- `upstream_capability_state`: `vibe_to_ui`, `ui_ux_pro_max`, `impeccable`, `awesome_design_md_reference_only`

### 6.3 Branch Flow

```text
feature has UI/UX impact
  -> version design style exists
    -> beacon-design route selected
    -> component system contract exists
      -> accepted design result exists
        -> binding exists
          -> requirement truth updated if affected
            -> implement / QA / release may continue
        -> binding missing
          -> block accepted_ui_ux_truth_gap
  -> version design style missing
    -> block design_truth_missing
```

### 6.4 State Machine

```text
design_unseen
  -> design_required
  -> design_contract_drafted
  -> component_system_bound
  -> design_result_accepted
  -> design_truth_binding_required
  -> design_truth_bound
  -> requirement_refreeze_required
  -> requirement_refrozen
  -> implementation_allowed
```

Terminal states:

- `implementation_allowed`
- `blocked_accepted_ui_ux_truth_gap`
- `blocked_requirement_truth_stale`
- `legacy_migration_input_only`

### 6.5 Decision Priority

```text
accepted human design facts
  > version-wide design style truth
  > product/design project truth
  > versioned PRD/user-story/test-case truth
  > prototype adapter evidence
  > beacon-design support route output
  > implementation convenience
  > legacy wireframe compatibility
```

## 7. Non Goals

- No browser fallback rename.
- No memory migration change.
- No intent router change.
- No test marker relayering.
- No direct embedding of all `ui-ux-dev` implementation internals.
- No treating upstream design skills as Beacon truth sources.
- No treating `awesome-design-md` as an execution skill.
- No direct automated overwrite of PRODUCT / DESIGN / PRD.
- No release verdict in this requirement freeze step.
