# Test Cases: beacon-v1.4.7 change refreeze human skill stable route

## Overview

**Feature**: `beacon-v1.4.7-change-refreeze-human-skill-stable-route`
**Version**: `v1.4.7`
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-CRSK47-001 | contract | `python3 -m pytest -q tests/test_v147_change_refreeze_human_skill_route.py -k "change_refreeze_skill_files_exist"` | both packaged and local agent skill files exist |
| AC-002 | TC-CRSK47-002 | contract | `python3 -m pytest -q tests/test_v147_change_refreeze_human_skill_route.py -k "change_refreeze_skill_declares_refreeze_chain_command"` | skill declares `beacon change ... --refreeze-chain` |
| AC-003 | TC-CRSK47-003 | contract | `python3 -m pytest -q tests/test_v147_change_refreeze_human_skill_route.py -k "change_refreeze_skill_declares_full_closure_chain"` | skill declares `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze` |
| AC-004 | TC-CRSK47-004 | boundary | `python3 -m pytest -q tests/test_v147_change_refreeze_human_skill_route.py -k "change_refreeze_skill_declares_non_stage_non_truth_non_gate"` | skill declares non-stage, non-truth, and non-gate boundaries |
| AC-005 | TC-CRSK47-005 | boundary | `python3 -m pytest -q tests/test_v147_change_refreeze_human_skill_route.py -k "change_refreeze_skill_does_not_execute_delivery_or_direct_truth_writes"` | skill does not claim implement, QA, release, or direct canonical truth writes |
| AC-006 | TC-CRSK47-006 | routing | `python3 -m pytest -q tests/test_v147_change_refreeze_human_skill_route.py -k "change_refreeze_skill_supports_stable_human_matching"` | metadata/body includes stable matching terms for one-shot refreeze intent |
| AC-007 | TC-CRSK47-007 | routing | `python3 -m pytest -q tests/test_v147_change_refreeze_human_skill_route.py -k "deep_and_change_docs_route_to_change_refreeze_skill"` | deep/change docs can route accepted adoption/refreeze intent to `beacon-change-refreeze` |
| AC-008 | TC-CRSK47-008 | regression | `python3 -m pytest -q tests/test_v147_change_refreeze_human_skill_route.py -k "change_refreeze_skill_uses_single_existing_machine_route"` | skill preserves `beacon change ... --refreeze-chain` as the single machine route |

## Required Scenario Families

1. Skill file packaging in `skills/beacon/`
2. Local agent skill packaging in `.agents/skills/`
3. Natural-language route discoverability
4. Non-stage / non-truth / non-gate boundary
5. Deep adoption route handoff
6. Existing refreeze transaction reuse

## Boundary and Negative Coverage

- must not create a new lifecycle stage
- must not introduce a new refreeze implementation
- must not bypass `prd -> user-story -> test-case -> requirement_clarity -> freeze`
- must not execute implementation, QA, or release
- must not write canonical truth directly from the skill

## QA Verification Note

This document defines coverage truth for the implemented package. The executable matrix is backed by `tests/test_v147_change_refreeze_human_skill_route.py`.
