# Test Cases: beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract

## Overview

**Feature**: `beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract`  
**Version**: `v1.4.7`  
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-AUTO47B-001 | contract | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "qa_can_route_to_support_review_with_executor_metadata"` | QA can emit `support_review` as next route and runtime records executor/reason metadata |
| AC-002 | TC-AUTO47B-002 | integration | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "support_review_outcome_can_route_back_to_implement_without_truth_delta"` | support-review/deep can conclude implementation-only defect and route back to `implement` with bounded deep-exit signal |
| AC-003 | TC-AUTO47B-003 | integration | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "support_review_outcome_can_route_to_change_refreeze_on_requirement_meaning_delta"` | support-review/deep can conclude requirement-meaning pressure and route to `change_refreeze` |
| AC-004 | TC-AUTO47B-004 | boundary | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "truth_recompile_barrier_is_written_and_can_be_cleared"` | runtime can write and clear `truth_recompiled_pending` plus explicit truth-recompile targets |
| AC-005 | TC-AUTO47B-005 | gate | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "implement_preflight_blocks_on_support_review_truth_refreeze_and_truth_recompile_barriers"` | `implement` preflight fail-closes while support review, truth refreeze, or truth recompile barriers are still active |
| AC-006 | TC-AUTO47B-006 | contract | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "scenario_discovery_is_split_between_closure_supplement_and_promotion_candidate"` | scenario discovery is classified into `closure_supplement` vs `promotion_candidate` with explicit truth-pressure flags |
| AC-007 | TC-AUTO47B-007 | runtime | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "promotion_candidate_does_not_block_release_route_but_is_retained_in_runtime_sink"` | pure promotion candidates do not force current closure reopen and remain in a non-canonical runtime sink |
| AC-008 | TC-AUTO47B-008 | proof | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "promotion_grade_proof_hooks_reflect_acceptance_and_real_project_evidence"` | promotion-proof projection exposes acceptance-kit / real-project proof strength and missing hooks |
| AC-009 | TC-AUTO47B-009 | regression | `python3 -m pytest -q tests/test_v147_automation_support_review_and_promotion_contract.py -k "second_slice_preserves_support_plane_boundary"` | second-slice runtime still blocks truth mutation and does not claim autonomous lifecycle ownership |

## Coverage Focus

This feature's coverage must explicitly include:

- `support_review` routing
- bounded `deep` exit signals
- `change_refreeze` route contract
- `truth_recompiled_pending`
- truth-recompile target list
- scenario discovery classification
- promotion proof hooks
- implement fail-closed preflight

## Required Scenario Families

1. QA routes to support-review
2. support-review routes back to implement with no truth delta
3. support-review routes to change-refreeze with requirement-meaning delta
4. truth refreeze barrier blocks implement until cleared
5. promotion candidate remains non-canonical and non-blocking
6. promotion proof hooks surface evidence strength

## Boundary and Negative Coverage

- automation must not auto-execute `change/refreeze`
- automation must not write canonical requirement truth
- promotion candidate must not silently become current closure truth
- proof hooks must not be treated as release verdict replacement

## QA Execution Snapshot

- QA date: `2026-05-15`
- Verified command:
  - `python3 -m pytest -q tests/test_v147_bounded_automation_closure_state_kernel.py tests/test_v147_automation_support_review_and_promotion_contract.py`
- Result:
  - `19 passed`
- QA verdict:
  - `pass_for_planning_line`

## Findings

- QA can now emit `support_review` route intent with explicit executor metadata
- support-review / deep outcome now separates implementation-only defects from requirement-meaning pressure
- `truth_recompiled_pending` now behaves as a hard barrier rather than advisory note
- scenario discovery now distinguishes `closure_supplement` from `promotion_candidate`
- implement preflight now rejects execution when automation truth barriers remain active
