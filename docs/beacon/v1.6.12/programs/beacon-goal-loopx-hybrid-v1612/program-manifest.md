---
program_slug: beacon-goal-loopx-hybrid-v1612
version: v1.6.12
plan_mode: auto
plan_mode_reason: cli_flag
scope_mode: full_parity
lake_or_ocean: 海
---

# Program Manifest

User utterance: 确保 beacon 生命周期能力特性不受影响，完整把 loopx 最优价值能力接入 beacon goal：配额内核、todo 所有权、具体 user gate、有界回合预算、模式目录与事故档案，让全流程足够完善

## 范围与硬护栏

目标：把 LoopX（`oss-sync/automation/autoresearch/loopx`）最有价值的能力接入
**beacon goal 公共面**（goal 命令 + loop-goal 模式 + goal 运行时），让长程任务全流程足够完善。

硬护栏（用户明确要求，P0 验收项）：

1. **不改变 beacon 生命周期能力特性**：plan/truth/design/implement/qa/release 阶段门禁、
   worktree admission、双轴版本规则、truth fill 管线、truth review gate、release 人类门禁
   全部保持现状；接入只发生在 goal 编排层。
2. 新能力默认关闭或渐进开关（env / goal mode flag），不改变既有 goal run 状态 schema
   （新增字段一律可选）。
3. 不假交付：每个湖必须有 canary 测试 + 可验证 AC，禁止 docs-only 或 placeholder 闭环。
4. LoopX 能力按“借用（接口对齐）”或“蒸馏（重新实现到 beacon 语义）”，不做整体代码搬运。

## 湖拆分（feature 包粒度，每个湖独立 plan → truth → freeze）

### Lake-1 `beacon-goal-quota-kernel-v1612`（P0）

- 借用：LoopX compute quota（占空比、window×slot 账本）、`quota should-run` 决策顺序
  （健康门禁 → operator gate → 证据等待 → focus 等待 → 配额）、spend-once、
  “可否常规交付”与“是否有界恢复动作”双布尔契约（outcome-floor 事故教训）。
- 落地：`beacon/utils/goal_quota.py`（新）；goal run 状态增加 quota 字段；
  resume/status 输出增加 should-run 视图。
- 验收：长程 run 在 focus/evidence 等待时不 spend；恢复路径独立布尔；quota=0 时可见不可跑。

### Lake-2 `beacon-goal-todo-ownership-v1612`（P0）

- 借用：IP-016 Task Lease、IP-019 Peer Scoped Continuation、IP-020 Claim/Supersede/
  Successor、IP-022 Claimed Todo Visibility、IP-021 Per-Todo Capability Gate。
- 落地：goal 状态增加 todo 表（owner/claim/lease/successor）；goal tick 推进基于 claim；
  per-todo capability gate 绑定现有 workspace admission。
- 验收：两个对等 agent 不能同时 claim 同一 todo；supersede 保留历史；无 claim 不执行。

### Lake-3 `beacon-goal-user-gate-projection-v1612`（P0）

- 借用：IP-004 Concrete User Todo Projection、IP-027 Deferred Gate Resume、
  IP-029 Handoff Todo Gate State、IP-014 Decision Write Preview And Append。
- 落地：阶段阻断（含 planner-review user_decision_required）输出具体 gate 卡片
  （问题、上下文、可选恢复命令），并进入决策缓存（对齐 AC-033：同 key 不重复提问）。
- 验收：每个阻断都有 gate todo + resume_action；重复决策不再二次提问。

### Lake-4 `beacon-goal-bounded-turn-budget-v1612`（P0）

- 借用：IP-001 Bounded Delivery（选择→交付/阻塞→聚焦校验→持久 writeback→spend once）、
  handoff_budget（16 行/1800 字符）、interface_budget、turn_identity。
- 落地：driver 回合契约化；交接文本上限；turn instance id 进入 run 历史。
- 验收：driver turn 无 writeback 不 spend；交接超限截断且有记录。

### Lake-5 `beacon-goal-pattern-catalog-v1612`（P1）

- 借用：interaction-pattern-catalog + incidents 档案、IP-013 Advisory Dreaming vs
  Autonomous Replan、ready-score、IP-017 User Reward Lesson Promotion。
- 落地：`skills/beacon/beacon-goal/references/patterns/` 目录 + incidents 档案；
  planner-review 退化（fallback）时降级为 advisory 而非硬停；`goal ready-score` 命令；
  用户纠错绑定 run 事件。
- 验收：模式目录每条配 canary；退化 review 不再产生假 P1 硬停。

## Parity Matrix（LoopX ↔ beacon-goal ↔ 接入方式）

| LoopX 能力 | beacon goal 现状 | 接入方式 | 影响面 |
|---|---|---|---|
| quota should-run + spend ledger | 无 | 蒸馏：新增 goal_quota 模块，goal 状态加可选字段 | goal-only |
| todo claim/lease/supersede | 阶段级状态 | 蒸馏：goal todo 表 + claim 推进 | goal-only |
| concrete user gate projection | user_decision_required 抽象值 | 借用：gate 卡片 + decision cache | goal-only |
| bounded delivery + handoff budget | max-driver-turns 无预算语义 | 借用：回合契约 + 文本上限 | goal-only |
| pattern catalog + incidents | 零散 research 文档 | 蒸馏：references/patterns + canary | goal-only |
| dreaming vs replan | 无（退化 review 即硬停） | 蒸馏：advisory 降级 | goal-only |
| ready-score | 无 | 借用：goal ready-score 命令 | goal-only |
| user lesson promotion | memory 未绑定 run | 借用：run-bound lesson 事件 | goal-only |
| event-sourced state / backup / migration | JSON 覆盖式 | 延后（Deferral） | — |
| visible multi-agent board | 无 | 延后 | — |
| capability/provider registry | skill registry | 延后 | — |

## Deferral Ledger（P2，不在本 program 范围）

| ID | 能力 | 原因 | 影响 |
|---|---|---|---|
| D-LH-001 | 事件溯源状态 + 备份/迁移 | 改动 state 底座，违背“生命周期不受影响”护栏 | 延后到独立 lake |
| D-LH-002 | 可见多 agent 工作台 | 属于 UI/投影面，非 goal 内核 | 延后 |
| D-LH-003 | Capability/Provider 注册框架 | 需要跨 harness 设计 | 延后 |

## 风险与护栏（验收时逐条核对）

1. 生命周期门禁（truth/freeze/implement/qa/release、admission、双轴）测试必须保持全绿。
2. 既有 goal run 状态文件向后兼容（新增字段可选，读旧文件不报错）。
3. 新模块默认 off；开启需显式 flag/env。
4. 每个湖冻结前必须过 pln-review；canary 测试随湖一起冻结。
5. 与 `test-modernization-v1612`（696 测试迁移）并行，不互相依赖。

## 推荐路由

- 本 program 已完成 P0（intent + plan_mode=auto）；P1–P4 按 Lake-1 → Lake-5 顺序推进。
- 每个湖：`beacon truth`（gen-truth 语义）→ pln-review → freeze → goal implement admission
  → worktree 实现 → 合并回 main。
- 下一步 harness：`goal`（逐湖走 plan → truth → freeze）。
