# Test Cases: QA Evidence Attribution Layer

**Feature**: `qa-evidence-attribution-layer`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-25`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-QA-ATTR-001 | taxonomy | `python3 -m pytest -q tests/test_v1410_qa_evidence_attribution.py -k "finite_failure_taxonomy"` | Attribution accepts only the supported failure families and rejects unknown families. | `.beacon/evidence/test-results/qa-evidence-attribution-layer/TC-QA-ATTR-001.json` |
| AC-002 | TC-QA-ATTR-002 | contract | `python3 -m pytest -q tests/test_v1410_qa_evidence_attribution.py -k "non_runner_attribution_requires_ac_and_evidence"` | Non-runner attribution requires non-empty affected AC IDs and current evidence refs. | `.beacon/evidence/test-results/qa-evidence-attribution-layer/TC-QA-ATTR-002.json` |
| AC-002 | TC-QA-ATTR-003 | blocked-admission | `python3 -m pytest -q tests/test_v1410_qa_evidence_attribution.py -k "runner_blocker_can_precede_ac_evaluation"` | Runner admission blockers may omit AC IDs only when AC evaluation was not reached and blocker evidence is present. | `.beacon/evidence/test-results/qa-evidence-attribution-layer/TC-QA-ATTR-003.json` |
| AC-003 | TC-QA-ATTR-004 | routing | `python3 -m pytest -q tests/test_v1410_qa_evidence_attribution.py -k "failure_family_route_matrix"` | Each failure family maps to the deterministic route recommendation defined by the PRD. | `.beacon/evidence/test-results/qa-evidence-attribution-layer/TC-QA-ATTR-004.json` |
| AC-004 | TC-QA-ATTR-005 | fail-closed | `python3 -m pytest -q tests/test_v1410_qa_evidence_attribution.py -k "ambiguous_or_missing_evidence_fails_closed"` | Ambiguous or missing evidence cannot pass and is classified as insufficient evidence unless a more specific blocker is proven. | `.beacon/evidence/test-results/qa-evidence-attribution-layer/TC-QA-ATTR-005.json` |
| AC-005 | TC-QA-ATTR-006 | skill-boundary | `python3 -m pytest -q tests/test_v1410_qa_evidence_attribution.py -k "skill_defect_is_proposal_only"` | Skill defect attribution produces research/change proposal input and does not modify skill files or requirement truth. | `.beacon/evidence/test-results/qa-evidence-attribution-layer/TC-QA-ATTR-006.json` |
| AC-006 | TC-QA-ATTR-007 | authority | `python3 -m pytest -q tests/test_v1410_qa_evidence_attribution.py -k "attribution_cannot_claim_truth_or_verdict_authority"` | Attribution fails closed if it claims canonical truth, QA verdict, release verdict, gate verdict, or freeze authority. | `.beacon/evidence/test-results/qa-evidence-attribution-layer/TC-QA-ATTR-007.json` |
| AC-007 | TC-QA-ATTR-008 | release-boundary | `python3 -m pytest -q tests/test_v1410_qa_evidence_attribution.py -k "release_consumes_only_formal_qa_closure"` | Release readiness may summarize attribution only through formal QA closure and never treats raw attribution as pass evidence. | `.beacon/evidence/test-results/qa-evidence-attribution-layer/TC-QA-ATTR-008.json` |

## Explicit Non Coverage

- These tests do not replace formal `beacon qa`.
- These tests do not produce release pass/fail verdicts.
- These tests do not execute hidden hooks or side-effect automation.
- These tests do not implement automatic SkillEvolver-style skill mutation.
- These tests do not implement Ralph long-task control or project skill injection.
