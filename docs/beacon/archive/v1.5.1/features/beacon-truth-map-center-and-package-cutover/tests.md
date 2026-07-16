# Tests: Beacon Truth Map Center and Package Cutover

| AC ID | TC ID | Layer | Planned Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-001 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_resolver_contract -q` | Resolver APIs and constants exist. |
| AC-002 | TC-002 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_json_is_projection_only -q` | JSON projection cannot be treated as authority. |
| AC-003 | TC-003 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_feature_package_canonical_ready_contract -q` | Package Markdown exposes v2 contract markers. |
| AC-004 | TC-004 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_static_contract_constants -q` | Static contract constants are stable. |
| AC-005 | TC-005 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_new_truth_consumers_use_resolver -q` | New truth consumers route through resolver. |
| AC-006 | TC-006 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_skill_guidance_points_to_truth_map_first -q` | Skills require truth-map-first reading. |
| AC-007 | TC-007 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_md_truth_does_not_require_json_twin -q` | Missing JSON twin does not fail canonical Markdown truth. |
| AC-008 | TC-008 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_doctor_rebuild_route_declared -q` | Doctor rebuild route exists or fails closed. |
| AC-009 | TC-009 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_change_absorb_route_declared -q` | Change absorb route exists or fails closed. |
| AC-010 | TC-010 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_verify_detects_drift -q` | Verify detects resolver/package/rebuild drift. |
| AC-011 | TC-011 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_rebuilds_requirement_machine_json -q` | Rebuild generates requirement-derived `.machine` JSON from resolver-selected Markdown. |
| AC-012 | TC-012 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_machine_json_role_labels_are_not_truth -q` | Generated machine JSON carries generated-state role labels and is not accepted as authority. |
| AC-013 | TC-013 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_machine_json_source_hash_freshness -q` | Source paths, resolver contract, and source hashes are recorded and verified. |
| AC-014 | TC-014 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_runtime_json_is_exempt_from_markdown_twin_requirement -q` | Runtime/process JSON is allowed without Markdown twins and cannot become requirement authority. |
| AC-015 | TC-015 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_stale_machine_json_fails_closed -q` | Stale, non-resolver, or source-hash mismatched `.machine` JSON fails verify. |
| AC-016 | TC-016 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_version_governance_resolver_contract -q` | Resolver exposes version governance truth resolution. |
| AC-017 | TC-017 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_governance_authority_classification -q` | Resolver classifies feature truth, governance truth, generated state, and runtime records. |
| AC-018 | TC-018 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_manifest_index_is_not_truth_authority -q` | Manifest/index/cache JSON cannot be used as truth authority. |
| AC-019 | TC-019 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_material_audit_reads_resolver_first -q` | Material audit asks resolver before manifest or legacy paths. |
| AC-020 | TC-020 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_qa_release_status_read_resolver_first -q` | QA, release, and status readers use resolver-first governance routes. |
| AC-021 | TC-021 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_governance_drift_fails_closed -q` | Missing governance truth or drifted generated governance state fails closed. |
| AC-022 | TC-022 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_feature_package_does_not_contain_version_governance -q` | Feature package is not overloaded with version governance materials. |
| AC-023 | TC-023 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_generated_governance_state_labels -q` | Generated governance state carries non-authority labels or equivalent declarations. |
| AC-024 | TC-024 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_implement_version_governance_preflight_blocks_metadata_branch_drift -q` | Implement plan/dev-run fail closed before execution when metadata branch truth and git workflow projection drift. |
| AC-025 | TC-025 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_center_integration_sweep_policy_boundary -q` | Normal truth read/write/gate/rebuild/absorb entrypoint APIs route through truth_center while v1.5.1 keeps authority in ready state. |
| AC-026 | TC-026 | static-contract | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_center_entrypoint_inventory_covers_high_risk_surfaces -q` | High-risk command, utility, packaged skill, and `.agents/skills` truth entrypoints are inventoried and classified as resolver/truth_center-routed or explicit v1.5.1 exceptions. |
