---
slug: beacon-v2-goal-durable-longrun
version: v2.0.0
status: support_advisory
authority: beacon-gen-change
promotion_ref: "user:2026-07-18 one-shot agent longrun + v2 requirements"
upstream: docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md
---

# Research: v2 Goal Durable Long-Run (one-shot agent)

## architecture

```text
User: $beacon-goal / beacon goal run --longrun
        │
        ▼
┌─────────────────── Operator Spine (Rust, v2) ───────────────────┐
│  GoalRun ledger (sqlite ~/.beacon/beacon.db)                      │
│  DurableSupervisor (opt-in or --longrun attaches for this run)  │
│  AgentDriver: spawn/resume host agent turns until terminal      │
│  Workers: ralph implement | qa run | design stage               │
│  Disk: execution.jsonl + checkpoint + resume-pack digest        │
└─────────────────────────────────────────────────────────────────┘
        │ host may die
        ▼
Resume: read checkpoint → inject digest → new agent turn → continue
```

- v1.6.7 parity: heartbeat 120s default, append-only log, host_interrupt ≠ stage_blocked, verifier complete, human release.
- v2 delta: **AgentDriver** owned by Rust orchestrator so "one command" can re-enter agent turns without user typing「继续」each time (still not a silent fake-complete daemon).

## business flow

1. User one-shot: `beacon goal run "..." --longrun` (or skill `$beacon-goal` with longrun flag).
2. Orchestrator creates GoalRun; `--longrun` attaches SupervisorSession for this run only.
3. Driver selects next_action from stage + checkpoint; spawns/resumes agent turn with **digest-only** context.
4. Every ≤120s (or substep): heartbeat + execution.jsonl append.
5. Host turn ends / context full → host_interrupted + checkpoint; Driver **auto-requeues** next turn unless blocked≥3 or awaiting human release.
6. QA workers via tick --execute / driver; complete only with verifier refs.
7. release_pending always human.

Illegal: auto-complete without verifier; overwrite logs; FTS as pass authority; second public entry skill.

## state machine

GoalRun: created → running → stage_active → host_interrupted|stage_blocked → awaiting_verifier → completed|blocked|release_pending  
SupervisorSession: detached → active → polling → waiting_host|stopped  
AgentDriver: idle → turn_active → turn_ended → requeue|halt

## three-piece map / version projection truth bindings

prd_refs: `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md`
user_story_refs: `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md`
test_case_refs: `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/tests.md`
coverage_notes: AC-V2-DLR-001..016 + legal/illegal walks; parity with v1.6.7 durable supervisor.
out_of_scope_notes: silent fake complete; multi-tenant SaaS fleet; zvec as orchestrator core.
