# Beacon、OpenSpec、GitHub Spec Kit：对比与 Beacon 可交付设计

## 1. 文档目的

本文做三件事：

1. **系统化对比**三类方案：**Beacon**（个人自研、交付导向）、**OpenSpec**（开源 spec 框架）、**GitHub Spec Kit**（开源 SDD 工具包）。
2. **澄清边界**：Beacon **不是** OpenSpec / Spec Kit 的替代品或分支；领域重叠在「规格与 AI 协作」，但 **Beacon  uniquely 绑定版本化交付物料与证据闭环**。
3. **给出 Beacon 侧「可交付设计」约束**：在 **极简人类面** 前提下，做到 **完备（生命周期闭合）、职责清晰、可审计**。

阅读顺序建议：先读「对比」，再读「Beacon 可交付设计」，最后按需对照 `docs/beacon/global-boundaries.md`。

---

## 2. 项目性质（必须先对齐的预期）

| 维度 | Beacon | OpenSpec（Fission-AI） | GitHub Spec Kit |
|------|--------|-------------------------|-----------------|
| **性质** | **个人自研**的交付类产品内核；仓库可为开源，但 **产品路线与物料模型由 Beacon 自治**。 | **开源社区项目**（MIT），npm 发布 `@fission-ai/openspec`。 | **开源**（GitHub 官方组织），**Specify CLI** 从 GitHub 安装（PyPI 同名包非官方）。 |
| **首要用户价值** | **证据优先的版本化交付**：需求 → 测试 → 实现 → QA → 发布，_truth 在 `docs/beacon/<version>/`。 | **轻量 spec + 按变更分包**，流体迭代，棕地友好。 | **规范驱动开发（SDD）全链路**：constitution → specify → plan → tasks → implement。 |
| **与本文关系** | **定义 Beacon 可交付设计的基准文档之一**。 | **对标对象**：借鉴「validate / 变更目录 / CLI JSON」等工程化思路，**不照搬目录协议**。 | **对标对象**：借鉴「阶段自检 / 模板 / 防伪安装说明」等，**不照搬阶段瀑布**。 |

---

## 3. 详细对比

### 3.1 真相源（Source of truth）

| 项目 | 真相放哪里 | 典型形态 |
|------|------------|----------|
| **Beacon** | **`docs/beacon/<version>/`**（SUMMARY、prd、user-story、qa/test-cases、prototype、execution…）；运行时状态在 **`.beacon/`** 等约定路径。 | **版本化交付树**；变更过大走 **change / refreeze** 等治理，而非随意覆盖 frozen 目录。 |
| **OpenSpec** | 仓库内 **`openspec/`**；每次特性一批 **`openspec/changes/<change-id>/`**（proposal、specs、design、tasks），归档进 **`changes/archive/`**。 | **变更包**为主增量；强调迭代与可追溯。 |
| **Spec Kit** | 由 **Specify 初始化**生成的一套 Markdown / 模板与命令产物（constitution、spec、plan、tasks…）。 | **阶段产出物**堆叠；「规格驱动生成实现」的叙事强。 |

**结论**：Beacon 的「真相」是 **产品线 + 版本号 + 证据链**；OpenSpec 是 **变更文件夹**；Spec Kit 是 **SDD 模板链**。三者 **不可混为一个目录结构**。

### 3.2 工作流形状

| 项目 | 形状 | 人类心智负担 |
|------|------|----------------|
| **Beacon** | 固定 **7 段主流程**：prd → user-story → test-case → prototype → implement → qa → release；辅助面 **help / status / doctor / archive** 等（见全局约束）。 | **极简**：人类记 **7+3**，不因内部 team/subagent 暴露而膨胀。 |
| **OpenSpec** | **流体**：`/opsx:propose` → apply → archive 等；可配置 profile，强调 **iterative not waterfall**。 |  slash 命令多，但可按 profile **收敛**；偏「棕地随时改 spec」。 |
| **Spec Kit** | **强阶段**：constitution → specify → plan → tasks → implement；顺序教育成本低，但仪式重。 | 阶段清晰；模板与文档量大。 |

### 3.3 CLI / 集成面

| 项目 | 入口 | 备注 |
|------|------|------|
| **Beacon** | **`beacon`**（Typer）；**`--project-root`、`--version`** 贯穿；技能侧优先 **`beacon <subcommand>`**，可选 `run_beacon.sh` 仅在有 vendored skill pack 时。 | 与 **Cursor/Codex 技能**结合时，人类面仍收敛到 Beacon 命令树。 |
| **OpenSpec** | **`openspec`**（Node）；`init`、`validate`、`update`；大量 **`/opsx:*`**。 | 生态面向 **多编辑器 / 多 Agent**；Telemetry 可关。 |
| **Spec Kit** | **`specify`**（Python，官方从 GitHub 安装）；**`/speckit.*`**。 | 与 Copilot 等集成写在官方 README；强调 **勿装错 PyPI 同名包**。 |

### 3.4 可验证、可审计、可测试（取向）

| 项目 | 可验证 | 可审计 | 可测试 |
|------|--------|--------|--------|
| **Beacon** | **doctor verify-context / gate / release check / qa** 等与 **物料一致性和门禁**绑定；证据在 **execution / qa** 可追溯。 | **版本目录 + 变更记录 + 技能/CLI 输出**；强调 **frozen truth 不被静默改写**。 | 仓库内 **pytest** 与 CLI 契约；真实项目可用 dedicated validation skill。 |
| **OpenSpec** | **`openspec validate`**；变更目录天然 diff 友好。 | **变更包 + archive**；CLI JSON；需注意 telemetry 策略（可禁用）。 | 上游 **Vitest** 等；CLI 行为可脚本化。 |
| **Spec Kit** | **`specify check`**、阶段产出是否存在。 | 模板与阶段 artifact **Review 友好**。 | 模板与命令链可被 CI 检查「文件是否生成」。 |

### 3.5 适用边界（何时用谁）

| 场景 | 建议 |
|------|------|
| 要把 **需求—测试—实现—QA—发布** 统一进 **版本化物料 + 证据**，并强调 **交付门禁** | **Beacon** |
| 要在现有仓里 **快速迭代 spec、按变更组织文档**，偏 Node/多 Agent slash | **OpenSpec** |
| 要从零搭 **完整 SDD 脚手架**，接受重模板与强阶段 | **Spec Kit** |
| **Beacon + OpenSpec/Spec Kit 共存** | **可以**：Beacon 管 **交付真相与门禁**；OpenSpec/Spec Kit 可在 **工具链或实验分支**使用，但须在项目内 **写明单一「交付真相」归属**，避免两套 spec 互相打架。 |

---

## 4. Beacon 可交付设计（极简 · 完备 · 职责清晰）

以下条款是对 **`docs/beacon/global-boundaries.md`** 的 **可交付视角展开**：便于评审「这一版 Beacon 是否算交付完整」，而不是功能清单堆砌。

### 4.1 极简（对人类）

1. **人类主面**仅限 **7 段主流程**（prd → … → release），不得被内部 orchestration 曝光稀释。
2. **人类辅助面**保持克制：**help、status、doctor、archive**（及全局约束中已列的扩展），新增辅助命令须论证「是否可由机器默认承担」。
3. **对外命令叙述**优先 **`beacon <subcommand>`**；复杂编排默认 **不进人类口诀**。
4. **技能（Skills）** 只做 **路由与护栏**：不长篇替代 CLI；与 OpenSpec/Spec Kit 的 slash 生态 **不对标数量**，对标 **清晰边界**。

### 4.2 完备（对交付）

「完备」指 **生命周期闭合**，而非「包含世上所有编辑器插件」：

| 闭合维度 | Beacon 应具备的能力（概念层） |
|----------|-------------------------------|
| **需求** | `docs/beacon/<version>/` 下 prd / user-story / test-case / prototype 与版本策略一致；冻结与变更路径可追溯。 |
| **实现** | implement 与 delivery contract、门禁可读证据对齐；prompt 边界可审计。 |
| **质量** | qa 输出可追溯到 test-case / AC；严重阻塞有明确 **stop_for_repair** 语义。 |
| **发布** | release 与 gate、scorecard、check 一致；**release-ready** 有定义而非口语。 |
| **运维** | doctor 能修复 **上下文 / 物料漂移**；必要时 **sync-materials** 有版本与范围参数。 |

完备性 **不以**「内置 OpenSpec 目录」或「内置 Spec Kit 全套 slash」为判据；而以 **Beacon 自有物料模型是否闭环** 为判据。

从版本演进角度看，Beacon 的完备性也不应被理解为“维护一个长期持续改写的源 `prd` 文件”。更合适的是：

- 以 **`docs/beacon/<version>/`** 作为每个版本的 **canonical truth tree**
- 以 **change / refreeze / supplement** 承接增删改
- 以 **archive governance** 隔离退出当前 delivery plane 的历史真相
- 以 **current-state index** 向人和 Agent 提供“当前系统承诺什么”的只读视图

这层补充与 OpenSpec 的 `main specs + changes + archive` 有抽象对齐关系，但不等同于照搬其目录协议。详细展开见：
[`openspec-archive-vs-beacon-version-evolution.md`](./openspec-archive-vs-beacon-version-evolution.md)。

### 4.3 职责清晰（架构分层）

建议在心里固定 **四层**，避免把开源竞品的能力挤进同一层：

| 层级 | 职责 | Beacon 对应（示意） |
|------|------|---------------------|
| **L1 人类接口** | 极简命令 + 技能路由 | `beacon`、公开 skills |
| **L2 交付真相** | 版本化文档与冻结语义 | `docs/beacon/<version>/` |
| **L3 运行时与投影** | 状态机、镜像、看板、SQLite 等 | `.beacon/`、projection / ledger（随版本演进） |
| **L4 宿主能力** | LLM、浏览器、外部 Runner | 可插拔；**默认不冒充交付真相** |

OpenSpec / Spec Kit 多数能力落在 **「通用 spec 工作流层」**，对标 Beacon 时映射到 **L1/L2 的工具辅助**，**不得替代 L2 的 frozen truth 定义权**。

### 4.4 可审计、可验证、透明（工程约束）

1. **可追溯**：关键 CLI **支持 `--json`**；release/gate 结论应能落到 **文件或结构化输出**，而非仅存聊天记录。
2. **可重复**：同一 `project-root` + `version` + 命令，**确定性优于魔法默认值**；默认行为必须在文档可述。
3. **防伪与误导防护**：对外说明中明确 **官方 CLI 入口**（类比 Spec Kit 对 PyPI 同名包的警示），避免「山寨命令面」稀释 Beacon。
4. **隐私**：Beacon 核心 CLI **不应默认上报未披露的使用数据**；若未来引入可选 telemetry，须 **opt-in 或与 OpenSpec 类似的可关闭声明**，并写入发布说明。

### 4.5 与开源方案的关系（吸收原则）

| 来源 | 可吸收 | 不应吸收 |
|------|--------|----------|
| **OpenSpec** | 变更可追溯、`validate` 思维、CLI JSON、棕地迭代叙事 | 整套 `openspec/` 目录取代 `docs/beacon` |
| **Spec Kit** | 阶段自检、`specify check` 类「一次性核对」体验、模板教育价值 | 完整 **constitution→implement** 瀑布替代 Beacon 7 段 |
| **二者共性** | **单一权威入口**、**机器可读输出**、**目录/模板可审查** | 把 Beacon 做成「又一个通用 SDD 脚手架」 |

---

## 5. 维护说明

- **版本**：本文随 `docs/beacon/v1.4.0/` 收敛；若全局策略变更，以 **`docs/beacon/global-boundaries.md`** 为准并同步修订本节与交叉引用。
- **竞品版本**：OpenSpec / Spec Kit 的功能以 **上游仓库当前发布** 为准；本文做的是 **结构层对比**，不锁死对方 minor 行为。

---

## 6. 相关链接（仓库内）

- `docs/beacon/global-boundaries.md` — 人类主面与辅助面硬约束  
- `docs/beacon/v1.4.0/SUMMARY.md` — 本版本总览（若存在）  
- `CLAUDE.md` / `AGENTS.md` — 运行时与文档版本指针（以 Beacon 托管块为准）
