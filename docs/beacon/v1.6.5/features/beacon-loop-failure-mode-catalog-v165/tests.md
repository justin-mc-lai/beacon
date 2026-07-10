---
slug: beacon-loop-failure-mode-catalog-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.5/features/beacon-loop-failure-mode-catalog-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Failure-Mode Catalog v1.6.5

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-FC-001 | contract | `python3 -m pytest tests/test_v165_loop_failure_mode_catalog.py::test_catalog_file_has_severity_sections -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Catalog file contains S1, S2, and S3 sections. |
| AC-002 | TC-FC-002 | contract | `python3 -m pytest tests/test_v165_loop_failure_mode_catalog.py::test_catalog_required_fields -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Validator fails entries missing required fields. |
| AC-003 | TC-FC-003 | contract | `python3 -m pytest tests/test_v165_loop_failure_mode_catalog.py::test_catalog_contains_baseline_modes -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Catalog includes truth drift, git alignment, stale evidence, infinite fix loop, and protected path attempt. |
| AC-004 | TC-FC-004 | contract | `python3 -m pytest tests/test_v165_loop_failure_mode_catalog.py::test_invalid_severity_fails -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Invalid severity returns `loop_failure_mode_invalid_severity`. |
| AC-005 | TC-FC-005 | integration | `python3 -m pytest tests/test_v165_loop_failure_mode_catalog.py::test_loop_audit_consumes_failure_catalog_status -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Loop audit includes failure catalog signal and findings. |

## Verification Notes

- Tests parse catalog content into structured entries before validating.
- Baseline mode test asserts ids, not just prose snippets.
