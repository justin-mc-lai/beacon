# Test Cases: QA Evo Deep Evidence-Bound AC-Aware Closure

**Feature**: `qa-evo-deep-evidence-bound-ac-aware-closure`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-QAED-BIND-001 | source | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "required_source_materials_are_loaded"` | QA evo-deep loads PRD, user-story, test-case, QA scorecard, and AC closure before status `ready`. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-QAED-BIND-001.json` |
| AC-001 | TC-QAED-BIND-002 | fail-closed | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "missing_source_material_blocks_ready_report"` | Missing source material produces `status=blocked` and reason code `qa_evo_deep_source_evidence_missing`. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-QAED-BIND-002.json` |
| AC-002 | TC-QAED-BIND-003 | contract | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "ready_findings_require_ac_and_evidence_refs"` | Ready findings require non-empty `affected_ac_ids` and `current_evidence_refs`. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-QAED-BIND-003.json` |
| AC-003 | TC-QAED-BIND-004 | fail-closed | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "empty_skeleton_findings_fail_closed"` | Skeleton findings without AC/evidence binding fail with `qa_evo_deep_empty_skeleton_finding`. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-QAED-BIND-004.json` |
| AC-003 | TC-QAED-BIND-005 | blocked-admission | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "blocked_admission_can_explain_source_gap"` | Blocked admissions include source refs, reason codes, and route recommendations. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-QAED-BIND-005.json` |
| AC-004 | TC-SKEV-REPLAY-001 | replay | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "skill_eval_replays_route_boundary_and_source_anchor"` | Skill Eval Kit replay traces record expected route, actual route, boundary preservation, source anchor coverage, and pass/fail. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-SKEV-REPLAY-001.json` |
| AC-004 | TC-SKEV-REPLAY-002 | fail-closed | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "skill_eval_replay_failure_blocks_case"` | Route, boundary, or source-anchor replay failure blocks the eval case. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-SKEV-REPLAY-002.json` |
| AC-005 | TC-QA-ABSORB-001 | scorecard | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "qa_scorecard_records_deep_absorption_status"` | QA scorecard records each deep finding as `absorbed`, `deferred`, `blocked`, or `not_applicable`. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-QA-ABSORB-001.json` |
| AC-006 | TC-REL-SUPP-001 | release | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "release_uses_only_absorbed_deep_findings"` | Release supplement treats only formally absorbed deep findings as release supplement input. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-REL-SUPP-001.json` |
| AC-007 | TC-QAED-BIND-006 | boundary | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_evidence_bound.py -k "authority_bypass_still_fails_closed"` | QA evo-deep and Skill Eval outputs fail closed on truth, QA verdict, release verdict, gate verdict, or freeze authority claims. | `.beacon/evidence/test-results/qa-evo-deep-evidence-bound-ac-aware-closure/TC-QAED-BIND-006.json` |

## Explicit Non Coverage

- These tests do not replace formal `beacon qa`.
- These tests do not produce release pass/fail verdicts.
- These tests do not execute browser automation, project hooks, Ralph long-task control, or project skill injection.
