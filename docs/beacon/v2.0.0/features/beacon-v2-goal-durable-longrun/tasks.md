---
slug: beacon-v2-goal-durable-longrun
version: v2.0.0
status: frozen
revision_id: R3
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md
---

# Tasks: v2 Goal Durable Long-Run (R3)

## R2 shipped (retained)

- [x] TASK-V2-DLR-01 Durable supervisor parity hooks
- [x] TASK-V2-DLR-02 AgentDriver requeue loop + --longrun CLI
- [x] TASK-V2-DLR-03 resume-pack digest injection into host agent turns
- [x] TASK-V2-DLR-04 Contract tests test_v200_goal_durable_longrun.py (DLR core)

## R3 — Codex steering distill (open until implement evidence)

- [x] TASK-V2-ST-01 Wire InjectBundle order in AgentDriver / render_turn_prompt
- [x] TASK-V2-ST-02 Load fixtures/steering templates; forbid private shortening of MUST sections
- [x] TASK-V2-ST-03 halt_budget → budget_limit inject
- [x] TASK-V2-ST-04 objective edit event → objective_updated inject
- [x] TASK-V2-ST-05 GoalTurnCounter for blocked audit (≥3)
- [x] TASK-V2-ST-06 Add TC-V2-ST-* tests in test_v200_goal_durable_longrun.py
- [x] TASK-V2-ST-07 Update beacon-goal / loom-goal skill longrun section to mention steering
- [x] TASK-V2-ST-08 Regenerate GoalRun main axis after freeze; validate

## Notes

- Implementation must not claim complete without evaluator.
- Source templates under `docs/beacon/v2.0.0/fixtures/steering/` are contract authority for wording.
