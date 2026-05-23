# QA Test Cases: Rules Encyclopedia Admin Closure

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-RPQA-001 | contract | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "import_evidence_marker_written"` | marker written | `.beacon/evidence/test-results/rules-encyclopedia-admin-closure/TC-RPQA-001.json` |
| AC-002 | TC-RPQA-002 | regression | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "markdown_matrix_compiles_without_fallback"` | markdown matrix only | `.beacon/evidence/test-results/rules-encyclopedia-admin-closure/TC-RPQA-002.json` |
| AC-003 | TC-RPQA-003 | integration | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "go_uniapp_runner_profile"` | Go + UniApp runner profile | `.beacon/evidence/test-results/rules-encyclopedia-admin-closure/TC-RPQA-003.json` |
| AC-004 | TC-RPQA-004 | contract | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "admission_blocker_taxonomy"` | blocker taxonomy | `.beacon/evidence/test-results/rules-encyclopedia-admin-closure/TC-RPQA-004.json` |
| AC-005 | TC-RPQA-005 | regression | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "bmtop_fixture_prevents_false_closure"` | fixture preserved | `.beacon/evidence/test-results/rules-encyclopedia-admin-closure/TC-RPQA-005.json` |
