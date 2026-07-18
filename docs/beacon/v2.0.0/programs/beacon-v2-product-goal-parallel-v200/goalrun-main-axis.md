# GoalRun Main Axis — beacon-v2-product-goal-parallel-v200

- **version**: `v2.0.0`
- **program**: `beacon-v2-product-goal-parallel-v200`
- **generated_at**: 2026-07-18T10:38:12.499900+00:00
- **policy**: UD-AXIS-001..005 (change must regenerate this artifact)

## User intent

一句话 goal → 按业务序实现 → verifier 验收 → 人工 release

## GoalRun (main axis states)

```text
created → running → stage_active{plan|truth|design?|implement|qa|release}
              ↻ host_interrupted --resume-pack--> stage_active
              → stage_blocked
         → awaiting_verifier → completed (verifier required)
         → release_pending → release_confirmed (human only)
```

### GoalRun states

- `created`
- `running`
- `stage_active`
- `host_interrupted`
- `stage_blocked`
- `awaiting_verifier`
- `completed`
- `release_pending`
- `release_confirmed`

## Mount table (program lakes on GoalRun)

| Lake | Mount | Role |
|------|-------|------|
| `beacon-v2-product-goal-orchestrator` | main axis owner (v2) | facade + stages; dual-track entry |
| `beacon-v2-main-star-satellite-pool` | implement topology | star/satellite structure |
| `beacon-v2-domain-fsm-authority` | truth hard gate | L2 business FSM |
| `beacon-v2-golden-commerce-fixture-parity` | truth/qa fixture | negative clamps |
| `beacon-v2-domain-fsm-qa-gate` | qa hard gate | legal/illegal + domain_fsm_coverage |
| `beacon-v2-ui-state-matrix-ship-gate` | design/ship | UX matrix when ux_required |
| `beacon-v2-ralph-implement-boundary` | implement delegate | no verdict write |
| `beacon-v2-goal-durable-longrun` | longrun bypass | SupervisorSession + AgentDriver |
| `loom-brand-surface` | L0 install surface | dual-install Loom; no replace beacon |
| `loom-goal-optional-subagent` | implement fan-out execute | SubagentSession opt-in spawn/merge |
| `loom-goal-trace-bundle` | longrun observability | agent_trace + goal trace CLI |
| `beacon-goalrun-main-axis-v167` | axis governance | regenerate on change |
| `beacon-v2-truth-human-readable-i18n` | truth hard gate | L0 human + humanizer zh/en parity |

## done_when

Default domain-bearing:

- `domain_fsm`
- `domain_fsm_coverage`
- `evidence_chain`
- `continuous_qa`

If `ux_required`: also `design_baseline`, `design_md_lint`.

## Illegal transitions

| ID | Illegal |
|----|---------|
| I-AXIS-001 | any → completed without verifier |
| I-AXIS-002 | host_interrupted → completed |
| I-AXIS-003 | stage_blocked → completed without clear |
| I-AXIS-004 | auto release_confirmed |
| I-AXIS-005 | submachine → completed |

### Submachines cannot complete GoalRun

- `SupervisorSession`
- `AgentDriver`
- `SubagentSession`
- `RalphDelegate`
- `DesignStage`

## Wave (implementation order)

```text
Wave 0   loom-brand-surface (L0 dual-install; if present)
Wave 1   domain-fsm-authority → golden → domain-fsm-qa-gate → ui-ship
Wave 1b  product-goal / v2 orchestrator (axis owner) + ralph-boundary
Wave 2   main-star-satellite → loom-goal-optional-subagent (true fan-out)
Wave 3   durable-longrun / agent-driver → loom-goal-trace-bundle
Wave 4   axis validate on change/freeze; rust carrier optional
```

## First-principles exit checklist (Q1–Q6)

| # | Question |
|---|----------|
| Q1 | 用户成功是否可观测？ |
| Q2 | 是否存在非法 complete/release 捷径？ |
| Q3 | domain-bearing 是否有实体前置+合法 walk？ |
| Q4 | 本 change 是否映射到主轴边/守卫？ |
| Q5 | 实现 Wave 是否依赖未完成 L2/L0？ |
| Q6 | 子机是否可能绕过 awaiting_verifier？ |

## Refreeze note

After regenerating this axis for a triggered change, run:

```text
beacon change "<feature>" --project . --version v2.0.0 --refreeze-chain
# or $beacon-gen-refreeze
```

Do not implement against stale axis.

## Subagent & Trace mounts (when present)

- `loom-goal-optional-subagent` / parallel_plan: **opt-in only**; SubagentSession must not complete GoalRun.
- Spawn path: planned → arming → running → collecting → merging → done|halted.
- `loom-goal-trace-bundle`: AgentDriver turns append `agent_trace.v1` under traces/; `goal trace --run-id` aggregates with execution.jsonl.
- Resume authority remains **resume-pack digest**, not full chat or full trace body.

## Shared with v2.0.0

State names in GoalRun are shared with v2.0.0 / Loom program axis (UD-AXIS-003).
