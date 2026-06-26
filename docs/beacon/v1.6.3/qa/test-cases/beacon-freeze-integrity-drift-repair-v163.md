# Test Cases: beacon-freeze-integrity-drift-repair-v163

## Overview

**Feature**: beacon-freeze-integrity-drift-repair-v163
**Test Type**: ALL
**Version**: v1.6.3
**Generated**: 2026-06-25 17:23
**Requested Mode**: auto
**Effective Mode**: markdown
**Fallback Reason**: N/A
**Memory Context**: N/A
**AC Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.3/.machine/qa/beacon-freeze-integrity-drift-repair-v163.ac-test-matrix.json
**QA9 Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.3/.machine/qa/beacon-freeze-integrity-drift-repair-v163.qa9-matrix.json
**Story Scenario Map JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.3/.machine/qa/beacon-freeze-integrity-drift-repair-v163.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-FI-001 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_parser_contract_v2_accepted -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | parser_contract=v2 的包通过 validation，无 parser_contract_mismatch | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-001.json` |
| AC-001 | TC-FI-002 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_parser_contract_v1_still_accepted -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | parser_contract=v1 的包仍通过 | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-002.json` |
| AC-001 | TC-FI-003 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_unknown_contract_still_mismatch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | parser_contract=beacon-feature-package-v9 仍报 parser_contract_mismatch | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-003.json` |
| AC-002 | TC-FI-010 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_forbidden_field_substring_not_banned -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | evidence 含路径子串 gate-truth 不触发 evidence_forbidden_gate_truth_field | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-010.json` |
| AC-002 | TC-FI-011 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_real_forbidden_authority_still_banned -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | authority=source_of_truth 仍报 evidence_invalid_authority | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-011.json` |
| AC-003 | TC-FI-020 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_integration_pytest_not_soft -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Layer=integration + pytest command 行无 soft_test_assertion finding | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-020.json` |
| AC-003 | TC-FI-021 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_hard_markers_regex_includes_pytest -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | _HARD_TEST_MARKERS_RE.search 含 pytest 的字符串命中 | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-021.json` |
| AC-004 | TC-FI-030 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_authority_table_error_self_describing -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | evidence_authority_table_missing diagnostic 含 allowed_authorities 与 surface/authority 列提示 | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-030.json` |
| AC-004 | TC-FI-031 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_invalid_authority_error_self_describing -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | evidence_invalid_authority diagnostic 含 allowed_authorities 列表 | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-031.json` |
| AC-005 | TC-FI-040 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_v1_package_backward_compat -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.2 已冻结 feature 包修复后仍 pass validation | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-040.json` |
| AC-006 | TC-FI-050 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_p03_package_no_regression -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | beacon-gate-truth-model-alignment-v163 包修复后仍 pass validation | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-050.json` |
| AC-007 | TC-FI-060 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_real_weak_assertion_still_blocked -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Layer=integration 且无 hard command 的行仍被 soft_test_assertion 标记 | `.beacon/evidence/test-results/beacon-freeze-integrity-drift-repair-v163/{run_id}/TC-FI-060.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-FI-001 | Pending | from AC-001 |
| TC-FI-002 | Pending | from AC-001 |
| TC-FI-003 | Pending | from AC-001 |
| TC-FI-010 | Pending | from AC-002 |
| TC-FI-011 | Pending | from AC-002 |
| TC-FI-020 | Pending | from AC-003 |
| TC-FI-021 | Pending | from AC-003 |
| TC-FI-030 | Pending | from AC-004 |
| TC-FI-031 | Pending | from AC-004 |
| TC-FI-040 | Pending | from AC-005 |
| TC-FI-050 | Pending | from AC-006 |
| TC-FI-060 | Pending | from AC-007 |
