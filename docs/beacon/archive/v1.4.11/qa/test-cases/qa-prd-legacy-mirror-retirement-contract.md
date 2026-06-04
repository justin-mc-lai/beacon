# Test Cases: QA and PRD Legacy Mirror Retirement Contract

**Feature**: `qa-prd-legacy-mirror-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-QA-PRD-MIRROR-001 | contract | `python3 -m pytest -q tests/test_v1411_qa_prd_legacy_mirror_policy.py -k "canonical_qa_status_is_default_authority"` | QA status helpers and current QA flows read canonical QA status by default and do not silently promote legacy auto-test status. | `.beacon/evidence/test-results/qa-prd-legacy-mirror-retirement-contract/TC-QA-PRD-MIRROR-001.json` |
| AC-002 | TC-QA-PRD-MIRROR-002 | compatibility | `python3 -m pytest -q tests/test_v1411_qa_prd_legacy_mirror_policy.py -k "legacy_qa_status_requires_explicit_admission"` | Legacy QA status requires explicit compatibility admission and is labeled historical evidence when admitted. | `.beacon/evidence/test-results/qa-prd-legacy-mirror-retirement-contract/TC-QA-PRD-MIRROR-002.json` |
| AC-003 | TC-QA-PRD-MIRROR-003 | release | `python3 -m pytest -q tests/test_v1411_qa_prd_legacy_mirror_policy.py -k "release_blocks_legacy_only_qa_pass"` | Release scorecard/check cannot pass when only legacy QA status reports pass. | `.beacon/evidence/test-results/qa-prd-legacy-mirror-retirement-contract/TC-QA-PRD-MIRROR-003.json` |
| AC-004 | TC-QA-PRD-MIRROR-004 | contract | `python3 -m pytest -q tests/test_v1411_qa_prd_legacy_mirror_policy.py -k "markdown_prd_remains_requirement_truth"` | Markdown PRD remains requirement truth and legacy PRD mirror cannot override it. | `.beacon/evidence/test-results/qa-prd-legacy-mirror-retirement-contract/TC-QA-PRD-MIRROR-004.json` |
| AC-005 | TC-QA-PRD-MIRROR-005 | gate | `python3 -m pytest -q tests/test_v1411_qa_prd_legacy_mirror_policy.py -k "current_prd_projection_drift_still_blocks"` | Current PRD projection drift remains blocking. | `.beacon/evidence/test-results/qa-prd-legacy-mirror-retirement-contract/TC-QA-PRD-MIRROR-005.json` |
| AC-006 | TC-QA-PRD-MIRROR-006 | compatibility | `python3 -m pytest -q tests/test_v1411_qa_prd_legacy_mirror_policy.py -k "legacy_prd_mirror_stale_is_compat_warning"` | Legacy PRD mirror mismatch is reported as compatibility warning by default, not current truth drift. | `.beacon/evidence/test-results/qa-prd-legacy-mirror-retirement-contract/TC-QA-PRD-MIRROR-006.json` |
| AC-007 | TC-QA-PRD-MIRROR-007 | registry | `python3 -m pytest -q tests/test_v1411_qa_prd_legacy_mirror_policy.py -k "mirror_policies_bind_to_compat_registry"` | QA and PRD mirror policies bind to registered compat IDs and fail validation if those IDs are missing. | `.beacon/evidence/test-results/qa-prd-legacy-mirror-retirement-contract/TC-QA-PRD-MIRROR-007.json` |
| AC-008 | TC-QA-PRD-MIRROR-008 | regression | `python3 -m pytest -q tests/test_v1411_qa_prd_legacy_mirror_policy.py -k "no_unrelated_legacy_retirement_in_mirror_policy_slice"` | This slice does not delete legacy files or change implement, prototype, browser, memory, intent, or command behavior. | `.beacon/evidence/test-results/qa-prd-legacy-mirror-retirement-contract/TC-QA-PRD-MIRROR-008.json` |

## Explicit Non Coverage

- These tests do not require implement package migration.
- These tests do not require prototype legacy inspector split.
- These tests do not require browser fallback rename.
- These tests do not require memory or intent behavior changes.
- These tests do not require command removal.
- These tests do not produce release pass or fail verdicts by themselves.
