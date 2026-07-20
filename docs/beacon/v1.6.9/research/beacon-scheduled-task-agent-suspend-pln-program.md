# Plan: Project Scheduled Task + Agent Suspend (v1.6.9)

**Surface**: `$beacon-plan` (program + review anchors)  
**Version**: v1.6.9 (dual-track note: v2.0.0/Loom parity later)  
**Date**: 2026-07-20  
**Status**: plan only — **not frozen truth**  
**Writes truth**: false | **May implement**: false

## 0. plan_artifact.v1

| Field | Content |
|-------|---------|
| surface_ask | v1.6.9 做定时任务：多 agent LLM + 任务挂起 + 项目内任务管理 + 系统定时能力驱动执行 |
| deep_want | 在 **项目内可审计的任务账本** 上，用 **OS 时钟只负责唤醒**，用 **Beacon 负责派发/挂起/续跑/门禁**，让多 host agent 能按计划执行并在阻塞时挂起而不是丢状态 |
| non_goals | plan 不写 frozen truth；不实现；不在本 plan 宣称 QA/release；不做「第二公共编排入口」替代 goal；不默认常驻 daemon；release 永不被定时器自动确认 |
| methodology | program 拆海 + review 状态机/parity 风险 |
| high_risk | 是 — 状态机、多 agent host、权限（系统定时安装）、与 durable-longrun / 1+6 公开面边界 |

## 1. 问题重述（第一性）

用户真正要的不是「再写一个 cron 包装器」，而是：

1. **项目权威任务**：任务定义、下次触发、状态、日志 **写在项目里**（可版本化/可盘点）。  
2. **多 Agent LLM**：Codex / Claude / bridge 等 host 可绑定到任务。  
3. **挂起（suspend）**：上下文满、等人、门禁失败、预算到 → **挂起而非静默失败**；可 resume。  
4. **系统定时 + 项目执行**：OS（launchd/cron/systemd）只 **thin wake**；真正执行逻辑在 `beacon task …` / goal 子系统。

已有能力可复用：

| 已有 | 复用点 | 缺口 |
|------|--------|------|
| `goal supervise` / heartbeat / resume-pack | 单 run 内 durable | 无日历调度、无项目级任务账本 |
| `AgentDriver` longrun | requeue / inject / multi-turn | 绑定 **一次 GoalRun**，不是 RecurringJob |
| `host_interrupt` / pause / blocked_streak | 挂起语义 | 未产品化为「任务挂起」一等公民 |
| `automation` | — | **已退役** |
| v2 durable-longrun Non-Goals | 明确不做 host cron/RecurringJob **本 lake** | 本需求需 **新湖** 承接 |

## 2. 推荐架构（方案 A — Project Scheduled Task）

### 2.1 分层

```text
┌──────────────────────────────────────────────────────────┐
│ OS Timer (opt-in install)                                 │
│ launchd plist / crontab / systemd timer                   │
│   → only: beacon task wake --task-id <id> --once          │
└───────────────────────────┬──────────────────────────────┘
                            │ thin wake (no business logic)
┌───────────────────────────▼──────────────────────────────┐
│ Project Task Ledger  (.beacon/tasks/  or .beacon/schedule)│
│ ScheduledTask record: schedule, agent, payload, state     │
└───────────────────────────┬──────────────────────────────┘
                            │ fire admitted?
┌───────────────────────────▼──────────────────────────────┐
│ Task Runner (Beacon runtime)                              │
│ arm → spawn host agent → running → suspend|done|fail      │
│ reuse: resume-pack, inject, workspace admit gates         │
└───────────────────────────┬──────────────────────────────┘
                            │ optional bind
┌───────────────────────────▼──────────────────────────────┐
│ GoalRun / WorkerJob (existing) when task kind = goal_tick │
│ never auto-release                                        │
└──────────────────────────────────────────────────────────┘
```

### 2.2 公开面位置（与 1+6 对齐）

| 选择 | 说明 |
|------|------|
| **推荐** | **不新增** 第 8 个 host-visible skill；CLI 挂在 `beacon task`（或 `beacon schedule`）+ 文档从 **goal** 渐进引用 |
| 禁止 | 新 `$beacon-cron` 公共 skill 与 goal 并列抢入口 |
| plan | 本需求规划用 `$beacon-plan`；长程执行仍 `$beacon-goal` / task runner 调 goal |
| progressive | 内部可有 `beacon-gov-*` 式运维说明，但 **用户只感知 task 账本 + goal** |

### 2.3 核心对象（草案 schema，待 truth 冻结）

**ScheduledTask.v1**

```json
{
  "schema": "scheduled-task.v1",
  "task_id": "st-…",
  "project_root": ".",
  "title": "…",
  "kind": "goal_tick | agent_prompt | cli_command",
  "schedule": {
    "expr": "cron|every|at",
    "cron": "0 9 * * 1-5",
    "timezone": "Asia/Shanghai",
    "next_fire_at": "ISO-8601",
    "enabled": true
  },
  "agent": {
    "host": "codex|claude|bridge|none",
    "bridge_cmd_env": "BEACON_HOST_GOAL_BRIDGE_CMD",
    "skill_hint": "beacon-goal|beacon-plan|…",
    "max_turns": 8,
    "timeout_sec": 3600
  },
  "payload": {
    "utterance": "…",
    "goal_run_id": "optional bind",
    "version": "v1.6.9",
    "worktree_policy": "admit_required|readonly"
  },
  "state": "scheduled|armed|running|suspended|waiting_human|succeeded|failed|disabled",
  "suspend": {
    "reason_code": "",
    "resume_pack_ref": "",
    "blocked_streak": 0,
    "since": ""
  },
  "audit": {
    "created_at": "",
    "updated_at": "",
    "last_fire_at": "",
    "last_result_ref": "",
    "events_log": ".beacon/tasks/<id>/events.jsonl"
  }
}
```

**状态机（legal）**

```text
disabled ⇄ scheduled --wake→ armed --admit→ running
running → succeeded | failed | suspended | waiting_human
suspended --resume→ armed|running
waiting_human --human_ack→ armed|running
* → disabled (user)
```

**Illegal**

- running → auto release confirm  
- wake 时在未 admit worktree 上写 implement（kind=goal_tick + implement stage）  
- OS timer 内嵌业务逻辑（必须 thin wake）  
- 无 task 记录的「幽灵 cron」  

### 2.4 系统定时（opt-in）

| OS | 产物 | 行为 |
|----|------|------|
| macOS | `~/Library/LaunchAgents/com.beacon.task.<task_id>.plist` | StartCalendarInterval / StartInterval → `beacon task wake --task-id … --once` |
| Linux | user systemd timer 或 crontab 行 | 同上 |
| 通用 | `beacon task install-timer --task-id` / `uninstall-timer` | **显式确认**；默认不装 |

原则：

- **账本权威在项目**；OS 只是闹钟  
- 机器换了：`beacon task rebind-timers --project .` 重装  
- dry-run 可打印将写入的 plist/cron 而不执行  

### 2.5 多 Agent LLM + 挂起

| 能力 | 机制 |
|------|------|
| 多 host | `agent.host` + 既有 bridge/env；fire 时解析 spawn 命令 |
| 注入 | InjectBundle：steering(可选) + **task resume-pack** + next_action |
| 挂起 | 映射 `host_interrupted` / budget / 连续 blocker≥3 / waiting_human → `suspended` |
| 续跑 | `beacon task resume --task-id` 或下次 wake 发现 suspended → 带 resume-pack 再 fire（策略可配置：skip_until_resume / auto_resume_on_wake） |
| 审计 | events.jsonl append-only；与 goal execution.jsonl 风格一致 |

### 2.6 与 goal longrun 的边界

| | Goal durable longrun | Scheduled Task（本 plan） |
|--|----------------------|---------------------------|
| 触发 | 用户/longrun driver 连续 turn | **日历/间隔** + 可选 wake |
| 对象 | 一个 GoalRun | 项目任务账本 N 条 |
| 默认 daemon | 否 | 否（OS timer opt-in） |
| release | 人工 | 人工（若任务触达 release 仅提示） |

可组合：`kind=goal_tick` 的任务只做 `goal supervise --once` / `goal tick --execute` / 指定 stage 续跑。

## 3. 方案对比

| 方案 | 描述 | 优点 | 缺点 | 推荐 |
|------|------|------|------|------|
| **A. Project Scheduled Task** | 项目账本 + thin OS wake + runner | 符合 Beacon 证据/门禁；可盘点 | 需新 schema/CLI | **推荐** |
| B. 仅扩展 supervise interval | 把 supervise 当 cron | 改动小 | 无项目任务管理；多任务差 | 否 |
| C. 复活 automation/launchd 业务面 | 旧 automation | — | 已退役；与 1+6 冲突 | 否 |
| D. 纯 host 外部脚本 | 用户自己写 cron 调 codex | 零产品成本 | 无统一挂起/账本/门禁 | 仅作临时 workaround |

## 4. 程序拆海（Lakes）

### Sea：`beacon-scheduled-task-agent-suspend`（建议 slug）

| Lake | Version | 范围 | 依赖 |
|------|---------|------|------|
| **L0 schema+CLI ledger** | v1.6.9 | `scheduled-task.v1`；`beacon task create/list/get/enable/disable/log`；项目路径 `.beacon/tasks/` | 无 |
| **L1 wake+runner+suspend** | v1.6.9 | `wake --once`；host agent spawn；suspend/resume；events.jsonl；resume-pack | L0, goal_agent_driver patterns |
| **L2 system timer install** | v1.6.9 | launchd/cron/systemd adapter；install/uninstall/rebind；`--confirm` | L1 |
| **L3 goal_tick kinds** | v1.6.9 | kind=goal_tick 绑定 GoalRun；workspace admit 硬门；no auto-release | L1, goal-implement-admission |
| **L4 loom/v2 parity** | v2.0.0 | `loom task` 同义；Rust 可选 store | L0–L3 |

**P0 交付建议**：L0+L1（账本+唤醒执行+挂起）即可演示「项目管任务 + agent 跑 + 挂起」；L2 再接系统定时。

## 5. UD / AC 草案（供 truth 冻结）

### UD（用户决策建议 — 推荐默认）

| ID | 决策 | 推荐 |
|----|------|------|
| UD-ST-001 | 公开入口 | CLI `beacon task`；不新增 host skill |
| UD-ST-002 | 权威存储 | 项目 `.beacon/tasks/`（jsonl/json）；非仅内存 |
| UD-ST-003 | OS 角色 | thin wake only；opt-in install |
| UD-ST-004 | 默认 daemon | **永不**默认常驻 |
| UD-ST-005 | release | 永不自动确认 |
| UD-ST-006 | implement 写路径 | 走 workspace admit；否则 readonly/block |
| UD-ST-007 | 挂起策略 | blocker≥3 / host_interrupt / budget → suspended；waiting_human 单独态 |
| UD-ST-008 | wake 遇 suspended | 默认 `skip_until_resume`（可配 auto_resume_on_wake） |
| UD-ST-009 | 双轨 | v1.6.9 Python 先；v2.0.0/loom 后 parity |

### AC（Must 草案）

| ID | 断言 |
|----|------|
| AC-ST-001 | create 后 `list` 可见且落盘项目内 |
| AC-ST-002 | `wake --once` 无 OS timer 也能执行一轮 |
| AC-ST-003 | running→suspended 必写 reason_code + resume_pack_ref |
| AC-ST-004 | resume 后可继续且 events append-only |
| AC-ST-005 | install-timer 无 `--confirm` 不改系统 |
| AC-ST-006 | uninstall-timer 后 OS 不再触发；账本仍在 |
| AC-ST-007 | goal_tick 路径不 auto-release |
| AC-ST-008 | 不出现第二公共 skill 入口抢 goal |
| AC-ST-009 | codex 与 claude host 至少各有一条 dry-run/integration 路径 |
| AC-ST-010 | package/host install 不把 internal task skill 扫成 40+ 历史 skill |

## 6. CLI 草图（非实现）

```bash
beacon task create --title "…" --cron "0 9 * * 1-5" --tz Asia/Shanghai \
  --host codex --kind agent_prompt --utterance "…" -p .
beacon task list -p . --json
beacon task get <id> -p .
beacon task wake <id> --once -p .
beacon task suspend <id> --reason host_interrupted -p .
beacon task resume <id> -p .
beacon task install-timer <id> -p . --confirm
beacon task uninstall-timer <id> -p . --confirm
beacon task doctor -p .   # ledger vs installed timers drift
```

## 7. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 与 longrun 概念混淆 | 文档对照表；task 管「何时」，goal 管「交付链」 |
| 定时误触 implement 污染 main | admit 硬门 + kind 默认 readonly |
| launchd 权限/多机漂移 | doctor rebind；账本为权威 |
| Agent 费用失控 | max_turns / timeout / daily fire cap |
| 1+6 膨胀 | 不新增 public skill |

## 8. recommended_next

1. **用户确认 UD-ST-001..009**（默认方案 A + P0=L0+L1）。  
2. `$beacon-goal` / truth：冻结 `scheduled-task.v1` + AC-ST-*（单湖或 L0+L1 合并湖）。  
3. implement → qa → release（人工）。  
4. L2 系统定时作为 follow-up lake。

## 9. Evidence anchors（源码/文档）

- `skills/beacon/beacon-goal/SKILL.md` — durable / supervise / longrun / **Not a system daemon**  
- `docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md` — opt-in supervise；外部 cron 仅调 CLI  
- `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md` — Non-Goal: host cron / RecurringJob  
- `beacon/commands/automation.py` — automation retired  
- `beacon/utils/goal_agent_driver.py` — host bridge / requeue / longrun  
- `beacon/utils/product_goal_runtime.py` — host_interrupt / resume-pack  

## 10. Dual-track note

| Track | 本需求 |
|-------|--------|
| Beacon v1.6.9 Python | **先做** L0–L3 |
| Loom v2.0.0 Rust | L4 parity；CLI 名 `loom task` 或 `beacon-v2 task` |

---

**Plan verdict**: 需求合理且与现有 durable 边界 **正交可加**；必须以 **项目任务账本 + thin OS wake + agent suspend** 三件套落地，禁止复活 automation 业务调度器。  
**Next stage hint**: `truth`（freeze scheduled-task lake）— 需用户 UD 确认后。
