# Test Cases: Implement Mode Human Playbooks And Routing Contract

**Feature**: `implement-mode-human-playbooks-and-routing-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-IMPL-MODE-001 | contract | `python3 -m pytest -q tests/test_v1410_implement_mode_playbooks.py -k "single_public_implement_entrypoint"` | Skill and agent surfaces expose `beacon-implement` as the only public implementation skill. | `.beacon/evidence/test-results/implement-mode-human-playbooks-and-routing-contract/TC-IMPL-MODE-001.json` |
| AC-002 | TC-IMPL-MODE-002 | contract | `python3 -m pytest -q tests/test_v1410_implement_mode_playbooks.py -k "mode_playbooks_have_required_sections"` | `single`, `team`, and `ralph` playbooks include purpose, admission, command, evidence, and boundary sections. | `.beacon/evidence/test-results/implement-mode-human-playbooks-and-routing-contract/TC-IMPL-MODE-002.json` |
| AC-003 | TC-IMPL-MODE-003 | routing | `python3 -m pytest -q tests/test_v1410_implement_mode_playbooks.py -k "mode_recommendation_rules"` | Help/status recommendations distinguish single, team, and Ralph conditions. | `.beacon/evidence/test-results/implement-mode-human-playbooks-and-routing-contract/TC-IMPL-MODE-003.json` |
| AC-004 | TC-IMPL-MODE-004 | boundary | `python3 -m pytest -q tests/test_v1410_implement_mode_playbooks.py -k "ralph_boundary_is_not_verdict"` | Ralph guidance cannot claim QA pass, release pass, gate pass, or frozen-truth authority. | `.beacon/evidence/test-results/implement-mode-human-playbooks-and-routing-contract/TC-IMPL-MODE-004.json` |
| AC-005 | TC-IMPL-MODE-005 | UX | `python3 -m pytest -q tests/test_v1410_implement_mode_playbooks.py -k "recommendation_includes_reason_and_command"` | Mode recommendations include reason text and canonical `beacon implement run ... --mode <mode>` command. | `.beacon/evidence/test-results/implement-mode-human-playbooks-and-routing-contract/TC-IMPL-MODE-005.json` |
| AC-006 | TC-IMPL-MODE-006 | eval | `python3 -m pytest -q tests/test_v1410_implement_mode_playbooks.py -k "skill_eval_route_stability_cases"` | Skill Eval Kit contains route-stability cases for normal implementation, team/subagent, and Ralph closure prompts. | `.beacon/evidence/test-results/implement-mode-human-playbooks-and-routing-contract/TC-IMPL-MODE-006.json` |
| AC-007 | TC-IMPL-MODE-007 | fail-closed | `python3 -m pytest -q tests/test_v1410_implement_mode_playbooks.py -k "nonexistent_mode_public_skills_fail_closed"` | Public routes to `beacon-implement-single`, `beacon-implement-team`, or `beacon-implement-ralph` fail closed or redirect to `beacon-implement` with mode explanation. | `.beacon/evidence/test-results/implement-mode-human-playbooks-and-routing-contract/TC-IMPL-MODE-007.json` |
| AC-008 | TC-IMPL-MODE-008 | authority | `python3 -m pytest -q tests/test_v1410_implement_mode_playbooks.py -k "mode_playbooks_preserve_truth_boundaries"` | Mode playbooks cannot modify PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict. | `.beacon/evidence/test-results/implement-mode-human-playbooks-and-routing-contract/TC-IMPL-MODE-008.json` |

## Explicit Non Coverage

- These tests do not execute implementation, QA, release, Ralph repair, or gate pass.
- These tests do not create public mode-specific skills.
- These tests do not implement full Ralph Task Loop checkpoint/recovery.
- These tests do not inject project skills through `beacon learn`.
