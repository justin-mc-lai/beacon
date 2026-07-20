---
slug: beacon-v2-goal-durable-longrun
version: v2.0.0
status: frozen
revision_id: R3
language: zh
change_reason: "R3 - distill Codex Goal continuation/budget_limit/objective_updated into Loom steering contract; user GO 2026-07-19 1A/2A/3A/4A"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
ux_required: false
design_deferral: "CLI/orchestrator long-run; no product marketing UI"
promotion_ref: "user:2026-07-19 GO 1A durable-longrun change; 2A objective_updated Must; 3A audit→awaiting_verifier; 4A gen-change"
source_advisory: docs/beacon/v2.0.0/research/loom-goal-steering-codex-continuation-pln-review.md
---

# Requirement Truth: v2 Goal Durable Long-Run (R3)

## 人话

一句话 goal 开长跑后，系统要自动续跑，并且每次续跑都带着「不能缩 scope、要查证据、不能自己宣布完成」的 steering 指令。

- 能做：`--longrun` 挂 Supervisor + AgentDriver；断会话用 resume-pack；续跑注入 Codex 蒸馏的 continuation / budget / objective_updated
- 不能做：用完整聊天记录当权威；预算耗尽却标 complete；agent 自证 complete 绕过 verifier；自动 release
- 怎样算完：工作经 completion audit 就绪 → `awaiting_verifier` → verifier 引用齐全 → completed → **人工** release

## Overview

在 v2 Rust Product Goal Orchestrator 上，**继承并强化** v1.6.7 `beacon-goal-durable-supervisor-v167`：

1. **磁盘耐久**：heartbeat / execution.jsonl / checkpoint / resume-pack  
2. **Agent 长跑驱动（v2 增量）**：`AgentDriver` 在 host turn 结束后自动 requeue，实现「一键长跑」而不要求用户每轮打「继续」  
3. **Loom Steering 蒸馏（R3）**：从 OpenAI Codex Goal `continuation.md` / `budget_limit.md` / `objective_updated.md` 蒸馏 inject 合同；**Beacon 增强**：completion audit 后只进 `awaiting_verifier`，禁止 model self-complete  
4. **仍防假交付**：verifier complete、release 人工门、禁止自证  

用户感知目标：

```text
$beacon-goal / beacon goal run "..." --longrun
→ 长时间自动推进（带 steering），直到 awaiting_verifier / blocked / release_pending
```

## User Intent（一行）

一句话 goal 后，agent 可在编排器驱动下长时间连续执行；断会话可自动续；上下文满只注入摘要；**每次续跑必须带完整 steering 语义**；验收与发版不放水。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-V2-DLR-001 | Public entry | 仍唯一 `beacon-goal`；`--longrun` 为 **同一入口 flag**，非第二 skill |
| UD-V2-DLR-002 | v1.6.7 parity | 必须兼容 v1.6.7 durable supervisor 合同（opt-in supervise、120s 心跳、append log、tick --execute、sqlite FTS P2） |
| UD-V2-DLR-003 | One-shot longrun | `beacon goal run ... --longrun` **本 run 自动 attach** Supervisor + AgentDriver；无 flag 时保持 v1 语义（默认不 attach） |
| UD-V2-DLR-004 | Heartbeat | 默认 **120s**；min 30s |
| UD-V2-DLR-005 | Context full | resume 只注入 resume-pack digest；禁止整段 chat 权威 |
| UD-V2-DLR-006 | AgentDriver | Rust orchestrator **拥有** turn requeue 循环；Python shim 可调同一 CLI |
| UD-V2-DLR-007 | Host turn end | `host_interrupted` 后 Driver **默认 auto-requeue**（除非 blocked≥3 / release_pending / user stop） |
| UD-V2-DLR-008 | Max turns / budget | 可配置 `max_agent_turns` / token_budget；耗尽 → stage_blocked 可恢复，不静默 complete |
| UD-V2-DLR-009 | Complete / release | complete 需 verifier；release 永不 auto |
| UD-V2-DLR-010 | Memory P2 | sqlite FTS 优先；zvec 可选插件非权威 |
| UD-V2-DLR-011 | Parallel | 与 main-star/satellite 组合：Driver 可 fan-out 卫星，合并回主星 |
| UD-V2-DLR-012 | SE binding | 遵守 SE-V2-00..13；不默认 BEACON_V2=1 直至 W4 |
| UD-V2-ST-001 | Steering source | Codex Goal templates 为蒸馏源；合同资产见 fixtures/steering + references/goal-steering |
| UD-V2-ST-002 | InjectBundle order | **`steering(template)` → `resume-pack digest` → `next_action`** |
| UD-V2-ST-003 | Must sections | scope fidelity、work-from-evidence、completion audit、blocked≥3、budget wrap-up、objective-as-data（见 MUST_SECTIONS.md） |
| UD-V2-ST-004 | Complete path | completion audit **仅**推进 `awaiting_verifier`；**禁止** model/self-cert complete（用户 GO 3A） |
| UD-V2-ST-005 | Template authority path | 单源：`docs/beacon/v2.0.0/fixtures/steering/`；checklist：`skills/beacon/references/goal-steering/MUST_SECTIONS.md`；runtime 禁止私自缩短 Must 段 |
| UD-V2-ST-006 | objective_updated | **本轮 Must**（用户 GO 2A）；用户编辑 objective 后必须 inject `objective_updated` |

## Public CLI / skill surface

| 入口 | 行为 |
|------|------|
| `beacon goal run "<目标>" --longrun` | 创建 run + attach supervisor + start AgentDriver loop |
| `$beacon-goal` / `$loom-goal` + 意图含「长跑/不中断/直到验收」 | skill 必须传 longrun=true |
| `beacon goal supervise` | 保留 opt-in（无 --longrun 时） |
| `beacon goal resume-pack` / `heartbeat` / `checkpoint` / `tick --execute` | v1.6.7 同构 |
| `beacon goal driver status\|stop` | 查询/停止 AgentDriver（v2） |

## Domain Model

| Entity | Key | Notes |
|--------|-----|-------|
| GoalRun | run_id | ledger 权威 |
| SupervisorSession | run_id + session_id | longrun 自动 active；否则 opt-in |
| AgentDriver | run_id + driver_id | v2 requeue 循环 |
| Heartbeat / ExecutionLog / Checkpoint | run_id | 同 v1.6.7 |
| WorkerJob | run_id + stage | ralph / qa / design |
| MemoryIndex | run_id | sqlite FTS P2 |
| SteeringTemplate | template_id | `continuation` \| `budget_limit` \| `objective_updated` |
| SteeringRender | run_id + turn_id | rendered text injected into host turn |
| GoalTurnCounter | run_id + blocker_id | consecutive goal turns for blocked audit |
| InjectBundle | turn_id | ordered: steering → resume-pack → next_action |

## Domain FSM — GoalRun（durable，继承 v1.6.7）

| State | From | Guard | Side effects |
|-------|------|-------|--------------|
| created | — | goal run | state written |
| running | created | — | stages progress |
| stage_active | running | stage set | progressive skills |
| host_interrupted | stage_active | host turn end / stall | checkpoint freeze |
| stage_blocked | stage_active | worker/gate fail | streak++ |
| awaiting_verifier | work done | no verifier | wait |
| completed | awaiting_verifier | verifier refs | completed_at |
| blocked | stage_blocked | streak≥3 | human |
| release_pending | completed path | human gate | human only |

## Illegal transitions — GoalRun

| From | To | Guard violated | TC slot |
|------|-----|----------------|---------|
| host_interrupted | completed | no verifier | TC-V2-DLR-ILLEGAL-01 |
| stage_blocked | completed | no repair | TC-V2-DLR-ILLEGAL-01 |
| awaiting_verifier | completed | missing refs | TC-V2-DLR-ILLEGAL-01 |

## Domain FSM — AgentDriver（v2 + R3 inject）

| State | From | Guard | Side effects |
|-------|------|-------|--------------|
| idle | — | no longrun | — |
| arming | idle | --longrun or supervise | load checkpoint |
| turn_active | arming, requeue | spawn/resume host agent | **InjectBundle**: continuation + resume-pack + next_action |
| turn_ended | turn_active | host exit / context full | write host_interrupt event |
| requeue | turn_ended | not terminal & budget ok | next turn（再次 continuation inject） |
| halt_budget | turn_ended | max_turns/token exhausted | inject **budget_limit**；stage_blocked reason=budget |
| objective_changed | * | user edits objective | inject **objective_updated** on next turn |
| halt_terminal | * | completed/blocked/release_pending/user_stop | stop loop |

### Legal walks

1. **W-V2-DLR-01** `run --longrun` → turn_active*（含 steering）→ awaiting_verifier → (verifier) → completed  
2. **W-V2-DLR-02** turn_ended(context full) → requeue → turn_active(continuation+digest) → continue  
3. **W-V2-DLR-03** 无 --longrun → 不 auto driver（parity v1 supervise opt-in）  
4. **W-V2-DLR-04** budget exhaust → halt_budget + budget_limit inject → stage_blocked，不 complete  
5. **W-V2-ST-01** requeue 后 inject 顺序 steering → digest → next_action  
6. **W-V2-ST-02** objective edit → next turn inject objective_updated  

## Illegal transitions — AgentDriver

| From | To | Guard violated | TC slot |
|------|-----|----------------|---------|
| turn_ended | completed | no verifier | TC-V2-DLR-ILLEGAL-01 |
| halt_budget | completed | budget exhaust must not complete | TC-V2-DLR-ILLEGAL-03 |
| turn_active | release_confirmed | auto release forbidden | TC-V2-DLR-ILLEGAL-02 |
| requeue | turn_active | digest-only without required steering | TC-V2-ST-ILLEGAL-01 |

## Illegal transitions — SupervisorSession

| From | To | Guard violated | TC slot |
|------|-----|----------------|---------|
| detached | polling | must active first | TC-V2-DLR-002 |
| idle default run | active | without --longrun or supervise | TC-V2-DLR-002 |

### Illegal (global IDs)

| ID | Illegal |
|----|---------|
| I-V2-DLR-001 | turn_ended → completed 无 verifier |
| I-V2-DLR-002 | driver auto-confirms release |
| I-V2-DLR-003 | inject full chat as sole authority |
| I-V2-DLR-004 | overwrite execution.jsonl |
| I-V2-DLR-005 | second public skill for longrun |
| I-V2-DLR-006 | memory FTS overrides verifier |
| I-V2-DLR-007 | silent complete on budget exhaust |
| I-V2-ST-001 | requeue 只 inject resume-pack，省略 required continuation steering |
| I-V2-ST-002 | steering 指示 agent 自证 GoalRun complete / 绕过 verifier |
| I-V2-ST-003 | budget_limit 后仍鼓励新实质工作 |
| I-V2-ST-004 | 第 1 次 blocker 即 blocked（未满 3 goal turns，含 auto-requeue） |
| I-V2-ST-005 | runtime 私自缩短 MUST_SECTIONS 段落 |
| I-V2-ST-006 | 用户改 objective 后不 inject objective_updated |

## Context-full / Inject protocol（Must）

### Resume-pack digest（仍 Must）

每个 agent turn 的 digest 仅含：

1. utterance + done_when + stage  
2. last ≤5 heartbeats  
3. open_blockers  
4. one next_action  
5. log/scorecard paths  

### InjectBundle（R3 Must）

| Order | Part | When |
|-------|------|------|
| 1 | `SteeringRender(template)` | always on requeue/arming turn_active；`budget_limit` on halt_budget；`objective_updated` after objective edit |
| 2 | resume-pack digest | always（context-full / requeue） |
| 3 | next_action | always |

Authority: resume-pack digest remains progress-summary authority; steering is behavioral contract; full chat is never sole authority.

### Steering assets（normative）

| template_id | Path |
|-------------|------|
| continuation | `docs/beacon/v2.0.0/fixtures/steering/continuation.md` |
| budget_limit | `docs/beacon/v2.0.0/fixtures/steering/budget_limit.md` |
| objective_updated | `docs/beacon/v2.0.0/fixtures/steering/objective_updated.md` |
| must checklist | `skills/beacon/references/goal-steering/MUST_SECTIONS.md` |

Source parity reference (oss-sync, non-authoritative for runtime): Codex `codex-rs/ext/goal/templates/goals/*`.

### Goal turn（blocked audit 定义）

A **goal turn** is one AgentDriver `turn_active` cycle, including turns started by auto-requeue. The same `blocker_id` on ≥3 consecutive goal turns satisfies blocked audit (then GoalRun may enter `blocked`). User resume starts a fresh counter.

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-DLR-001 | parity-v167 | v1.6.7 durable supervisor 行为 fixture 在 v2 可加载/通过（**Must**） |
| AC-V2-DLR-002 | longrun-flag | `--longrun` 本 run attach supervisor+driver；默认 run 不 attach（**Must**） |
| AC-V2-DLR-003 | skill-one-shot | `$beacon-goal` 识别长跑意图并设置 longrun（**Must**） |
| AC-V2-DLR-004 | heartbeat-120 | 默认 120s 心跳（**Must**） |
| AC-V2-DLR-005 | execution-jsonl | 事件 append-only JSONL（**Must**） |
| AC-V2-DLR-006 | resume-pack | digest-only resume-pack（**Must**） |
| AC-V2-DLR-007 | interrupt-semantics | host_interrupted ≠ stage_blocked（**Must**） |
| AC-V2-DLR-008 | auto-requeue | turn_ended 后 driver 自动 requeue（除非 terminal/budget/stop）（**Must**） |
| AC-V2-DLR-009 | tick-execute | tick --execute 可派 ralph/qa；不 auto-release（**Must**） |
| AC-V2-DLR-010 | no-self-cert | complete 需 verifier（**Must**） |
| AC-V2-DLR-011 | human-release | release 永不 auto（**Must**） |
| AC-V2-DLR-012 | budget | max_agent_turns/token_budget 可配；耗尽不 complete（**Must**） |
| AC-V2-DLR-013 | rust-own | AgentDriver 归属 Rust Operator Spine；Python shim 同 CLI（**Must**） |
| AC-V2-DLR-014 | parallel | 与 satellite pool 可组合（**Should**） |
| AC-V2-DLR-015 | fts-p2 | sqlite FTS 非权威（**Should**） |
| AC-V2-DLR-016 | legal-illegal-tests | tests 含 legal walk + illegal 行（**Must**） |
| AC-V2-ST-001 | steering-assets | 存在 continuation/budget_limit/objective_updated 规范模板 + MUST_SECTIONS checklist（**Must**） |
| AC-V2-ST-002 | inject-bundle | requeue→turn_active **必须** InjectBundle 顺序 steering→digest→next_action（**Must**） |
| AC-V2-ST-003 | objective-as-data | objective 按 untrusted user data 处理，非 system override（**Must**） |
| AC-V2-ST-004 | completion-audit-gate | completion audit 段存在且 **禁止** 指示绕过 verifier 的 complete；只进 awaiting_verifier（**Must**） |
| AC-V2-ST-005 | blocked-audit | blocked audit 段：≥3 consecutive goal turns（含 auto-requeue）（**Must**） |
| AC-V2-ST-006 | budget-wrap-up | halt_budget 时 inject budget_limit；禁新实质工作；禁预算伪 complete（**Must**） |
| AC-V2-ST-007 | objective-updated | 用户改 objective 后 next turn inject objective_updated（**Must**） |
| AC-V2-ST-008 | section-tests | tests 含 section presence / inject order / illegal inject（**Must**） |
| AC-V2-ST-009 | budget-fields | remaining tokens/turns 字段可渲染（**Should**） |

## Full parity with v1.6.7 durable supervisor (Must)

v2 必须 **完整继承** 下列 v1.6.7 能力（不得降级）。映射：

| v1.6.7 AC | v2 AC / 合同 | 能力 |
|-----------|--------------|------|
| AC-DGS-001 | AC-V2-DLR-002 | supervise/driver 默认不挂；`--longrun` 或显式 supervise 才挂 |
| AC-DGS-002 | AC-V2-DLR-004 | 心跳默认 120s |
| AC-DGS-003 | AC-V2-DLR-005 | execution.jsonl append-only |
| AC-DGS-004 | AC-V2-DLR-006 | checkpoint + resume-pack digest only |
| AC-DGS-005 | AC-V2-DLR-007 + stall | idle≥interval → host_interrupted/stall |
| AC-DGS-006 | AC-V2-DLR-007 | host_interrupted ≠ stage_blocked |
| AC-DGS-007 | AC-V2-DLR-009 | tick --execute 派工、不 auto-release |
| AC-DGS-008 | AC-V2-DLR-010 | complete 需 verifier |
| AC-DGS-009 | AC-V2-DLR-011 | release 人工 |
| AC-DGS-010 | AC-V2-DLR-002/003 | 非第二公共入口 |
| AC-DGS-011 | AC-V2-DLR-005 | 日志不可覆写 |
| AC-DGS-012 | AC-V2-DLR-015 | sqlite FTS 非权威 |
| AC-DGS-013 | AC-V2-DLR-003 | skill 长跑/续跑说明 |
| AC-DGS-014 | AC-V2-DLR-016 | legal/illegal TC 行 |

**额外 v2-only**：AC-V2-DLR-008 auto-requeue、AC-V2-DLR-012 budget、AC-V2-DLR-013 Rust Driver、**AC-V2-ST-001..008 steering 蒸馏**。

Upstream freeze 权威：`docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md`  
Planner advisory：`docs/beacon/v2.0.0/research/loom-goal-steering-codex-continuation-pln-review.md`

## Non-Goals

- 不保证任意 LLM host 零失败无限跑（预算与 blocker 仍停）  
- 不把 zvec 当编排内核  
- 不在 W4 前默认 BEACON_V2=1  
- 不删除 v1.6.7 Python durable 路径直到兼容 shim 完成  
- **不**引入 Codex 式 agent `update_goal(complete)` 为 GoalRun 完成权威  
- **不**在本 lake 实现 host cron / RecurringJob daemon  
- **不**用 MVP 三行 prompt 替代 MUST_SECTIONS  

## Dependencies

- `beacon-v2-product-goal-orchestrator`  
- `beacon-v2-main-star-satellite-pool`  
- `beacon-v2-ralph-implement-boundary`  
- `loom-goal-trace-bundle`（trace 与 resume-pack 权威分工）  
- Upstream: `beacon-goal-durable-supervisor-v167` (v1.6.7)  
- Source: OpenAI Codex Goal templates（蒸馏源，非 runtime 权威）

## How one-shot works (normative)

```text
beacon goal run "..." --longrun
  → create GoalRun
  → SupervisorSession.active (this run)
  → AgentDriver.arming
  loop:
      steering = render(continuation | budget_limit | objective_updated)
      pack = resume-pack digest
      spawn/resume host agent with InjectBundle(steering, pack, next_action)
      on exit → heartbeat/checkpoint
      if terminal (awaiting_verifier|blocked|release_pending|user_stop|budget): break
      else requeue
  → user attaches verifier → complete
  → human release
```
