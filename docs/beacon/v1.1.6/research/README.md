# Beacon v1.1.6 — 开源库横向研究（源码复核版）

> 研究时间：2026-03-24
> 研究目标：为 Beacon v1.1.6 的工作流、执行控制、验证体系与上下文策略提供**源码级**借鉴
> 研究范围：本地快照 `oss-sync/` 下的开源仓库，不使用 Stars / 下载量作为结论依据

> 本文件是 `research/` 目录的**当前结论页**。各子目录 README 仍可保留为项目笔记，但若与本文件冲突，以本文件的源码复核结果为准。

---

## 1. 本次重写修正了什么

上一版总览存在两个核心问题：

1. **信息深度不对等**：`gstack` 是源码级深挖，其余项目多为 README 级摘要。
2. **比较层级不一致**：把 workflow、runtime、QA、memory research 放到同一张表里直接对比，容易得出伪结论。

本次重写做了四个修正：

- **移除 Stars / 热度字段**：这类信息不稳定，也不是源码研究结论。
- **改为分层比较**：先分清项目处于 workflow / runtime / verification / research 哪一层，再讨论借鉴价值。
- **增加证据分级**：所有结论都标注证据强度，避免“看起来一样确定”。
- **修正事实口径**：例如 OpenSpec 不再被描述为“固定 22 个独立 SKILL 目录”；其 workflow/skill/command 交付是 profile + delivery 驱动的生成结果。

---

## 2. 研究方法与证据等级

### 2.1 研究方法

本次研究只使用以下两类证据：

- **源码 / 配置 / 测试 / 运行时实现**
- **仓库内官方文档 / README / ADR / reference 文档**

不把以下内容当成核心结论依据：

- GitHub Stars / 热度
- 二手文章
- 未在本地快照中出现的口头描述

### 2.2 证据等级

| 等级 | 含义 |
|------|------|
| A | 已交叉核对 `src/` / `tests/` / 官方 docs，结论可直接进入 Beacon 设计讨论 |
| B | 已核对官方 docs / README / 目录结构，方向可信，但实现细节仍需继续看源码 |
| C | 偏论文 / README / 研究框架层，不适合直接落到 v1.1.6 设计 |

### 2.3 本次研究对象与证据覆盖

| 项目 | 抽象层 | 本次关注点 | 证据等级 | 本地源码根目录 |
|------|--------|------------|----------|----------------|
| gstack | QA / browser harness / skill delivery | 模板化 skill、浏览器 ref、验证体系、自调节 QA | A | `oss-sync/agents/agent-skills/gstack/` |
| OpenSpec | artifact-driven workflow / multi-tool delivery | 提案-实施-归档工作流、profile/delivery 生成机制 | A | `oss-sync/automation/autoresearch/openspec/` |
| GSD 2 | coding-agent runtime / orchestration | Pi SDK、fresh session、worktree、custom workflow engine、hallucination guard | A | `oss-sync/automation/autoresearch/gsd-2/` |
| BMAD-METHOD | guided workflow + agent ecosystem | 分阶段文档流、agent/skill 分工、`bmad-help` 导航 | B | `oss-sync/automation/autoresearch/bmad-method/` |
| autoresearch | 单目标自主实验循环 | 固定时间盒、单文件修改、program.md 指令机制 | A | `oss-sync/automation/autoresearch/karpathy-autoresearch/` |
| MemEvolve | memory-system research framework | memory provider registry、benchmark harness、auto-evolve CLI | B | `oss-sync/automation/autoresearch/memevolve/` |
| DeerFlow | super-agent runtime / full-stack harness | harness/app split、thread isolation、sandbox、skills+MCP、custom agents、gateway/frontend | A | `oss-sync/agents/agent-skills/deer-flow/` |

---

## 3. 分层结论总览

### 3.1 哪些项目和 Beacon 在同一问题域最接近

| 层级 | 最相关项目 | 为什么 relevant |
|------|------------|-----------------|
| **工作流 / 产物编排** | OpenSpec、BMAD-METHOD | 都在回答“如何把需求、计划、实现、验证组织成稳定的 AI 工作流” |
| **执行 runtime / 隔离 / 调度** | GSD 2、DeerFlow | 回答“agent 如何被调度、隔离、恢复、约束，以及如何走向平台化运行时” |
| **验证 / QA / 高成本测试治理** | gstack | 直接回答“如何给 AI 生成的行为加上可分层验证与质量信号” |
| **自主循环 / 时间盒优化** | autoresearch | 回答“当任务可量化时，如何让 agent 在固定预算内持续迭代” |
| **上下文 / 记忆进化** | MemEvolve | 回答“memory system 本身如何演化”，更偏长期研究 |
| **全栈产品化 / 扩展面设计** | DeerFlow | 回答“super-agent runtime 如何同时承载 gateway、frontend、skills、MCP、custom agents” |

### 3.2 这 7 个项目不应该被强行放进同一维度打分

以下比较是**错误比较方式**，本次不再采用：

- 用同一列去比较 `SKILL.md.tmpl`、`Pi SDK + YAML`、`Meta-evolution`
- 把 `LLM Judge`、`health checks`、`GAIA/WebWalkerQA` 都叫“同一种验证机制”
- 把 workflow 产品、super-agent 平台、browser harness、memory research 框架当作同类产品

因此，本版总览不再使用“单张万能对比表”，而改成**逐项目 + 按能力维度归纳**。

---

## 4. 逐项目源码复核结论

### 4.1 gstack

**定位（复核后）**

gstack 的强项不是“通用 coding agent runtime”，而是：

- 面向 AI 工作流的 **browser harness**
- 模板生成的 **skill 交付系统**
- 分层的 **QA / 文档质量验证体系**

**从源码和官方文档确认到的关键机制**

1. **基于 Playwright accessibility tree 的 ref 系统**
   `BROWSER.md` 明确说明其 ref 选择机制基于 `page.locator(scope).ariaSnapshot()`，再把元素映射为 `@e1` / `@e2` 等 ref，并构建回 Playwright `Locator`，不依赖 DOM 注入。

2. **skill 文档由模板生成，不是运行时拼接**
   `ARCHITECTURE.md` 与 `scripts/gen-skill-docs.ts` 明确显示 `SKILL.md.tmpl -> SKILL.md` 的生成链路；仓库还用测试校验模板和生成产物一致性。

3. **验证是分层设计，而不是单点测试**
   `ARCHITECTURE.md` 定义了 3-tier template tests：
   - Tier 1: static validation
   - Tier 2: E2E via real session
   - Tier 3: LLM-as-judge

4. **QA workflow 有自调节机制，不是无限修 bug**
   `qa/SKILL.md` 中的 `WTF-likelihood` 明确规定：连续修复到一定程度必须停下来评估，超过阈值就中止并向用户汇报。

**对 Beacon 最有价值的借鉴点**

- `SKILL.md.tmpl -> generated SKILL.md` 的交付方式
- 免费静态检查 + 昂贵评审/回归测试分层治理
- diff-aware 测试选择、health score、自调节 stop heuristic

**不建议直接照搬的部分**

- browser daemon / ref system 本身（除非 Beacon 明确要做浏览器执行面）
- 针对 Playwright / live-site QA 的大量流程细节

**关键证据文件**

- `oss-sync/agents/agent-skills/gstack/BROWSER.md`
- `oss-sync/agents/agent-skills/gstack/ARCHITECTURE.md`
- `oss-sync/agents/agent-skills/gstack/scripts/gen-skill-docs.ts`
- `oss-sync/agents/agent-skills/gstack/qa/SKILL.md`

---

### 4.2 OpenSpec

**定位（复核后）**

OpenSpec 的本质不是“固定数量的 skill 目录集合”，而是：

- 一个 **artifact-guided workflow system**
- 一个能把 workflow 按不同 AI 工具交付为 **skills / commands / both** 的分发系统

**从源码确认到的关键机制**

1. **workflow 是 profile 驱动的，不是固定全集默认安装**
   `src/core/profiles.ts` 明确给出：
   - core profile: `propose`, `explore`, `apply`, `archive`
   - all workflows: 共 11 个 workflow id

2. **workflow 的交付方式是 delivery 驱动的**
   `src/core/init.ts` 明确说明 init/update 时会根据：
   - `profile` 决定生成哪些 workflows
   - `delivery` 决定生成 `skills` / `commands` / `both`

3. **OpenSpec 不是仓库内手写一堆固定 skill 目录，而是生成式安装**
   `docs/supported-tools.md` 明确写了 workflow-dependent installation：生成哪些 skills/commands 取决于 profile 和 delivery；并且支持多种工具目录。

4. **工作流主轴是 artifact lifecycle，而不是 QA/doctor/runtime**
   `docs/commands.md` 与 README 显示其核心主轴是：
   `propose/explore -> apply -> verify/sync/archive`

**本次修正的关键事实**

- 不再把 OpenSpec 描述为“仓库里固定 22 个独立 SKILL 目录”
- 不再把 skill 数量当成其核心能力
- 更准确的说法应是：**OpenSpec 通过 workflow profile + delivery 机制，为不同 AI 工具生成 workflow skills/commands**

**对 Beacon 最有价值的借鉴点**

- `proposal/spec/design/tasks` 这种 artifact lifecycle
- `core vs custom` 的 workflow profile 思路
- `skills / commands / both` 的交付模式
- `verify / sync / archive` 这种实现后续管理能力

**不建议直接照搬的部分**

- 把 Beacon 设计成一个“以安装到外部 AI 工具目录为核心”的产品
- 过早围绕 cross-tool distribution 扩大复杂度

**关键证据文件**

- `oss-sync/automation/autoresearch/openspec/src/core/profiles.ts`
- `oss-sync/automation/autoresearch/openspec/src/core/init.ts`
- `oss-sync/automation/autoresearch/openspec/docs/commands.md`
- `oss-sync/automation/autoresearch/openspec/docs/supported-tools.md`

---

### 4.3 GSD 2

**定位（复核后）**

GSD 2 是本次样本里最接近 Beacon “执行控制面”的项目：

- coding-agent runtime
- dispatch pipeline
- state-on-disk
- worktree isolation
- custom workflow engine

**从源码与官方文档确认到的关键机制**

1. **基于 Pi SDK 的 runtime，而不是纯 prompt 框架**
   `docs/architecture.md` 明确写明 GSD built on Pi SDK，并在其上扩展 workflow engine、auto mode state machine 和 project management primitives。

2. **fresh session per unit 是一等设计原则**
   `docs/architecture.md` 与 `docs/auto-mode.md` 都明确说明每个 dispatch/unit 都用全新 session，以避免上下文累积污染。

3. **worktree isolation 是默认的重要执行边界**
   `docs/auto-mode.md` 与 `src/worktree-cli.ts` 显示：GSD 把 milestone 级工作放在 worktree 内，并提供完整的 worktree lifecycle。

4. **custom workflow engine 已经是“定义即数据”的实现，而不是口号**
   `custom-workflow-engine.ts` + `run-manager.ts` 明确展示：
   - workflow 定义冻结为 `DEFINITION.yaml`
   - 运行图写入 `GRAPH.yaml`
   - step 进度由磁盘状态驱动

5. **hallucination guard 是硬规则，不只是 README 文案**
   `src/resources/extensions/gsd/auto/phases.ts` 明确处理：execute-task 完成但 0 tool calls 时，视为 hallucinated summary 并标记失败重试。

**对 Beacon 最有价值的借鉴点**

- state-on-disk + fresh-session-per-unit
- worktree / branch / none 这种可配置隔离边界
- 0-tool-call / 0-output 的 hallucination guard
- 自定义 workflow definition 的 YAML 化与 run-state 持久化

**不建议直接照搬的部分**

- 直接追随 Pi SDK / GSD 的整套 runtime 复杂度
- 在 v1.1.6 阶段过早引入完整 web UI / forensics / parallel milestone orchestration

**关键证据文件**

- `oss-sync/automation/autoresearch/gsd-2/docs/architecture.md`
- `oss-sync/automation/autoresearch/gsd-2/docs/auto-mode.md`
- `oss-sync/automation/autoresearch/gsd-2/src/resources/extensions/gsd/custom-workflow-engine.ts`
- `oss-sync/automation/autoresearch/gsd-2/src/resources/extensions/gsd/run-manager.ts`
- `oss-sync/automation/autoresearch/gsd-2/src/resources/extensions/gsd/auto/phases.ts`
- `oss-sync/automation/autoresearch/gsd-2/src/worktree-cli.ts`

---

### 4.4 BMAD-METHOD

**定位（复核后）**

BMAD-METHOD 更像：

- 多阶段 guided development framework
- agent + workflow + help/navigation 体系
- 通过项目文档渐进构建上下文

它不是像 GSD 2 那样的 runtime/harness 项目，也不是像 gstack 那样的 QA/verification 专项项目。

**从仓库文档与结构确认到的关键机制**

1. **默认 BMM 套件是“agent + workflow”组织方式**
   `docs/reference/agents.md` 列出了默认 BMM agents（如 analyst / pm / architect / sm / dev / qa / ux / tech writer 等），每个 agent 通过 skill 调用。

2. **工作流是分阶段推进的**
   `docs/reference/workflow-map.md` 明确分为：
   - Analysis
   - Planning
   - Solutioning
   - Implementation
   - Quick Flow（平行捷径）

3. **`bmad-help` 是实时导航器，不只是 FAQ**
   workflow-map 和 how-to 文档都把 `bmad-help` 放在“随时问下一步”的核心位置，这一点对 Beacon 的 doctor / navigator 很有借鉴意义。

4. **上下文管理依赖项目文档逐步累积**
   workflow-map 中 `project-context.md` 的设计，体现出 BMAD 更强调“文档成为后续 agent 的共享上下文”。

**本次修正的关键口径**

- 不再把 BMAD 简化成“12+ agents”一句话
- 更准确的说法是：**默认 BMM 套件提供一组 agent + phase-based workflows，模块生态再继续扩展能力**

**对 Beacon 最有价值的借鉴点**

- phase-based workflow map
- `doctor/help/next-step` 型导航器
- `project-context.md` 这类跨工作流共享上下文文件
- Quick Flow 与 Full Method 并存的分层复杂度策略

**不建议直接照搬的部分**

- 大量 agent persona 命名与菜单式触发体系
- 在 v1.1.6 就引入完整 Party Mode / 全模块生态

**关键证据文件**

- `oss-sync/automation/autoresearch/bmad-method/docs/reference/agents.md`
- `oss-sync/automation/autoresearch/bmad-method/docs/reference/workflow-map.md`
- `oss-sync/automation/autoresearch/bmad-method/src/bmm-skills/module-help.csv`
- `oss-sync/automation/autoresearch/bmad-method/src/core-skills/`

---

### 4.5 autoresearch

**定位（复核后）**

autoresearch 不是通用产品工作流框架，而是一个非常纯粹的：

- 单目标优化循环
- 固定时间预算实验框架
- human-edited instruction + agent-edited implementation 的分离模型

**从源码确认到的关键机制**

1. **唯一可修改代码目标被强约束**
   `program.md` 明确规定 agent 只能改 `train.py`，`prepare.py` 和评估 harness 不可改。

2. **固定 5 分钟 wall clock 预算是硬约束**
   `program.md` 与 `prepare.py` 都显示 time budget = 300 秒，不是“建议时长”。

3. **评估目标是单一指标 `val_bpb`**
   这是一个高度可量化、可比较、可回滚的实验框架。

4. **`program.md` 扮演的是轻量 human-edited agent instruction**
   README 与 `program.md` 都明确把它描述为 lightweight skill / instructions 文件。

**对 Beacon 最有价值的借鉴点**

- 对长循环任务引入固定 timebox
- 把“允许改哪些文件 / 不允许改哪些文件”写成一等约束
- 用单一指标或单一验收口径约束自主迭代任务

**不建议直接照搬的部分**

- `LOOP FOREVER` 这种无限自主策略
- 把通用产品 workflow 强行简化成单指标优化问题

**关键证据文件**

- `oss-sync/automation/autoresearch/karpathy-autoresearch/program.md`
- `oss-sync/automation/autoresearch/karpathy-autoresearch/prepare.py`
- `oss-sync/automation/autoresearch/karpathy-autoresearch/train.py`
- `oss-sync/automation/autoresearch/karpathy-autoresearch/README.md`

---

### 4.6 MemEvolve

**定位（复核后）**

MemEvolve 是一个 **memory system research framework**，核心问题是：

- memory content 怎么更新
- memory architecture 本身能否被自动生成 / 进化 / 评估

它更适合作为 Beacon 的**长期上下文策略研究输入**，而不是 v1.1.6 的直接产品蓝图。

**从源码确认到的关键机制**

1. **memory system 在代码里是显式 registry**
   `EvolveLab/memory_types.py` 用 `MemoryType` + `PROVIDER_MAPPING` 统一管理 memory providers，而不是抽象概念停留在论文层。

2. **既有 baseline memory，也有 evolved memory**
   当前 registry 中同时包含 baseline systems 与 evolved systems（如 `lightweight_memory`、`cerebra_fusion_memory`）。

3. **评估 harness 是实装的**
   `run_flash_searcher_mm_gaia.py`、`run_flash_searcher_webwalkerqa.py`、`run_flash_searcher_mm_xbench.py` 都是实际 runner，不是只写在论文里。

4. **auto-evolve CLI 是真实的多轮演化入口**
   `evolve_cli.py` 明确提供 `auto-evolve`，支持 dataset、round、num-systems、top-t、creativity 等参数。

**对 Beacon 最有价值的借鉴点**

- 把 memory strategy 视为可替换 provider，而不是单一固定实现
- 让 context/memory 策略具备可评估接口
- 用 benchmark 驱动长期 memory 改进，而不是拍脑袋优化 prompt

**不建议直接照搬的部分**

- meta-evolution / provider generation / benchmark tournament 本身
- 在 v1.1.6 就把 context system 做成 research platform

**关键证据文件**

- `oss-sync/automation/autoresearch/memevolve/Flash-Searcher-main/EvolveLab/memory_types.py`
- `oss-sync/automation/autoresearch/memevolve/Flash-Searcher-main/EvolveLab/config.py`
- `oss-sync/automation/autoresearch/memevolve/Flash-Searcher-main/evolve_cli.py`
- `oss-sync/automation/autoresearch/memevolve/Flash-Searcher-main/run_flash_searcher_mm_gaia.py`
- `oss-sync/automation/autoresearch/memevolve/Flash-Searcher-main/run_flash_searcher_webwalkerqa.py`

---

### 4.7 DeerFlow

**定位（复核后）**

DeerFlow 更像一个 **full-stack super-agent harness**，而不是单一 deep research agent：

- backend 有明确的 Harness / App 双层架构
- runtime 同时覆盖 LangGraph、Gateway API、sandbox、subagents、memory、skills、MCP
- frontend 是与 runtime 深度耦合的工作台，而不是薄壳 demo
- custom agents、uploads、artifacts、channels 都已产品化

**从源码确认到的关键机制**

1. **Harness / App split 是显式架构约束**
   `backend/CLAUDE.md`、`backend/docs/HARNESS_APP_SPLIT.md` 与 `tests/test_harness_boundary.py` 共同表明：`packages/harness/deerflow/` 是可发布 runtime 层，`app/` 是应用层，且 harness 被硬性禁止反向 import `app.*`。

2. **thread-scoped data contract 是一等运行契约**
   `config/paths.py` 把每个 thread 的 `workspace / uploads / outputs` 目录和 `/mnt/user-data/*` 虚拟路径都明确建模；上传、工作区、产物展示在工具层和 gateway 层有完整闭环。

3. **runtime safety 下沉到 middleware**
   `lead_agent/agent.py` 与 `agents/middlewares/*` 可以看到 loop detection、tool error degradation、subagent limit、clarification、todo、uploads、memory、view_image 等 concern 被拆成独立 middleware，而不是全靠 prompt 约束。

4. **subagent 是真实执行面，不是概念展示**
   `tools/builtins/task_tool.py` 与 `subagents/executor.py` 显示：子 agent 具备后台执行、状态机、timeout、事件回传、thread/sandbox/model 继承等完整运行时行为。

5. **extensibility 是 skills + MCP + custom agents + community tools 组合模型**
   `skills/loader.py`、`config/extensions_config.py`、`app/gateway/routers/skills.py`、`app/gateway/routers/agents.py` 表明 DeerFlow 不只支持技能包，还支持 MCP servers、custom agents（`config.yaml + SOUL.md`）和 community tool adapters。

6. **它已经是产品化系统，而非单仓库 runtime 实验**
   root Makefile、docker compose、gateway routers、frontend routes、issue templates、backend CI 表明 DeerFlow 已覆盖配置、部署、治理、前端工作台和渠道集成。

**对 Beacon 最有价值的借鉴点**

- Harness / App split
- 线程级目录契约（`workspace / uploads / outputs`）
- middleware-based runtime safety
- 扩展面分层（skills / MCP / custom agents / community adapters）
- 上传到产物展示的文件生命周期设计

**不建议直接照搬的部分**

- DeerFlow 的 full-stack 功能广度（frontend、channels、K8s provisioner）
- 对 LangGraph / 当前技术栈的具体绑定
- 一次性复制完整 super-agent 平台能力

**关键证据文件**

- `oss-sync/agents/agent-skills/deer-flow/backend/docs/HARNESS_APP_SPLIT.md`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/config/paths.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/packages/harness/deerflow/subagents/executor.py`
- `oss-sync/agents/agent-skills/deer-flow/backend/app/gateway/routers/agents.py`
- `oss-sync/agents/agent-skills/deer-flow/frontend/src/core/threads/hooks.ts`


## 5. 面向 Beacon 的能力矩阵（只比较相关维度）

### 5.1 Workflow / Artifact 生命周期

| 项目 | 结论 |
|------|------|
| OpenSpec | **强**：artifact lifecycle 是核心能力，且 profile/delivery 机制清晰 |
| BMAD-METHOD | **强**：phase-based 文档流很明确，但更偏 guided workflow 而非 runtime |
| GSD 2 | **中**：有 run/graph/state，但重点是执行控制，不是 artifact 设计本身 |
| gstack | **弱**：不是 artifact workflow 项目 |
| DeerFlow | **中**：有上传、产物、custom agents 等对象链路，但重点仍是平台运行时而非 artifact-first 设计 |
| autoresearch | **弱**：只有实验日志与单文件修改约束 |
| MemEvolve | **弱**：重点不在产品产物流 |

### 5.2 Runtime / 调度 / 隔离

| 项目 | 结论 |
|------|------|
| GSD 2 | **强**：fresh session、state-on-disk、worktree、dispatch pipeline、hallucination guard |
| DeerFlow | **强**：harness/app split、thread isolation、sandbox provider、subagent runtime、middleware safety 都很成熟 |
| gstack | **中**：browser daemon 很强，但只覆盖浏览器执行面 |
| autoresearch | **中**：实验 loop 强，但仅限单目标训练场景 |
| OpenSpec | **弱**：更像 workflow 交付层，不是 runtime 层 |
| BMAD-METHOD | **弱**：偏 methodology |
| MemEvolve | **中**：有 evolution loop，但不是通用 coding runtime |

### 5.3 验证 / 质量控制

| 项目 | 结论 |
|------|------|
| gstack | **强**：分层验证、health score、expensive checks gating 最完整 |
| GSD 2 | **中**：doctor / stuck detection / hallucination guard / runtime diagnostics 很强，但不是 QA 金字塔 |
| DeerFlow | **中**：backend 测试、issue template、runtime guards 较强，但重点仍是平台稳定性而非 QA 金字塔 |
| OpenSpec | **中**：有 verify workflow，但重点是 spec consistency，不是 multi-tier QA |
| BMAD-METHOD | **中**：implementation readiness / review / help 导航有价值，但验证不是其独特强项 |
| autoresearch | **强（单指标）**：单一 metric 极其明确，但不适合通用产品验证 |
| MemEvolve | **中**：benchmark harness 强，但属于研究评估，不是产品 QA |

### 5.4 Context / Memory 策略

| 项目 | 结论 |
|------|------|
| BMAD-METHOD | `project-context.md` 适合做共享上下文文件 |
| GSD 2 | state-on-disk + `KNOWLEDGE.md` 类机制更贴近执行期上下文治理 |
| DeerFlow | global/per-agent memory、`USER.md`、thread-scoped user-data 说明它更偏平台级上下文数据面 |
| MemEvolve | provider-based memory architecture 最适合长期研究 |
| OpenSpec | 更偏 planning/context artifacts，而非 memory system |
| gstack | 更偏技能和验证，不是 memory 项目 |
| autoresearch | `program.md` 适合做轻量 instruction 文件，不适合做通用 memory 架构 |

---

## 6. 对 Beacon v1.1.6 的建议（按优先级）

### 6.1 适合立刻吸收（v1.1.6）

1. **OpenSpec：artifact lifecycle + workflow profile 思想**
   - 吸收 `proposal/spec/design/tasks` 的结构化思路
   - 但不要误解为“先做 22 个 skill”
   - Beacon 更适合先定义：核心 workflow、扩展 workflow、交付方式

2. **GSD 2：fresh session / state-on-disk / hallucination guard**
   - 每个执行单元重新开 session
   - 运行状态落盘
   - 对“0 tool calls / 0 实际产出”的执行直接判失败

3. **DeerFlow：Harness / App split + 线程级数据契约**
   - 把 runtime 框架层与产品/API/UI 层解耦
   - 明确 `workspace / uploads / outputs` 三种语义目录
   - 把 loop guard、tool-error degradation、subagent limits 下沉到 middleware

4. **gstack：模板生成 + 分层验证 + stop heuristic**
   - `tmpl -> generated docs`
   - 免费检查优先、昂贵检查后置
   - 用明确 heuristic 约束自主修复 loop

5. **BMAD：doctor/help 型导航器**
   - Beacon 的 `doctor` 不应只做诊断
   - 还应回答“你现在在哪一阶段、下一步该做什么”

6. **autoresearch：长循环任务时间盒**
   - 对高成本自主执行引入固定 timebox
   - 避免“永远继续”造成成本和上下文失控

### 6.2 适合下一阶段吸收（v1.2.x）

1. **GSD 2：workflow definition as data**
   - 把部分 Beacon workflow 外部化为声明式定义
   - 但只做少量高价值 workflow，不要一开始全 YAML 化

2. **DeerFlow：custom agents 资源化 + skills/MCP 双层扩展**
   - 让 `config.yaml + SOUL.md` 这类 agent 定义成为正式资源对象
   - 把 workflow skills 与 protocol/tool adapters 分层管理

3. **BMAD：Quick Flow vs Full Method**
   - 为不同规模任务提供轻/重两档流程

4. **gstack：diff-aware expensive checks**
   - 把昂贵验证限制到“受影响部分”

### 6.3 暂不建议进入 v1.1.6 主线

| 来源 | 暂缓原因 |
|------|----------|
| gstack browser daemon / ref system | 太偏浏览器执行面，不是 Beacon 当前主战场 |
| OpenSpec 的跨工具安装/分发复杂度 | 太早，会稀释 Beacon 自身产品边界 |
| GSD 2 全量 runtime / web UI / parallel orchestration | 复杂度高，超出 v1.1.6 合理范围 |
| DeerFlow 的 full-stack 广度（frontend、channels、K8s provisioner） | 平台能力太多，短期直接照搬会导致范围失控 |
| MemEvolve 的 meta-evolution | 研究价值高，但产品落地周期长 |
| autoresearch 的无限循环自治 | 风险高，不适合直接迁移到通用产品任务 |

---

## 7. 本轮研究后的客观结论

### 7.1 如果只选最值得借鉴的四个方向

1. **OpenSpec 的 artifact lifecycle**
2. **GSD 2 的 runtime hygiene（fresh session / state-on-disk / guard）**
3. **DeerFlow 的 Harness / App split + thread-scoped data contract**
4. **gstack 的模板化交付 + 分层验证**

### 7.2 如果只选一个长期研究方向

- **MemEvolve 的 provider-based memory strategy**

但它应被放进 Beacon 的**长期 context architecture research backlog**，而不是 v1.1.6 的直接实现目标。

### 7.3 当前最需要避免的误判

- 不要把“skill 数量”当成能力强弱指标
- 不要把“health checks”和“QA 金字塔”当成同一件事
- 不要把 memory research 框架误当成短期产品工作流模板
- 不要因为 gstack 研究更深，就默认它对 Beacon 的所有层面都最 relevant

---

## 8. 关键证据索引

| 项目 | 本次主要核对文件 |
|------|------------------|
| gstack | `BROWSER.md`, `ARCHITECTURE.md`, `qa/SKILL.md`, `scripts/gen-skill-docs.ts` |
| OpenSpec | `src/core/profiles.ts`, `src/core/init.ts`, `docs/commands.md`, `docs/supported-tools.md` |
| GSD 2 | `docs/architecture.md`, `docs/auto-mode.md`, `src/resources/extensions/gsd/custom-workflow-engine.ts`, `src/resources/extensions/gsd/run-manager.ts`, `src/resources/extensions/gsd/auto/phases.ts`, `src/worktree-cli.ts` |
| BMAD-METHOD | `docs/reference/agents.md`, `docs/reference/workflow-map.md`, `src/bmm-skills/module-help.csv`, `src/core-skills/` |
| autoresearch | `program.md`, `prepare.py`, `train.py`, `README.md` |
| MemEvolve | `EvolveLab/memory_types.py`, `EvolveLab/config.py`, `evolve_cli.py`, `run_flash_searcher_mm_gaia.py`, `run_flash_searcher_webwalkerqa.py` |
| DeerFlow | `backend/docs/HARNESS_APP_SPLIT.md`, `config/paths.py`, `lead_agent/agent.py`, `subagents/executor.py`, `gateway/routers/agents.py`, `frontend/src/core/threads/hooks.ts` |

---

## 9. 下一步建议

如果继续完善 `research/` 目录，推荐按以下顺序继续补齐：

1. **新增 `design-input.md`**：把客观研究与 Beacon 内部采纳清单分离
2. **给各项目补“证据等级 + 适配层级 + 迁移成本”打分卡**
3. **把 DeerFlow / GSD 2 / gstack 的共性抽成一份 runtime design note**
4. **把 OpenSpec / BMAD 的共性抽成一份 workflow design note**

