# Tests: Truth Skill Lifecycle Rename

## Coverage Intent

The implementation must prove that lifecycle wording and skill routing follow the v1.5.2 package-authoritative model without breaking existing public skill entrypoints.

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-001 | contract | `python3 -m pytest tests/test_v152_truth_skill_lifecycle.py::test_beacon_truth_skill_exists_in_packaged_and_agent_surfaces -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Public skill guidance exposes `beacon-truth` and the preferred truth modes. |
| AC-002 | TC-002 | contract | `python3 -m pytest tests/test_v152_truth_skill_lifecycle.py::test_beacon_truth_preserves_distinct_modes_and_change_route -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | The umbrella keeps separate modes for definition, acceptance, coverage, and change. |
| AC-003 | TC-003 | contract | `python3 -m pytest tests/test_v152_truth_skill_lifecycle.py::test_beacon_truth_is_resolver_first_and_package_authoritative -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Truth authoring guidance remains resolver-first for v1.5.2. |
| AC-004 | TC-004 | contract | `python3 -m pytest tests/test_v152_truth_skill_lifecycle.py::test_legacy_truth_skills_are_marked_compatibility_aliases -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Existing `beacon-prd`, `beacon-user-story`, and `beacon-test-case` are documented as compatibility aliases. |
| AC-005 | TC-005 | contract | `python3 -m pytest tests/test_v152_truth_skill_lifecycle.py::test_root_and_brainstorm_prefer_truth_mode_lifecycle_language -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Root and brainstorm guidance use the new preferred lifecycle language. |
| AC-006 | TC-006 | contract | `python3 -m pytest tests/test_v152_truth_skill_lifecycle.py::test_beacon_truth_does_not_inflate_support_or_gate_surfaces -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | The umbrella does not inflate support, QA, release, or refreeze into truth stages. |
| AC-007 | TC-007 | contract | `python3 -m pytest tests/test_v152_truth_skill_lifecycle.py::test_beacon_truth_is_resolver_first_and_package_authoritative -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Guidance keeps requirement/acceptance truth in `truth.md` and coverage truth in `tests.md`. |
| AC-008 | TC-008 | integration | `python3 -m pytest tests/test_v152_truth_skill_lifecycle.py::test_validate_feature_package_cli_for_truth_skill_lifecycle_package -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | The frozen package validates as v1.5.2 feature-package authoritative truth. |

## Coverage Boundary

- These tests validate requirement closure and guidance contracts.
- Runtime implementation tests may be added later if `beacon-truth` becomes a CLI command instead of a skill-only umbrella.
- Passing coverage must not require old `prd/`, `user-story/`, or `qa/test-cases/` files to exist.
