# Change: beacon-loop-goal-v166 Public Skill Release Shape

**Version**: `v1.6.6`
**Feature**: `beacon-loop-goal-v166`
**Revision**: `R2`
**Status**: `frozen`
**Scope**: narrow requirement change

## Intent

Freeze `beacon-loop-goal` as a public host-visible governor skill.

## Accepted Change

- `beacon-loop-goal` is a public host-visible skill, not an internal-only reference surface.
- It remains governor harness: route, state, metadata, and diagnostic support only.
- It is a v1.6 taxonomy exception to the `beacon-(pln|gen|eval|gov)-*` naming pattern and is classified as governor.
- Agent surface setup/verify must include it in the expected public skill list.
- Skill inventory and release governance counts become 38 public host-visible skills: planner(7), generator(11), evaluator(5), governor(15).
- `beacon-loop-goal` orchestrates the other 37 public skills and must not self-orchestrate.

## Affected Requirement Surfaces

- `docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/truth.md`
- `docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/tests.md`
- `docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/tasks.md`
- `docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/evidence.md`

## Downstream Route

- `beacon-gen-implement v1.6.6` to update packaged skill source, agent surface taxonomy, skill inventory, and release governance tests.
- `beacon-eval-qa v1.6.6` to judge evidence after implementation.
- `beacon-eval-release v1.6.6` remains a separate evaluator step.
