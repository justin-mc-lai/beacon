# GoalRun Main Axis — beacon-product-goal-domain-delivery-v167

- **version**: `v1.6.7`
- **program**: `beacon-product-goal-domain-delivery-v167`
- **generated_at**: 2026-07-18T08:38:10.901489+00:00
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
| `beacon-domain-fsm-authority-v167` | truth hard gate | L2 business FSM |
| `beacon-golden-commerce-fixture-v167` | truth/qa fixture | negative clamps |
| `beacon-domain-fsm-qa-gate-v167` | qa hard gate | legal/illegal |
| `beacon-product-goal-runtime-v167` | main axis owner | facade + stages |
| `beacon-ui-design-ship-gate-v167` | design/ship | UX matrix when ux_required |
| `beacon-loop-discover-goal-finish-v167` | support only | discovery queue |
| `beacon-ralph-implement-boundary-v167` | implement delegate | no verdict write |
| `beacon-goal-durable-supervisor-v167` | longrun bypass | SupervisorSession |
| `beacon-goal-agent-driver-v167` | longrun bypass | AgentDriver |
| `beacon-goalrun-main-axis-v167` | axis governance | regenerate on change |

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
Wave 1   domain-fsm-authority → golden → domain-fsm-qa-gate → ui-ship
Wave 1b  product-goal-runtime (axis owner) + ralph-boundary
Wave 2   loop-discover (support)
Wave 3   durable-supervisor → agent-driver
Wave 4   axis validate on change/freeze
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
beacon change "<feature>" --project . --version v1.6.7 --refreeze-chain
# or $beacon-gen-refreeze
```

Do not implement against stale axis.

## Shared with v2.0.0

State names in GoalRun are shared with v2.0.0 / Loom program axis (UD-AXIS-003).
