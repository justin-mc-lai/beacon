# Change: beacon-loop-goal-v166 R7 Intent-Aware Continuation

**Version**: `v1.6.7`
**Feature**: `beacon-loop-goal-v166`
**Revision**: `R7`
**Status**: `draft`
**Promotion ref**: `friction:2e306f7acea7`

## Intent

Extend frozen v1.6.6 R6 loop-goal with intent-aware continuation, topology_gate consumption, dual runtime (CLI + host skill), and v2 schema parity—without weakening release human gate or harness boundaries.

## Accepted Change

- Add `IntentContext.v1`, `record_intent_fork`, `decision_cache`, interrupt vs blocked semantics
- Add `beacon loop-goal run` CLI sharing state with host skill
- Add resume utterance short-map (`继续|continue|resume|go`)
- Consume `GitScopeGraph` / `topology_gate_status` in standard_execution_precheck (depends on `beacon-git-scope-graph-v167`)
- Add AC-031..AC-040; retain AC-001..AC-030 from R6 lineage
- Resilient stop: every stop emits `reason_code` + `resume_action`

## Affected Surfaces

- `docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/{truth,tests,tasks,evidence}.md`
- `beacon/utils/loop_goal_state.py`
- `beacon/commands/status.py` + new `beacon loop-goal run`
- `skills/beacon/beacon-loop-goal/SKILL.md`
- `tests/test_v167_loop_goal.py`
- `docs/beacon/v2.0.0/` parity fixture references

## Downstream Route

- Implement after `beacon-git-scope-graph-v167` freeze
- `beacon-eval-qa` / `beacon-eval-release`
