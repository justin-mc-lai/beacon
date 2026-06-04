# Test Cases: QA Evo Deep And Skill Eval Kit v1.4.10

**Feature**: `qa-evo-deep-and-skill-eval-kit-v1410`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-QAED-001 | contract | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "qa_evo_deep_output_contract"` | QA evo-deep findings include source refs, finding type, risk, affected ACs, route recommendation, blocked admissions, and release supplement input. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-QAED-001.json` |
| AC-002 | TC-QAED-002 | contract | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "round_memory_is_advisory_influence"` | Prior QA round memory is labeled as influence and is not counted as current pass evidence. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-QAED-002.json` |
| AC-003 | TC-QAED-003 | contract | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "deep_finding_taxonomy_supported"` | QA evo-deep supports state-machine, business-flow, scenario-combination, permission-boundary, data-source-consistency, cross-surface-closure, and repeated-failure finding families. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-QAED-003.json` |
| AC-004 | TC-QAED-004 | topology | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "qa_evo_deep_write_topology"` | QA evo-deep detailed output writes to `docs/beacon/<version>/qa/evo-deep/<feature>.md` and research stores only an index or design summary. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-QAED-004.json` |
| AC-005 | TC-SKEV-001 | contract | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "skill_eval_case_schema"` | Skill Eval Kit cases include id, prompt, expected route, boundary expectations, source anchors, tags, split, expected evidence, and scoring dimensions. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-SKEV-001.json` |
| AC-006 | TC-SKEV-002 | contract | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "skill_eval_splits_and_regression_core"` | Skill Eval Kit defines optimization and holdout splits plus a small regression core. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-SKEV-002.json` |
| AC-007 | TC-SKEV-003 | boundary | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "skill_eval_outputs_are_evidence_only"` | Skill Eval Kit run outputs are stored as runtime or machine evidence and do not become requirement truth. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-SKEV-003.json` |
| AC-008 | TC-SKEV-004 | routing | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "route_stability_cases_cover_support_and_implement_modes"` | Route-stability cases cover ordinary support skills, `beacon-deep`, `beacon-learn`, and `beacon-implement --mode single/team/ralph`. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-SKEV-004.json` |
| AC-009 | TC-QAED-005 | gate | `python3 -m pytest -q tests/test_v1410_qa_evo_deep_skill_eval.py -k "authority_bypass_fails_closed"` | Requirement clarity or release readiness fails closed when QA evo-deep or Skill Eval output claims PRD, user-story, test-case, QA verdict, release verdict, or freeze authority. | `.beacon/evidence/test-results/qa-evo-deep-and-skill-eval-kit-v1410/TC-QAED-005.json` |

## Explicit Non Coverage

- These tests do not execute implementation, QA, release, project hooks, or Ralph long-task control.
- These tests do not promote QA evo-deep findings or Skill Eval outputs into canonical requirement truth.
- These tests do not create public `beacon-implement-single`, `beacon-implement-team`, or `beacon-implement-ralph` skills.
