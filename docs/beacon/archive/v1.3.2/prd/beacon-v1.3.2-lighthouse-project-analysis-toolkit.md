# PRD：Beacon v1.3.2 Beacon Toolkit Lighthouse 项目分析工具包

**Feature**: `beacon-v1.3.2-lighthouse-project-analysis-toolkit`  
**Version**: `v1.3.2`  
**Date**: `2026-04-15`  
**Status**: `planning line`

## 1. 一句话定义

`Beacon Toolkit Lighthouse` 是一个**不进入主工作流**的可选分析型工具包能力。

它的职责不是生成 requirement truth，而是：

> 对任意目标项目、开源库、第三方包、基础设施链路或功能切片，快速生成一份单文件 Markdown 分析工件，使用 Mermaid + 中文说明，帮助用户在几分钟内建立正确的系统理解。

---

## 2. 要解决的问题

Beacon 现在已经能围绕 requirement → implement → qa → release 做正式闭环，
但还缺一个**主工作流之外**的“快速认知工具包”。

当前用户经常会遇到以下需求：

1. 刚接手一个开源库，想快速知道它的系统结构和入口文件
2. 想分析一个第三方包，但不想立刻进入 PRD / user-story 主链
3. 想搞清楚一个项目的链路基础设施设计：
   - gateway
   - BFF
   - service
   - queue
   - storage
4. 想快速拆解一个功能切片：
   - 入口在哪里
   - 调用了哪些模块
   - 涉及哪些依赖与边界
5. 想产出一份类似 `system-architecture-map.md` 的单文件成果，方便分享和后续继续深入

现在这些需求只能零散地依赖：

- 临时聊天分析
- 手写研究笔记
- 非结构化的 repo ramp-up

缺少一个正式产品面来承接。

---

## 3. 为什么这不应该进入主工作流

`Beacon Toolkit Lighthouse` 必须明确是：

- **分析工具包**
- **理解加速器**
- **认知地图生成器**

而不是：

- 主工作流新阶段
- freeze 前置常驻步骤
- 实现/QA/gate 的替代品

它与主工作流的关系应该是：

```text
Lighthouse 先帮助人建立系统理解
→ 若用户需要正式 requirement / implementation / QA 闭环
→ 再进入 Beacon 主链
```

也就是说：

> Toolkit Lighthouse 可以喂给 PRD / implement / QA，  
> 但 Toolkit Lighthouse 自己不应变成主链的一部分。

---

## 4. 脑暴收敛（嵌入 PRD）

按照 `$brainstorm` 七维发散，这个能力收敛成下面这组判断。

## 4.1 用户维度

### 核心用户

1. **Beacon 操作者 / 维护者**
   - 需要快速读懂目标项目
2. **接手型开发者**
   - 需要对陌生仓库做快速系统建模
3. **架构/平台负责人**
   - 需要快速梳理链路、依赖和边界
4. **产品/技术沟通者**
   - 需要一页式结构图文文档来对齐认知

### 直接排斥用户

1. 只想要代码执行，不想看分析的人
2. 不关心证据来源和文件引用，只想要一段随口总结的人

## 4.2 场景维度

### 典型场景

1. **Repo ramp-up**
   - 刚拿到一个项目，需要 10 分钟建立系统心智模型
2. **开源库研究**
   - 想快速掌握一个开源库的实现形态、关键模块和能力边界
3. **第三方依赖梳理**
   - 分析某个 package 在本项目里的职责、调用点和风险
4. **基础设施链路拆解**
   - 梳理 gateway → service → queue → storage 的路径
5. **功能切片解构**
   - 把一个 feature 从入口到核心模块画成单文件

## 4.3 业务维度

这个能力的价值不在于“增加工作流环节”，而在于：

1. 降低陌生代码库理解成本
2. 降低错误进入主工作流的概率
3. 提高团队共享认知的速度
4. 让 Beacon 不只是 workflow kernel，也具备“照亮项目”的工具包能力

## 4.4 技术维度

### 技术挑战

| 挑战 | 难度 | 说明 |
|---|---|---|
| 多语言/多框架项目 | 中 | 入口文件和模块边界识别不稳定 |
| 任意项目通用分析 | 中 | 需要约束输出深度，避免变成全仓漫游 |
| 输出既要快又要有用 | 高 | 不能只有目录树，也不能写成长报告 |
| 引用证据和推断边界 | 高 | 必须区分 confirmed / inferred |

### 技术原则

1. 默认只读分析
2. 默认单文件输出
3. 默认包含 Mermaid 图
4. 默认包含 source refs / key files
5. 必须显式区分“确认事实”和“推断判断”

## 4.5 体验维度

用户期待的体验不是“帮我研究一下”，而是：

> 给我一份像 `system-architecture-map.md` 那样，一眼能看懂、还能继续深挖的单文件分析图文。

这意味着输出必须有：

1. 总体结论
2. Mermaid 图
3. 关键入口
4. 模块边界
5. 外部依赖/系统关系
6. 风险和开放问题
7. 下一步建议

## 4.6 价值维度

### 核心价值

1. **功能价值**
   - 快速看懂项目/库/链路
2. **认知价值**
   - 帮用户建立正确心智模型
3. **协作价值**
   - 产出可共享单文件，不再依赖口头转述

## 4.7 风险维度

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| 分析过深，变成长报告 | 中 | 中 | 强制单文件 + 限制 sections |
| 把推断写成事实 | 高 | 高 | 显式 `Confirmed / Inferred / Open Questions` |
| 被误当成主工作流阶段 | 中 | 高 | 明确标注 optional toolkit, not workflow |
| 项目太大导致输出失焦 | 高 | 中 | 默认要求分析 scope（repo/package/feature/infra） |

---

## 5. 产品目标

## 5.1 总目标

在 `v1.3.2` 下新增一个 **Beacon Toolkit Lighthouse** 工具包能力，使用户能够：

1. 对任意目标项目进行快速分析
2. 产出一份单文件图文工件
3. 用于快速掌握：
   - 开源库
   - 第三方包
   - 链路基础设施
   - 功能特性切片
4. 如有需要，再把分析结果喂回 Beacon 主工作流

## 5.2 非目标

1. 不把 Lighthouse 变成 `prd -> user-story` 主链的新阶段
2. 不让 Lighthouse 自动 freeze 或写回正式 requirement truth
3. 不把 Lighthouse 做成新的 browser/QA/deploy runtime
4. 不在 v1.3.2 一次性引入完整图数据库或代码索引系统

---

## 6. 功能需求

### FR-001 必须提供独立的 Beacon skill 入口

新增一个独立 skill：

- `beacon-toolkit-lighthouse`

该 skill 必须被视为：

- optional toolkit
- analysis surface
- not a main workflow step

### FR-001A 必须采用统一 toolkit 命名

该能力必须明确进入 `Beacon toolkit` 命名体系：

- `beacon-toolkit-lighthouse`

后续如果 Beacon 继续扩展 workflow 外工具包能力，应统一采用：

- `beacon-toolkit-*`

规则：

> 不再使用 `beacon-<tool>` 形式命名这类 workflow 外分析工具，避免与主工作流技能表面混淆。

### FR-002 必须支持任意目标项目分析

Lighthouse 至少要支持以下分析对象：

1. 当前本地项目
2. 指定路径的子模块/子目录
3. 开源库镜像目录
4. 第三方包在目标项目中的使用切片
5. 基础设施链路或功能特性范围

### FR-003 必须支持单文件输出

默认输出必须是：

- 单个 Markdown 文件

建议默认输出位置：

- `.beacon/analysis/<slug>.md`

如果用户明确指定，也可以输出到：

- `docs/beacon/<version>/analysis/<slug>.md`

### FR-003A Beacon 源码迭代必须默认交付 Lighthouse 单文件

当分析对象是 **Beacon 源码自身** 时，默认交付物不能只落在 `.beacon/analysis/`。

它必须默认同时形成一份 versioned 单文件交付：

- `docs/beacon/<version>/execution/beacon-toolkit-lighthouse-<slug>.md`

这份交付物的职责是：

1. 成为 Beacon 源码迭代中的标准认知地图
2. 让版本包自带对当前功能/架构/链路的快速理解入口
3. 作为后续 PRD / implement / QA / release 的共享分析底图

规则：

> 对任意目标项目，Lighthouse 可以默认落到 `.beacon/analysis/`；  
> 但对 Beacon 源码自身迭代，必须额外默认交付一份 versioned Lighthouse 单文件。

### FR-004 输出必须类似 `system-architecture-map`

输出必须默认包含：

1. 一句话总结
2. 目标范围说明
3. 1~3 张 Mermaid 图
4. 关键入口与关键文件
5. 模块/子系统说明
6. 外部依赖或链路关系
7. 风险 / 开放问题 / 下一步建议

### FR-005 必须提供多种分析视角

Lighthouse 至少应支持这些输出模式：

1. `repo-ramp`
   - 用于快速理解整个项目
2. `system-architecture-map`
   - 用于输出系统分层和模块关系图
3. `package-brief`
   - 用于第三方包/开源库快速解构
4. `infra-chain-map`
   - 用于基础设施链路梳理
5. `feature-slice`
   - 用于单个功能切片解构

### FR-006 必须显式区分事实与推断

输出中必须存在这类分层：

- Confirmed Facts
- Inferred Structure
- Open Questions

不能把推断直接写成正式事实。

### FR-007 必须带源引用

输出必须至少包含：

1. 关键源码路径
2. 关键 README/文档路径
3. 关键配置/入口文件

### FR-008 必须与主工作流解耦

Lighthouse 不应默认触发：

- `freeze`
- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`

只有当用户明确要求时，才应把分析输出转成主工作流输入。

### FR-009 必须支持“分析后继续”

当用户明确要求时，Lighthouse 输出应可作为下游输入：

1. 喂给 `beacon-prd`
2. 喂给 `beacon-implement`
3. 喂给 `beacon-qa`

但这种转换必须是显式动作，而不是默认发生。

### FR-010 必须保持 Beacon 风格

Lighthouse 输出必须遵循 Beacon 风格：

1. evidence-first
2. source-ref aware
3. machine/human artifact 可落盘
4. 不扩张主面

---

## 7. 输出合同

推荐的单文件输出结构：

```markdown
# <Target> Lighthouse Map

## 1. Summary

## 2. Scope

## 3. Mermaid Maps
- overall map
- execution/data/dependency map
- optional module map

## 4. Key Entry Points

## 5. Key Modules / Subsystems

## 6. External Dependencies / Infra Chain

## 7. Confirmed Facts

## 8. Inferred Structure

## 9. Open Questions / Risks

## 10. Recommended Next Steps
```

---

## 8. 成功判定

当下面条件都满足时，视为 Lighthouse 设计闭合：

1. `v1.3.2` 下存在正式 PRD
2. 存在 `beacon-toolkit-lighthouse` skill 设计
3. 明确它不属于主工作流
4. 明确它能对任意项目输出单文件图文分析
5. 明确它的输出合同、输入范围和后续接入边界
6. 明确 Beacon 源码迭代默认交付 versioned Lighthouse 单文件

---

## 9. 推荐实现顺序

### Phase 1

1. 新增 `beacon-toolkit-lighthouse` skill
2. 固定单文件输出模板
3. 支持本地 repo/path 分析

### Phase 2

1. 支持 package-brief / infra-chain-map / feature-slice
2. 支持对 Lighthouse 输出继续进入 PRD/implement/qa

### Phase 3

1. 如果必要，再增加更强的自动索引/图谱能力

---

## 10. 最终判断

Beacon 现在已经有很强的 workflow kernel，
但还缺一个“让用户快速看懂陌生系统”的工具包面。

`Beacon Toolkit Lighthouse` 正是这个补位：

> 它不进入主工作流，  
> 但能像灯塔一样先把目标项目、开源库、第三方依赖和链路结构照亮，  
> 再决定是否进入 Beacon 主链。  
