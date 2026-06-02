# Test Cases: Beacon Truth Map Center and Package Cutover

- version: `v1.5.1`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
|---|---|---|---|---|---|
| AC-001 | TC-001 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_resolver_contract -q` | Resolver APIs and constants exist. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-001/__RUN_ID__.json` |
| AC-002 | TC-002 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_json_is_projection_only -q` | JSON projection cannot be treated as authority. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-002/__RUN_ID__.json` |
| AC-003 | TC-003 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_feature_package_canonical_ready_contract -q` | Package Markdown exposes v2 contract markers. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-003/__RUN_ID__.json` |
| AC-004 | TC-004 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_static_contract_constants -q` | Static contract constants are stable. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-004/__RUN_ID__.json` |
| AC-005 | TC-005 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_new_truth_consumers_use_resolver -q` | New truth consumers route through resolver. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-005/__RUN_ID__.json` |
| AC-006 | TC-006 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_skill_guidance_points_to_truth_map_first -q` | Skills require truth-map-first reading. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-006/__RUN_ID__.json` |
| AC-007 | TC-007 | unit | `python3 -m pytest tests/test_v151_truth_map.py::test_md_truth_does_not_require_json_twin -q` | Missing JSON twin does not fail canonical Markdown truth. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-007/__RUN_ID__.json` |
| AC-008 | TC-008 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_doctor_rebuild_route_declared -q` | Doctor rebuild route exists or fails closed with explicit unsupported reason. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-008/__RUN_ID__.json` |
| AC-009 | TC-009 | contract | `python3 -m pytest tests/test_v151_truth_map.py::test_change_absorb_route_declared -q` | Change absorb route exists or fails closed with explicit unsupported reason. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-009/__RUN_ID__.json` |
| AC-010 | TC-010 | integration | `python3 -m pytest tests/test_v151_truth_map.py::test_truth_map_verify_detects_drift -q` | Verify detects resolver/package/rebuild drift. | `.beacon/evidence/qa-feature/beacon-truth-map-center-and-package-cutover/tc-010/__RUN_ID__.json` |

