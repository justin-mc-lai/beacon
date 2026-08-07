# Beacon Competitor & Open-Source Benchmark Registry

**Date**: 2026-07-27  
**Purpose**: 登记与深入分析 Agent / Spec / Workflow 领域的主流开源竞品，对比其在需求拆解、状态机编排、偏差控制（Drift/Inflation Detection）及任务追踪方面的实现机制，为 Beacon Goal / Truth 的持续演进提供可查验的开源参考账本与本地镜像索引。  
**Canonical Mirror Root**: `/Users/apple/Developer/Personal/oss-sync`

---

## 1. 竞品登记总览 (Competitor Inventory)

| 项目名称 | 官方/上游 GitHub | 本地镜像路径 (`oss-sync`) | 核心定位与关注点 | Beacon 借鉴方向 |
| --- | --- | --- | --- | --- |
| **`spec-kit`** | [github/spec-kit](https://github.com/github/spec-kit) | `pm/pm/spec-kit` | Spec-Driven Development (SDD) 工具链与规范模板 | 规范驱动开发 (SDD)、需求到任务图的结构化推导 |
| **`mattpocock-skills`** | [mattpocock/skills](https://github.com/mattpocock/skills) | `core-skills/mattpocock-skills` | TypeScript/前端高效 Agent Skill 规范集 | 渐进式 Context 注入、轻量化规则决策树与 Validation Checklist |
| **`everything-claude-code (ECC)`** | [affaan-m/ECC](https://github.com/affaan-m/ECC) | `agents/agent-skills/everything-claude-code` | 全景 Agent 生产力库 (Rules/Skills/Agents/Dashboard/Hooks) | 任务进度实时回显、Runtime Hooks 拦截、动态 Context 状态管理与注水/偏离纠正 |
| **`loopx`** | [huangruiteng/loopx](https://github.com/huangruiteng/loopx) | `automation/autoresearch/loopx` | Loop 工程状态内核 / agent-agnostic 本地控制平面 | quota-aware 唤醒、claims/leases 所有权、evidence 回写、typed handoff 交接契约 |
| **`oh-my-pi`** | [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi) | `agents/agent-systems/oh-my-pi` | Pi (badlogic/pi-mono) 的 coding-first fork，终端 AI coding agent | hashline 行锚定编辑防 diff 漂移、snapcompact 位图帧上下文压缩、agentLoop 显式状态/事件流 |
| **`kun`** | [KunAgent/Kun](https://github.com/KunAgent/Kun) | `agents/agent-systems/kun` | 本地优先 AI Agent 工作台（GUI+TUI），需求先行 coding 闭环 | cache-first agent loop、成本分层模型组合（长流程跑得起的预算前提）、追加式 JSONL 事件日志 |
| **`simple-long-horizon-agent`** | [simple-agent-lab/simple-long-horizon-agent](https://github.com/simple-agent-lab/simple-long-horizon-agent) | `automation/autoresearch/simple-long-horizon-agent` | Simple by design 的长程任务 agent（Python） | Δ vs Baseline 评测口径（分离 agent 价值与模型能力）、cost/task 度量 |

---

## 2. 竞品实现剖析与 Beacon 对照

### 2.1 GitHub Spec-Kit (`github/spec-kit`)
* **核心理念**：Specification-Driven Development (SDD)。认为自然语言在没有结构化规范前极易导致 AI 偏离，因此将 Spec 作为生成代码与任务拆解的唯一真理源。
* **架构与工作流**：
  - 通过 `specify` CLI + 模板驱动：`specify init` -> `specify spec` -> `specify plan` -> `specify tasks` -> `specify execute`。
  - `spec.md` 确定目标与界限，`plan.md` 建立架构变更，`tasks.md` 生成含依赖关系与测试约束的具体任务列表。
* **偏差与注水控制**：
  - 静态约束：任务只有当依赖项完成且 AST/Diff 验证通过后才能进入下一个节点。
  - 规则显式化：拒绝在没有 Spec 定义的情况下直接生成代码。
* **Beacon 对照与借鉴**：
  - **契合点**：Beacon 的 1+6 契约（`gen-truth` -> `tasks.md` -> `evidence.md`）与 Spec-Kit 的 SDD 思想高度同构。
  - **借鉴点**：可借鉴其 `specify tasks` 的任务拓扑依赖生成逻辑，优化 Beacon 的 `parallel_plan` 与 `task-graph` 动态排程。

---

### 2.2 Matt Pocock Skills (`mattpocock/skills`)
* **核心理念**：轻量、实效、Task-Focused。为开发者的特定领域小任务（如 TypeScript 重构、类型检查、组件拆分）提供高密度的 Agent 指导。
* **架构与工作流**：
  - 无重型 Python/Rust 引擎，纯 Markdown/YAML 编写的工程化 Skill 集合。
  - 强调 "Just-in-Time Context"（按需加载）：只在执行特定开发动作时引入对应的 Skill 指导。
* **偏差与注水控制**：
  - 使用严格的 Checklist（检查清单）与 Decision Tree（决策树）。
  - 规定 Agent 必须在每个关键步骤输出特定格式的 Verification Proof（验证凭据），防止虚假完成。
* **Beacon 对照与借鉴**：
  - **契合点**：Beacon 的渐进式 Skill 加载（Progressive Load）及 Stage-Exit Gates 与其思路一致。
  - **借鉴点**：可吸收 Matt Pocock Skills 中针对具体编码场景的轻量化 Step-by-Step 验证 Checklist，增强 Beacon 的 `gen-implement` 与 `eval-qa` 的原子验证能力。

---

### 2.3 Everything Claude Code / ECC (`affaan-m/ECC`)
* **核心理念**：全景 Agent 研发协同框架。覆盖智能体规则 (Rules)、系统指令 (Agents)、常用命令 (Commands)、自动化 Hook (Hooks) 和可视化面板 (Dashboard)。
* **架构与工作流**：
  - `WORKING-CONTEXT.md` 动态维护当前上下文与活跃任务。
  - 支持多 IDE / 多模型 (Codex, Claude, Cursor 等) 统一适配。
  - `hooks/` 在 Agent 工具调用前后实施强行拦截与校验。
* **偏差与注水控制**：
  - **动态 Task Breakdown**：将复杂需求实时切割并记录在任务看板中。
  - **Runtime Hook 拦截**：在 Agent 试图提交未验证代码或出现幻觉/注水（Padding）时，Hook 直接触发中断并重新引导。
  - **自适应恢复**：如果检测到当前路径停滞或偏离，通过上下文提取进行恢复或跳过。
* **Beacon 对照与借鉴**：
  - **契合点**：Beacon 的 `GoalRun` 阶段机、`durable-supervisor` 和 `execution.jsonl` 日志。
  - **借鉴点（高价值）**：ECC 的 **Runtime Hooks + WORKING-CONTEXT 任务看板** 为 Beacon 补充「注水检测、任务进度实时回显、取消当前偏差任务并自适应调度下一个」提供了极佳的落地方案。

### 2.4 Agent Loop 项目族（2026-08-03 新增，详见 [长程任务稳定性分析](./beacon-longrun-stability-analysis-2026-08.md)）

- **`loopx`**：与 Beacon GoalRun / DurableSupervisor 最同构——不替换 executor，只保状态。**quota-aware 唤醒**（S4 预算缺口）、**claims/leases 所有权**（S7 并发缺口）是 Beacon 直接可借鉴的两项。
- **`oh-my-pi`**：运行时稳定性——hashline 编辑锚定（变更应用层稳定）、snapcompact 压缩评测（S6 升级路径）。
- **`kun`**：长流程成本稳定性——cache-first loop + 模型成本分层，与 Beacon 需求先行/refreeze 思想同构。
- **`simple-long-horizon-agent`**：Δ vs Baseline 评测口径——给 Beacon 稳定性机制提供量化验收方法。

---

## 3. 检索与借鉴查阅指引 (Search & Reference Guide)

后续在演进 Beacon Goal/Truth 机制时，可直接通过 `oss-sync` 检索上述项目的具体实现文件：

```bash
# 1. 查阅 Spec-Kit 的任务拆解与规范模板
ls /Users/apple/Developer/Personal/oss-sync/pm/pm/spec-kit/templates/
cat /Users/apple/Developer/Personal/oss-sync/pm/pm/spec-kit/spec-driven.md

# 2. 查阅 Matt Pocock Skills 的轻量化规则与验证 Checklist
ls /Users/apple/Developer/Personal/oss-sync/core-skills/mattpocock-skills/skills/

# 3. 查阅 ECC 的 Runtime Hooks 与 Task Breakdown 机制
ls /Users/apple/Developer/Personal/oss-sync/agents/agent-skills/everything-claude-code/hooks/
ls /Users/apple/Developer/Personal/oss-sync/agents/agent-skills/everything-claude-code/rules/
cat /Users/apple/Developer/Personal/oss-sync/agents/agent-skills/everything-claude-code/WORKING-CONTEXT.md
```

---

## 4. 维护规范 (Maintenance Policy)

当引入新的同行竞品或开源参考时：
1. 确认已通过 `oss-sync` 镜像至 `/Users/apple/Developer/Personal/oss-sync/`。
2. 在本文 `§1 竞品登记总览` 中补充登记条目与本地相对路径。
3. 同步更新 `docs/beacon/research/beacon-open-source-reference-source-map.md` 与 `docs/beacon/research/index.md`。
