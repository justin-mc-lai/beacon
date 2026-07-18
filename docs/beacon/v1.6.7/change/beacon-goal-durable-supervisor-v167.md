# Change: beacon-goal-durable-supervisor-v167

- **version**: v1.6.7
- **feature**: `beacon-goal-durable-supervisor-v167`
- **kind**: new lake (additive to product-goal-runtime)
- **status**: change_open → freeze R1
- **authority**: beacon-gen-change
- **date**: 2026-07-18

## Why

Product Goal 当前是 **facade 账本**：`tick` 只改 stage，implement/QA 靠宿主 agent 会话。会话中断 / 上下文满 / 数小时无 history 导致「goal 中断」体验。需 **opt-in durable supervisor + 执行日志 + checkpoint resume + tick --execute**。

## User-locked decisions

1. Supervisor：**opt-in** `beacon goal supervise`
2. Heartbeat：**默认 2 分钟（120s）**
3. P2 memory：**sqlite FTS first**（zvec 非 P0）

## Scope in

- GoalRun durable FSM + SupervisorSession FSM
- execution.jsonl + checkpoint + resume-pack
- stall / host_interrupted semantics
- tick --execute worker dispatch (qa/ralph)
- skill docs for continue/resume
- contract tests AC-DGS-001..014

## Scope out

- default background daemon
- zvec required dependency
- auto release human gate
- second public entry skill
- multi-tenant orchestration SaaS

## Downstream

```text
freeze package
  → beacon-gen-implement
  → beacon-eval-qa (contract)
  → release human gate
```

## Files

- `docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/{truth,tests,tasks,evidence}.md`
- `docs/beacon/v1.6.7/prd|user-story|qa/test-cases/...`
- research (already): `.../research/beacon-goal-durable-supervisor-v167-planner-review.md`
