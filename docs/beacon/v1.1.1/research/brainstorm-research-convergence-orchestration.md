# Brainstorm：Beacon 研究资料编排与收敛入工作流（v1.1.1）

**日期**：2026-03-13  
**主题**：将 brainstorm / analysis / research 按统一目录落盘，并可持续收敛到 Beacon 工作流主链  
**目标**：确保发散信息可记录、可追踪、可复盘，但不会污染 PRD / User Story / Test Case 这些最终交付主源。

---

## 维度一：用户维度

### 核心用户
| 用户类型 | 典型角色 | 关键诉求 | 典型痛点 |
|---|---|---|---|
| 专业高频 | 产品经理 / 需求负责人 | 发散想法可沉淀，不丢失上下文 | brainstorm 结果容易散落在聊天或临时文档中 |
| 专业高频 | QA / 研发负责人 | 最终进入主链的内容必须可验证 | research 与 PRD 边界混乱 |
| 代理用户 | AI Agent / LLM | 能先记录发散，再逐步收敛 | 当前 workflow 更擅长生成主链，不擅长管理研究层 |
| 管理/评审 | 项目负责人 | 需要区分“研究材料”与“正式交付物” | 容易把分析稿误当正式需求 |

### 结论
研究层文档的目标不是直接交付，而是：
- 保留推导过程
- 支持后续收敛
- 避免主链需求被无约束发散内容污染

---

## 维度二：场景维度

### 推荐场景
| 场景类型 | 具体场景 | 目标 |
|---|---|---|
| 发散场景 | 需求刚提出，问题尚未定型 | 先做 brainstorm / analysis / research |
| 方案比选 | 多个实现方向、治理路径、目录策略待比较 | 在 research 中沉淀分支方案 |
| 复盘场景 | 需求已收敛，需要回看来源 | 从 research 追溯到 PRD / US / TC |
| 迭代场景 | 同一 feature 多轮讨论 | 用 research 持续追加，而不是直接反复改 PRD |

### 连续场景
1. 先记录 brainstorm / analysis / research
2. 再进行 triage / 聚类 / 收敛
3. 最终进入：
   - `user-story`
   - `prd`
   - `test-case`

---

## 维度三：业务维度

### 统一编排原则
1. **analysis = research 的一个子类型**
2. **brainstorm 也是 research 的一个子类型**
3. research 不是最终交付主源，而是主链输入层
4. PRD / User Story / Test Case 才是面向交付与 gate 的主链文档

### 价值
- 让发散与收敛分层
- 保留上下文链路
- 降低“随手写的分析稿被误当正式需求”的风险

---

## 维度四：技术维度

## 4.1 推荐目录编排

统一放入：

```text
docs/beacon/<version>/research/
├── brainstorm-*.md
├── analysis-*.md
├── research-*.md
├── architecture-*.md
├── compare-*.md
└── convergence-*.md
```

### 规则
- `analysis` 归类到 `research/`
- `brainstorm` 归类到 `research/`
- `research` 目录允许多轮追加与分类沉淀
- 不要求同步到 `docs/product/`

---

## 4.2 文档状态模型（建议）

每份 research 文档建议带以下头信息：

```md
- type: brainstorm | analysis | research | architecture | compare
- status: divergent | triaged | converged | archived
- feature: beacon-strict-config-governance
- version: v1.1.1
- convergence_targets: [user-story, prd, test-case]
- source_of_truth: false
```

### 状态语义
- `divergent`：纯发散记录，尚未整理
- `triaged`：已分类、可进入收敛讨论
- `converged`：已提炼进主链文档
- `archived`：仅保留历史，不再参与当前版本

---

## 4.3 收敛流程（推荐）

```text
brainstorm / analysis / research
        ↓
triage / 聚类 / 去重
        ↓
提炼为问题、范围、验收项、风险
        ↓
写入 user-story / prd
        ↓
由 prd / user-story 生成 test-case
```

### 关键约束
- **research 不直接进入 gate**
- **test-case 不直接从 research 生成**
- **必须先收敛到 user-story / prd，再进入 test-case**

---

## 维度五：体验维度

### 推荐使用体验
| 体验点 | 重要度 | 建议 |
|---|---|---|
| 记录方便 | ★★★★★ | brainstorm 信息直接落盘到 research |
| 结构清晰 | ★★★★★ | 类型 + 状态 + feature/version 元数据 |
| 可追溯 | ★★★★☆ | research 文档指向收敛目标 |
| 不易误用 | ★★★★★ | 明确 research 不是最终交付主源 |
| 可持续迭代 | ★★★★☆ | 允许多轮追加，但必须标记状态 |

### 推荐命名方式
- `brainstorm-ai-agent-ux.md`
- `analysis-directory-governance.md`
- `research-git-alignment-options.md`
- `convergence-workspace-routing.md`

---

## 维度六：价值维度

| 价值类型 | 优先级 | 说明 |
|---|---|---|
| 功能价值 | ★★★★★ | 发散信息不丢失，可被后续工作流消费 |
| 情感价值 | ★★★★☆ | 团队不会因“先写错地方”而焦虑 |
| 治理价值 | ★★★★★ | 防止 research 与 PRD 混淆 |
| 交付价值 | ★★★★☆ | 主链文档更干净、更适合 gate |

---

## 维度七：风险维度

| 风险类型 | 概率 | 影响 | 应对方案 |
|---|---|---|---|
| research 无限膨胀 | 中 | 大 | 用状态模型 + triage 控制 |
| analysis 被当 PRD | 高 | 大 | 明确 `source_of_truth=false` |
| 人工继续维护 docs/product | 中 | 大 | 禁止手工维护 compat 镜像 |
| research 与主链脱节 | 中 | 中 | 要求 `convergence_targets` 与收敛记录 |
| 同一主题多文档重复 | 高 | 中 | 建议 feature + type 命名规范 |

---

# 推荐编排方式（确认版）

## 推荐
- `analysis = research` 的一个子类型
- `brainstorm = research` 的一个子类型
- 统一放进：`docs/beacon/<version>/research/`
- 再从 research 收敛到：
  - `user-story`
  - `prd`
  - `test-case`

## 不建议
- 不要把 `analysis / research` 当作和 `PRD` 同级的“最终交付主源”
- 不要同时人工维护 `docs/product` 和 `docs/beacon`
- 不要让 `test-case` 直接消费 research，而跳过 PRD / User Story

---

# 对 Beacon 工作流体系的补充建议

## 建议新增治理约束
1. `workflow` 主链只消费：
   - `user-story`
   - `prd`
   - `test-case`
2. `research` 作为输入层，不直接参与 gate
3. compat 镜像 (`docs/product`) 只允许自动同步
4. brainstorm / analysis 命令默认目标目录应可配置为：
   - `docs/beacon/<version>/research/`

## 建议后续能力
- `beacon brainstorm create --output docs/beacon/<version>/research/...`
- `beacon analyze create --output docs/beacon/<version>/research/...`
- `beacon research converge <feature>`：将 research 提炼为 user-story / prd 输入
- `beacon research triage <feature>`：给 research 文档打状态标签

---

# 收敛结论

Beacon 应形成如下编排层次：

```text
研究层（brainstorm / analysis / research）
        ↓
收敛层（user-story / prd）
        ↓
验证层（test-case / matrix）
        ↓
执行层（implementation / verify / gate）
```

这样可以保证：
- 发散信息可落盘、可追溯
- 正式需求主链保持清晰
- workflow / gate 不被 research 噪音干扰

---

**落盘目录**：`docs/beacon/v1.1.1/research/`
