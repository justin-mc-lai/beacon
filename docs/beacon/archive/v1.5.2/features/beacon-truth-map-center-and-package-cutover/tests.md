# Tests: Feature Package Authoritative Cutover

## Coverage Intent

v1.5.2 tests must prove that feature-package Markdown is not only readable, but authoritative for normal Beacon production and consumption. The suite must fail if legacy `prd/`, `user-story/`, or `qa/test-cases/` silently regain authority.

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-001 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_package_markdown_is_authoritative -q` | Feature package Markdown is authoritative. |
| AC-002 | TC-002 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_consumers_require_truth_map_resolver -q` | Consumers resolve via truth map. |
| AC-003 | TC-003 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_legacy_triptych_is_not_canonical -q` | Legacy triptych has rebuild/absorb role only. |
| AC-004 | TC-004 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_doctor_rebuilds_legacy_from_package -q` | Doctor rebuild route works or fails closed. |
| AC-005 | TC-005 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_change_absorbs_legacy_into_package -q` | Change absorb route works or fails closed. |
| AC-006 | TC-006 | unit | `python3 -m pytest tests/test_v152_package_authoritative.py::test_json_twin_not_required -q` | Markdown truth validates without JSON twin. |
| AC-007 | TC-007 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_gate_qa_release_consume_package_truth -q` | Gate/QA/release use package truth through resolver/parser. |
| AC-008 | TC-008 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_legacy_drift_fails_closed_package_wins -q` | Legacy drift is reported and package truth wins. |
| AC-001 | TC-009 | unit | `python3 -m pytest tests/test_v152_package_authoritative.py::test_resolver_policy_is_version_aware -q` | v1.5.1 remains `feature_package_authoritative_ready`; v1.5.2+ returns `feature_package_authoritative`. |
| AC-001 | TC-010 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_truth_frontmatter_model_matches_resolver_policy -q` | `truth.md` frontmatter and resolver payload agree on authority model. |
| AC-002 | TC-011 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_entrypoint_inventory_rejects_v151_legacy_exceptions_for_v152 -q` | v1.5.2 inventory fails unless normal truth entrypoints are resolver-routed. |
| AC-002 | TC-012 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_entrypoint_inventory_rejects_v151_legacy_exceptions_for_v152 -q` | PRD/user-story/test-case/workflow/truth/gate/release entrypoints are package-routed with no cutover-blocked normal consumer. |
| AC-002 | TC-013 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_skill_guidance_points_to_package_authoritative_truth_map_first -q` | Packaged and installed skills tell LLMs to resolve package truth first and do not present old triptych as normal v1.5.2 authority. |
| AC-003 | TC-014 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_material_audit_package_complete_without_legacy_triptych -q` | Material audit passes package completeness even when legacy PRD/story/test-case files are absent. |
| AC-003 | TC-015 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_manifest_truth_paths_are_generated_index_not_authority -q` | Manifest truth paths are generated index state and cannot override resolver package paths. |
| AC-004 | TC-016 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_doctor_rebuilds_legacy_from_package -q` | Doctor rebuild target paths are legacy outputs with package sources, not authority inputs. |
| AC-005 | TC-017 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_change_absorbs_legacy_into_package -q` | Change absorb reads legacy triptych only to update package truth, not to promote legacy authority. |
| AC-006 | TC-018 | unit | `python3 -m pytest tests/test_v152_package_authoritative.py::test_existing_machine_json_may_be_absent_or_stale_without_invalidating_markdown -q` | Missing/stale generated JSON is diagnostics unless a generated-state freshness gate explicitly checks it. |
| AC-006 | TC-019 | unit | `python3 -m pytest tests/test_v152_package_authoritative.py::test_generated_json_claiming_truth_authority_fails_closed -q` | Any generated JSON with `truth_authority=true` or `json_authority=true` fails closed. |
| AC-007 | TC-020 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_acceptance_kit_uses_package_refs_for_skill_scenario_trace -q` | Requirement and acceptance projections derive refs from package `truth.md` and `tests.md`. |
| AC-007 | TC-021 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_acceptance_kit_uses_package_refs_for_skill_scenario_trace -q` | Acceptance kit references package truth/tests instead of old PRD/story/test-case defaults. |
| AC-007 | TC-022 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_gate_qa_release_consume_package_truth -q` | Release scorecard reports package authority and does not require legacy triptych completeness. |
| AC-007 | TC-023 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_status_surface_reports_package_authority -q` | Status output reports feature package as authority and generated state as non-authority. |
| AC-008 | TC-024 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_legacy_drift_fails_closed_package_wins -q` | Conflicting legacy PRD/story/test-case content is reported as drift and never considered a competing truth candidate. |
| AC-008 | TC-025 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_gate_blocks_when_package_surfaces_are_missing_even_if_legacy_exists -q` | Gate blocks when package truth/tests/tasks/evidence are missing even if old triptych files exist. |

## Coverage Boundary

- These tests validate authority and routing contracts, not release readiness by themselves.
- Generated JSON may be asserted as diagnostics, but no test may require JSON as a twin before accepting package Markdown truth.
- A test passes only when package truth wins every conflict against legacy triptych material.
