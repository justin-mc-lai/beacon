# Test Cases: Test Directory / Marker Re-Layering Contract

**Feature**: `test-directory-marker-relayering-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-MARKER-001 | marker | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "marker_registry_contains_required_layers"` | Required pytest markers are registered. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-001.json` |
| AC-002 | TC-MARKER-002 | marker | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "v1411_retirement_tests_are_marked"` | v1.4.11 retirement tests have deterministic marker classification. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-002.json` |
| AC-003 | TC-MARKER-003 | current | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "current_contract_tests_do_not_assert_legacy_defaults"` | Current contract tests do not make legacy fallback the default. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-003.json` |
| AC-004 | TC-MARKER-004 | compatibility | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "compat_tests_bind_to_registry_ids"` | Compat tests reference registered compatibility ids. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-004.json` |
| AC-005 | TC-MARKER-005 | historical | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "historical_fixture_tests_are_not_current_closure"` | Historical fixture tests cannot satisfy current closure. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-005.json` |
| AC-006 | TC-MARKER-006 | migration | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "migration_tests_assert_evidence_or_transactions"` | Migration tests assert evidence or transaction behavior. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-006.json` |
| AC-007 | TC-MARKER-007 | deprecated | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "deprecated_tests_do_not_promote_default_routes"` | Deprecated tests do not promote default current routes. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-007.json` |
| AC-008 | TC-MARKER-008 | projection | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "projection_tests_are_marked_separately"` | Projection integrity tests are separate from human truth authority. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-008.json` |
| AC-009 | TC-MARKER-009 | validation | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "marker_validation_payload_is_deterministic"` | Marker validation emits deterministic pass/block payload. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-009.json` |
| AC-010 | TC-MARKER-010 | regression | `python3 -m pytest -q tests/test_v1411_test_directory_marker_relayering.py -k "no_runtime_behavior_changes"` | Runtime behavior is out of scope. | `.beacon/evidence/test-results/test-directory-marker-relayering-contract/TC-MARKER-010.json` |

## Explicit Non Coverage

- These tests do not execute release check.
- These tests do not move broad test directories.
- These tests do not change runtime behavior.
- These tests do not remove legacy or deprecated tests.

