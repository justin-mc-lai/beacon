---
slug: beacon-v2-program-coherence-fsm
version: v2.0.0
status: support_advisory
authority: beacon-pln-review
kind: planner_review
date: 2026-07-18
user_intent: "分析 v2.0.0 需求是否整体对应用户意图的业务状态机、逻辑自洽可闭环；原有需求叠加 Loom 新湖是否有顺序并保持业务状态机，避免功能切片"
---

# Planner Review: v2.0.0 整体自洽性 · 业务状态机 · 防切片

## intent_snapshot

用户要的不是「又堆几个 feature 包」，而是：

1. **一句话 goal → 可验收交付**（全生命周期）
2. 交付过程 **有业务/编排有限状态机**，不是功能点拼接
3. **v1.6.7 权威能力** 进化到 v2/Loom 时 **顺序正确、可闭环**
4. 新立 Loom 三湖 **叠加上去不打乱** 原 domain/goal 状态机

## scope_mode

- **海**：program `beacon-v2-product-goal-parallel-v200`（11 湖 + rust kernel）
- **审什么**：状态机层级、依赖序、done_when、新旧叠加、切片风险
- **不做什么**：不改 truth、不实现、不 QA verdict

---

# 1. 用户意图对应的「总状态机」应是什么

应存在 **三层状态机**（缺一层就会变切片）：

```text
L0  InstallSurface（装什么轨）
    v1_only | dual_installed | loom_preview | (W4+) optional default
         │
L1  ProductGoalRun（交付编排 — 用户感知主轴）
    created → running → stage_active → host_interrupted?
         → stage_blocked | awaiting_verifier → completed
         → release_pending → (human) release_confirmed
    并行旁路: SubagentSession idle→…→done（不跳 complete）
    长跑旁路: AgentDriver / SupervisorSession
         │
L2  DomainAggregate FSM（业务真值 — 防空中楼阁）
    每业务特征: Domain Model + legal/illegal + entity precedence
    QA: domain_fsm_coverage 绑 done_when
```

| 层 | 回答的问题 | 权威湖 |
|----|------------|--------|
| L0 | 跑 beacon 还是 loom？状态写哪？ | loom-brand-surface |
| L1 | goal 跑到哪一步？能否 complete？ | orchestrator + durable-longrun + ralph + subagent + trace |
| L2 | 业务上能不能这么走？（有商品才能下单） | domain-fsm-authority + golden + domain-fsm-qa + ui-ship |

**用户意图闭环条件**：L1 complete **且**（domain-bearing 时）L2 coverage 过；release **仅人工**；L0 不默认盖生产。

---

# 2. 现有 11 湖是否映射到这三层？

| 湖 | 层 | 状态机强度 | 角色 |
|----|----|------------|------|
| product-goal-orchestrator | L1 | **弱**（AC 多，缺显式 GoalRun FSM 段） | 入口/阶段/done |
| main-star-satellite-pool | L1 并行拓扑 | **中**（模式/合并/禁写） | 结构约束 |
| domain-fsm-authority | L2 | **强** | 业务 FSM 硬门 |
| golden-commerce-fixture | L2 夹具 | **弱**（包内少 FSM 段，靠夹具） | 正负例 |
| domain-fsm-qa-gate | L2 验收 | **中强** | legal/illegal 强制 |
| ui-state-matrix-ship-gate | L2 UX | **中** | 界面状态矩阵 |
| ralph-implement-boundary | L1 委托 | **中** | 禁写 verdict |
| goal-durable-longrun | L1 长跑 | **强**（GoalRun+Driver+Supervisor FSM） | 耐久+自动续 |
| **loom-brand-surface** | **L0** | **中**（安装非法路径） | 双轨品牌 |
| **loom-goal-optional-subagent** | **L1 并行执行** | **强**（SubagentSession FSM） | plan→spawn→merge |
| **loom-goal-trace-bundle** | **L1 可观测** | **中** | 排查面，非业务真值 |
| rust-kernel-redesign | 平台内核 | 厚 | 实现载体，非业务域 |

**判断**：层级 **大体齐**；问题在 **L1 总图未写成一张跨湖状态机**，且 **部分 P0 湖 FSM 文档强度不均**。

---

# 3. 逻辑是否自洽、能否闭环？

## 3.1 自洽点（好）

| 点 | 说明 |
|----|------|
| 防假交付一致 | complete 需 verifier；release 永不 auto（orchestrator / durable / subagent / ralph 一致） |
| 防切片核心在 | domain-fsm-authority + qa-gate + golden 负例 + done_when domain_fsm_coverage |
| 并行不乱写 | 卫星禁写主 truth；merge 只回主星（MSS + subagent 对齐） |
| 长跑不抢验收 | host_interrupted ≠ stage_blocked；budget 不 complete |
| Loom 不抢生产 | 双装、不默认替换、状态隔离 |
| 委托边界 | Ralph 只 implement，不写 QA/release verdict |

## 3.2 张力 / 不自洽风险（P0–P1）

| ID | Sev | 问题 | 影响 |
|----|-----|------|------|
| C-01 | P0 | **双 facade 文案冲突**：PGO 写「唯一 beacon-goal」；Loom 写「loom-goal」 | 读者以为违 AC；需 **「语义单入口 × 安装双轨」** 统一段写进 orchestrator R4 |
| C-02 | P0 | **L1 总状态机未单点成文** | 实现易按湖切功能，拼不出用户旅程 |
| C-03 | P1 | **durable-longrun depends_on ralph** | 长跑逻辑依赖「边界合同」略拧；建议 depends **软依赖/文档依赖**，运行时不强制 ralph 包 |
| C-04 | P1 | **topology_order 缺 durable-longrun** | 图与 lakes 列表不一致，排期易漏 |
| C-05 | P1 | **orchestrator / MSS / golden 包内 Domain FSM 段弱** | L2 靠「硬门湖」兜底，但 L1 包自己不像「有状态业务」 |
| C-06 | P1 | **subagent 与 durable/driver 组合序未写清** | 先 attach driver 还是先 fan-out？并发谁写 execution.jsonl？ |
| C-07 | P1 | **trace 与 resume 权威** 写清了，但 **loom 状态根** 下 traces 路径双轨未与 durable 路径统一 FSM |
| C-08 | P2 | **rust-kernel** 与 product-goal program 并行，**未在 feature-graph lakes 列表** | 易做成另一条切片实现 |

## 3.3 闭环判定

| 闭环问题 | 答案 |
|----------|------|
| 用户一句话能否定义终点？ | **能**（awaiting_verifier→completed + human release） |
| domain-bearing 能否挡空壳绿？ | **合同能**（DFSM+FQA）；**实现/执行须 enforce** |
| 叠加 Loom 后能否仍闭环？ | **能**，若 L0 不污染 L1 权威，且 subagent 不得 complete |
| 现在是否「已闭环实现」？ | **否**（多湖仍 plan/parity/docs；subagent 未 spawn）——本 review 评的是 **需求结构** |

---

# 4. 原有需求 + Loom 新需求：顺序是否正确？

## 4.1 推荐业务/交付实现序（防切片）

```text
Wave 0  L0  loom-brand-surface
        （先有轨，再往轨上挂能力；双装验收矩阵）

Wave 1  L1  core  product-goal-orchestrator
              + ralph-implement-boundary（委托边界）
        L2  core  domain-fsm-authority
              → golden-commerce-fixture
              → domain-fsm-qa-gate
              → ui-state-matrix-ship-gate（ux_required）

Wave 2  L1  parallel topology  main-star-satellite-pool
              → loom-goal-optional-subagent（真执行 fan-out）

Wave 3  L1  longrun  goal-durable-longrun（含 v167 parity）
              → loom-goal-trace-bundle（挂 driver）

Wave 4  platform  rust-kernel + 可选 default loom/beacon policy（人工 GO）
```

## 4.2 与当前 graph 对比

| 项 | 当前 graph | 评价 |
|----|------------|------|
| domain 链 | authority→golden→qa-gate | ✅ 正确 |
| MSS → durable | durable depends MSS | ✅ 合理 |
| subagent depends brand+MSS+orchestrator | ✅ 正确 |
| trace depends brand+durable | ✅ 正确 |
| brand deps=[] 与 orchestrator 并行 | ⚠️ 可并行 **文档**；**实现**应 Wave0 先于用户可见 loom CLI |
| durable depends ralph | ⚠️ 建议改为文档依赖，避免错误实现序 |
| topology_order 无 durable | ❌ 应补上 |

## 4.3 「叠加」会不会打成功能切片？

| 风险 | 会否 | 缓解 |
|------|------|------|
| Loom 三湖变成独立小工具 | **会**，若单独实现不接 L1 GoalRun | 强制：subagent/trace **仅** goal run 子状态 |
| 只做 brand 包装 | **会** | brand 完成不宣称 goal 能力完成 |
| domain 与 goal 脱节 | **会**，若 done_when 不绑 domain_fsm_coverage | AC-V2-PGO-010 必须实现 enforce |
| 并行 fan-out 当完成 | **会** | AC-LOOM-SA-010 已禁；实现须测 |
| 长跑当发版 | **会** | release 人工；已有合同 |

**结论**：合同 **方向对**（有 L2 硬门 + L1 防自证）；**缺口是跨湖「总状态机叙事 + 组合序 + 实现 enforce」**，不是「完全没状态机」。

---

# 5. 跨湖「主状态机」应显式写成（建议写入 orchestrator R4）

### GoalRun（用户主轴，唯一 complete 权）

```text
created
  → running / stage_active{plan,truth,design?,implement,qa,release}
  → host_interrupted  ↔  (resume digest) stage_active
  → stage_blocked (含 budget / deps)
  → awaiting_verifier → completed   [guard: verifier.refs]
  → release_pending → release_confirmed  [guard: human only]
```

### 子机（不得跃迁到 completed）

| 子机 | 合法终态 | 禁止 |
|------|----------|------|
| SupervisorSession | detached / active | complete |
| AgentDriver | halt_* | complete/release |
| SubagentSession | done/halted | complete/release |
| DesignStage | done/blocked | complete |
| RalphDelegate | handoff_qa | verdict |

### Domain walk（domain-bearing）

```text
goal.done_when includes domain_fsm_coverage
  → QA 无 legal/illegal → 不得 release_ready
  → golden 负例必须 fail
```

### InstallSurface

```text
install_loom ↛ replace_beacon
dual_installed → state roots isolated
```

---

# 6. Findings 汇总

| ID | Sev | Finding |
|----|-----|---------|
| F-01 | P0 | **意图结构正确**：L1 交付 + L2 业务序 + 防自证；不是纯功能清单 |
| F-02 | P0 | **缺一张跨湖 GoalRun 总图**（应落 orchestrator）；否则实现易切片化 |
| F-03 | P0 | **beacon-goal vs loom-goal** 须统一「双轨单语义」叙述，消除假冲突 |
| F-04 | P1 | 叠加 Loom 三湖 **依赖方向大体正确**；应固定 Wave0→1→2→3 实现序 |
| F-05 | P1 | durable↔ralph 依赖、topology 缺 durable、subagent×driver 组合序 需补 |
| F-06 | P1 | L2 强、部分 L1 包 FSM 弱；MSS/golden 应补 legal walk 引用或投影 |
| F-07 | P2 | rust-kernel 与 program 关系要在拓扑中显式，避免第二切片 |

---

# 7. recommended_route

```text
1) 用户确认本 review 的 Wave 序与「总状态机」叙事
2) beacon-gen-change / refreeze:
   - orchestrator R4: 嵌入 L0/L1/L2 总图 + Loom 双轨语义
   - feature-graph: 修 topology_order；durable 对 ralph 改 soft-dep
   - optional: MSS/golden 补 FSM 引用段
3) implement 严格按 Wave0→3，禁止先做 trace UI 或 brand 网页而空 goal
4) QA：domain_fsm_coverage + subagent 不 complete + dual-install 矩阵
```

---

# 8. 大白话结论

1. **有没有整体业务/交付状态机？**  
   **有骨架**：防空壳靠 domain FSM；交付靠 goal run；长跑/并行是旁路子机。  
   **缺总装说明书**：没把 11 湖画成一张用户旅程状态机。

2. **逻辑能否闭环？**  
   **合同上能闭环**（verifier + 人工 release + domain 覆盖）。  
   **实现上还没闭环**（subagent 未真 spawn 等）——那是执行债，不是「需求只有切片」。

3. **新旧叠加有没有顺序？**  
   **大体有**（domain 链、subagent 依赖 MSS、trace 依赖 durable）。  
   **建议死死按** Wave0 品牌 → Wave1 编排+domain → Wave2 真并行 → Wave3 长跑+trace，否则 Loom 会做成「三个插件」。

4. **会不会做成功能切片？**  
   **有风险，但合同已防一半**（domain 硬门 + 禁自证 + 卫星禁写 truth）。  
   **要再防一半**：总状态机进 orchestrator、实现 enforce done_when、禁止 fan-out/长跑当完成。

**一句话**：v2.0.0 需求 **不是一盘散沙切片**，是「交付状态机 + 业务状态机 + 安装轨」三层设计；**自洽度中上**，要闭环必须 **补总图、统一双轨语义、按 Wave 序实现**。
