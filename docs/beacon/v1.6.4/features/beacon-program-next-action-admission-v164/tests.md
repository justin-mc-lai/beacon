---
slug: beacon-program-next-action-admission-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-program-next-action-admission-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# Tests: Program Next-Action Admission and Non-Behavior Evidence R1

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-028 | TC-PNA-001 | integration | `python3 -m pytest tests/test_v164_program_next_action_admission.py::test_program_next_action_blocks_wrong_lake -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | SidePilot-style fixture with `next_action=beacon-gen-implement:content-hub-foundation` blocks `pi-host-ui-ux` with `program_next_action_mismatch`; no implementation evidence path is written. |
| AC-029 | TC-PNA-002 | unit | `python3 -m pytest tests/test_v164_program_next_action_admission.py::test_program_next_action_allows_current_lake -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Target `content-hub-foundation` matches `next_action`; admission result includes program slug, lake slug, material path, and next_action source. |
| AC-030 | TC-PNA-003 | integration | `python3 -m pytest tests/test_v164_program_next_action_admission.py::test_program_dependency_closure_blocks_downstream_lake -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Downstream W7 lake with W0-W6 dependencies and missing prerequisite QA acceptance blocks with `program_dependency_unclosed`. |
| AC-031 | TC-PNA-004 | regression | `python3 -m pytest tests/test_v164_program_next_action_admission.py::test_per_feature_implement_admission_unchanged_without_program_topology -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Feature without owning program topology keeps normal per-feature implement admission and does not require `program-run-state.json`. |
| AC-032 | TC-PNA-005 | contract | `python3 -m pytest tests/test_v164_program_next_action_admission.py::test_static_shell_ui_evidence_is_non_acceptance -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Full-parity UI evidence containing required surfaces with `coming_soon`, preview-only, static shell, or no-op recovery controls is rejected with `static_shell_implementation_evidence`. |
| AC-033 | TC-PNA-006 | contract | `python3 -m pytest tests/test_v164_program_next_action_admission.py::test_source_grep_only_tests_do_not_satisfy_behavior_ac -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Evidence built only from source string assertions such as `readFileSync(...).toContain(...)` cannot satisfy runtime/browser/user-behavior AC and returns `static_source_assertion_only`. |
| AC-034 | TC-PNA-007 | integration | `python3 -m pytest tests/test_v164_program_next_action_admission.py::test_blocked_generator_writes_diagnostic_only -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Blocked implement admission writes diagnostic state only and does not mark tasks done, write implementation summary, or update QA/release evidence. |

## Verification Notes

- TC-PNA-001 and TC-PNA-003 use SidePilot-shaped fixtures, not the live SidePilot repository, so Beacon harness behavior is deterministic.
- TC-PNA-005 and TC-PNA-006 verify evidence classification, not visual design quality.
- Formal QA verdict remains evaluator-owned; these tests define the required contract for implementation.

## Must vs Should

| Priority | AC |
|----------|----|
| Must | AC-028..AC-034 |
