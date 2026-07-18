---
slug: beacon-goalrun-main-axis-change-coherence
version: v1.6.7
also_applies: v2.0.0
status: support_advisory
authority: beacon-pln-review
kind: planner_review
date: 2026-07-18
user_intent: "不论 v1.6.7 或 v2.0.0 做 change，都要重新生成用户主轴 GoalRun，保证业务状态机自洽、第一性原理意图、实现顺序、防空中阁楼；用一张主轴把 11 湖嵌进去"
---

# Planner Review: GoalRun 用户主轴 · change 必重生 · 11 湖嵌入

## intent_snapshot

| 要什么 | 不要什么 |
|--------|----------|
| change 后 **重生成主轴**（意图→阶段→子机→done_when→非法转移） | 只改一个 feature 切片文档就 implement |
| v1.6.7 与 v2.0.0 **同一主轴语法** | 两套互相打架的完成定义 |
| 11 湖 **嵌进 GoalRun**，各是子状态机/守卫 | 11 个独立插件各跑各的 |
| 第一性原理：用户一句话能否合法走到验收 | 功能点堆叠可绿 |

## 确定结论（本 review 锁定建议）

### GO 建议（请用户确认后 change）

> **不论 docs 线是 v1.6.7 还是 v2.0.0：凡 `beacon-gen-change` / refreeze 触及「承诺、验收、阶段、并行、长跑、入口轨」之一，必须重新产出/更新「用户主轴 GoalRun 投影」，不得只改单湖 truth 就进 implement。**

| ID | 建议规则 |
|----|----------|
| UD-AXIS-001 | change 触发 **主轴重生**（见 §3 触发表） |
| UD-AXIS-002 | 主轴工件权威：**GoalRun 主图 + done_when + 子机挂载表 + 实现 Wave 序** |
| UD-AXIS-003 | v1.6.7 与 v2.0.0 **共用主轴状态名**（下表）；版本只扩子机/载体 |
| UD-AXIS-004 | domain-bearing 时 done_when **必须**含 `domain_fsm_coverage`（已有 AC-PGR/AC-V2-PGO-010） |
| UD-AXIS-005 | 任何子机终态 **不得** 直接 `completed` / `release_confirmed` |

---

# 1. 第一性原理：用户主轴是什么

用户只关心一条链：

```text
一句话意图
  → 拆成可冻结需求（含业务序）
  → 按序实现（可并行但不乱写）
  → 可证明验收
  → 人工发版
```

Beacon/Loom 的 **唯一主账本** 应是 **GoalRun**（v1.6.7 durable 已定义；runtime 已有 stages/done_when/verifier）。

**湖不是主轴**；湖是 **挂在主轴边上的能力/守卫/旁路**。

---

# 2. 一张用户主轴 GoalRun（嵌入 11 湖）

## 2.1 主状态（跨 v1.6.7 / v2.0.0 稳定）

沿用并 **升格为 program 级权威**（今日写在 durable 湖；应同时出现在 product-goal / orchestrator）：

```text
created
  → running
  → stage_active{plan | truth | design? | implement | qa | release}
       ↻ host_interrupted ──resume-pack──► stage_active(last_substep)
       → stage_blocked (streak; ≥3 可 blocked)
  → awaiting_verifier
  → completed                 [guard: verifier.refs ∧ done_when]
  → release_pending
  → release_confirmed         [guard: human only]
```

**非法（全局）**

| 禁止 | 原因 |
|------|------|
| * → completed 无 verifier | 假交付 |
| host_interrupted → completed | 断会话当完成 |
| stage_blocked → completed 未清 blocker | 带伤过门 |
| * → release_confirmed 自动 | 假发版 |
| Subagent/Driver/Ralph → completed | 子机抢主权 |

## 2.2 子状态机挂载（11 湖嵌法）

```text
                    ┌─ L0 InstallSurface ─────────────────────┐
                    │  loom-brand-surface                      │
                    │  dual_install | no_replace_beacon        │
                    │  选择 public_entry: beacon-goal|loom-goal │
                    └──────────────────┬──────────────────────┘
                                       ▼
┌──────────────────────────────── GoalRun (主轴) ────────────────────────────────┐
│ created → running → stage_active* → awaiting_verifier → completed → release_*   │
│                                                                                 │
│  stage 技能/门禁（渐进加载，不是切片堆叠）:                                      │
│   plan    ← orchestrator 拆海/program                                            │
│   truth   ← domain-fsm-authority 硬门（freeze/clarity）                           │
│             golden-commerce 正负夹具                                              │
│   design? ← ui-state-matrix-ship-gate（ux_required 时）                           │
│   implement ← ralph-implement-boundary（delegate 旁路，不写 verdict）              │
│               main-star-satellite-pool（拓扑）                                    │
│               loom-goal-optional-subagent（opt-in 执行 fan-out）                   │
│   qa      ← domain-fsm-qa-gate（legal/illegal / domain_fsm_coverage）             │
│   release ← human gate only                                                      │
│                                                                                 │
│  长跑旁路（不改 complete 权）:                                                    │
│   SupervisorSession + AgentDriver ← goal-durable-longrun                         │
│   agent_trace 旁路 ← loom-goal-trace-bundle                                      │
│                                                                                 │
│  done_when 默认: domain_fsm + evidence_chain + continuous_qa                      │
│               (+ design_* 若 ux_required)                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 11 湖 → 主轴角色一览

| # | 湖 | 嵌在主轴哪 | 角色类型 |
|---|-----|------------|----------|
| 1 | product-goal-orchestrator / PGR | **主轴 owner** | 状态机权威 + facade |
| 2 | main-star-satellite-pool | implement 拓扑 | 结构守卫 |
| 3 | domain-fsm-authority | truth 硬门 | **L2 业务序** |
| 4 | golden-commerce-fixture | truth/qa 夹具 | 负例防空壳 |
| 5 | domain-fsm-qa-gate | qa 硬门 | legal/illegal |
| 6 | ui-state-matrix-ship-gate | design/ship | UX 状态矩阵 |
| 7 | ralph-implement-boundary | implement 委托 | 禁写 verdict |
| 8 | goal-durable-longrun | 长跑旁路 | Supervisor+Driver |
| 9 | loom-brand-surface | **L0 入口前** | 双轨安装 |
|10 | loom-goal-optional-subagent | implement 并行执行 | SubagentSession |
|11 | loom-goal-trace-bundle | 长跑可观测 | 排查面 |

**插件化禁令**：实现某湖时必须回答「它改变 GoalRun 的哪条边/哪个 guard？」答不上来 = 切片，change 应拒或补主轴。

---

# 3. change 时强制「主轴重生」

## 3.1 现有能力（可挂，不必从零发明）

| 能力 | 位置 | 用途 |
|------|------|------|
| GoalRun FSM | v1.6.7 durable truth + runtime JSON | 主轴状态 |
| stages / done_when / verifier | `product_goal_runtime` | 运行时主轴 |
| domain_fsm 硬门 | v1.6.7/v2 domain-fsm-authority | 业务序 |
| change → refreeze-chain | `beacon-gen-change` / `beacon-gen-refreeze` | 需求重冻 |
| progressive skills | product_goal_runtime | 阶段加载 |
| parallel_plan | product_goal_runtime | 并行规划（执行待 loom-subagent） |

## 3.2 触发：何时必须重生主轴

| 变更类型 | 主轴重生？ | 重生内容 |
|----------|------------|----------|
| 改 AC/承诺/验收 | **必须** | done_when、legal walks、非法转移 |
| 改阶段顺序/增减 stage | **必须** | stage_active 集合与技能 map |
| 改并行/subagent/worktree | **必须** | 子机挂载 + 合并守卫 |
| 改 longrun/driver/supervise | **必须** | 旁路 FSM + 与 complete 隔离 |
| 改入口品牌/双装（Loom） | **必须** | L0 + public_entry 绑定 |
| 改 domain FSM/实体序 | **必须** | L2 + done_when domain 绑定 |
| 纯文案/typo | 否 | — |
| 纯任务勾选/证据索引 | 否 | — |

## 3.3 change 主轴重生流水线（两版共用）

```text
1. 用户/GO 接受 change scope
2. 更新受影响湖 truth（change）
3. 【新增强制】再生主轴工件 GoalRun-Main-Axis：
     a. 用户意图一行（第一性原理）
     b. GoalRun 主状态图（上表）
     c. 本 program 湖 → 挂载点表（11 行）
     d. done_when 列表（含 domain_fsm_coverage 若 domain-bearing）
     e. 全局非法转移表
     f. 实现 Wave 序（防切片排期）
     g. 与 v1.6.7 差异（若 v2/Loom）
4. domain-bearing：刷新 domain FSM + illegal TC 槽
5. requirement_clarity / freeze fail-closed 若主轴缺项
6. refreeze-chain
7. 才允许 implement
```

**建议工件路径（实现时）**

```text
docs/beacon/<ver>/programs/<program>/goalrun-main-axis.md
docs/beacon/<ver>/.machine/goalrun/main-axis.json   # 投影，非权威
```

v1.6.7 program：`beacon-product-goal-domain-delivery-v167`  
v2.0.0 program：`beacon-v2-product-goal-parallel-v200`

## 3.4 第一性原理检查清单（change 出口必过）

| # | 问题 | 不过则 |
|---|------|--------|
| Q1 | 用户一句话的 **成功** 是否可观测？ | 拒 freeze |
| Q2 | 是否存在 **非法捷径** complete/release？ | 拒 freeze |
| Q3 | domain-bearing 是否有 **实体前置 + 合法 walk**？ | 拒 freeze |
| Q4 | 本 change 的实现是否映射到 **主轴边/守卫**？ | 标切片，拆 scope 或补轴 |
| Q5 | 实现 Wave 是否依赖未完成的 L2/L0？ | 调整序 |
| Q6 | 子机是否可能 **绕过** awaiting_verifier？ | 拒 |

---

# 4. 实现顺序（挂在主轴上的 Wave）

与前次 review 一致，**钉死**：

```text
Wave 0  L0  loom-brand-surface
Wave 1  L1+L2  orchestrator(=主轴 owner) + domain-fsm-authority
               → golden → domain-fsm-qa-gate → ui-ship
               + ralph-boundary
Wave 2  L1并行  main-star-satellite → loom-optional-subagent
Wave 3  L1长跑  durable-longrun → loom-trace-bundle
Wave 4  载体    rust-kernel / default 轨策略（人工）
```

**change 重生主轴时必须重算 Wave**：新增依赖不得插队破坏 L2 在 implement 前。

---

# 5. v1.6.7 vs v2.0.0

| 维度 | v1.6.7 | v2.0.0 / Loom |
|------|--------|----------------|
| 主轴状态名 | GoalRun durable FSM | **同名继承** |
| 入口 | `$beacon-goal` | + `$loom-goal` 双轨，语义同构 |
| 子机 | Supervisor, Driver, Ralph, parallel_plan | + SubagentSession 真执行, Trace, Brand L0 |
| domain | 七湖+硬门 | Option A 并入 program |
| change | refreeze-chain | **同一规则 + 主轴重生** |

**差异只允许**：子机集合、载体（Python/Rust）、安装轨；**不允许**两套 complete 定义。

---

# 6. 现有能力如何「接」主轴重生（不空谈）

| 步骤 | 接法 |
|------|------|
| 写主轴 | change 模板强制章节；program `goalrun-main-axis.md` |
| 校验 | 扩展 requirement_clarity / freeze：缺主轴章节 → block |
| 运行时 | `create_goal_run` 已有 stages/done_when；change 后 **同步** default done_when 与 stage map |
| domain | 已有 domain-fsm 硬门；主轴 Q3 直接调 |
| 并行 | parallel_plan 已有；subagent 湖补执行边 |
| 长跑 | durable FSM 已是主轴子集；升格为 program 引用而非仅 durable 私货 |
| 防切片 | implement 前 check：任务 ↔ 主轴边 映射表 |

---

# 7. Findings

| ID | Sev | Finding |
|----|-----|---------|
| F-01 | P0 | **应确定**：v1.6.7/v2.0.0 的 change **均需主轴重生**（触发表 §3.2） |
| F-02 | P0 | 主轴权威今日 **散落 durable 湖**；应 **升格 program 级 GoalRun 图** 并被 orchestrator 引用 |
| F-03 | P0 | 11 湖可嵌主轴（§2.2）；缺此图则 Loom 三湖必变插件 |
| F-04 | P0 | 第一性原理出口清单 Q1–Q6 应进 freeze 硬门（clarity） |
| F-05 | P1 | 现有 refreeze-chain **未**强制主轴工件；需 change 合同扩展 |
| F-06 | P1 | runtime 已具备 stages/done_when/verifier，主轴重生要 **驱动这些字段** 而非另起文档空转 |
| F-07 | P2 | topology_order 补 durable；durable→ralph 改软依赖（前 review）随主轴 R 修订一并改 |

---

# 8. recommended_route

```text
User GO: UD-AXIS-001..005
  → gen-change（两版可各开一刀，合同同文）:
     a) program goalrun-main-axis.md 模板 + 11 湖挂载表
     b) product-goal / orchestrator：引用主轴为权威
     c) gen-change / freeze / clarity：触发主轴重生与 fail-closed
  → freeze
  → implement（先校验器与模板，再 Loom 能力）
  → qa：change 场景测「缺主轴拒 freeze」
```

---

# 9. 大白话

1. **主轴只有一条：GoalRun**（创建→干活→可中断→等 verifier→完成→人发版）。  
2. **11 湖都是挂件**：要么守业务序，要么帮并行/长跑/装轨/记日志；**谁都不能自己宣布完工**。  
3. **以后 change（1.6.7 或 2.0.0）**：改了承诺/阶段/并行/长跑/业务序/入口，就必须 **重画这张主轴** 再冻结，否则必成空中楼阁。  
4. **现成能力够用**：durable 状态机、runtime stages、domain 硬门、refreeze-chain——缺的是 **强制「主轴重生」工序** 和 **program 级总图**。  

**一句话**：先定「change 必重生 GoalRun 主轴」；把 11 湖嵌进这张图；实现才不会各做各的插件。
