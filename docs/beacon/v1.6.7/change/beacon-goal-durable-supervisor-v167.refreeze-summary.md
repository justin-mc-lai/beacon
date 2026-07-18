# Refreeze summary: beacon-goal-durable-supervisor-v167

- **version**: v1.6.7
- **revision**: R1
- **status**: frozen (2026-07-18)
- **CLI**: `beacon freeze beacon-goal-durable-supervisor-v167 -v v1.6.7` → status=frozen

## Locked user decisions

1. Supervisor: **opt-in** `beacon goal supervise`
2. Heartbeat default: **120 seconds**
3. P2 memory: **sqlite FTS** (zvec not P0)

## Package

- truth / tests / tasks / evidence under `docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/`
- Domain FSM: GoalRun + SupervisorSession (+ machine projection)
- ACs: AC-DGS-001..014; legal walks + illegal TCs
- research: `docs/beacon/v1.6.7/research/beacon-goal-durable-supervisor-v167.md`

## Next route

`beacon-gen-implement` → contract tests → `beacon-eval-qa` → release human gate
