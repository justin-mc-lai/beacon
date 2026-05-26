# Change: QA Multi-Layer Real Browser E2E Acceptance

**Feature**: `qa-multi-layer-real-browser-e2e-acceptance`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-25`

## 1. Change Reason

Beacon QA must stop treating a local pytest pass, a hand-written "passed" note, or a listed E2E script as enough proof for feature closure. Real projects such as `slow_uni_bmtop` already contain Playwright E2E suites and historical real-browser evidence, but Beacon's formal QA materials can still miss `browser_required` coverage, accept thin transactions, or fail to bind browser reports into release-facing evidence.

This change promotes QA into the formal multi-layer acceptance authority for Beacon's truth-delivery model.

## 2. Accepted Change

Freeze `qa-multi-layer-real-browser-e2e-acceptance` as the requirement package for full-range dynamic QA orchestration:

- Non-browser service features must dynamically cover the applicable full QA range: unit, interface, contract, integration, smoke, regression, exception, and compatibility.
- Browser, frontend, H5, miniapp, and admin-surface features must additionally require real browser E2E acceptance for function, UI, UX, compatibility, session, and state/data consistency.
- Human operators may explicitly select QA profiles, layers, and commands, but Beacon must mark partial runs as partial and cannot let them masquerade as complete closure.
- Browser runner registry must support Playwright, Playwright CLI, Playwright CDP, browser-use, agent-browser, attached browser, web-access, and Obscura CDP as runner candidates.
- QA acceptance evidence must record command execution, runner/browser identity, result, evidence refs, accepted test IDs, and failure attribution.
- QA cannot rewrite frozen truth, but it has closure-veto authority: weak evidence blocks release and routes back to change, test-case, implement, or QA rerun.

## 3. Scope

### In Scope

- QA profile semantics for `basic`, `complete`, `closure`, and `browser`.
- Dynamic layer selection and completeness reporting.
- Human-provided layer command admission and evidence capture.
- Real browser evidence import/execution contracts for Playwright-style reports, JUnit, traces, screenshots, console/network summaries, storage/session state, and browser evidence packs.
- Browser UI/UX acceptance requirements so visual layout, interaction state, and user flow regressions cannot pass as backend-only success.
- Failure attribution integration with `qa-evidence-attribution-layer`.
- Release-facing blocker semantics for missing browser evidence, placeholder-only browser evidence, test listing commands, and partial QA runs.

### Out Of Scope

- Making QA a truth-authoring surface.
- Silently editing PRD, user-story, or test-case materials from QA.
- Hidden browser or hook side effects without operator command/confirmation.
- Mandating every project to use the same runner.
- Replacing project-native test suites with Beacon-owned test scripts.

## 4. Route Decision

This change must enter the v1.4.10 requirement truth chain before implementation. Downstream implementation should extend current QA/auto-test/runtime code rather than create a new lifecycle stage.

## 5. Freeze Deliverables

- `docs/beacon/v1.4.10/research/qa-multi-layer-real-browser-e2e-acceptance.md`
- `docs/beacon/v1.4.10/change/qa-multi-layer-real-browser-e2e-acceptance.md`
- `docs/beacon/v1.4.10/prd/qa-multi-layer-real-browser-e2e-acceptance.md`
- `docs/beacon/v1.4.10/user-story/qa-multi-layer-real-browser-e2e-acceptance.md`
- `docs/beacon/v1.4.10/qa/test-cases/qa-multi-layer-real-browser-e2e-acceptance.md`

## 6. Boundary

QA is below frozen truth definition authority but above truth closure claims. QA cannot define what the product should be, but it can reject any claim that the product has been delivered.
