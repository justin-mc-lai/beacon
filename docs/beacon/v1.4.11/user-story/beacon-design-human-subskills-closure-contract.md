# User Story: Beacon Design Human Subskills Closure Contract

**Feature**: `beacon-design-human-subskills-closure-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Story

As a Beacon operator, I want each design intent to have a clear `beacon-design-*` child skill, so I can ask for exploration, extraction, component-system planning, review, polish, reference lookup, bootstrap checks, or first-principles simplicity audits without relying on the AI to reinterpret one broad design skill every time.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | aggregate entry | `beacon-design` remains the support-only aggregate design entry. |
| AC-002 | explore | `beacon-design-explore` exists and maps only to route `explore` / upstream `vibe-to-ui`. |
| AC-003 | extract | `beacon-design-extract` exists and maps only to route `extract` / upstream `vibe-to-ui`. |
| AC-004 | system | `beacon-design-system` exists and maps only to route `system` / upstream `ui-ux-pro-max`. |
| AC-005 | review | `beacon-design-review` exists and maps only to route `review` / upstream `impeccable`. |
| AC-006 | polish | `beacon-design-polish` exists and maps only to route `polish` / upstream `impeccable`. |
| AC-007 | library | `beacon-design-library` exists, maps to route `library`, and treats `awesome-design-md` as reference-only. |
| AC-008 | bootstrap | `beacon-design-bootstrap` exists, maps to route `bootstrap`, and is capability-admission-only. |
| AC-009 | boundary | Every child skill declares support-only / non-truth / non-gate / non-lifecycle boundaries. |
| AC-010 | truth binding | Accepted design facts route to truth binding, prototype adapter, or change/refreeze before implementation. |
| AC-011 | testability | Tests verify installed child skills match deterministic design routes. |
| AC-012 | no runtime change | No new design route, prototype adapter change, or release verdict change is introduced. |
| AC-013 | simplify existence | `beacon-design-simplify` exists and maps to route `simplify` with Beacon-native first-principles capabilities. |
| AC-014 | simplify capabilities | The simplify route provides `lazy_user_axiom`, `core_scenario_extraction`, `engineer_abstraction_detection`, `information_deduplication`, and `complexity_burden_score`. |
| AC-015 | simplify boundary | `beacon-design-simplify` declares support-only boundaries and has no upstream skill dependency. |
| AC-016 | simplify SKILL.md | `beacon-design-simplify/SKILL.md` describes the first-principles simplicity audit with operator command `beacon design route simplify`. |
| AC-017 | simplify regression | Tests verify `simplify` route exists in `DESIGN_ROUTES` and matches installed `beacon-design-simplify` subskill. |

## Test Story Map

| Test ID | Covers | Scenario |
| --- | --- | --- |
| TEST-001 | AC-001 | Aggregate `beacon-design` remains installed and support-only. |
| TEST-002 | AC-002 | Explore subskill exists and invokes/points to `beacon design route explore`. |
| TEST-003 | AC-003 | Extract subskill exists and invokes/points to `beacon design route extract`. |
| TEST-004 | AC-004 | System subskill exists and invokes/points to `beacon design route system`. |
| TEST-005 | AC-005 | Review subskill exists and invokes/points to `beacon design route review`. |
| TEST-006 | AC-006 | Polish subskill exists and invokes/points to `beacon design route polish`. |
| TEST-007 | AC-007 | Library subskill states reference-only behavior. |
| TEST-008 | AC-008 | Bootstrap subskill states capability-admission-only behavior. |
| TEST-009 | AC-009 | Every child skill states non-truth, non-gate, non-lifecycle boundaries. |
| TEST-010 | AC-010 | Truth binding next-route text exists in child skill family. |
| TEST-011 | AC-011 | Route list from `beacon design contract` and installed subskills match. |
| TEST-012 | AC-012 | Runtime route list remains unchanged. |
| TEST-013 | AC-013 | Simplify subskill exists and invokes/points to `beacon design route simplify`. |
| TEST-014 | AC-014 | Simplify route payload includes five first-principles capabilities. |
| TEST-015 | AC-015 | Simplify subskill states support-only boundary and no-upstream constraint. |
| TEST-016 | AC-016 | Simplify SKILL.md contains operator command and first-principles axioms. |
| TEST-017 | AC-017 | Installed subskills include `beacon-design-simplify` matching `simplify` route. |
