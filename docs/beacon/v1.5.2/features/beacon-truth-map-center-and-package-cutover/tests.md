# Tests: Feature Package Authoritative Cutover

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

