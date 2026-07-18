---
slug: beacon-goalrun-main-axis-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: "User GO UD-AXIS-001..005 2026-07-18: change must regenerate GoalRun main axis; embed program lakes; anti-slice"
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-goalrun-main-axis-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-goalrun-main-axis-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-goalrun-main-axis-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-goalrun-main-axis-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
ux_required: false
design_deferral: "Program/CLI governance; no marketing UI"
---

# Requirement Truth: GoalRun Main Axis v1.6.7 (R1)

## Overview

**用户主轴只有一条：GoalRun。**  
program 内所有湖是挂载在主轴上的 **守卫 / 阶段门 / 旁路子机**，不是并列产品线。

凡 **change / refreeze** 触及承诺、验收、阶段、并行、长跑、入口或业务序，必须 **重新生成主轴工件** 后再冻结；禁止只改单湖切片就 implement。

与 v2.0.0 **共用同一套主状态名**（版本只扩子机/载体）。

## User Intent（一行）

change 后重画「一句话→验收」主轴，保证业务状态机自洽、实现有序、不空中阁楼。

## User Decisions（locked — GO 2026-07-18）

| ID | Decision | Value |
|----|----------|-------|
| UD-AXIS-001 | change 触发 | **必须** 主轴重生（触发表见下） |
| UD-AXIS-002 | 主轴工件 | GoalRun 主图 + done_when + 子机挂载表 + 实现 Wave 序 |
| UD-AXIS-003 | 跨版本 | v1.6.7 与 v2.0.0 **同状态名** |
| UD-AXIS-004 | domain-bearing | done_when **必须**含 `domain_fsm_coverage` |
| UD-AXIS-005 | 子机 | 任何子机 **不得** 直接 completed / auto release |

## Domain FSM — GoalRun（program 主轴权威）

| State | From | Guard | Side effects |
|-------|------|-------|--------------|
| created | — | create_goal_run | state file |
| running | created, host_interrupted, stage_blocked(streak<3) | not completed | current_stage |
| stage_active | running | stage in plan,truth,design?,implement,qa,release | progressive skills |
| host_interrupted | stage_active, running | host end or stall | last_substep; resume-pack |
| stage_blocked | stage_active | worker/gate/truth fail | blocked_streak++ |
| awaiting_verifier | work stages done | no verifier refs | wait |
| completed | awaiting_verifier | verifier.present and refs | completed_at |
| release_pending | completed path | release_human_gate | human only |
| release_confirmed | release_pending | **human** | never auto |

### Illegal (GoalRun)

| ID | Illegal |
|----|---------|
| I-AXIS-001 | * to completed without verifier |
| I-AXIS-002 | host_interrupted to completed |
| I-AXIS-003 | stage_blocked to completed without clear |
| I-AXIS-004 | * to release_confirmed auto |
| I-AXIS-005 | Subagent/Driver/Supervisor/Ralph to completed |

## Submachine mount table（v1.6.7 program 湖）

| Lake | Mount on GoalRun | Role |
|------|------------------|------|
| beacon-product-goal-runtime-v167 | **main axis owner** | facade + stages |
| beacon-domain-fsm-authority-v167 | truth hard gate | L2 business FSM |
| beacon-golden-commerce-fixture-v167 | truth/qa fixture | negative clamps |
| beacon-domain-fsm-qa-gate-v167 | qa hard gate | legal/illegal |
| beacon-ui-design-ship-gate-v167 | design/ship | UX matrix when ux_required |
| beacon-ralph-implement-boundary-v167 | implement delegate | no verdict write |
| beacon-loop-discover-goal-finish-v167 | support only | discovery queue |
| beacon-goal-durable-supervisor-v167 | longrun bypass | SupervisorSession |
| beacon-goal-agent-driver-v167 | longrun bypass | AgentDriver |
| (v2+) loom-* | L0 / fan-out / trace | see v2 axis doc |

## Change trigger — main axis regenerate

| Change type | Regenerate? |
|-------------|-------------|
| AC / promise / acceptance | **Yes** |
| stage order / stages | **Yes** |
| parallel / subagent / worktree | **Yes** |
| longrun / driver / supervise | **Yes** |
| public entry / dual install | **Yes** |
| domain FSM / entity precedence | **Yes** |
| typo / tasks checkbox only | No |

## Main-axis artifact（Must）

Canonical path:

```text
docs/beacon/<ver>/programs/<program_slug>/goalrun-main-axis.md
```

Must contain:

1. User intent one-liner (first principles)
2. GoalRun state diagram (this truth)
3. Lake to mount table
4. done_when list (incl. domain_fsm_coverage if domain-bearing)
5. Global illegal transitions
6. Implementation Wave order
7. Diff vs prior axis revision (if any)

Machine projection (non-authoritative):

```text
docs/beacon/<ver>/.machine/goalrun/main-axis.json
```

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-AXIS-001 | artifact | program goalrun-main-axis.md exists and lists GoalRun states (**Must**) |
| AC-AXIS-002 | mount-table | all program lakes appear in mount table (**Must**) |
| AC-AXIS-003 | change-trigger | change touching trigger types requires axis regenerate API/CLI (**Must**) |
| AC-AXIS-004 | fail-closed | validate_main_axis missing required sections blocked (**Must**) |
| AC-AXIS-005 | done-when | domain-bearing default includes domain_fsm_coverage (**Must**) |
| AC-AXIS-006 | no-submachine-complete | contract: submachines cannot complete GoalRun (**Must**) |
| AC-AXIS-007 | wave-order | axis doc includes Wave implementation order (**Must**) |
| AC-AXIS-008 | runtime-sync | regenerate updates machine projection; create_goal_run uses stages/done_when (**Must**) |
| AC-AXIS-009 | first-principles | Q1-Q6 checklist in axis doc (**Must**) |
| AC-AXIS-010 | legal-illegal | tests include legal walk + illegal change-without-axis (**Must**) |
| AC-AXIS-011 | dual-version | same state names usable for v2.0.0 program axis (**Should**) |
| AC-AXIS-012 | refreeze-hook | docs/skill note: refreeze after axis regenerate (**Must**) |

## First-principles exit checklist (Q1-Q6)

| # | Question |
|---|----------|
| Q1 | 用户成功是否可观测？ |
| Q2 | 是否存在非法 complete/release 捷径？ |
| Q3 | domain-bearing 是否有实体前置+合法 walk？ |
| Q4 | 本 change 是否映射到主轴边/守卫？ |
| Q5 | 实现 Wave 是否依赖未完成 L2/L0？ |
| Q6 | 子机是否可能绕过 awaiting_verifier？ |

## Implementation Wave（v1.6.7 program）

```text
Wave 1  domain-fsm-authority then golden then domain-fsm-qa-gate then ui-ship
Wave 1b product-goal-runtime (axis owner) + ralph-boundary
Wave 2  loop-discover support
Wave 3  durable-supervisor then agent-driver
Wave 4  axis validator gates on freeze/change
```

## Non-Goals

- chat as main-axis authority
- auto human release
- Loom packaging (v2 loom-brand-surface)

## Dependencies

- beacon-product-goal-runtime-v167
- beacon-goal-durable-supervisor-v167
- beacon-domain-fsm-authority-v167
- research: docs/beacon/v1.6.7/research/beacon-goalrun-main-axis-change-coherence-pln-review.md

## Public CLI

| Command | Behavior |
|---------|----------|
| `beacon goal axis generate --program <slug> -v <ver>` | write/update goalrun-main-axis.md + machine json |
| `beacon goal axis validate --program <slug> -v <ver>` | fail-closed validate |

## Planner promotion

User confirmed UD-AXIS-001..005; implement to deliverable on v1.6.7 via beacon-goal.
