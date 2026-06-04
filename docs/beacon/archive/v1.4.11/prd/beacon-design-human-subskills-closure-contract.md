# PRD: Beacon Design Human Subskills Closure Contract

**Feature**: `beacon-design-human-subskills-closure-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Overview

Beacon v1.4.11 design capability already has seven deterministic design routes, but the host-visible human skill surface is incomplete.

This feature closes that gap by making the seven `beacon-design-*` subskills discoverable and boundary-safe without changing the underlying `beacon design` CLI contract.

## 1. Problem

The existing design route contract exposes:

```text
explore
extract
system
review
polish
library
bootstrap
```

The requirement contract names corresponding human subskills, but the installed skill surface only exposes `beacon-design` and `beacon-design-review`.

A single broad design skill makes intent resolution unstable. It also increases the chance that support outputs are mistaken for truth, gate evidence, or release evidence.

## 2. Goals

- AC-001: `beacon-design` remains the support-only aggregate design entry.
- AC-002: `beacon-design-explore` exists and maps only to route `explore` / upstream `vibe-to-ui`.
- AC-003: `beacon-design-extract` exists and maps only to route `extract` / upstream `vibe-to-ui`.
- AC-004: `beacon-design-system` exists and maps only to route `system` / upstream `ui-ux-pro-max`.
- AC-005: `beacon-design-review` exists and maps only to route `review` / upstream `impeccable`.
- AC-006: `beacon-design-polish` exists and maps only to route `polish` / upstream `impeccable`.
- AC-007: `beacon-design-library` exists, maps to route `library`, and treats `awesome-design-md` as reference-only.
- AC-008: `beacon-design-bootstrap` exists, maps to route `bootstrap`, and is capability-admission-only.
- AC-009: Every design subskill declares support-only boundaries: not truth source, not gate source, not lifecycle stage, not release verdict.
- AC-010: Accepted design facts still route to Beacon truth binding, prototype adapter, or change/refreeze before implementation.
- AC-011: Tests verify the installed skill family matches the deterministic `beacon design contract` route list.
- AC-012: This feature does not add design runtime routes, change prototype adapter behavior, or change release verdicts.

## 3. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Keep `beacon-design` as the aggregate design support route. |
| FR-002 | AC-002 | Add `beacon-design-explore` with operator command `beacon design route explore`. |
| FR-003 | AC-003 | Add `beacon-design-extract` with operator command `beacon design route extract`. |
| FR-004 | AC-004 | Add `beacon-design-system` with operator command `beacon design route system`. |
| FR-005 | AC-005 | Align `beacon-design-review` with operator command `beacon design route review`. |
| FR-006 | AC-006 | Add `beacon-design-polish` with operator command `beacon design route polish`. |
| FR-007 | AC-007 | Add `beacon-design-library` with reference-only boundary. |
| FR-008 | AC-008 | Add `beacon-design-bootstrap` with capability-admission-only boundary. |
| FR-009 | AC-009 | Ensure every child skill states support-only / non-truth / non-gate / non-stage boundaries. |
| FR-010 | AC-010 | Document next routes for accepted design facts. |
| FR-011 | AC-011 | Add regression coverage for host-visible skill family discoverability and route matching. |
| FR-012 | AC-012 | Keep runtime design CLI, prototype adapter, and release behavior unchanged. |

## 4. Subskill Contract

| Skill | CLI route | Upstream | Output role |
| --- | --- | --- | --- |
| `beacon-design-explore` | `explore` | `vibe-to-ui` | Design direction candidates. |
| `beacon-design-extract` | `extract` | `vibe-to-ui` | Screenshot/reference structure candidates. |
| `beacon-design-system` | `system` | `ui-ux-pro-max` | Component system, token, state, responsive, accessibility baseline candidates. |
| `beacon-design-review` | `review` | `impeccable` | UX findings and change/refreeze candidates. |
| `beacon-design-polish` | `polish` | `impeccable` | Ship-readiness polish candidates. |
| `beacon-design-library` | `library` | `awesome-design-md` | Reference-only patterns and adaptation notes. |
| `beacon-design-bootstrap` | `bootstrap` | upstream compatibility | Installed/mirror/bootstrap capability admission evidence. |

## 5. Truth Binding Contract

Subskill output is support evidence only.

Accepted design facts must follow one of these routes:

```text
accepted non-promise design fact -> PRODUCT.md / DESIGN.md / docs/beacon/<version>/design/* truth binding
accepted prototype adapter input -> beacon prototype adapt
accepted promise-changing design fact -> beacon change ... --refreeze-chain
```

Only after truth binding may implementation use the design facts as delivery input.

## 6. Non Goals

- No new `beacon design` CLI route.
- No design runtime behavior change.
- No prototype adapter behavior change.
- No direct PRODUCT.md / DESIGN.md content mutation.
- No release verdict change.
- No new lifecycle stage.
- No upstream design capability promoted to Beacon truth source.

## 7. Success Metrics

- Seven `beacon-design-*` child skills are present in `.agents/skills` and packaged skills.
- The child skill names match `beacon design contract` route names.
- Each skill has an operator command for its route.
- Each skill states the same support-only boundary.
- Regression tests fail if a route exists without a corresponding human subskill.
# PRD: Beacon Design Human Subskills Closure Contract

**Feature**: `beacon-design-human-subskills-closure-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Overview

Beacon v1.4.11 design capability already has seven deterministic design routes, but the host-visible human skill surface is incomplete.

This feature closes that gap by making the seven `beacon-design-*` subskills discoverable and boundary-safe without changing the underlying `beacon design` CLI contract.

R3 revision adds an eighth route, `simplify`, to give operators a first-principles simplicity audit that helps escape engineer thinking, extract the core user scenario, detect abstraction-to-UI mapping drift, deduplicate information, and quantify complexity burden.

## 1. Problem

The existing design route contract exposes:

```text
explore
extract
system
review
polish
library
bootstrap
```

The requirement contract names corresponding human subskills, but the installed skill surface only exposes `beacon-design` and `beacon-design-review`.

A single broad design skill makes intent resolution unstable. It also increases the chance that support outputs are mistaken for truth, gate evidence, or release evidence.

Additionally, none of the existing routes challenge whether a design is unnecessarily complex. Every route starts from "how to design this feature" rather than "should this feature be simpler." This allows engineer thinking — where data models map directly to UI layers — to pass unchallenged through explore, system, review, and polish.

## 2. Goals

- AC-001: `beacon-design` remains the support-only aggregate design entry.
- AC-002: `beacon-design-explore` exists and maps only to route `explore` / upstream `vibe-to-ui`.
- AC-003: `beacon-design-extract` exists and maps only to route `extract` / upstream `vibe-to-ui`.
- AC-004: `beacon-design-system` exists and maps only to route `system` / upstream `ui-ux-pro-max`.
- AC-005: `beacon-design-review` exists and maps only to route `review` / upstream `impeccable`.
- AC-006: `beacon-design-polish` exists and maps only to route `polish` / upstream `impeccable`.
- AC-007: `beacon-design-library` exists, maps to route `library`, and treats `awesome-design-md` as reference-only.
- AC-008: `beacon-design-bootstrap` exists, maps to route `bootstrap`, and is capability-admission-only.
- AC-009: Every design subskill declares support-only boundaries: not truth source, not gate source, not lifecycle stage, not release verdict.
- AC-010: Accepted design facts still route to Beacon truth binding, prototype adapter, or change/refreeze before implementation.
- AC-011: Tests verify the installed skill family matches the deterministic `beacon design contract` route list.
- AC-012: This feature does not add design runtime routes, change prototype adapter behavior, or change release verdicts.
- AC-013: `beacon-design-simplify` exists and maps to route `simplify` with Beacon-native first-principles capabilities (no external upstream dependency).
- AC-014: The simplify route provides `lazy_user_axiom`, `core_scenario_extraction`, `engineer_abstraction_detection`, `information_deduplication`, and `complexity_burden_score` capabilities.
- AC-015: `beacon-design-simplify` declares support-only boundaries and has no upstream skill dependency (Beacon-native).
- AC-016: `beacon-design-simplify/SKILL.md` describes the first-principles simplicity audit with operator command `beacon design route simplify`.
- AC-017: Tests verify `simplify` route exists in `DESIGN_ROUTES` and matches installed `beacon-design-simplify` subskill.

## 3. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Keep `beacon-design` as the aggregate design support route. |
| FR-002 | AC-002 | Add `beacon-design-explore` with operator command `beacon design route explore`. |
| FR-003 | AC-003 | Add `beacon-design-extract` with operator command `beacon design route extract`. |
| FR-004 | AC-004 | Add `beacon-design-system` with operator command `beacon design route system`. |
| FR-005 | AC-005 | Align `beacon-design-review` with operator command `beacon design route review`. |
| FR-006 | AC-006 | Add `beacon-design-polish` with operator command `beacon design route polish`. |
| FR-007 | AC-007 | Add `beacon-design-library` with reference-only boundary. |
| FR-008 | AC-008 | Add `beacon-design-bootstrap` with capability-admission-only boundary. |
| FR-009 | AC-009 | Ensure every child skill states support-only / non-truth / non-gate / non-stage boundaries. |
| FR-010 | AC-010 | Document next routes for accepted design facts. |
| FR-011 | AC-011 | Add regression coverage for host-visible skill family discoverability and route matching. |
| FR-012 | AC-012 | Keep runtime design CLI, prototype adapter, and release behavior unchanged. |
| FR-013 | AC-013 | Add `beacon-design-simplify` with operator command `beacon design route simplify` and no upstream dependency. |
| FR-014 | AC-014 | Add `simplify` route to `DESIGN_ROUTES` in `beacon/utils/design_contract.py` with five first-principles capabilities. |
| FR-015 | AC-015 | Ensure `beacon-design-simplify` states support-only boundary and no-upstream-dependency constraint. |
| FR-016 | AC-016 | Write `beacon-design-simplify/SKILL.md` with first-principles simplicity audit guidance and operator command. |
| FR-017 | AC-017 | Add regression test for simplify route existence and subskill matching. |

## 4. Subskill Contract

| Skill | CLI route | Upstream | Output role |
| --- | --- | --- | --- |
| `beacon-design-explore` | `explore` | `vibe-to-ui` | Design direction candidates. |
| `beacon-design-extract` | `extract` | `vibe-to-ui` | Screenshot/reference structure candidates. |
| `beacon-design-system` | `system` | `ui-ux-pro-max` | Component system, token, state, responsive, accessibility baseline candidates. |
| `beacon-design-review` | `review` | `impeccable` | UX findings and change/refreeze candidates. |
| `beacon-design-polish` | `polish` | `impeccable` | Ship-readiness polish candidates. |
| `beacon-design-library` | `library` | `awesome-design-md` | Reference-only patterns and adaptation notes. |
| `beacon-design-bootstrap` | `bootstrap` | upstream compatibility | Installed/mirror/bootstrap capability admission evidence. |
| `beacon-design-simplify` | `simplify` | Beacon-native | First-principles simplicity audit: lazy-user axiom, core scenario extraction, engineer abstraction detection, information deduplication, complexity burden scoring. |

## 5. Truth Binding Contract

Subskill output is support evidence only.

Accepted design facts must follow one of these routes:

```text
accepted non-promise design fact -> PRODUCT.md / DESIGN.md / docs/beacon/<version>/design/* truth binding
accepted prototype adapter input -> beacon prototype adapt
accepted promise-changing design fact -> beacon change ... --refreeze-chain
```

Only after truth binding may implementation use the design facts as delivery input.

## 6. Non Goals

- No new `beacon design` CLI route.
- No design runtime behavior change.
- No prototype adapter behavior change.
- No direct PRODUCT.md / DESIGN.md content mutation.
- No release verdict change.
- No new lifecycle stage.
- No upstream design capability promoted to Beacon truth source.
- No external upstream dependency for the simplify route (Beacon-native).
- The simplify route does not replace existing explore/extract/system/review/polish routes; it is an optional pre-check.

## 7. Success Metrics

- Eight `beacon-design-*` child skills are present in `.agents/skills` and packaged skills.
- The child skill names match `beacon design contract` route names.
- Each skill has an operator command for its route.
- Each skill states the same support-only boundary.
- Regression tests fail if a route exists without a corresponding human subskill.
- `beacon-design-simplify` is present in both `.agents/skills` and packaged skills.
- `beacon design route simplify` resolves without error and lists five first-principles capabilities.

## 8. State Axes

| Axis | Values | Description |
| --- | --- | --- |
| route_resolution | resolved \| blocked | Whether `beacon design route simplify` resolves. |
| skill_install | installed \| missing | Whether `beacon-design-simplify/SKILL.md` exists. |
| audit_progress | idle \| audit_requested \| auditing \| audit_complete \| audit_blocked | Simplify audit lifecycle. |
| truth_binding | unbound \| bound \| refreeze_pending | Whether accepted simplify findings are truth-bound. |

## 9. Diagram Truth

**Branch-flow**: Simplify audit decision tree — Q1 check core scenario defined → Q2 check ≤ 5 inputs and ≤ 1.5 screens → Q3 check concept duplication → Q4 check engineer abstraction. Each branch terminates in pass/flag/block.

**State-machine**: idle → audit_requested → auditing → audit_complete \| audit_blocked. Transitions driven by route resolution and capability check results.

**Decision-priority**: Core scenario detection > complexity scoring > duplication check > abstraction detection. Block conditions: missing truth refs, missing DESIGN_ROUTES entry, operator has not defined core scenario.
