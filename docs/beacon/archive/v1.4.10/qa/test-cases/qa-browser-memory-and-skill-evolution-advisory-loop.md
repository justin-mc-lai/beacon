# Test Cases: QA Browser Memory And Skill Evolution Advisory Loop

**Feature**: `qa-browser-memory-and-skill-evolution-advisory-loop`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-QA-MEM-001 | contract | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "browser_memory_capture_requires_current_browser_evidence"` | Browser memory captures feature, route, host, browser, runner, auth/session mode, AC/test IDs, outcome, and evidence refs from current browser evidence. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-001.json` |
| AC-002 | TC-QA-MEM-002 | fail-closed | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "browser_memory_admission_rejects_non_acceptance_evidence"` | Placeholder-only, listing-only, dry-run, documentation-only, stale, unscoped, or evidence-missing memory candidates are rejected. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-002.json` |
| AC-003 | TC-QA-MEM-003 | integration | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "admitted_memory_is_retrieved_for_matching_qa_context"` | Admitted memory is retrievable for matching feature/host/route/browser/auth/session contexts. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-003.json` |
| AC-004 | TC-QA-MEM-004 | integration | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "memory_influence_guides_runner_session_selector_and_task_hints"` | Retrieved memory can influence runner selection, session bridge recommendation, selector/action hints, repeated failure detection, and browser task compilation. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-004.json` |
| AC-005 | TC-QA-MEM-005 | authority | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "memory_influence_has_no_truth_or_verdict_authority"` | Memory influence is advisory/runtime support evidence only and cannot satisfy QA, release, gate, or frozen truth. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-005.json` |
| AC-006 | TC-QA-MEM-006 | recovery | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "stale_conflicting_or_mismatched_memory_downgrades_or_blocks_reuse"` | Expired, conflicting, host/version/browser/auth mismatched, or protected-surface mismatched memory downgrades or blocks reuse with reason codes. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-006.json` |
| AC-007 | TC-QA-MEM-007 | attribution | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "skill_evolution_classifies_reflection_family"` | Skill evolution classifies trace observations as Discovery, Optimization, SkillDefect, or ExecutionLapse. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-007.json` |
| AC-008 | TC-QA-MEM-008 | skill-boundary | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "skill_evolution_outputs_proposal_only_without_mutation"` | Skill evolution may create proposal artifacts but does not mutate skill, code, or truth files automatically. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-008.json` |
| AC-009 | TC-QA-MEM-009 | traceability | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "skill_evolution_proposal_binds_trace_ac_test_evidence_route_and_risk"` | Each proposal includes trace refs, AC/test IDs, evidence refs, failure family, expected route, and risk. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-009.json` |
| AC-010 | TC-QA-MEM-010 | auditor | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "independent_auditor_blocks_authority_bypass_and_overfit"` | Independent auditor blocks authority bypass, support evidence promoted to verdict, single-project overfitting, missing evidence binding, silent bypass, and lifecycle-stage sprawl. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-010.json` |
| AC-011 | TC-QA-MEM-011 | routing | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "accepted_proposals_route_to_change_refreeze_before_implementation"` | Accepted proposals route to Beacon change/refreeze before implementation; rejected/deferred proposals remain support evidence. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-011.json` |
| AC-012 | TC-QA-MEM-012 | release-boundary | `python3 -m pytest -q tests/test_v1410_qa_browser_memory_skill_evolution.py -k "release_consumes_formal_current_qa_closure_not_memory_or_proposals"` | QA/release scorecards can summarize memory/proposal support evidence, but only formal current-run QA closure can produce release readiness. | `.beacon/evidence/test-results/qa-browser-memory-and-skill-evolution-advisory-loop/TC-QA-MEM-012.json` |

## Explicit Non Coverage

- These tests do not execute hidden browser side effects.
- These tests do not let memory count as current QA evidence.
- These tests do not mutate Beacon skills, code, PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict.
- These tests do not add a new Beacon lifecycle stage.
