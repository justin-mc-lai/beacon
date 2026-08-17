# GoalRun Main Axis — beacon-friction-closeout-v168

- **version**: `v1.6.8`
- **program**: `beacon-friction-closeout-v168`
- **generated_at**: 2026-07-19T10:42:30.802877+00:00
- **policy**: UD-AXIS-001..005 + UD-FC-001..006
- **parent**: `beacon-prod-ops-hardening-v168`

## User intent

降低日常摩擦：安装真相可信 → longrun 默认兑现 → 热修门可减负 → implement 按业务状态机顺序。  
一句话 goal → 按业务序实现 → verifier 验收 → 人工 release。

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

## Mount table

| Lake | Mount | Role |
|------|-------|------|
| `beacon-runtime-install-truth-v168` | install truth | CLI/version-truth/git diagnose + pin |
| `beacon-longrun-contract-align-v168` | longrun contract | longrun_default matches code |
| `beacon-release-profile-wiring-v168` | release profile | full/hotfix drives release check |
| `beacon-fsm-implement-order-v168` | implement order | entity precedence admission |

## done_when

Default domain-bearing:

- `domain_fsm`
- `domain_fsm_coverage`
- `evidence_chain`
- `continuous_qa`

If `ux_required`: also `design_baseline`, `design_md_lint`.

本 program 四湖额外：

- 合同测绿
- `beacon goal axis validate -v v1.6.8 --program beacon-friction-closeout-v168` pass

## Illegal transitions

| ID | Illegal |
|----|---------|
| I-AXIS-001 | any → completed without verifier |
| I-AXIS-002 | host_interrupted → completed |
| I-AXIS-003 | stage_blocked → completed without clear |
| I-AXIS-004 | auto release_confirmed |
| I-AXIS-005 | submachine → completed |
| I-FC-001 | implement 推进下游实体而前置未 verified（domain_required） |
| I-FC-002 | release check 忽略 profile 仍宣称 hotfix 减负 |
| I-FC-003 | longrun_default=true 但 facade 静默 longrun=false（无 CLI opt-out） |

### Submachines cannot complete GoalRun

- `SupervisorSession`
- `AgentDriver`
- `SubagentSession`
- `RalphDelegate`
- `DesignStage`

## Wave (implementation order)

```text
Wave 0  beacon-runtime-install-truth-v168
Wave 1  beacon-longrun-contract-align-v168
Wave 2  beacon-release-profile-wiring-v168
Wave 3  beacon-fsm-implement-order-v168
```

## First-principles exit checklist (Q1–Q6)

| # | Question |
|---|----------|
| Q1 | 用户成功是否可观测？（diagnose-runtime / longrun doctor / profile release / FSM block reason） |
| Q2 | 是否存在非法 complete/release 捷径？ |
| Q3 | domain-bearing 是否有实体前置+合法 walk？ |
| Q4 | 本 change 是否映射到主轴边/守卫？ |
| Q5 | 实现 Wave 是否依赖未完成 L2/L0？ |
| Q6 | 子机是否可能绕过 awaiting_verifier？ |

## Refreeze note

After regenerating this axis for a triggered change, run:

```bash
beacon goal axis validate -v v1.6.8 --program beacon-friction-closeout-v168
```
