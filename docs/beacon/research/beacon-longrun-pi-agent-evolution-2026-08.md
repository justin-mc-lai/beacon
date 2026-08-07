# Research: Beacon 长程稳定性机制深度对照 + pi agent 长程交付演进方案

**日期**：2026-08-03
**前置**：`beacon-longrun-stability-analysis-2026-08.md`（8 维稳定性框架与缺口定位：S4 预算、S7 并发）
**素材**：`oss-sync/agents/agent-systems/kun`（kun/kun/src）、`oss-sync/automation/autoresearch/loopx`（loopx/loopx）、`oss-sync/agents/agent-systems/oh-my-pi`（packages/agent、packages/coding-agent）
**目标**：把 kun/loopx 的 goal 与长程 loop 机制对照到 Beacon，给出稳定性落地清单，并为「Beacon 真相交付基于 pi agent 做长程交付/创作/定时任务」设计架构。

---

## 1. 三家 Goal/长程机制对照

### 1.1 kun：Goal 是 thread 上的持久化对象 + 双协调器

- **数据模型**（`kun/src/contracts/threads.ts:43-65`）：`goal { objective, tokenBudget, tokensUsed, timeUsedSeconds, status: active|paused|blocked|usageLimited|budgetLimited|complete }`，随 thread 持久化。**无独立任务表**——goal 只是 thread 上的一等字段。
- **GoalTurnCoordinator**（记账，`loop/goal-turn-coordinator.ts`）：`begin()` 启计时、`recordUsage()` 累计 tokens（超 tokenBudget 自动翻 `usageLimited`）、`noteToolExecuted()/hasMadeProgress()`——除 goal 工具外的任何工具调用都算有进展。
- **GoalResumeCoordinator**（跨回合策略，`loop/goal-resume-coordinator.ts`）：
  - 回合结束仍 active → 调度续跑；**有进展重置计数，连续无进展才烧预算**；`maxNoProgressAttempts=5` → goal 转 `blocked`。
  - 指数退避 `2s × 2^(n-1)` 封顶 60s（`setTimeout` + `unref()`，不挡进程退出）。
  - **path A**：runtime 重启后立刻续跑（`reconcileOrphanedTurns()` → `resumeInterruptedGoals()`）；**path B**：回合正常/异常终止后定时续跑。
  - 防御：fire 前重校验 goal 仍 active + thread 不忙；`defer()` 处理 TurnCapacityError 且不烧 no-progress 预算。
- **完成/阻塞判定在 prompt 层**（`loop/continuation-instructions.ts:8-57`）：注入 objective + 预算 + completion audit（必须核实证据）+ blocked audit（**同一 blocker 连续 ≥3 个 goal turn 才能标 blocked**）。
- **稳定性机制**（详见前一份分析的机制清单）：TurnBudgetGate（model 请求边界原子保留 + compaction 后重查）、token-economy + request-history-hygiene（只改发送内容不动磁盘）、ContextCompactor（真实 provider prompt_tokens 驱动，6 倍信任因子）、tool-storm-breaker（相同工具调用窗口 8 内第 3 次抑制）、steering-queue（32 条/64KB 上限 + 终局 seal）、auto-model-router（4s 超时 flash/pro 路由）、**cache-first**（不可变前缀 sha256 指纹，漂移即抛错；实测热命中 94.7-98.1%）。

**对 Beacon 的价值**：① "无进展才烧预算 + 5 次封顶"防空转公式；② 完成/阻塞判定放 prompt 层而非代码层（证据制与 Beacon verifier 同构）；③ 预算门在边界原子保留；④ cache-first 指纹防漂移（对应 Beacon truth 层可做 digest 指纹）。

### 1.2 loopx：确定性 no-LLM 控制平面

- **三层持久化**：`registry.json`（goal 注册）→ Markdown+YAML frontmatter 的 `ACTIVE_GOAL_STATE.md`（人类可读主状态）→ `events.jsonl`（**追加式事件溯源**：幂等 event_id、fingerprint 冲突检测、流校验和、flock 串行）。
- **Quota**（`quota.py:389`）：`goal_quota_config { compute, window_hours, slot_minutes, allowed_slots, spent_slots, next_eligible_at }`；spend ledger 从 run 事件 `quota_slot_spent`/`quota_slot_voided` 重算；耗尽 → `throttled`。
- **should_run 判定流水线**（`quota/decision_summary.py:166-227`）：有序门卫 `capability_gate → workspace_guard → automation_prompt_upgrade_required`，然后 `should_run = normal_delivery ∨ recovery_delivery ∨ self_repair ∨ capability_repair ∨ workspace_repair`；覆盖规则：`replan 义务` 强制跑、`terminal_no_followup` 全禁、`inbox_reply_due` 强制跑。
- **调度契约**（`scheduler/scheduler_hint.py:963`）：纯函数把 quota 决策投影为宿主 cadence/backoff（如 active_work=3/10min、quiet_wait=30/120min、unchanged_wait=60/240min、human_gate=30/120min + 退避序列）；**通过宿主 automation 接口改写 rrule**（`FREQ=MINUTELY;INTERVAL=N`）实现唤醒；ack 流程 + host_update_failures 退避。
- **Handoff**（`handoff/`）：readiness 检查 + **delivery_contract**（post-handoff 退化检测：small_scale_streak / outcome_gap_streak 超阈值 → 强制 `minimum_scale` + `must_include=[coherent_artifact, targeted_validation, state_writeback]` + `spend_rule=spend_only_after_artifact_validation_writeback`）；跨宿主全走文件系统。
- **Claims/Leases**（`work_items/task_lease.py`）：软 claim（todo.claimed_by）+ 硬 lease（`task_lease_v0`：write_scopes 重叠冲突、版本号乐观并发、幂等 key、TTL、lease.lock flock）。
- **Claude Code 集成哲学**（`claude_goal_mode/README.md:3-7`）：**用原生 `/loop`，刻意不用 `/goal`**（/goal 从 transcript 判定完成，与确定性门冲突）；MCP 4 工具 `should_run / list_todos / claim_task / complete_task`，`complete_task` 仅成功后 `spend-slot`（spend-after-validated-writeback）；可选 `--harden` PreToolUse 全工具 gate（只读放行、should_run=false 拒绝非只读、write_scope 限制、probe fail-closed）。
- **Capabilities**（`capabilities/catalog.py`）：`issue-fix`、`reward-memory`、`periodic-report`（周报）、**`content-ops`（自媒体运营：source/angle/draft/feedback/publish-gate）**、`auto-research`。

**对 Beacon 的价值**：① 确定性 should_run 门卫链（不依赖 LLM 判定）；② quota 配额/槽位/耗尽态（S4 缺口直接答案）；③ rrule 改写式唤醒 + ack 契约；④ 硬 lease 的 write_scopes 冲突检测（S7 缺口直接答案）；⑤ spend-after-validated-writeback（与 Beacon 证据制同构）；⑥ 边界扫描（public_safe_compact_text 剥离本地路径/secret）。

### 1.3 oh-my-pi：组合式长程能力（无 cron 的一等公民缺失）

- **agentLoop**（`packages/agent/src/agent-loop.ts:515`）：事件流 `agent_start→turn_start→message_*→tool_execution_*→turn_end→agent_end`；`deadline` 硬超时、**steering 队列跨 run 存活**（abort 不清）、`agentLoopContinue` 断点续跑、`beforeModelCall` 可拦停。
- **AsyncJobManager**（`async/job-manager.ts:117`）：后台 bash/task job + 结果自动投递（500ms→30s 退避）、maxRunningJobs=15、smart 轮询阶梯 `[5s,10s,30s,60s,300s]`、owner 作用域 cancel。
- **autoresearch**（`coding-agent/src/autoresearch/`）：agent 驱动的自主实验循环（prompt 明言 "MUST keep iterating until interrupted or max iterations"）、git 分支隔离、SQLite 会话存储——形态是 **"agent 自己用工具驱动循环"而非代码层硬循环**。
- **swarm**（`packages/swarm-extension/`）：YAML DAG（pipeline/parallel/sequential）、wave 拓扑执行、单 agent 失败不中断整体、StateTracker 落盘、`omp-swarm` CLI。
- **创作**：`image_gen`（多 provider 文生图）、`browser`（全栈自动化 + relay daemon）、ArtifactManager（subagent 产出 artifact）。
- **缺失**：真正的 cron/定时调度器、把"某时刻自动触发某任务"做成一等公民。
- **CLI 无人值守友好**：`cleanse`（自动修代码质量）、`commit`、`worktree`、`stats/usage`、`browser-relay`（daemon）。

**对 Beacon 的价值**：① agentLoop 的 steering/deadline/pause 语义是 AgentDriver 的成熟参照；② autoresearch 的"agent 驱动循环 + git 隔离 + 会话存储"是长程交付的实验范式；③ 创作工具链（image/browser/artifact）直接支撑创作任务；④ 缺调度 → 与 kun/loopx 的调度机制互补。

---

## 2. Beacon 稳定性落地清单（合并三家机制）

基于前一份 8 维缺口（S4 预算、S7 并发、S6 量化）与本次源码级对照：

| # | 落地项 | 借鉴源 | Beacon 落点 | 优先级 |
|---|---|---|---|---|
| 1 | **quota 配额层**：GoalRun ledger 增加 `quota { compute, window, slots, spent, next_eligible_at }`；AgentDriver 每次 requeue 前跑确定性 should_run 门卫（capability→workspace→prompt_upgrade→delivery 链） | loopx quota.py:389 + decision_summary.py:166 | v2 GoalRun 状态机增加 `quota_exhausted|throttled` | **P0** |
| 2 | **无进展退避公式**：连续无进展（maxNoProgress=5）指数退避后 blocked；有进展重置 | kun goal-resume-coordinator.ts | AgentDriver requeue 策略 | **P0** |
| 3 | **spend-after-validated-writeback**：evidence 落盘后才计配额/报告完成 | loopx MCP complete_task + kun verifier | QA/implement 完成判定 | **P0** |
| 4 | **事件溯源强化**：execution.jsonl 升级为幂等 event_id + 校验和的追加式事件流（可回放重建状态） | loopx event_sourced_state.py:527 | DurableSupervisor 日志层 | **P1** |
| 5 | **硬 lease 并发所有权**：worker（implement/qa/design）领取 todo 带 write_scopes 冲突检测 + 版本乐观并发 | loopx task_lease.py | v2 workers 并行 | **P1** |
| 6 | **frontier 触发 replan 义务**：长 todo 链（≥15/≥20）、monitor 无变化 streak → 强制 replan 而非静默继续 | loopx goal_frontier.py:50 | GoalRun 状态机 | **P1** |
| 7 | **预算门原子保留**：model 请求边界做 quota 原子保留 + compaction 后重查 | kun turn-budget-gate.ts | AgentDriver turn 边界 | **P1** |
| 8 | **truth 指纹校验**：refreeze 的 truth 生成 sha256 digest，加载时校验防漂移 | kun cache/immutable-prefix.ts | change-refreeze 流程 | **P2** |
| 9 | **fail-closed 边界**：公共/私有边界扫描 + 配置不一致拒绝调度（不静默放行） | loopx boundary_authority.py + arbitration.py:100 | release/QA gate | **P2** |
| 10 | **Δ vs Baseline 评测**：压缩/恢复/quota 机制改进必须有量化证据（score 提升 + cost/task） | SLHA + kun 命中率统计 | 机制 freeze 门槛 | **P0** |

---

## 3. Beacon 真相交付 × pi agent 演进方案

### 3.1 目标

Beacon 保持「truth 层 + 状态机 + gate + evidence」的控制面不变，**把执行引擎切换/扩展为 oh-my-pi（pi agent）**，支撑三类任务：**长程交付任务、创作任务、定时任务**。

### 3.2 架构：Beacon 控制平面 × pi 执行引擎 × loopx/kun 调度契约

```text
┌────────────────────────── Beacon 控制平面（不变）──────────────────────────┐
│  truth 冻结 (refreeze) → goal ledger (sqlite) → 状态机 → evidence → gate    │
│  + 新增: quota 层 (P0-1) + lease 层 (P1-1) + event 溯源 (P1-1)             │
└───────────────────────────────────────────────────────────────────────────┘
          │ should_run / quota 决策                    ▲ evidence / artifact 回写
          ▼                                            │
┌────────────────────────── AgentDriver (适配器层) ──────────────────────────┐
│  driver_pi:    pi coding-agent CLI / agentLoop（长程交付、创作）            │
│  driver_host:  宿主 skill 直跑（现状兼容）                                  │
│  scheduler:    rrule 改写 / setInterval tick / async job 队列（定时任务）    │
└───────────────────────────────────────────────────────────────────────────┘
          │                                                        │
          ▼                                                        ▼
┌──────────────────── pi agent (执行面) ──────────────┐    ┌── 定时/无人值守 ──┐
│ agentLoop (steering/deadline/pause)                 │    │ kun GraphScheduler │
│ autoresearch 循环 (git 隔离 + 会话存储)              │    │ loopx scheduler    │
│ image_gen / browser / artifact (创作)               │    │ hint + ack         │
│ AsyncJobManager (后台 job)                          │    │ pi async jobs      │
└─────────────────────────────────────────────────────┘    └───────────────────┘
```

### 3.3 三类任务映射

**A. 长程交付任务**（Beacon truth → pi 执行）
1. Beacon refreeze truth 后创建 GoalRun；AgentDriver 选 `driver_pi`。
2. 每轮：Beacon 跑确定性 should_run + quota 门卫（loopx 式）→ 通过则给 pi 一个**有界 turn**（digest-only 上下文 + objective + budget + completion audit，kun continuation-instructions 式）。
3. pi 执行（agentLoop + worktree 隔离 + commit 产物）→ 回写 evidence/artifact（artifact 满足 delivery_contract 的 must_include 后计配额）。
4. 无进展退避公式 + 5 次封顶 → blocked；verifier 完成制不变；release 人工门不变。
5. 中断恢复：pi 的 `agentLoopContinue` 断点续跑 + Beacon checkpoint digest 注入（现有机制保留）。

**B. 创作任务**（内容创作、设计、图文）
- 用 pi 的 `image_gen` + `browser`（设计验证/截图）+ ArtifactManager 作为创作执行面。
- Beacon 侧用 kun 的 design-mode 思路：创作 turn 带 `guiDesignMode/guiDesignArtifact` 上下文（turn 上挂创作元数据）。
- 创作产物（图片/HTML 原型/文案）走同一 evidence 回写通道，满足"coherent_artifact"要求后进 review gate。
- 复用 loopx `content-ops` capability 的契约形状：`source → angle → draft → feedback → publish-gate`（自媒体运营的 publish-gate 正好对应 Beacon 的 release gate）。

**C. 定时任务**（周期性触发长程/创作）
- Beacon 不引入 cron；采用 **loopx scheduler-hint 契约**：quota 决策 → 投影为宿主 cadence（interval/backoff/unchanged_poll）→ 改写宿主 automation rrule → ack 回写。
- 短周期/图内调度用 kun GraphScheduler 的 setInterval tick（unref 不挡退出）。
- 一次性长任务用 pi AsyncJobManager（后台 bash/task job + 结果自动投递 + 退避）。
- 三个层级共用 quota/evidence 记账，防"定时任务无人值守跑飞"。

### 3.4 关键设计决策（对照三家）

| 决策点 | 选择 | 理由 |
|---|---|---|
| 完成判定放哪 | **prompt 层**（kun continuation-instructions） | 证据制与 Beacon verifier 同构；代码层只做记账 |
| should_run 是否要 LLM | **确定性 no-LLM**（loopx） | 门卫链不许幻觉；LLM 只用于执行 |
| 调度用不用 cron | **不用**（loopx rrule + kun tick + pi async） | 与宿主 automation 集成优于自建调度器 |
| 状态持久化 | **事件溯源 JSONL + sqlite ledger**（loopx 追加式 + Beacon 现状） | 可回放、可审计、可恢复 |
| 多 worker 所有权 | **硬 lease + write_scopes**（loopx task_lease） | S7 缺口的直接答案 |
| 预算 | **quota 槽位 + spend-after-validated-writeback**（loopx + kun 预算门） | S4 缺口的直接答案 |
| 创作执行面 | **pi image_gen/browser/artifact** | 现成工具链，无需自研 |

### 3.5 落地路线图

- **阶段 1（本轮冻结）**：P0-1 quota 层 + P0-2 Δ 评测口径 + P0-3 spend-after-validated-writeback（对齐 Beacon verifier）。
- **阶段 2（下一版本线）**：AgentDriver 增加 `driver_pi` 适配器（先接 pi CLI 的 `launch --agent` / worktree 模式，跑通长程交付闭环）；P1 lease、P1 事件溯源强化。
- **阶段 3**：创作任务（image_gen/browser 接入）→ 定时任务（scheduler-hint 契约 + ack）。

---

## 4. 结论

1. **kun 与 loopx 提供了互补的两套答案**：kun 证明"goal 挂在 thread 上 + 双协调器 + prompt 层判定"的轻量正确性；loopx 证明"确定性 should_run 门卫 + quota 槽位 + 硬 lease + 事件溯源"的重型完整性。Beacon 的 v2 GoalRun 已经处于两者之间的位置，缺口（S4/S7）两家都有现成机制可直接移植。
2. **pi agent 作为执行引擎成立**：agentLoop 的 steering/deadline/pause、autoresearch 的自主循环范式、创作工具链（image/browser/artifact）都齐备；唯一缺失的定时调度由 loopx scheduler-hint 契约 + kun GraphScheduler 补上——**Beacon 不需要自研执行引擎，只需要定义 driver 适配器契约**。
3. **风险与边界**：pi 是 agent-agnostic 的——Beacon 必须保持"truth/状态机/gate 在 Beacon、执行在 pi"的边界不模糊；pi 的 `--harden` 式工具门（fail-closed）应作为 driver_pi 的强制配置。

## 附：源码速查

- kun：`oss-sync/agents/agent-systems/kun/kun/kun/src/loop/{goal-turn-coordinator,goal-resume-coordinator,turn-budget-gate,continuation-instructions,context-compactor,steering-queue,tool-storm-breaker}.ts`、`cache/{immutable-prefix,ttl-lru-cache}.ts`、`docs/workflow-loop.md`
- loopx：`oss-sync/automation/autoresearch/loopx/loopx/{quota.py, control_plane/{goals,quota,scheduler,handoff,todos}, work_items/task_lease.py, event_sourced_state.py, claude_goal_mode/}`
- oh-my-pi：`oss-sync/agents/agent-systems/oh-my-pi/packages/{agent/src/agent-loop.ts, coding-agent/src/{async,autoresearch,autolearn,advisor}/, swarm-extension/, mnemopi/, snapcompact/}`
