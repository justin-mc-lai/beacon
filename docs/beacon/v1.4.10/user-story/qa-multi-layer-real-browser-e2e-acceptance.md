# User Story: QA Multi-Layer Real Browser E2E Acceptance

**Feature**: `qa-multi-layer-real-browser-e2e-acceptance`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-25`

## Story 1: Full-Range QA Closure

As a Beacon operator preparing a feature for release, I want QA to determine the full applicable test range dynamically, so that a feature cannot pass by running only a convenient subset of tests.

### Acceptance Criteria

- [ ] AC-001 QA recognizes the full layer taxonomy: unit, interface, contract, integration, smoke, functional, regression, exception, compatibility, and browser E2E.
- [ ] AC-002 QA profiles distinguish `basic`, `complete`, `closure`, and `browser`, and report whether a run is partial or complete.
- [ ] AC-003 Human-selected layers and commands are allowed, but partial runs are explicitly marked and cannot satisfy closure unless the selected scope matches the required profile.

## Story 2: Non-Browser Feature Completeness

As a backend or service owner, I want QA to run or justify all applicable non-browser layers, so that service correctness is not inferred from one proxy check.

### Acceptance Criteria

- [ ] AC-004 Non-browser features run or justify unit, interface, contract, integration, smoke, regression, exception, and compatibility coverage before closure.
- [ ] AC-011 Failure attribution routes gaps to implement, test-case, change/refreeze, QA rerun, or blocked admission based on evidence.

## Story 3: Real Browser Function UI UX Acceptance

As a product owner of a browser, H5, miniapp, or admin feature, I want QA to exercise real user workflows in a real browser, so that function, UI, UX, layout, interaction, session, and data regressions cannot pass unnoticed.

### Acceptance Criteria

- [ ] AC-005 Browser features require real browser E2E evidence for function, UI, UX, compatibility, session, and state/data consistency.
- [ ] AC-006 Project-native E2E scripts can be discovered or selected and bound to AC/test IDs.
- [ ] AC-010 Browser-required scenarios without valid browser evidence block QA/release.

## Story 4: Governed Browser Runner Registry

As a QA operator, I want Beacon to support multiple browser runner candidates, so that protected surfaces, local apps, and CDP-attached sessions can use the right runner without changing QA truth.

### Acceptance Criteria

- [ ] AC-007 Browser runner registry includes Playwright, Playwright CLI, Playwright CDP, browser-use, agent-browser, attached browser, web-access, and Obscura CDP.
- [ ] AC-008 Listing commands, placeholder transcripts, and documentation-only pass notes cannot satisfy acceptance.

## Story 5: Evidence-Bound Closure and Release Boundary

As a release owner, I want QA acceptance to include executable evidence and attribution, so that release readiness is based on formal QA closure rather than raw support output.

### Acceptance Criteria

- [ ] AC-009 QA acceptance transactions include run ID, source commands, runner/browser identity, accepted test IDs, evidence refs, and failure attribution.
- [ ] AC-012 Release consumes formal QA closure only; raw runner output or support evidence cannot directly become release pass evidence.

## Boundary

QA has closure-veto authority. It cannot define or rewrite frozen truth, but it can reject delivery claims and route back to the correct truth or execution surface.
