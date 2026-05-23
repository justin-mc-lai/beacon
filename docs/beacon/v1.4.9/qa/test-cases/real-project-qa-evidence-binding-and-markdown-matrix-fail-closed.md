# Test Cases: Real Project QA Evidence Binding and Markdown Matrix Fail-Closed

**Feature**: `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`  
**Version**: `v1.4.9`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-RPQA-001 | contract | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "implementation_evidence_marker_written"` | Implement run or import-evidence writes a QA-readable implementation marker with required source refs. | `.beacon/evidence/test-results/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed/TC-RPQA-001.json` |
| AC-001 | TC-RPQA-002 | regression | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "qa_blocks_when_marker_missing"` | QA blocks as evidence_binding_missing when implementation marker is absent and no import evidence exists. | `.beacon/evidence/test-results/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed/TC-RPQA-002.json` |
| AC-002 | TC-RPQA-003 | contract | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "markdown_matrix_compiles_without_fallback"` | Markdown QA table rows compile into machine AC matrix preserving AC ID, TC ID, command, assertion, and evidence path. | `.beacon/evidence/test-results/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed/TC-RPQA-003.json` |
| AC-002 | TC-RPQA-004 | gate | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "markdown_matrix_parser_fail_closed"` | Parser failure blocks with diagnostics and does not write placeholder acceptance fallback. | `.beacon/evidence/test-results/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed/TC-RPQA-004.json` |
| AC-003 | TC-RPQA-005 | integration | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "go_uniapp_runner_profile"` | QA resolves Go + UniApp backend target, frontend type-check, miniapp build, and route check commands. | `.beacon/evidence/test-results/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed/TC-RPQA-005.json` |
| AC-004 | TC-RPQA-006 | contract | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "admission_blocker_taxonomy"` | QA classifies product/test failures separately from runner, environment, auth, evidence, coverage, and truth projection blockers. | `.beacon/evidence/test-results/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed/TC-RPQA-006.json` |
| AC-005 | TC-RPQA-007 | regression | `python3 -m pytest -q tests/test_v149_real_project_qa_closure.py -k "bmtop_fixture_prevents_false_closure"` | BMTOP fixture prevents implementation marker missing, matrix fallback, runner mismatch, unavailable frontend script, and environment blocker regressions. | `.beacon/evidence/test-results/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed/TC-RPQA-007.json` |

## Regression Fixture Inputs

- `fixtures/bmtop/rules-encyclopedia-admin-closure/prd.md`
- `fixtures/bmtop/rules-encyclopedia-admin-closure/user-story.md`
- `fixtures/bmtop/rules-encyclopedia-admin-closure/qa-test-cases.md`
- `fixtures/bmtop/rules-encyclopedia-admin-closure/implementation-summary.md`
- `fixtures/bmtop/rules-encyclopedia-admin-closure/ac-test-matrix-fallback.json`

## Explicit Non Coverage

- Better Harness Skill Eval Kit is not covered by this P0 matrix.
- `qa-evo-deep` output reporting is not covered by this P0 matrix.
