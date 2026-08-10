# LoopX 能力解析与 beacon-goal 强化建议（2026-08）

> 镜像来源：`oss-sync/automation/autoresearch/loopx`（huangruiteng/loopx，commit 91d8ed0）
> 用途：为 v1.6.12 test-modernization 之外的 goal 长程能力强化提供可借用/可蒸馏清单。

## 一、LoopX 是什么

LoopX 是**面向长程 AI agent 工作的本地控制平面**：不替代 agent runtime，而是把
“目标、门禁、待办、范围、证据、配额、交接”做成一个持久化的状态内核，让 Codex、
Claude Code、Cursor 或自研 runner 在**有界回合**内执行，人工保留判断权。

核心心智模型：**agent-native Kanban**——卡片（todo）带身份、权限、证据、续接，
移动是校验过的操作符（claim / gate / monitor / writeback）；看板只是投影，
LoopX 状态才是事实源。

## 二、能力特性全解析

### 1. 状态内核（七层架构）

registry（已知 goal 清单）→ goal state（单 goal 活动状态）→ adapter pre-tick
（只读项目探针）→ run log（JSON/MD 报告）→ run history（紧凑索引）→
status/attention queue（第一屏该谁行动）→ compute quota（本地自动计算配额）。

关键：goal 是**生命周期目标对象**，不是聊天线程；能活过线程重载、网络中断、多个项目 agent。
事件溯源状态（`event_sourced_state.py`）+ 状态备份/迁移（`state_backup.py`、
`state_migration.py`）+ 状态投影（`state_projection.py`）。

### 2. 职责模型（四个所有者，互不越界）

| 角色 | 拥有 | 禁止 |
|---|---|---|
| Agent | 一次有界执行（计划/分析/工具） | 持久的 goal 生命周期、无界权限 |
| Provider | 外部调用与 readback | 域转移策略、todo 状态 |
| Capability | 结果契约、归一化、校验、typed transition 提案 | 调度、claim、门禁、生命周期写入 |
| Kernel | goal/todo/claim/gate/monitor/quota/writeback/recovery/scheduling | 域推理、provider 实现 |

执行路径 `Agent → Capability → Provider`；控制路径
`Provider readback → Capability transition → Kernel`。观察 ≠ 转移；provider 收据
≠ 进度，必须经 Capability 校验、Kernel 提交才算。

### 3. 五个产品问题

1. 目标是什么？（active goal + scope + authority）
2. 下一步是什么？（有序 user/agent todo、ownership、claim、lease）
3. 什么需要人判断？（**具体** user gate，而不是含糊的“等 owner”）
4. 证据变了吗？（紧凑 run history、validation、blocker、accepted writeback）
5. 循环还能继续吗？（quota、capability、safe fallback、scheduler hint、stop 条件）

### 4. 配额内核（quota）

- 每 goal 一个 compute 配额数（0~1 占空比），`window_hours`×`slot_minutes` 槽位账本；
- **应用顺序**：健康/安全 gate → operator gate → 证据等待 → focus 等待 → quota；
- `quota should-run` 输出 `decision / should_run / state / scheduler_hint`；
- 只在**校验后的 writeback** 之后 spend 一次；quiet skip/preflight/dry-run 不 spend；
- `handoff_budget`（交接文本上限 16 行 / 1800 字符）+ `interface_budget`。

### 5. 交互模式目录（可蒸馏的模式库，IP 编号稳定）

- Work Routing：IP-001 Bounded Delivery、IP-002 Blocked Priority With Safe Fallback、
  IP-003 Scoped Gate With Safe Fallback、IP-021 Per-Todo Capability Gate
- Human Decision：IP-004 Concrete User Todo Projection、IP-027 Deferred Gate Resume、
  IP-029 Handoff Todo Gate State、IP-014 Decision Write Preview And Append、
  IP-017 User Reward Lesson Promotion、IP-009 Active User Assistance
- State And Boundary：IP-005 State Projection Gap、IP-006 Checkpointed Scope Mismatch、
  IP-011 Authority Material Intake、IP-016 Task Lease Claim、
  IP-019 Peer Scoped Continuation、IP-020 Todo Claim/Supersede/Successor Lifecycle、
  IP-022 Claimed Todo Visibility、IP-026 Agent-Scoped No-Candidate Gap、
  IP-023 Status Neutral Run Window、IP-025 Experimental Diagnostic Sidecar Boundary、
  IP-028 Connector Runtime Boundary
- Evidence Lifecycle：IP-012 External Evidence Observation、
  IP-015 Benchmark Lifecycle Countability
- Planning Governance：IP-013 Autonomous Replan vs Advisory Dreaming、
  IP-010 Cadence Hint、IP-018 Plan To Todo Writeback、IP-024 Repair Delta Contract

### 6. 事故档案（长程鲁棒性的真实教训）

- outcome-floor-safe-bypass：`should_run=false` 与 `safe_bypass_allowed=true` 混在一个
  布尔里 → 执行器走错分支；教训：**“可否常规交付”和“是否有界恢复动作”必须分成两个显式答案**；
- agent-scoped-replan-precedence / user-gate-overreach：replan 与 user gate 的作用域越界；
- monitor-only-replan-stall：只监控不推进会 stall；
- default-workflow-planner-gap：默认 planner 缺口导致循环假死；
- standing-authorization-reprompt：长期授权被反复打断；
- auto-research-replan-multiround-badcase：多轮 replan 坏例。

### 7. 多 agent 与宿主桥

- 对等 agent：claim/lease/任务边界/capability/typed continuation，**不需要持久 leader**；
- 可见多 agent 启动器（`visible_multi_agent_launcher/tmux`）、worker bridge、
  session runtime、cross-runtime（Codex/Claude/Cursor）；
- 宿主桥：heartbeat prompt、codex-cli bootstrap/TUI/scheduler、slash commands、
  host loop activation、status server、Lark Kanban 投影（投影不成为事实源）。

### 8. 域能力与自进化

- 域能力包：issue-fix、content-ops、value-connectors、ml-experiment、benchmark、
  explore（图）、material lifecycle、decision-context、periodic-report、change-quality、
  semantic-preference、agent-turn-recall、integration-branch；
- 自进化：self-update、self-repair skill、ready-score（循环是否可重复跑）、presets、
  configuration catalog、Reward Memory（provider 中立、默认关闭）；
- 边界：public/private boundary check、authority registry、`loopx check` 发布前扫描。

## 三、beacon-goal 现状对照

beacon goal（loop-goal 模式）已有：

- 持久 goal run 状态（intent forks、decision cache、last_substep、resume tokens、
  `resume_action` 契约）；
- 阶段门禁：governance precheck → truth freeze → planner review →
  standard execution precheck（topology gate + workspace admission）→ implement →
  QA → release（人类 gate）；
- fill 管线（scaffold → fill-request/response → apply）与 truth review gate；
- harness 边界、no-fake-delivery、longrun driver（bounded turns、max-driver-turns）；
- worktree pool / service-scoped admission；
- 事故级教训散落在 research 文档（longrun-stability-analysis 等）。

明显缺口：

| 能力 | LoopX | beacon goal |
|---|---|---|
| 计算配额/spend 账本 | ✅ quota kernel + should-run | ❌ 无 |
| todo 级 claim/lease/supersede | ✅ IP-016/019/020/022 | ⚠️ 阶段级，无 todo 所有权 |
| 具体 user gate 投影 | ✅ IP-004/027/029 | ⚠️ 只有 blocking/user_decision_required |
| 有界回合 spend-once 契约 | ✅ IP-001 + handoff/interface budget | ⚠️ 有 max turns，无 spend 语义 |
| 模式目录 + 事故档案机制化 | ✅ catalog + incidents + canary | ❌ 只有零散文档 |
| 建议性 dreaming vs 自主 replan | ✅ IP-013 + dreaming 模块 | ❌ planner review 退化即硬停 |
| 循环就绪度评分 | ✅ ready-score | ❌ 无 |
| 用户纠错→持久 lesson | ✅ IP-017 reward overlay | ⚠️ memory 有，未绑定 run |
| 事件溯源/状态备份迁移 | ✅ event_sourced_state/backup/migration | ❌ JSON 覆盖式状态 |

## 四、可借用/蒸馏建议（按优先级）

### P0 — 直接蒸馏，收益最大

1. **配额内核（quota should-run）**：给 goal 增加 compute 配额 + 槽位账本，
   决策顺序固定为 健康门禁 → operator gate → 证据等待 → focus 等待 → 配额，
   且只在校验后的 writeback 后 spend；quiet skip 不 spend。这是长程任务“不空转”的核心。
2. **Todo 所有权模型**：把阶段推进细化成 todo claim / update / supersede / successor
   生命周期 + 任务级 lease + per-todo capability gate（复用现有 workspace admission）。
3. **具体 user gate 投影**：planner review / 阶段阻断时，把“等什么、问什么、恢复命令”
   落成具体 gate todo（IP-004/027），而不是抽象 `user_decision_required`。
   本轮 v1.6.12 planner-review 退化包就是活例：应标为 advisory 或要求重跑，而非硬停。
4. **Bounded turn + spend-once + 交接预算**：driver 回合契约化——
   选一个界内片段 → 交付/阻塞 → 聚焦校验 → 持久 writeback → spend 一次；
   交接文本限 16 行/1800 字符（handoff_budget）。
5. **should-run 双布尔契约**：恢复路径永远不与 skip 混在同一个布尔里
   （outcome-floor 事故教训），beacon 的 resume/continue 语义同样适用。

### P1 — 模式化蒸馏

6. **交互模式目录**：为 beacon goal 建 IP 风格目录（bounded delivery、safe fallback、
   gate resume、task lease、replan vs dreaming），每条配 canary 测试；
   把已有 longrun research 文档升级为正式 incidents 档案（含修复契约）。
7. **Advisory dreaming vs 自主 replan**：分离“只读建议”（不阻断、可并入下一回合）与
   “自主 replan”（必须经过 review/freeze 门禁）；避免退化 fallback 产生假 P1 硬停。
8. **Ready-score**：longrun 启动前评分（truth frozen、worktree reconciled、admission、
   quota、证据新鲜度），不足则给出具体修复 todo 而不是直接开跑。
9. **用户纠错 → 持久操作 lesson**：把用户对某一回合的纠错写成 run-bound 事件/lesson，
   后续 tick 必须可见（IP-017），而非只留在聊天里。

### P2 — 参考实现

10. 事件溯源状态 + 备份/迁移（长程 state 可回放、可恢复）；
11. 可见多 agent 工作台（peer claim/lease 可视化，参考 visible_multi_agent_*）；
12. Capability/Provider 注册与归一化（beacon 的 host bridge 可对齐
    `Agent → Capability → Provider` 双向路径）；
13. 状态服务器/投影只读化（board/status 一律消费投影，事实源保持 CLI 状态）。

## 五、落地路径建议

- 纳入 v1.6.12 goal 强化 feature（可与 test-modernization 并行开第二个 lake），
  按 P0(1-5) → P1(6-9) → P2(10-13) 分批 plan → truth → freeze；
- 每个 P0 项先写一条 IP 模式 + 一条 canary 测试（对照 LoopX 的 pattern-to-canary 矩阵）；
- 事故档案与模式目录放进 `skills/beacon/beacon-goal/references/`，由 goal 模式文件链接。
