---
slug: beacon-loop-readiness-audit-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.5/features/beacon-loop-readiness-audit-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Readiness Audit v1.6.5

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-LA-001 | cli | `python3 -m pytest tests/test_v165_loop_readiness_audit.py::test_loop_audit_json_shape -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Doctor loop-audit returns score, level, signals, findings, suggestions, and version fields. |
| AC-002 | TC-LA-002 | contract | `python3 -m pytest tests/test_v165_loop_readiness_audit.py::test_score_level_thresholds -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Scores map to L0/L1/L2/L3 at the defined thresholds. |
| AC-003 | TC-LA-003 | contract | `python3 -m pytest tests/test_v165_loop_readiness_audit.py::test_signal_inventory_contains_required_signals -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Required signal ids are present and each signal has status, weight, and reason code fields. |
| AC-004 | TC-LA-004 | cli | `python3 -m pytest tests/test_v165_loop_readiness_audit.py::test_strict_below_threshold_blocks -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Strict mode below threshold returns blocked status and reason_code `loop_readiness_below_threshold`. |
| AC-005 | TC-LA-005 | contract | `python3 -m pytest tests/test_v165_loop_readiness_audit.py::test_suggestions_are_ordered_and_actionable -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Failed signals emit ordered repair suggestions with command or route fields. |
| AC-006 | TC-LA-006 | contract | `python3 -m pytest tests/test_v165_loop_readiness_audit.py::test_non_strict_is_report_only -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Non-strict low score is labeled report-only and is not a release verdict. |

## Verification Notes

- Tests call helper functions directly for deterministic score cases and use CliRunner for command behavior.
- Readiness score is a support signal, not requirement truth.
