---
artifact_type: planner_review
skill: beacon-pln-review
versions: [v1.6.7, v2.0.0]
created_at: 2026-07-18
status: support_advisory
not: [implementation, qa_verdict, release_verdict, truth_write]
sources:
  - docs/beacon/v2.0.0/SUMMARY.md
  - docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/goalrun-main-axis.md
  - docs/beacon/v2.0.0/features/loom-*/truth.md
  - packages/beacon-rs/README.md
  - https://github.com/op7418/Humanizer-zh
  - https://github.com/blader/humanizer
  - beacon/utils/design_baseline.py
  - beacon/utils/design_md_lint.py
  - beacon/utils/design_company_templates.py
---

# Planner Review: v1.6.7 / v2.0.0 能力边界 · Loom skill · 真相可读性 · UI design

## intent_snapshot

用户要确认：

1. **v2 是否全量实现**（不是只有合同）
2. **交付的 6 个 skill 是否已以 `loom-*` 改名交付**
3. **v2 能力边界**（能用 / 不能用 / 禁止）
4. **需求真相太 AI、人类看不懂** → 蒸馏 Humanizer-zh + humanizer，作 truth 文风规范；中英双语适配
5. **UI design 能力**是否可用、是否与需求闭环

## scope_mode

`full_parity_audit` + `boundary_map` + `human_readability_gap` + `ui_capability_verify`  
**不写 truth / 不 implement / 不给 release GO**。

---

## 1. 结论总表（大白话）

| 问题 | 答案 |
|------|------|
| v2 全量实现了吗？ | **没有。** 合同/主轴/湖包大多 **frozen**；运行时仍是 **v1.6.7 Python 生产轨** + Rust **骨架** + Loom **未实现任务清单**。 |
| 6 个 skill 已 loom-* 改名交付？ | **没有。** 「六能力」是 harness 面（loop/truth/design/implement/qa-evidence/release），**不是** 六个 `loom-*` skill。`loom-*` 现有 **3 个湖合同**（brand/subagent/trace），**0 个** 已装 skill 包 / CLI。 |
| 日常能用什么？ | **`$beacon-goal` + CLI v1.6.7**（goal、domain FSM、durable/driver、UI design baseline/lint 等已在生产轨）。 |
| v2 默认接管 beacon？ | **禁止**（UD-LOOM-009 / DEF-SE-004：W4 前不得默认 `BEACON_V2=1` / loom 盖 beacon）。 |
| 真相人类可读？ | **弱。** 多为表格+AC+UD 机器合同；最长 842 行；**无** humanizer 门；中英仅有 `language: zh` frontmatter，**无** 并行 en 摘要层。 |
| UI design？ | **v1.6.7 已实现且测过**（baseline + 10 公司模板 + design.md lint + ship gate + goal design stage）。v2 只是 **继承合同**，未单独再实现一套。 |

---

## 2. v2 实现度（parity matrix）

### 2.1 湖状态

| Lake | Truth | Code / Runtime | Verdict |
|------|-------|----------------|---------|
| GoalRun main-axis (shared) | frozen + validate ok (12 lakes) | `goalrun_main_axis.py` + CLI generate/validate | **合同+工具绿**，非产品闭环 |
| loom-brand-surface | frozen R1 | tasks 全未勾；无 `skills/loom`、无 pip `loom` | **合同 only** |
| loom-goal-optional-subagent | frozen R1 | 仍 plan-only / 未真 spawn | **合同 only** |
| loom-goal-trace-bundle | frozen R1 | agent_trace 模块有；driver **默认接线未交付** | **合同 only** |
| beacon-v2-product-goal-orchestrator | frozen R3 | 运行时仍 v1.6.7 product-goal | **parity 未切 Rust** |
| beacon-v2-main-star-satellite-pool | frozen | 拓扑合同；真并行未闭环 | **部分概念 / 未交付** |
| domain-fsm / golden / qa-gate | frozen | 生产能力在 **v1.6.7** | **v2 镜像合同；权威在 v167** |
| ui-state-matrix-ship-gate | frozen inherit | 生产在 **v1.6.7** UI ship | **同上** |
| ralph boundary | frozen | v167 有边界 | **同上** |
| goal-durable-longrun | frozen R1 | SUMMARY: **implement pending**；上游 v167 shipped | **v2 湖未实现** |
| beacon-v2-rust-kernel-redesign | frozen 大文档 | `packages/beacon-rs` ~6k LOC；README: **P0 scaffold**；orchestrator/cli/gate 多为 stub | **骨架 ≠ 全量生产** |

### 2.2 Rust Spine 含义（纠正「全量」误解）

```text
有 crates + 类型/DB skeleton  ≠  六能力 harness 可生产替代 Python
```

- 存在：`beacon-core` / `store` / stub `orchestrator|gate|cli|python`
- 不存在：默认 `loom` CLI、默认走 Rust goal、W4 默认切换
- 证据索引写明：`implementation-beacon-rs` = historical P0 scaffold；R8 revalidation required

### 2.3 与 v1.6.7 权威的关系

| 面 | 权威轨 | 说明 |
|----|--------|------|
| 日常 goal 长跑 | **v1.6.7** | durable supervisor + AgentDriver 已 merge main |
| Domain FSM / 防空中阁楼 | **v1.6.7** | product-goal + domain 七湖链 |
| UI design 闭环 | **v1.6.7** | ui-goal-design-lifecycle + ship gate |
| v2 program | **合同+主轴** | 对标 v167 full_parity；实现 Wave 0–4 **未煮干** |

---

## 3. 「六个 skill」与 loom-* 命名（关键澄清）

### 3.1 两套不同概念（勿混）

| 概念 | 是什么 | 现状 |
|------|--------|------|
| **六一等能力**（Rust harness） | `loop \| truth \| design \| implement \| qa-evidence \| release` | **设计目标**；非六个已交付 skill 目录 |
| **Loom 品牌面** | `loom` CLI + `$loom-goal` + 可选 `$loom-loop-goal` | **truth frozen；未实现** |
| **Loom 三湖** | brand / optional-subagent / trace-bundle | **合同 frozen；实现 0** |
| **Beacon 生产 skill 面** | ~40 个 `beacon-*` host skills | **已装、可用** |

### 3.2 UD-LOOM-007（已锁）

- Phase-1：**共享** `skills/beacon/*` 内容路由  
- Phase-2：可选 `loom-*` **镜像**  
→ **不是**「把 6 个 skill 全部改名 loom-* 立刻交付」

### 3.3 用户若期望的「loom 交付清单」（推荐冻结后 implement）

最小可交付面（仍非 6 个任意改名）：

1. `loom` console_script + 不覆盖 `beacon`
2. `$loom-goal` skill（facade → 同 goal 语义 / dual state root）
3. `$loom-loop-goal` support only（可选）
4. doctor dual-install check
5. subagent opt-in 真 spawn（挂 goal）
6. `goal trace` 聚合（挂 goal）

→ 这是 **Wave 0–3 实现海**，需 change 后 goal；**今天没有**。

---

## 4. v2 能力边界（boundary map）

### 4.1 允许（In）

- 写 / 读 `docs/beacon/v2.0.0` 合同、主轴、program graph
- `beacon goal axis generate|validate -v v2.0.0`
- 用 **v1.6.7 生产能力** 交付真实项目（selfmedia 等）
- 规划 Loom 双装与并行（合同层）

### 4.2 禁止 / 未就绪（Out）

| ID | 边界 |
|----|------|
| B-V2-001 | 宣称「v2 全量可交付 / Rust 已替代 Python」 |
| B-V2-002 | 默认 `BEACON_V2=1` 或 loom 覆盖 beacon（W4 前） |
| B-V2-003 | 无 opt-in 却声称 subagent 真并行 |
| B-V2-004 | Submachine（Driver/Supervisor/Subagent/Ralph）写 complete/release |
| B-V2-005 | 无 verifier 宣称 GoalRun completed |
| B-V2-006 | 把 research/SUMMARY 当 ship 证据 |
| B-V2-007 | 仅 design_primitives 无 ui-state-matrix 过 UX release（继承 V2SE-006） |

### 4.3 双轨模型（用户心智）

```text
生产轨 Beacon v1.6.7  ──  $beacon-goal  ──  真项目交付
进化轨 Loom / v2      ──  合同 + 骨架   ──  验收后并行安装（未完成）
```

---

## 5. 需求真相可读性 + Humanizer 蒸馏（新湖建议）

### 5.1 问题证据

- v2 rust truth **842 行**；durable/longrun **200+ 行**；loop-goal **389 行**
- 结构偏：UD 表 + AC 表 + Non-Goals + 多轮 change 痕迹 → **agent 友好、人难扫**
- frontmatter `language: zh` 全覆盖；**无** `language: en` 并行包 / 无「人读一页纸」层
- 仓库 **无** humanizer 规范挂入 gen-truth / change

### 5.2 Source inventory（Humanizer）

| Source | 用途 | 蒸馏到 Beacon 的层 |
|--------|------|-------------------|
| [blader/humanizer](https://github.com/blader/humanizer) | EN signs-of-AI writing | `truth_prose.en.md` 规则 + CI 可选 lint |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | 中文去痕 | `truth_prose.zh.md` 规则 |
| Wiki Signs of AI writing | 共同根 | 引用不复制全文 |

**核心 5 原则（中英共用，技术合同例外）：**

1. 删填充短语（此外/值得注意/It is important to note…）
2. 破公式结构（三段式、二元对比排比）
3. 变化句长；少「金句」
4. 信任读者：直接写谁-做什么-验收什么
5. 技术 truth：**保持中性、短句、可测试** — 不注入博客腔「灵魂」（humanizer 对 technical 的例外）

**额外 Beacon 约束（truth 专用，区别 blog humanize）：**

- **不得** 为「好读」删掉 AC ID / 非法转移 / FSM 态
- **双层文档**：
  - L0 **人读**：`## 人话` ≤1 屏（意图 / 能做什么 / 不能做什么 / 完成长什么样）
  - L1 **合同**：UD / AC / FSM / Non-Goals（机器与 gate 权威）
- **双语**：
  - 默认 `language: zh` 时 L0 中文必填
  - `language: en` 或 `i18n: [zh,en]` 时 L0 中英各一段；L1 可单语权威 + 另语摘要

### 5.3 建议新湖（海拆湖）

**湖名（建议）**：`beacon-truth-human-readable-i18n-v167`（先挂 v1.6.7 生产轨）  
**v2 镜像**：`beacon-v2-truth-human-readable-i18n`（parity，实现后）

| AC 草案 | 描述 |
|---------|------|
| AC-HR-001 | truth 必有 `## 人话` / `## In plain language` 之一（按 language） |
| AC-HR-002 | L0 ≤ 40 行或 ≤ 800 字（中）/ 500 words（英） |
| AC-HR-003 | gen-truth/change 后跑 humanizer checklist（zh 或 en 规则包） |
| AC-HR-004 | 禁止把 L0 当 gate 权威；gate 只读 L1 AC/FSM |
| AC-HR-005 | 示例：skills/beacon/examples/truth-human-readable.{zh,en}.md |

**非目标**：全文文学改写；删 AC；替代 domain FSM。

### 5.4 中英适配模型

```text
truth.md
  frontmatter: language: zh|en|bilingual
  ## 人话 / Plain language   ← humanizer 作用面
  ## User Intent (one line)
  ## Acceptance Criteria     ← 合同权威，可表格式
  ## Domain FSM              ← 合同权威
  ## Non-Goals
```

可选投影（不反写权威）：

- `truth.human.zh.md` / `truth.human.en.md` 由 L0 抽出，仅给人读 / 评审

---

## 6. UI design 能力核实

### 6.1 v1.6.7（生产 — 已落地）

| 能力 | 状态 | 证据 |
|------|------|------|
| `beacon design baseline` | 已实现 | design_baseline.py + tests |
| 公司模板 auto-select | 10 个（vercel/stripe/linear/notion/figma/apple/shopify/airbnb/slack/ibm） | design_company_templates.py |
| `beacon design lint` | google design.md + fallback | design_md_lint.py |
| goal `ux_required` → design stage | product_goal_runtime | tests/test_v167_ui_goal_design_lifecycle.py **绿** |
| ui-state-matrix ship gate | QA scorecard 挂钩 | ui_design_ship + qa_feature |
| 示例 DESIGN | golden commerce + examples/design-md-complete | fixtures |

**15 tests passed**（本机 review 时跑通 design baseline + ui lifecycle）。

### 6.2 v2

- **合同**：完整继承 ui-state-matrix ship gate（V2SE-006）
- **实现**：不另起炉灶；**依赖 v167 能力** 直到 Rust design stage 真接线
- **缺口（仍为海）**：各端（PC 中台/H5/客户端）「可直接拷贝」示例包可再增厚，但 **不是**「完全没有 UI 能力」

### 6.3 边界

- awesome-design-md / company template = **seed only**，永不 ship 权威
- ship 权威 = DESIGN + ui-state-matrix +（ux）design_md_lint + domain FSM 一致

---

## 7. Findings（severity）

| ID | Sev | Finding | Route |
|----|-----|---------|-------|
| F1 | P0 | 用户可能误以为 v2/Loom 已全量交付 | 文档/对话明确双轨；禁止假交付 |
| F2 | P0 | loom-* skill/CLI 未实现；tasks 全未勾 | implement Wave 0 或 defer 明示 |
| F3 | P0 | 「6 skill = loom 改名」概念错误 | 本 review 冻结澄清；必要时 change 写进 brand truth 人话层 |
| F4 | P1 | 需求真相难读、缺 humanizer 规范 | 新湖 truth-human-readable-i18n |
| F5 | P1 | 中英双语无标准层 | 同湖 AC-HR |
| F6 | P2 | Rust spine 骨架与「全量生产」话术冲突 | SUMMARY 大白话 + 人话层 |
| F7 | info | UI design 生产轨可用 | 保持 v167；v2 只继承 |

---

## 8. Deferral ledger（显式）

| Item | Status | Owner decision needed |
|------|--------|------------------------|
| loom CLI + $loom-goal 真安装 | deferred implement | Wave 0 GO? |
| subagent 真并行 | deferred implement | Wave 2 |
| driver→agent_trace 默认 | deferred implement | Wave 3 |
| BEACON_V2 默认 | **rejected until W4** | locked |
| 6× loom-* 全量 skill 镜像 | Phase-2 optional | 默认不做 |
| humanizer 进 truth 规范 | **proposed lake** | change GO? |
| 历史 800+ 行 truth 全量蒸馏 | sea → 分批 | 新写必遵；旧文渐进 |

---

## 9. recommended_route

### 立即（沟通 / 不改代码）

1. 对用户固定口径：**生产 = v1.6.7 `$beacon-goal`；v2/Loom = 合同+骨架，未全量交付。**
2. 六能力 ≠ 六个 loom skill。

### 下一跳（需用户 GO 后 change）

| 优先级 | 动作 | Skill |
|--------|------|-------|
| P0 | 可选：先实现 Wave 0 `loom-brand-surface`（双装最小面） | `beacon-gen-change` → `beacon-goal` |
| P0 | 立项 `beacon-truth-human-readable-i18n-v167`：蒸馏 humanizer 中英规则进 gen-truth/change | `beacon-gen-change` |
| P1 | 主轴 12 湖按 Wave 实现 Loom subagent + trace | `beacon-goal` v2 program |
| P1 | 旧超长 truth 渐进加 `## 人话`（不一次煮海） | change 分批 |
| — | UI：无新缺口则 **不单独立项**；示例包增厚可 P2 friction | — |

### 禁止本 review 直接做

- 改 package truth / 装假 loom skill / 宣称 release
- 把 humanizer 当「可以削弱 AC/FSM」

---

## 10. 一句话

**v1.6.7 是能干活的灯塔；v2/Loom 是已画好的织布机图纸和半成品机架——名字可以叫 Loom，但线还没织完，六个 skill 也没有整包改名发货。**
