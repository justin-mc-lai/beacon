# Beacon v1.2.0 Target Project Kernel Blueprint

**状态**：Proposal  
**日期**：2026-04-07  
**范围**：下一阶段 Beacon 目标项目内核定义  
**定位**：把 Beacon 从“单项目 requirement/workflow 内核”推进为“统一治理内核下的多项目严格隔离 capsule 系统”

---

## 1. Intent

这份文档定义 Beacon 下一阶段的**目标项目内核**。

这里的目标不是继续扩命令面，也不是把 Beacon 变成另一个通用 super-agent runtime。
目标是建立一个更稳的内核，使 Beacon 可以同时满足：

1. 统一管理多个项目的版本需求文档物料
2. 对项目上下文、经验、执行面实现严格隔离
3. 明确 “人类负责思考，agent 负责执行” 的长期工作模型
4. 让每个项目拥有独立的经验沉淀闭环
5. 让跨项目复用通过受控蒸馏进行，而不是默认共享上下文

一句话：

> Beacon v1.2.0 的目标内核不是“更大的共享工作区”，而是“统一治理内核 + 独立项目 capsule + 受控蒸馏复用平面”。

---

## 2. Problem Statement

Beacon 当前已经形成较强的 requirement/governance/evidence kernel，但在多项目长期使用场景中仍存在四个结构性缺口：

1. **统一管理与严格隔离没有同时成立**
   - workspace 层面已有多项目配置研究
   - 但项目级知识层、经验层、执行层的默认隔离合同尚未成为正式内核

2. **知识沉淀仍偏版本包，不够项目化**
   - `docs/beacon/<version>/` 已是强版本知识包
   - 但缺少每个目标项目自己的 compiled knowledge layer

3. **跨项目复用路径不清晰**
   - 当前更像“手工参考经验”
   - 尚未定义什么经验可以导出、如何蒸馏、如何导入

4. **human lane / agent lane 仍然隐含**
   - 实践中已经在这么做
   - 但尚未成为正式 artifact contract 和 runtime contract

这些缺口会带来三个风险：

- 项目之间发生隐性串料
- 高价值经验留在会话中而不是长期资产里
- Beacon 逐渐滑向“什么都能编排”的大一统壳层，而失去内核边界

---

## 3. Design Inputs

本蓝图主要吸收以下四类输入：

### 3.1 Beacon 现有内核

来自 `v1.1.12` 的正式架构：

- requirement kernel
- delivery evidence kernel
- project execution adapters
- learning plane

### 3.2 `LLM Wiki` 模式

吸收其三层结构：

- raw sources
- compiled wiki
- schema

以及三种长期操作：

- ingest
- query
- lint

### 3.3 StatsClaw

吸收其两个信号：

- pipeline / role isolation 是一等产品面
- brain / seedbank 说明可复用知识应与项目执行面分层

### 3.4 `autoresearch`

吸收其两个纪律：

- subject surface 与 org/program surface 分离
- 固定预算、keep/discard、可回滚的进化面

---

## 4. Core Thesis

Beacon 的目标项目内核应建立在以下五条命题上：

1. **统一管理不等于统一上下文**
2. **项目隔离必须默认为真，而不是靠约定**
3. **跨项目复用必须通过蒸馏资产，不通过直接读取私有材料**
4. **人类主要编程于规则、方向、裁决面；agent 主要编程于执行、编译、维护面**
5. **Beacon 的价值在治理和知识编译，不在吞并项目自己的执行平台**

---

## 5. System Shape

目标系统形态如下：

```text
Beacon Kernel
→ resolve version truth
→ resolve project capsule
→ enforce read/write isolation
→ ingest project sources
→ compile project materials/wiki
→ query / writeback / lint
→ compile implementation/evidence artifacts
→ verify / gate / release
→ distill reusable assets
→ opt-in import into other capsules
```

它不是：

```text
shared workspace
→ all projects read everything
→ all agents share the same memory
→ reuse happens implicitly
```

也不是：

```text
Beacon becomes a universal runtime shell
→ every project operation moves into Beacon core
```

---

## 6. Primary Layers

### Layer 1: Beacon Kernel

这是全局统一的治理内核，负责：

- version truth
- docs/material contracts
- command surface
- requirement kernel
- delivery evidence kernel
- learning-plane governance
- isolation enforcement
- distill/import governance

Kernel 只解决“如何治理”，不吞项目自己的执行平台。

### Layer 2: Project Capsule

每个项目是一个独立 capsule。

它负责：

- project manifest
- project profile binding
- project-private docs/materials
- project-private compiled knowledge layer
- project-private logs and indexes
- project-private runtime state
- project-private experience ledger

这是 Beacon 未来多项目能力的真正隔离单位。

### Layer 3: Distill Plane

这是唯一允许跨项目复用的平面。

只保存：

- 已脱敏经验
- 已模板化合同
- profile packs
- design governance packs
- evidence/review packs
- distilled lessons

它不保存项目私有 source，不保存原始上下文，不保存可直接泄漏项目信息的运行状态。

---

## 7. Kernel Responsibilities

Kernel 的职责应严格收敛为以下九项：

1. 定义版本真相和 release line
2. 定义 project capsule 生命周期
3. 定义 artifact contract
4. 定义读写边界和访问控制
5. 定义 human lane / agent lane 合同
6. 定义 ingest / query / lint / distill / import 操作语义
7. 定义 project execution adapter 接口，但不实现项目私有执行逻辑
8. 定义 verify/gate/release 的证据面
9. 定义跨项目可复用资产的蒸馏和导入规则

Kernel 不应直接负责：

- 项目私有业务代码执行细节
- 项目私有部署流程
- 项目私有基础设施编排
- 任意 shell 级 orchestration 扩张

---

## 8. Project Capsule Model

### 8.1 Capsule Identity

每个 capsule 至少应包含：

- `project_id`
- `project_root`
- `beacon_version_line`
- `project_mode`
- `profile_binding`
- `adapter_binding`
- `isolation_policy`
- `distill_policy`

### 8.2 Capsule Modes

建议统一支持三种模式：

1. `greenfield`
   - 从需求到实现闭环构建新项目或新模块
2. `takeover`
   - 先建立 current-state truth，再进入 feature/implement
3. `project-profiled`
   - 已有项目 adapter / verify / delivery surface 明确绑定

### 8.3 Capsule Scope

capsule 的 scope 至少覆盖：

- project-private requirements
- project-private research
- project-private execution docs
- project-private runtime outputs
- project-private memory/wiki
- project-private evidence

---

## 9. Human Lane vs Agent Lane

### 9.1 Human Lane

人类负责：

- framing
- prioritization
- acceptance judgement
- keep/discard
- distill approval
- version and scope changes
- boundary decisions

### 9.2 Agent Lane

agent 负责：

- source ingest
- requirements compilation
- wiki/material maintenance
- cross-reference updates
- query synthesis
- query writeback
- lint/consistency checking
- implementation-plan compilation
- verify evidence collection
- distill draft generation

### 9.3 Why this split matters

这不是角色装饰，而是内核边界：

- 人类不应被迫做大量 bookkeeping
- agent 不应默认拥有重定义边界和跨项目迁移经验的权力

换句话说：

> 人类写“组织代码”，agent 写“执行代码”和“材料代码”。

这与 `autoresearch` 中 `program.md` vs `train.py` 的分离是一致的。

---

## 10. Artifact Contract

目标内核至少需要以下五类一等 artifact。

## 10.1 `manifest`

作用：

- 声明 capsule 的身份、模式、版本、边界和绑定

最小字段建议：

- `project_id`
- `project_root`
- `beacon_version`
- `project_mode`
- `profile`
- `execution_surface`
- `allowed_imports`
- `distill_policy`

## 10.2 `index`

作用：

- 让 agent 与人快速知道当前项目有哪些正式材料

最小内容建议：

- 页面清单
- 一句话摘要
- 优先阅读顺序
- 核心 artifact 标记

## 10.3 `log`

作用：

- 记录 capsule 的时间线演化

应记录：

- ingest
- query
- lint
- implement
- verify
- gate
- distill
- import

## 10.4 `experience-ledger`

作用：

- 管理经验从 private → distilled → imported 的状态机

应记录：

- 经验 id
- 当前归属 capsule
- 当前状态
- 是否脱敏
- 是否已批准导出
- 是否已被其他 capsule 导入

## 10.5 `distill-pack`

作用：

- 作为跨项目复用的最小单位

可包含：

- 摘要
- 适用条件
- 不适用条件
- 复用方法
- 相关 template / profile / policy
- provenance

---

## 11. Knowledge Model

### 11.1 Raw Sources

项目原始材料：

- 需求原文
- 历史文档
- 设计资料
- 代码库参考
- 外部研究资料

只读。

### 11.2 Compiled Knowledge Layer

项目 capsule 内部的编译层：

- research pages
- decision notes
- comparisons
- design summaries
- implementation guidance
- verification notes

这是项目内长期知识工作面。

### 11.3 Governance Layer

描述如何维护知识层和执行层：

- AGENTS / CLAUDE style schema
- version truth
- lane rules
- distill/import rules

这与 `LLM Wiki` 的三层模型对应：

```text
raw sources
→ compiled knowledge
→ schema/governance
```

---

## 12. Operations

目标内核需要把以下操作正式化。

## 12.1 Ingest

用途：

- 把新 source 编译进 capsule

结果：

- 更新 summary
- 更新 index
- 更新相关 pages
- 追加 log

## 12.2 Query

用途：

- 对 compiled knowledge 进行综合回答

结果：

- 生成回答
- 如有长期价值，可写回正式 docs

## 12.3 Lint

用途：

- 做知识和材料一致性检查

检查对象：

- 冲突 claim
- orphan pages
- stale decisions
- missing links
- missing evidence

## 12.4 Distill

用途：

- 从 project-private knowledge 中提炼可复用资产

要求：

- 去私有化
- 去项目耦合
- 说明适用边界

## 12.5 Import

用途：

- 把 distill plane 中的共享资产导入 capsule

要求：

- 显式 opt-in
- 记录 provenance
- 不把导入资产误认为本地私有经验

## 12.6 Implement / Verify / Gate

这些操作继续保留 Beacon 既有优势：

- implementation-plan compiler
- verification evidence
- gate/release closure

但执行时必须带上 capsule identity 与 execution surface identity。

---

## 13. Isolation Model

严格隔离必须同时在四个面成立。

### 13.1 Read Isolation

默认只允许读取：

- 当前 capsule 的 private materials
- Kernel 正式文档
- 当前 capsule 显式导入的 distilled assets

默认禁止读取：

- 其他 capsule 的 private materials
- 其他 capsule 的 private logs
- 其他 capsule 的 private runtime state

### 13.2 Write Isolation

默认只允许写入：

- 当前 capsule 的 docs/runtime/log/index/ledger
- Kernel 允许写入的全局受控面

禁止跨 capsule 无意写入。

### 13.3 Experience Isolation

经验默认 private。

只有通过：

```text
private
→ distill draft
→ human review
→ sanitize
→ shared
```

才允许离开 capsule。

### 13.4 Execution Isolation

每个 capsule 的：

- adapter
- verify surface
- delivery surface
- debug surface

必须显式绑定。

Beacon 不能因为“统一管理”而默认把所有项目拉回同一 native path。

---

## 14. Distill Plane Contract

distill plane 应满足四个条件：

1. **可审计**
   - 知道资产来自哪个 capsule、哪次蒸馏
2. **可批准**
   - 必须有 human approval 或等价 gate
3. **可边界化**
   - 知道资产适合什么，不适合什么
4. **可导入**
   - 被其他 capsule 以显式方式消费

建议 distill plane 的资产类型包括：

- `profile-pack`
- `policy-pack`
- `design-pack`
- `evidence-pack`
- `example-bundle`
- `lesson-pack`

---

## 15. Relationship to External Reference Projects

### StatsClaw

Beacon 应借鉴：

- 隔离验证的产品清晰度
- proof surface
- brain/seedbank 分层

Beacon 不应照搬：

- 统计软件包这一窄领域定位
- 多角色 runtime 作为主产品叙事

### awesome-design-md

Beacon 应借鉴：

- portable asset surface
- 单工件贡献漏斗

Beacon 不应照搬：

- 设计素材仓库本身

### DeerFlow

Beacon 应借鉴：

- Harness / App 边界纪律
- runtime assetization

Beacon 不应照搬：

- 大一统 super-agent harness 产品定位
- 以 thread isolation 替代 project isolation

### autoresearch

Beacon 应借鉴：

- 极小 subject surface
- org/program surface 与 subject surface 分离
- keep/discard discipline

Beacon 不应照搬：

- 单实验 repo 结构
- 把多项目治理退化成单优化环

---

## 16. Non-Goals

以下内容不属于本蓝图目标：

1. 把 Beacon 变成通用 super-agent runtime
2. 把所有项目 execution logic 并入 core
3. 让所有项目共享一个全局记忆池
4. 直接跨项目复用私有上下文
5. 为了多项目支持而无限扩张命令面

---

## 17. Migration Direction

建议分三步推进。

### Phase 1: Contract First

先定义：

- capsule manifest
- index/log/experience-ledger
- distill-pack
- read/write/import rules

### Phase 2: Docs and Runtime Alignment

让：

- version truth
- execution surface routing
- per-project binding
- log/index generation

与新 contract 对齐。

### Phase 3: Controlled Distill/Import

最后才实现：

- distill draft generation
- approval flow
- import flow
- provenance tracking

不要反过来先做 runtime patch。

---

## 18. Acceptance Criteria for the Kernel

当以下问题都能被稳定回答时，说明目标项目内核成立：

1. 当前操作属于哪个 project capsule？
2. 当前使用的 Beacon 版本线是什么？
3. 当前 project mode 是什么？
4. 当前允许读取哪些知识面？
5. 当前允许写入哪些 artifact？
6. 当前经验是 private 还是 distilled/imported？
7. 当前 implementation/verify/gate 绑定的是哪个 execution surface？
8. 当前有哪些长期知识页面、最近发生了什么、哪些经验可复用？
9. 某条经验为什么可以被别的项目导入？
10. 如果导入了共享资产，能否追溯其来源与适用边界？

如果这些问题仍需要靠隐含约定回答，而不是 artifact + runtime contract 回答，那么内核仍未完成。

---

## 19. Final Statement

Beacon v1.2.0 的目标项目内核可以总结为：

> 用统一治理内核管理多个项目，但把每个项目封装为独立 capsule；用 agent 维护项目知识与执行物料，用人类维护方向与裁决；用 distill plane 实现可审计、可批准、可导入的跨项目复用。

它成功的标志不是“支持了更多命令”，而是：

- 多项目不串料
- 长期知识可编译
- 经验可沉淀
- 复用可治理
- 人与 agent 的职责边界清楚

这才是 Beacon 下一阶段应该稳定下来的真正内核。

