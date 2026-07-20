# Change: beacon-v2-goal-durable-longrun R3 — Loom Steering distill

- version: v2.0.0
- feature: beacon-v2-goal-durable-longrun
- kind: post-freeze requirement revision
- date: 2026-07-19
- revision: R2 → R3
- program: beacon-v2-product-goal-parallel-v200
- user_decisions: 1A hang durable-longrun; 2A objective_updated Must; 3A audit→awaiting_verifier; 4A GO change
- advisory: docs/beacon/v2.0.0/research/loom-goal-steering-codex-continuation-pln-review.md

## Intent

把 OpenAI Codex Goal `continuation.md` / `budget_limit.md` / `objective_updated.md` **蒸馏进** Loom/Beacon longrun steering 合同，并写清 InjectBundle、illegal inject、Beacon complete gate。

## Scope in

- UD-V2-ST-001..006
- AC-V2-ST-001..009
- I-V2-ST-001..006
- AgentDriver FSM inject 更新
- fixtures/steering + MUST_SECTIONS
- tests TC-V2-ST-*

## Scope out

- host cron / RecurringJob
- Codex agent update_goal(complete) 权威
- 微信日更产品化

## Surfaces touched

- features/beacon-v2-goal-durable-longrun/{truth,tests,tasks,evidence}.md
- fixtures/steering/*
- skills/beacon/references/goal-steering/*
- change/this file

## Downstream

refreeze-chain → axis generate/validate → implement (TASK-V2-ST-*) → eval-qa

## Complete gate (hard)

completion audit **never** self-completes GoalRun; only `awaiting_verifier` then verifier refs.
