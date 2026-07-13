---
slug: beacon-loop-stagnation-detector-v166
version: v1.6.6
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Stagnation Detector v1.6.6

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-ST-001 | contract | `python3 -m pytest tests/test_v166_stagnation_detector.py::test_repeat_failure_detected -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 3+ identical reason_code failures in window → `stagnation_type=repeat_failure` finding |
| AC-002 | TC-ST-002 | contract | `python3 -m pytest tests/test_v166_stagnation_detector.py::test_repeat_labor_detected -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 3+ same (feature_slug, summary_prefix) iterations → `stagnation_type=repeat_labor` finding |
| AC-003 | TC-ST-003 | contract | `python3 -m pytest tests/test_v166_stagnation_detector.py::test_plateau_detected -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 3+ output events with incrementing iteration, empty reason_code, similar summary → `stagnation_type=plateau` finding |
| AC-004 | TC-ST-004 | contract | `python3 -m pytest tests/test_v166_stagnation_detector.py::test_clean_trace_no_findings -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Diverse trace → `status=clean`, findings empty |
| AC-005 | TC-ST-005 | integration | `python3 -m pytest tests/test_v166_stagnation_detector.py::test_upstream_correlation_in_finding -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Finding includes `pattern_ref` and `failure_ref` from upstream |
| AC-006 | TC-ST-006 | contract | `python3 -m pytest tests/test_v166_stagnation_detector.py::test_determinism_same_input_same_output -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Two calls with same trace + params → identical report |
| AC-007 | TC-ST-007 | integration | `python3 -m pytest tests/test_v166_stagnation_detector.py::test_doctor_loop_audit_stagnation_signal -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `doctor loop-audit --json` output contains `stagnation_detection` signal |
| AC-008 | TC-ST-008 | contract | `python3 -m pytest tests/test_v166_stagnation_detector.py::test_report_schema_valid -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Report matches `stagnation-report.v1` schema |

## Verification Notes

- Test module `tests/test_v166_stagnation_detector.py` is created in implement phase; tasks note `BLOCKED:implement` until then.
- All tests use `tmp_path` project roots with synthetic traces; no live agent required.
- Upstream modules (agent_trace, loop_patterns, loop_failure_catalog, loop_budget) are consumed read-only.

## Must vs Should

| Priority | AC |
|----------|-----|
| Must | AC-001..008 |
