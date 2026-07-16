---
slug: beacon-protected-path-denylist-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.5/features/beacon-protected-path-denylist-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Protected Path Denylist v1.6.5

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-PD-001 | contract | `python3 -m pytest tests/test_v165_protected_path_denylist.py::test_global_boundaries_contains_protected_path_principle -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Global boundaries contains protected path principle and planner/write-surface distinction. |
| AC-002 | TC-PD-002 | contract | `python3 -m pytest tests/test_v165_protected_path_denylist.py::test_protected_path_matcher_patterns -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Matcher detects exact, glob, extension, and path segment patterns. |
| AC-003 | TC-PD-003 | contract | `python3 -m pytest tests/test_v165_protected_path_denylist.py::test_write_guard_blocks_protected_path -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Write guard blocks protected path with reason_code `protected_path_denylist`. |
| AC-004 | TC-PD-004 | contract | `python3 -m pytest tests/test_v165_protected_path_denylist.py::test_planner_risk_is_advisory -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Planner advisory helper reports risk without write-block verdict. |
| AC-005 | TC-PD-005 | contract | `python3 -m pytest tests/test_v165_protected_path_denylist.py::test_block_payload_contains_human_route -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Block payload includes route recommendation for explicit human handling. |

## Verification Notes

- Tests must assert allowed ordinary files remain allowed.
- Tests must not create real secrets.
