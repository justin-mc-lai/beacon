# Change: beacon-v2-goal-durable-longrun

- version: v2.0.0
- kind: post-freeze revision R3 (steering distill) + original lake
- date: 2026-07-19
- intent: durable longrun AgentDriver + Codex Goal steering distill into Loom inject contract

## R1/R2 Scope (retained)

- AgentDriver auto-requeue
- `--longrun` on same public entry
- parity with v1.6.7 durable supervisor
- budget halt, verifier, human release

## R3 Scope (2026-07-19 user GO 1A/2A/3A/4A)

- Distill Codex `continuation.md` / `budget_limit.md` / `objective_updated.md`
- InjectBundle: steering → resume-pack digest → next_action
- Complete path: completion audit → awaiting_verifier only (no self-complete)
- Assets: `docs/beacon/v2.0.0/fixtures/steering/*`, `skills/beacon/references/goal-steering/MUST_SECTIONS.md`
- Detail: `docs/beacon/v2.0.0/change/beacon-v2-goal-durable-longrun-steering-r3.md`

## Downstream

refreeze → axis generate/validate → implement TASK-V2-ST-* → QA → release (human)
