# Implementation Summary: beacon-loop-goal-v166 R3

## Scope

Implemented the frozen R3 change that makes `review_routing` a public loop-goal decision contract.

## Bound Truth

- `docs/beacon/v1.6.6/features/beacon-loop-goal-v166/truth.md`
- `docs/beacon/v1.6.6/features/beacon-loop-goal-v166/tests.md`
- `docs/beacon/v1.6.6/features/beacon-loop-goal-v166/tasks.md`
- `docs/beacon/v1.6.6/features/beacon-loop-goal-v166/evidence.md`

## Implementation Changes

- Added `review_routing -> beacon-pln-review` to packaged and projected `beacon-loop-goal` public skill decision trees.
- Added planner-review decision packet outputs to `loop_goal_state.init()`.
- Added `record_review_decision()` to consume structured planner-review artifacts and fail closed before implementation when review requires truth/change/refreeze or human decision.
- Added pytest coverage for AC-012..014.

## Evidence Commands

- `beacon doctor verify-truth-integrity beacon-loop-goal-v166 --project-root . --version v1.6.6 --mode block --json`
- `beacon change "beacon-loop-goal-v166" --project . --version v1.6.6 --reason "add review_routing public skill contract, planner-review decision packet state outputs, and fail-closed loop-goal review gate tests" --refreeze-chain`
- `python3 -m pytest tests/test_v166_loop_goal.py -q`

## QA Handoff

R3 implementation is ready for `beacon-eval-qa`. This summary does not assert QA or release verdict.
