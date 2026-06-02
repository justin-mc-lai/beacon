# Test Cases: Feature Package Authoritative Cutover

- version: `v1.5.2`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
|---|---|---|---|---|---|
| AC-001 | TC-001 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_package_markdown_is_authoritative -q` | Feature package Markdown is authoritative. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-001/__RUN_ID__.json` |
| AC-002 | TC-002 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_consumers_require_truth_map_resolver -q` | Consumers resolve via truth map. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-002/__RUN_ID__.json` |
| AC-003 | TC-003 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_legacy_triptych_is_not_canonical -q` | Legacy triptych has rebuild/absorb role only. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-003/__RUN_ID__.json` |
| AC-004 | TC-004 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_doctor_rebuilds_legacy_from_package -q` | Doctor rebuild route works or fails closed. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-004/__RUN_ID__.json` |
| AC-005 | TC-005 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_change_absorbs_legacy_into_package -q` | Change absorb route works or fails closed. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-005/__RUN_ID__.json` |
| AC-006 | TC-006 | unit | `python3 -m pytest tests/test_v152_package_authoritative.py::test_json_twin_not_required -q` | Markdown truth validates without JSON twin. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-006/__RUN_ID__.json` |
| AC-007 | TC-007 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_gate_qa_release_consume_package_truth -q` | Gate/QA/release use package truth through resolver/parser. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-007/__RUN_ID__.json` |
| AC-008 | TC-008 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_legacy_drift_fails_closed_package_wins -q` | Legacy drift is reported and package truth wins. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-008/__RUN_ID__.json` |

## Cutover Regression Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
|---|---|---|---|---|---|
| AC-001 | TC-009 | unit | `python3 -m pytest tests/test_v152_package_authoritative.py::test_resolver_policy_is_version_aware -q` | v1.5.1 remains ready-only while v1.5.2 is authoritative. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-009/__RUN_ID__.json` |
| AC-001 | TC-010 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_truth_frontmatter_model_matches_resolver_policy -q` | Package frontmatter and resolver model agree. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-010/__RUN_ID__.json` |
| AC-002 | TC-011 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_entrypoint_inventory_rejects_v151_legacy_exceptions_for_v152 -q` | v1.5.1 legacy exceptions cannot pass v1.5.2 inventory. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-011/__RUN_ID__.json` |
| AC-002 | TC-012 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_entrypoint_inventory_rejects_v151_legacy_exceptions_for_v152 -q` | High-risk CLI entrypoints are package-routed or cutover-blocked. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-012/__RUN_ID__.json` |
| AC-002 | TC-013 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_skill_guidance_points_to_package_authoritative_truth_map_first -q` | Skills instruct package-first resolver usage for v1.5.2. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-013/__RUN_ID__.json` |
| AC-003 | TC-014 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_material_audit_package_complete_without_legacy_triptych -q` | Material audit accepts complete package truth without old triptych files. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-014/__RUN_ID__.json` |
| AC-003 | TC-015 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_manifest_truth_paths_are_generated_index_not_authority -q` | Manifest cannot override resolver package paths. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-015/__RUN_ID__.json` |
| AC-004 | TC-016 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_doctor_rebuilds_legacy_from_package -q` | Doctor rebuild writes legacy outputs from package sources only. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-016/__RUN_ID__.json` |
| AC-005 | TC-017 | contract | `python3 -m pytest tests/test_v152_package_authoritative.py::test_change_absorbs_legacy_into_package -q` | Change absorb promotes legacy text into package truth, not legacy authority. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-017/__RUN_ID__.json` |
| AC-006 | TC-018 | unit | `python3 -m pytest tests/test_v152_package_authoritative.py::test_existing_machine_json_may_be_absent_or_stale_without_invalidating_markdown -q` | Missing/stale generated JSON does not invalidate Markdown package truth. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-018/__RUN_ID__.json` |
| AC-006 | TC-019 | unit | `python3 -m pytest tests/test_v152_package_authoritative.py::test_generated_json_claiming_truth_authority_fails_closed -q` | Generated JSON that claims truth authority fails closed. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-019/__RUN_ID__.json` |
| AC-007 | TC-020 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_acceptance_kit_uses_package_refs_for_skill_scenario_trace -q` | Requirement and acceptance projections consume package AC/test rows. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-020/__RUN_ID__.json` |
| AC-007 | TC-021 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_acceptance_kit_uses_package_refs_for_skill_scenario_trace -q` | Acceptance kit traces package truth/tests instead of old defaults. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-021/__RUN_ID__.json` |
| AC-007 | TC-022 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_gate_qa_release_consume_package_truth -q` | Release scorecard uses package authority model. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-022/__RUN_ID__.json` |
| AC-007 | TC-023 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_status_surface_reports_package_authority -q` | Status reports package truth as authority. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-023/__RUN_ID__.json` |
| AC-008 | TC-024 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_legacy_drift_fails_closed_package_wins -q` | Legacy conflicts are drift, not competing truth. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-024/__RUN_ID__.json` |
| AC-008 | TC-025 | integration | `python3 -m pytest tests/test_v152_package_authoritative.py::test_gate_blocks_when_package_surfaces_are_missing_even_if_legacy_exists -q` | Gate requires package surfaces even when old triptych exists. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-025/__RUN_ID__.json` |

## Test Admission Rules

- v1.5.2 QA must not pass if any normal truth entrypoint still passes only because it is listed as `v1.5.1_legacy_exception`.
- v1.5.2 QA must not pass if package Markdown requires a generated JSON twin to be considered valid.
- v1.5.2 QA must not pass if legacy PRD/user-story/test-case files can satisfy completeness while package surfaces are missing.
- v1.5.2 QA may accept old files on disk only when they are classified as rebuild/absorb/archive artifacts.
