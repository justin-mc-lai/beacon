# Brainstorm: Beacon 多项目严格隔离、独立经验沉淀与人机分工模型

**日期**：2026-04-07  
**方法**：基于 `$brainstorm` 七维发散框架收敛  
**目标**：设想一种可复用的 Beacon 形态，使多个项目在同一 Beacon 体系下实现：

- 版本需求文档物料统一管理
- 项目之间严格隔离
- 人类负责思考，agent 负责执行
- 每个项目都有独立经验沉淀工作流
- 跨项目只复用被允许输出的经验资产，而不是直接打通上下文

**主要输入**：

- `docs/beacon/v1.1.0/research/beacon-workspace-multiproject-config-research.md`
- `docs/beacon/research/beacon-karpathy-llm-wiki-pattern-analysis.md`
- `docs/beacon/v1.1.12/research/beacon-external-reference-study-statsclaw-awesome-design-md.md`
- `docs/beacon/v1.1.12/execution/architecture-blueprint.md`

---

## 1. 核心问题

现在要解决的不是“如何让 Beacon 支持多个项目”这么简单，而是同时满足五个约束：

1. **统一管理**
   - 所有项目都能用同一套 Beacon 版本文档与治理协议
2. **严格隔离**
   - 项目 A 的上下文、经验、执行面不能默认泄漏到项目 B
3. **人机分工**
   - 人类主要负责 framing、判断、裁决、重构规则
   - agent 主要负责执行、整理、编译、更新物料
4. **独立沉淀**
   - 每个项目都可以拥有自己的经验库、索引、日志、治理历史
5. **可复用**
   - 跨项目可复用的是“蒸馏后的模板、策略、contract、经验包”，不是原始项目私有材料

一句话：

> Beacon 要从“单项目工作流工具”进一步演化成“多项目隔离治理内核 + 项目独立知识工作区 + 受控经验蒸馏系统”。

---

## 2. 七维发散

## 2.1 用户维度

### 核心用户

1. **产品/研究负责人**
   - 负责 framing、需求判断、优先级、最终裁决
2. **项目执行型 agent**
   - 负责 ingest、实现计划编译、writeback、验证与文档维护
3. **跨项目维护者**
   - 负责升级 Beacon 版本线、维护 schema、抽取可复用经验

### 潜在用户

- 需要同时维护多个客户项目的工作室
- 多产品线团队
- 既做研究又做交付的个人开发者

### 不适合的用户

- 希望所有项目直接共享上下文、不在意隔离的人
- 只想要一个临时脚本，不关心长期知识沉淀的人

### 初步判断

这个系统最适合高频、多项目、强治理要求场景，不适合一次性轻量任务。

---

## 2.2 场景维度

### 典型场景

#### 场景 A：同一 workspace 管多个项目

- 用户在统一工作区里同时维护 `beacon`、`project-a`、`project-b`
- 希望 Beacon 能统一版本治理，但绝不串项目材料

#### 场景 B：同一 Beacon 版本服务多个项目

- `v1.2.x` 是统一治理内核
- 不同项目各自绑定自己的 profile、skill、经验库、交付规则

#### 场景 C：接手型项目与绿地项目并存

- takeover 项目需要严格 baseline freeze
- greenfield 项目则主要围绕需求与原型治理

#### 场景 D：跨项目复用经验

- 用户在项目 A 里沉淀了一个高价值经验
- 想让项目 B 受益
- 但必须先经过“蒸馏/脱敏/模板化”，不能直接读取 A 的私有上下文

### 连续场景

使用前：

- 人类在做 framing，决定这轮要推进哪个项目、哪个版本、哪个问题

使用中：

- agent 在严格 scope 内执行 ingest / compile / update / verify

使用后：

- 结果被写回该项目独立知识层
- 只有经过显式蒸馏的部分才能进入跨项目可复用层

---

## 2.3 业务维度

如果把 Beacon 看成产品内核，这个方向的商业和产品价值在于：

### 最直接的价值

- 一个团队可以用同一套 Beacon 内核治理多个项目
- 项目之间不混料
- 经验沉淀不会随聊天记录消失

### 差异化机会

相对普通 agent 工具：

- 它们多是“会执行”
- Beacon 可以强调“会治理多项目执行，并保持隔离”

相对普通知识库：

- 它们多是“能记住”
- Beacon 可以强调“能把需求、执行、验证、版本治理与知识沉淀放进同一个闭环”

### 对 Beacon 的产品机会

可形成三层产品面：

1. **Kernel**
   - 版本真相、治理协议、命令面、artifact contract
2. **Project Capsule**
   - 每个项目的独立材料与独立经验层
3. **Distilled Asset Plane**
   - 跨项目复用的模板、经验包、policy pack、profile pack

---

## 2.4 技术维度

### 主要技术挑战

| 挑战类型 | 难度 | 初步应对 |
|---------|-----|---------|
| 项目隔离 | 高 | project capsule + namespace + write/read boundary |
| 版本治理 | 高 | single-source version truth + per-project binding |
| 经验复用 | 高 | 只允许 distill/export，不允许默认 cross-read |
| 人机分工 | 中 | human lane / agent lane contract |
| 统一管理 | 中 | workspace registry + project manifest |
| 可追踪性 | 高 | index/log/ledger + execution evidence |

### 最需要明确的技术原则

#### 原则 1：默认隔离，显式输出

不允许：

- 项目 A 默认读项目 B 的 materials
- 项目 A 默认读项目 B 的经验库

只允许：

- 项目 A 产出 `distilled asset`
- 该资产经过批准后进入共享层

#### 原则 2：Beacon core 只做内核，不吞项目执行面

继续保持：

- requirement kernel
- delivery evidence kernel
- learning plane governance

保持外部：

- project execution adapters
- project-specific verify/delivery/debug operations

#### 原则 3：经验复用走“编译”而非“共享内存”

跨项目经验不应是直接共享上下文，而应是：

```text
project-private raw knowledge
→ project-private wiki/materials
→ distill
→ sanitized reusable pack
→ opt-in import by other projects
```

这与 `LLM Wiki` 的 compiled knowledge 思路一致，也与 StatsClaw 的 `brain / brain-seedbank` 分层相呼应。

---

## 2.5 体验维度

### 关键体验

| 体验点 | 重要度 | 目标体验 |
|-------|-------|---------|
| 不串项目 | ★★★★★ | 用户对“不会串料”有强信心 |
| 可理解 | ★★★★★ | 一眼知道当前在操作哪个项目、哪个版本、哪个 lane |
| 可追踪 | ★★★★★ | 每次 ingest / query / lint / implement 都有证据 |
| 低心智负担 | ★★★★☆ | 人不需要手动整理大量材料 |
| 复用感 | ★★★★☆ | 能感受到经验在沉淀，而不是聊天即消失 |

### 理想心智模型

用户应感知到：

- Beacon 不是一个大杂烩工作区
- 它是一个统一内核下的多个独立 capsule
- 每个 capsule 都有自己的 wiki/materials/log
- 跨 capsule 的复用必须经过可见、可审计的蒸馏流程

### 最重要的 UX 信号

每次执行前，Beacon 都应该显式展示：

```text
Resolved Project Capsule: project-a
Beacon Version Line: vX.Y.Z
Project Mode: takeover | greenfield | project-profiled
Human Lane: framing / decision / review
Agent Lane: ingest / compile / verify / writeback
Knowledge Scope: private | distilled-imports-only
```

---

## 2.6 价值维度

### 功能价值

- 多项目治理不混乱
- 经验沉淀可持续
- 版本文档物料不失控

### 认知价值

- 把“人思考、agent执行”明确制度化
- 把知识资产从聊天里捞出来，变成长期可维护文档

### 品牌价值

如果做对了，Beacon 会更清楚地成为：

> 一个治理 AI-assisted product work 的操作系统，而不是仅仅一堆工作流命令。

---

## 2.7 风险维度

| 风险类型 | 概率 | 影响 | 应对方案 |
|---------|-----|-----|---------|
| 隔离做成表面文章 | 中 | 大 | 默认禁止 cross-read，必须有 namespace 与导出合同 |
| 统一管理变成大一统臃肿系统 | 中 | 大 | core / capsule / distill plane 严格分层 |
| 经验沉淀过重，用户懒得维护 | 高 | 中 | 让 agent 负责维护，人类只做裁决 |
| 复用时泄漏项目私有信息 | 中 | 大 | 增加 sanitize/distill/export 审查面 |
| 项目 lane 太复杂，使用门槛上升 | 中 | 中 | 保持默认路径简单，复杂能力后置 |

---

## 3. 聚类收敛：最合理的系统形态

综合七维发散，最值得推进的不是“共享大 workspace”，而是：

## 3.1 三层结构

### Layer 1: Beacon Kernel

负责统一：

- version truth
- docs contract
- command surface
- requirement kernel
- delivery evidence kernel
- learning-plane boundary

### Layer 2: Project Capsule

每个项目一个独立 capsule，负责：

- project manifest
- project profile
- docs/materials
- private research wiki
- private log/index
- private runtime state
- private experience ledger

建议心智模型：

```text
workspace/
  beacon-kernel/
  capsules/
    project-a/
    project-b/
```

### Layer 3: Distilled Asset Plane

只存放被允许跨项目复用的蒸馏资产：

- profile templates
- design governance packs
- evidence/review templates
- implementation-plan templates
- distilled lessons

这个层不保存项目私有材料，只保存“已经被清洗并批准公开复用”的资产。

---

## 3.2 两条工作 lane

### Human lane

人类负责：

- framing
- problem selection
- priority
- constraint setting
- keep/discard
- release judgement
- distill approval

### Agent lane

agent 负责：

- source ingest
- summary/update/index/log maintenance
- requirement material compilation
- implementation-plan compilation
- verify evidence collection
- lint / consistency audit
- draft distillation pack

这正是把本次对话中 `LLM Wiki` 的 insight 转进 Beacon：

> 人类不负责做繁琐维护；agent 承担编译和维护工作；人类负责高阶判断。

---

## 3.3 四个关键 artifact

为让这个模型真正落地，建议每个 project capsule 至少具备以下四类 artifact：

### A. `manifest`

定义：

- project id
- project root
- Beacon version binding
- mode
- allowed adapters
- isolation policy
- distill/export policy

### B. `index`

项目知识索引，回答：

- 当前项目有哪些正式 materials
- 哪些是核心页面
- 哪些是高价值经验页

### C. `log`

项目时间线，记录：

- ingest
- query
- lint
- implement
- verify
- distill/export

### D. `experience ledger`

显式记录：

- 哪些经验只属于该项目
- 哪些经验已蒸馏
- 哪些经验已导出到共享层
- 哪些经验被别的项目导入

---

## 4. 严格隔离应该长什么样

这里的“严格隔离”不能只靠目录结构，必须同时有四个约束。

## 4.1 读隔离

默认只允许 agent 读取：

- 当前 capsule 内 materials
- 当前 capsule 明确声明允许读取的 shared distilled assets
- Beacon kernel 的正式协议文档

默认禁止读取：

- 其他 capsule 的 private materials
- 其他 capsule 的 private logs
- 其他 capsule 的 private runtime state

## 4.2 写隔离

默认只允许 agent 写：

- 当前 capsule 的 docs/runtime/log/index
- kernel 允许写入的受控全局面

禁止：

- 在未切换 capsule 的情况下写其他项目

## 4.3 经验隔离

项目经验默认 private。

只有通过以下链路才允许外流：

```text
private experience
→ distill draft
→ human review
→ sanitize
→ shared asset
```

## 4.4 执行隔离

每个项目的 adapter、verify、delivery、debug surface 都必须显式绑定。

Beacon 只做：

- route
- govern
- validate
- record evidence

不替项目吞掉具体执行面。

---

## 5. 支持独立经验沉淀工作流的推荐模型

结合 `LLM Wiki` 模式，建议每个项目 capsule 内都有自己的小型知识编译闭环：

```text
raw project sources
→ ingest
→ project wiki/materials
→ query
→ query writeback
→ lint
→ distill candidate
```

其中：

- `raw sources` 是项目原始材料
- `project wiki/materials` 是该项目的 compiled knowledge layer
- `query writeback` 确保重要洞察不丢失在对话里
- `distill candidate` 是未来可复用资产候选

这意味着每个项目都拥有自己的：

- private index
- private log
- private compiled knowledge
- private experience ledger

而不是所有项目共享一个模糊的“大记忆池”。

---

## 6. 把这次对话经验沉淀成 Beacon 可复用原则

这次对话至少沉淀出六条 Beacon 可复用原则：

### Principle 1

**统一管理不等于共享上下文。**

统一的是 kernel、version truth、artifact contract；隔离的是项目上下文、执行面、经验库。

### Principle 2

**跨项目复用应该走蒸馏，不走直连。**

复用的是 distilled assets，不是原始项目知识。

### Principle 3

**人类负责 thinking lane，agent 负责 execution lane。**

不要让人类承担大规模整理、交叉引用、材料维护工作。

### Principle 4

**每个项目都应有独立的 compiled knowledge layer。**

不是只有 workflow state，还要有项目自己的研究/经验 wiki。

### Principle 5

**需要 index/log/ledger 三件套。**

- `index` 解决找什么
- `log` 解决最近做了什么
- `ledger` 解决哪些经验可复用

### Principle 6

**Beacon 下一版本应优先增强 capsule 与 distill 机制，而不是继续扩命令面。**

问题已经不是“命令够不够多”，而是“多项目治理和知识隔离是否清晰”。

---

## 7. 收敛后的候选方案

最值得继续推进的是这个方案：

## 方案名

**Beacon Capsule + Distill Plane**

## 定义

在统一 Beacon kernel 之上，为每个项目建立独立 capsule，并建立一个受控共享的 distill plane。

## 最小闭环

1. kernel 管理版本真相、协议和治理
2. capsule 管理每个项目的私有 materials / wiki / logs / runtime
3. distill plane 管理经批准可复用的共享资产
4. human lane 做裁决
5. agent lane 做维护和执行

## 为什么它最稳

- 兼容当前 Beacon 的四层边界模型
- 兼容 `LLM Wiki` 的知识编译思路
- 兼容 StatsClaw 的隔离与 shared-brain 灵感
- 兼容 awesome-design-md 的资产化启发

---

## 8. 建议下一步

如果要把这个 brainstorm 继续推进成 Beacon 正式方案，建议按顺序做三件事：

1. **先写 architecture research / PRD**
   - 明确 `kernel / capsule / distill plane` 三层合同
2. **再定义 artifact contract**
   - `manifest / index / log / experience-ledger / distill-pack`
3. **最后再落 runtime**
   - workspace routing
   - read/write isolation
   - distill/export flow

不要反过来先做 runtime patch。
先把系统边界和 artifact contract 说清，才能避免多项目支持变成又一轮通用 shell orchestration 膨胀。

---

## 9. 最终结论

这轮 brainstorm 最终收敛成一个明确判断：

> Beacon 的下一步不应是“让所有项目共享一个更强大的 agent 工作区”，而应是“在统一治理内核下，为每个项目提供严格隔离的 capsule，并通过受控 distill plane 实现跨项目复用”。

这样才能同时满足：

- 统一管理
- 严格隔离
- 人类思考 / agent 执行
- 项目独立经验沉淀
- 跨项目可复用

这也是把本次对话中最重要的经验真正沉淀成 Beacon 长期可复用方向的最稳方式。

