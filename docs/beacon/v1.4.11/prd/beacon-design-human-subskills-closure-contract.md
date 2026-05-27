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
