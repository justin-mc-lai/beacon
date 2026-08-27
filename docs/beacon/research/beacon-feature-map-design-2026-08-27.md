# Research: Feature Map 设计 —— 需求真相 × 代码锚定的功能地图（beacon-native）

**日期**：2026-08-27
**用途**：planner 设计提案（support_advisory，非 requirement truth）。回答两个问题：
1. 如何让软件开发的功能迭代更明确（复用 beacon 需求真相能力）；
2. 如何设计方法论里的「功能地图」（Feature Map），确保需求 → 实现 → 验收交付清晰闭环。

**源锚定**：
- beacon 需求真相：`features/<slug>/{truth,tests,tasks,evidence}.md`（Intent Matrix / AC / FSM / 用户旅程 / 人话 L0）
- 方法论：`docs/beacon/research/beacon-agent-coding-methodology-cursor-poteto-2026-08.md` M2（feature map：功能在哪、怎么进入、agent 能自验证）
- D1 调研结论：`docs/beacon/research/beacon-v1613-planning-source-audit-2026-08-27.md` §2（第三方只有 enabler：deer-flow sandbox RBAC、mempalace 内容寻址、checkpoint 持久 run；**无完整 feature-map 路由实现，需自研**）
- beacon 现有资产：`.beacon/code2truth/`（system map）、`beacon-qa/references/failure-mode-catalog.md`（L3 已交付）、eval-real-project
- 约束：`docs/beacon/global-boundaries.md`（support surface 有界、单真值多投影、不新增命令面、truth 人话）

---

## 1. 问题：功能迭代为什么不够明确

当前 beacon 的 truth 侧已经很强：每个 feature 有「人话 L0 + Intent Matrix + AC + FSM + 用户旅程 + tests/tasks/evidence」。但**实现/验收侧缺少「代码锚定」**：

| 问 | 现状 | 缺口 |
|---|---|---|
| 做什么 / 为什么 / 怎样算完 | ✅ truth 冻结（人话 + AC + FSM） | — |
| 功能**在哪**（代码位置/入口） | ⚠️ 靠 implement/qa 临时翻代码 | 无持久 feature map |
| 怎么**运行产品来验证** | ⚠️ 每次现找启动命令 | 无统一验证入口 |
| 观察**什么信号**算验证通过 | ⚠️ 靠人盯 | 无信号契约 |
| 一张截图/模糊 bug 描述 → 复现 | ❌ 无路由 | 方法论 M2 的空白 |

结论：beacon 缺的是「truth ↔ 代码」的桥——**Feature Map**。它不替代 truth，而是把 truth 的 AC/FSM/旅程**投影到代码空间**，让 agent 从"知道要做什么"升级为"知道去哪改、怎么自证、看什么"。

## 2. Feature Map 设计（beacon-native）

### 2.1 定位与边界

- **支撑面**：feature map 是 truth 的投影/支撑面，**不是新 truth 源**（global-boundaries：support surface 有界，不改写 truth）。
- **单向投影**：AC/FSM/用户旅程是权威，map 只引用它们；map 不得反向驱动 truth（违反则 fail-closed）。
- **可执行**：验证命令必须能真正跑（复用 v1.6.13 L2 的 pytest junitxml 模式：Command+Assertion+信号）。
- **不新增命令面**：map 是 `features/<slug>/` 下的文档 + 机器投影，不进公开 CLI。

### 2.2 Schema（`features/<slug>/feature-map.md` + `.machine/feature-map.json` 投影）

```text
FeatureMap
├─ slug / version / truth_refs（truth/tests/evidence 路径）
├─ entry_points[]        # 功能在哪、怎么进入
│    ├─ ac_id（绑定 truth AC）
│    ├─ type: route|function|file|ui|service
│    ├─ path（代码/路由/UI 路径）
│    └─ how_to_enter（进入命令/导航步骤）
├─ verification[]        # 怎么自证
│    ├─ ac_id
│    ├─ command（可执行，pytest/脚本/curl）
│    ├─ assertion（期望结果）
│    └─ signal（观察什么：exit code / trace / UI 状态 / log 模式）
├─ reproduce[]           # 模糊描述 → 复现
│    ├─ symptom_hint（截图/一句话 bug 描述的关键词）
│    └─ steps[]（复现路径，路由到 entry_points + verification）
└─ observation_signals[] # 通用信号约定（trace/UI/heap 等）
```

### 2.3 数据流（怎么填、谁维护）

```text
truth freeze（gen-truth）
  → 生成 feature-map 骨架（从 AC/FSM/domain model 派生 ac_id + 待填 entry/verification）
  → implement（gen-implement）源码锚定填 entry_points + verification_commands
  → QA（eval-qa）用 verification 命令自证 + 作为对抗式审查输入
  → change/refreeze（gen-change）时随 truth 同步更新 map
```

- 骨架由 `gen-truth` 冻结时派生（ac_id 绑定保证与 truth 不漂移）。
- entry/verification 由 implement 填（**源码锚定**，pln-source 的防漂移纪律）。
- QA 用同一 map 验收 → 需求-实现-验收三面对齐。

## 3. 如何让功能迭代更明确（落地后的迭代闭环）

```text
需求（truth 冻结，人话 L0）
  → 地图（feature-map：在哪改/怎么验证/看什么）
  → 实现（implement 按 map 找入口，改完跑 verification 自证）
  → 自证（verification 命令 exit 0 + 信号匹配）
  → 验收（qa 用 map+truth 对齐；失败模式目录 L3 作为对抗输入）
  → 发布（release 人类 gate）
```

每次迭代 agent 的固定动作：**先读 truth（what/why/done）→ 再读 map（where/how/verify）→ 实现 → 用 map 自证**。这直接兑现方法论 M1（验证 > 生成）与 M2（feature map 路由模糊描述）。

## 4. 分阶段建设（避免过度设计，第三方无现成实现）

- **Phase 1（最小可用）**：feature-map.md 骨架 + entry_points + verification_commands，truth 冻结时派生、implement 填、qa 用。覆盖「在哪改 + 怎么验证」——这是让迭代明确的 80% 收益。
- **Phase 2（复现路由）**：reproduce[]（模糊 bug 描述 → 复现步骤），对接方法论 M2 的"截图/一句话 → 定位"。
- **Phase 3（agent 自验证）**：复用 `.beacon/code2truth/` system map 资产 + eval-real-project，让 agent 能按 map 自动运行产品、观察信号（对齐 deer-flow checkpoint / mempalace 内容寻址 enabler）。

## 5. 与既有能力的关系

| 能力 | 关系 |
|---|---|
| truth 包（AC/FSM/旅程） | map 的权威源（单向引用） |
| 人话 L0 | 迭代可读性（继续保留，map 不替代） |
| L3 失败模式目录 | 与 map 互补：map 给"去哪验证"，失败目录给"防什么错" |
| code2truth system map | Phase 3 的资产底座 |
| D2 spend 账本 | map 的验证命令可纳入 spend（已验证的 writeback 才扣） |

## 6. 结论

- **功能迭代更明确** = truth（做什么）+ feature-map（在哪/怎么验证）双面锚定，agent 固定走「读 truth → 读 map → 实现 → 自证」。
- **Feature Map 设计** = 支撑面投影（不新增 truth/命令面），`features/<slug>/feature-map.md` 骨架由冻结派生、implement 填、qa 消费，分三阶段建设（骨架 → 复现路由 → agent 自验证）。
- **交付保障** = map 与 truth 单向绑定 + verification 可执行 + 与 L3 失败目录/对抗式审查/QA 门禁衔接，确保需求清晰且支撑实现验收。

**recommended_next_harness**：`plan`（如需推进，进入 pln-program 把 Phase 1 拆成 v1.6.14 的 lake）。
