# Test Cases: QA Multi-Layer Real Browser E2E Acceptance

**Feature**: `qa-multi-layer-real-browser-e2e-acceptance`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-25`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-QA-FULL-001 | contract | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "qa_layer_taxonomy"` | QA accepts the finite full-range layer taxonomy and rejects unmapped layers. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-001.json` |
| AC-002 | TC-QA-FULL-002 | contract | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "qa_profiles_report_completeness"` | `basic`, `complete`, `closure`, and `browser` profiles report required/executed/skipped/blocked/not-applicable layers and partial/complete status. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-002.json` |
| AC-003 | TC-QA-FULL-003 | integration | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "human_selected_commands_are_partial_until_complete"` | Human-selected layer commands are recorded, but partial selection cannot masquerade as full closure. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-003.json` |
| AC-004 | TC-QA-FULL-004 | integration | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "non_browser_features_require_applicable_full_range"` | Non-browser features require unit/interface/contract/integration/smoke/regression/exception/compatibility execution or explicit not-applicable reasons. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-004.json` |
| AC-005 | TC-QA-FULL-005 | browser-e2e | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "browser_features_require_function_ui_ux_evidence"` | Browser features require real browser function, UI, UX, compatibility, session, and state/data evidence. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-005.json` |
| AC-006 | TC-QA-FULL-006 | discovery | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "project_e2e_scripts_bind_to_ac_test_ids"` | Project-native E2E scripts and reports can be bound to AC/test IDs. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-006.json` |
| AC-007 | TC-QA-FULL-007 | runner-registry | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "browser_runner_registry_contains_supported_candidates"` | Runner registry includes Playwright, Playwright CLI, Playwright CDP, browser-use, agent-browser, attached browser, web-access, and Obscura CDP. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-007.json` |
| AC-008 | TC-QA-FULL-008 | fail-closed | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "listing_and_placeholder_evidence_cannot_pass"` | `playwright test --list`, placeholder transcripts, and documentation-only pass notes are non-acceptance evidence. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-008.json` |
| AC-009 | TC-QA-FULL-009 | acceptance-transaction | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "acceptance_transaction_records_executable_evidence"` | QA acceptance records run ID, commands, runner/browser identity, accepted test IDs, evidence refs, and attribution. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-009.json` |
| AC-010 | TC-QA-FULL-010 | release-boundary | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "missing_browser_evidence_blocks_release"` | Browser-required scenarios without valid browser evidence block QA/release. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-010.json` |
| AC-011 | TC-QA-FULL-011 | attribution | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "qa_failure_attribution_routes_deterministically"` | Failure attribution routes to implement, test-case, change/refreeze, QA rerun, or blocked runner admission. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-011.json` |
| AC-012 | TC-QA-FULL-012 | release-boundary | `python3 -m pytest -q tests/test_v1410_qa_multi_layer_browser_acceptance.py -k "release_consumes_formal_qa_closure_only"` | Release consumes formal QA closure only and cannot treat raw support/runner output as pass evidence. | `.beacon/evidence/test-results/qa-multi-layer-real-browser-e2e-acceptance/TC-QA-FULL-012.json` |

## Browser Acceptance Evidence Requirements

Browser E2E evidence is valid only when it can identify:

- source command and current run ID;
- runner/browser or CDP endpoint;
- target URL or app route;
- session bridge, storage state, or explicit anonymous admission;
- result status and accepted test IDs;
- at least one concrete UI/UX/function evidence ref such as Playwright JSON/JUnit, trace, screenshot, video, DOM snapshot, current URL, console/network summary, or browser evidence pack.

## Explicit Non Coverage

- These tests do not execute hidden browser side effects.
- These tests do not make Playwright CLI, Obscura, or any runner a verdict source.
- These tests do not allow QA to rewrite frozen PRD/user-story/test-case truth.
- These tests do not replace project-native E2E suites.
