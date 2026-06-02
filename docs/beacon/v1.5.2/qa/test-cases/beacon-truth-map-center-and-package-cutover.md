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

