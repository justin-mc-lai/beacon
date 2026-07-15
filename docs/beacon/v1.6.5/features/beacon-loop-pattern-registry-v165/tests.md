---
slug: beacon-loop-pattern-registry-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.5/features/beacon-loop-pattern-registry-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Pattern Registry v1.6.5

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-PR-001 | contract | `python3 -m pytest tests/test_v165_loop_pattern_registry.py::test_registry_file_contains_required_patterns -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Registry file exists and includes ralph, team, and beacon-loop ids. |
| AC-002 | TC-PR-002 | contract | `python3 -m pytest tests/test_v165_loop_pattern_registry.py::test_registry_required_fields -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Missing any required field returns validation failure with field-level findings. |
| AC-003 | TC-PR-003 | contract | `python3 -m pytest tests/test_v165_loop_pattern_registry.py::test_duplicate_pattern_ids_block -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Duplicate ids fail with reason_code `loop_pattern_duplicate_id`. |
| AC-004 | TC-PR-004 | contract | `python3 -m pytest tests/test_v165_loop_pattern_registry.py::test_risk_values_are_governed -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Invalid risk values fail and accepted values pass. |
| AC-005 | TC-PR-005 | integration | `python3 -m pytest tests/test_v165_loop_pattern_registry.py::test_loop_audit_consumes_registry_status -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Loop audit includes registry signal and propagates registry findings. |

## Verification Notes

- Registry parsing uses structured YAML parsing.
- Tests construct invalid registries in temporary directories.
