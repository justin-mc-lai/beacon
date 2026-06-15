# Source Architecture Index v1.6.1

## Feature

- `beacon-harness-program-plan-v161`

## Source Surfaces

- `beacon/commands/plan.py`
- `beacon/commands/program.py`
- `beacon/utils/program_plan_state.py`
- `beacon/utils/program_graph.py`
- `beacon/utils/program_freeze_gate.py`
- `beacon/utils/program_plan_runtime.py`
- `skills/beacon/beacon-pln-program{,-auto,-interactive}/SKILL.md`
- `docs/beacon/v1.6.1/execution/program-plan-contract.md`
- `docs/beacon/v1.6.1/features/beacon-harness-program-plan-v161/`

## Architectural Constraint

Program plan is a **planner harness** layered on v1.6.0 truth freeze, TIG, and loop orchestrator. It must not add a new main lifecycle stage.

## Implementation Notes

CLI `beacon plan start` is the single public operator entry; `beacon program validate-graph|guard-sea-single-lake|freeze` enforce graph and gate contracts.
