# Test Cases: Version Aggregate Projection Guard Contract

**Feature**: `version-aggregate-projection-guard-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-AGG-PROJ-001 | wording | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "projection_wording_not_truth"` | Aggregate change artifacts are described as projection/read model, not requirement truth. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-001.json` |
| AC-002 | TC-AGG-PROJ-002 | projection | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "qa_accepted_feature_requires_feature_change_projection"` | QA accepted current feature has feature projection or repairable missing-projection finding. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-002.json` |
| AC-003 | TC-AGG-PROJ-003 | release-create | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "release_create_rebuilds_version_projection_with_dependency_order"` | Version aggregate projection includes expected feature count/list and explicit dependency waves. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-003.json` |
| AC-004 | TC-AGG-PROJ-004 | release-check | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "release_check_blocks_when_current_feature_missing_from_aggregate"` | Release check fails closed when current QA accepted feature is missing from aggregate projection. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-004.json` |
| AC-005 | TC-AGG-PROJ-005 | release-check | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "release_check_passes_when_current_feature_included"` | Release check aggregate inclusion passes when current QA accepted feature is included. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-005.json` |
| AC-006 | TC-AGG-PROJ-006 | doctor | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "doctor_repair_rebuilds_projection_without_truth_authority"` | Doctor repair-only path rebuilds projection artifacts and does not claim truth authority. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-006.json` |
| AC-007 | TC-AGG-PROJ-007 | test-index | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "test_contract_index_repair_clears_stale_index_risk"` | build + strict verify clears stale test-contract-index risk. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-007.json` |
| AC-008 | TC-AGG-PROJ-008 | boundary | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "guard_does_not_add_lifecycle_stage"` | No new lifecycle stage, mandatory human command, release publish, or post-release install is introduced. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-008.json` |
| AC-009 | TC-AGG-PROJ-009 | regression | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "projection_guard_regression_suite_covers_required_axes"` | Regression suite covers missing projection, repaired projection, feature count/list, dependency order, and wording. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-009.json` |
| AC-010 | TC-AGG-PROJ-010 | repair-route | `python3 -m pytest -q tests/test_v1411_version_aggregate_projection_guard.py -k "blocked_release_output_includes_projection_repair_route"` | Blocked release output includes actionable projection repair guidance. | `.beacon/evidence/test-results/version-aggregate-projection-guard-contract/TC-AGG-PROJ-010.json` |

## Explicit Non Coverage

- These tests do not publish a release.
- These tests do not execute post-release install hooks.
- These tests do not add a new lifecycle stage.
- These tests do not treat machine projections as requirement truth.
