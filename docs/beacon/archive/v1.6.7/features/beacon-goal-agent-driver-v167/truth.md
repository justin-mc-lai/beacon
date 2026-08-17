---
slug: beacon-goal-agent-driver-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: "P0 Python AgentDriver for one-shot longrun auto-requeue; GO parallel path C 2026-07-18; depends durable-supervisor"
canonical_refs:
  truth: docs/beacon/archive/v1.6.7/features/beacon-goal-agent-driver-v167/truth.md
  tests: docs/beacon/archive/v1.6.7/features/beacon-goal-agent-driver-v167/tests.md
  tasks: docs/beacon/archive/v1.6.7/features/beacon-goal-agent-driver-v167/tasks.md
  evidence: docs/beacon/archive/v1.6.7/features/beacon-goal-agent-driver-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
ux_required: false
design_deferral: "CLI AgentDriver; no product marketing UI"
---

# Requirement Truth: Goal AgentDriver v1.6.7 (R1)

## Overview

在 **已冻结并实现** 的 `beacon-goal-durable-supervisor-v167` 之上，增加 **Python AgentDriver**：

- 用户 **一键** `beacon goal run "..." --longrun`（或 `$beacon-goal` 长跑意图）
- host agent turn 结束后 **自动 requeue 下一轮**（不用每轮打「继续」）
- 每轮只注入 **resume-pack digest**
- **不**削弱 verifier complete / 人工 release

与 v2 `beacon-v2-goal-durable-longrun` **行为 parity**（v1 先 Python 可用；v2 Rust Spine 后迁）。

## User Intent（一行）

一句话 goal 后 agent 长时间自动续轮执行，直到验收门或预算/阻断停。

## User Decisions（locked — GO 2026-07-18 Path C）

| ID | Decision | Value |
|----|----------|-------|
| UD-GAD-001 | Parallel path | **C**：v1 Python Driver 先用；v2 parity 同行为 |
| UD-GAD-002 | Depends | **必须**依赖 durable-supervisor（心跳/JSONL/checkpoint/resume-pack） |
| UD-GAD-003 | One-shot | `beacon goal run --longrun` **本 run** attach supervisor + start driver |
| UD-GAD-004 | Default run | **无** `--longrun` → **不** auto driver（保持 supervise opt-in） |
| UD-GAD-005 | Public entry | 仍唯一 `beacon-goal`；`--longrun` 为 flag，**非**第二 skill |
| UD-GAD-006 | Host spawn | **Bridge 优先** `BEACON_HOST_GOAL_BRIDGE_CMD`；可选 codex/claude adapter |
| UD-GAD-007 | Heartbeat | 复用 durable 默认 **120s** |
| UD-GAD-008 | Budget | `max_agent_turns` 默认 32；`turn_timeout_sec` 默认 3600；耗尽 **不 complete** |
| UD-GAD-009 | Complete/Release | complete 需 verifier；release **永不** auto |
| UD-GAD-010 | Skill | `$beacon-goal` 识别「长跑/不中断/直到验收/自动续」→ longrun=true |
| UD-GAD-011 | Concurrency | 单 run 单 driver（lock）；禁止同 run 双 driver |
| UD-GAD-012 | v2 parity | 行为与 `beacon-v2-goal-durable-longrun` AC-V2-DLR-008/012 对齐 |

## Public CLI

| 命令 | 行为 |
|------|------|
| `beacon goal run "<u>" --longrun` | 创建 run + longrun attach + **可选** `--driver-start` 默认 true |
| `beacon goal driver start --run-id` | 启动 Driver 循环（已有 run） |
| `beacon goal driver status --run-id` | idle/arming/turn_active/... + pid |
| `beacon goal driver stop --run-id` | 用户停止 → halt_terminal |
| 已有 | heartbeat / checkpoint / resume-pack / supervise / tick --execute |

环境变量：

| Var | 作用 |
|-----|------|
| `BEACON_HOST_GOAL_BRIDGE_CMD` | 启动 host agent 的 shell 模板；可用 `{prompt_file}` `{run_id}` `{project}` |
| `BEACON_GOAL_MAX_TURNS` | 覆盖 max_agent_turns |
| `BEACON_GOAL_TURN_TIMEOUT_SEC` | 覆盖 turn timeout |

## Domain Model

| Entity | Key | Precedence |
|--------|-----|------------|
| GoalRun | run_id | durable-supervisor 权威 |
| SupervisorSession | run_id | longrun 时 active |
| AgentDriver | run_id + driver_id | 本湖权威 |
| DriverTurn | run_id + turn_n | prompt/result 文件 |
| ExecutionLog / Checkpoint | run_id | durable-supervisor |

## Domain FSM — AgentDriver

| State | From | Guard | Side effects |
|-------|------|-------|--------------|
| idle | — | 无 longrun / 未 start | — |
| arming | idle | start/--longrun | load checkpoint; lock |
| turn_active | arming, requeue | spawn host | write turn-N.prompt.md; pid |
| turn_ended | turn_active | exit/timeout | heartbeat; optional result.json |
| requeue | turn_ended | not terminal & budget ok | turn_n++ |
| halt_budget | turn_ended | turns≥max or timeout policy | stage_blocked reason=budget |
| halt_terminal | * | completed path / blocked≥3 / user stop / release_pending | release lock |

### Legal walks

1. **W-GAD-01** `--longrun` → arming → turn_active* → awaiting_verifier  
2. **W-GAD-02** turn_ended(context/host exit) → requeue → turn_active(digest)  
3. **W-GAD-03** 无 --longrun → driver 保持 idle  
4. **W-GAD-04** budget → halt_budget → **不** complete  

## Illegal transitions — AgentDriver

| From | To | Guard violated | TC slot |
|------|-----|----------------|---------|
| turn_ended | completed | no verifier | TC-GAD-ILLEGAL-01 |
| halt_budget | completed | budget must not complete | TC-GAD-ILLEGAL-02 |
| turn_active | release_confirmed | auto release forbidden | TC-GAD-ILLEGAL-03 |
| idle | turn_active | without start/longrun | TC-GAD-ILLEGAL-04 |

## Illegal transitions — GoalRun（driver 路径）

| From | To | Guard violated | TC slot |
|------|-----|----------------|---------|
| host_interrupted | completed | no verifier | TC-GAD-ILLEGAL-01 |
| awaiting_verifier | completed | missing refs | TC-GAD-ILLEGAL-01 |

### Illegal (global IDs)

| ID | Illegal |
|----|---------|
| I-GAD-001 | turn_ended → completed 无 verifier |
| I-GAD-002 | driver auto-confirms release |
| I-GAD-003 | full chat as sole authority |
| I-GAD-004 | second public skill for longrun |
| I-GAD-005 | budget exhaust → complete |
| I-GAD-006 | default run auto-starts driver without --longrun |
| I-GAD-007 | dual driver same run |

## Turn artifacts（Must）

```text
.beacon/state/product-goal/<run_id>/
  driver.json                 # state, pid, turn_n, budget
  turn-<n>.prompt.md          # resume-pack digest + next_action
  turn-<n>.result.json        # optional agent output
  execution.jsonl             # from durable-supervisor
  checkpoint.json
```

`turn-*.prompt.md` **必须**含 resume-pack 字段，**禁止**默认粘贴完整 history JSONL。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-GAD-001 | depends | 实现依赖 durable-supervisor API（resume-pack/heartbeat/log）（**Must**） |
| AC-GAD-002 | longrun-flag | `--longrun` 启动 driver；默认 run 不启动（**Must**） |
| AC-GAD-003 | skill-intent | skill 长跑意图 → longrun（**Must**） |
| AC-GAD-004 | auto-requeue | turn_ended 后 auto requeue（除非 terminal/budget/stop）（**Must**） |
| AC-GAD-005 | digest-inject | 每 turn 仅 digest prompt 文件（**Must**） |
| AC-GAD-006 | bridge | BEACON_HOST_GOAL_BRIDGE_CMD 可 spawn；缺 bridge 且无 adapter → blocked 可恢复（**Must**） |
| AC-GAD-007 | budget | max_turns/timeout 可配；耗尽 halt_budget 不 complete（**Must**） |
| AC-GAD-008 | no-self-cert | driver 路径 complete 仍要 verifier（**Must**） |
| AC-GAD-009 | no-auto-release | 永不 auto release（**Must**） |
| AC-GAD-010 | single-lock | 同 run 单 driver lock（**Must**） |
| AC-GAD-011 | cli-surface | driver start/status/stop CLI（**Must**） |
| AC-GAD-012 | single-entry | 非第二公共入口（**Must**） |
| AC-GAD-013 | v2-parity-note | truth/tests 声明与 v2 longrun 行为对齐（**Must**） |
| AC-GAD-014 | legal-illegal | tests 含 legal walk + illegal 行（**Must**） |

## Non-Goals

- 系统级默认 launchd daemon（可用外部 cron 调 driver start，但非默认安装）  
- 实现 Rust Spine（归 v2）  
- 替换 durable-supervisor  
- zvec 编排  

## Dependencies

- `beacon-goal-durable-supervisor-v167`（required）  
- `beacon-product-goal-runtime-v167`  
- v2 peer: `beacon-v2-goal-durable-longrun`（parity，非实现阻塞）  

## Planner promotion

- `docs/beacon/archive/v1.6.7/research/beacon-goal-agent-driver-v167.md`  
- User GO Path C: 2026-07-18  
