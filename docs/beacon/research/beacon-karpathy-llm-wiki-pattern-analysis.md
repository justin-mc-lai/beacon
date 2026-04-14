# 调研：Karpathy `LLM Wiki` 模式及其对 Beacon 的长期启发

**日期**：2026-04-07  
**来源**：<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>  
**原文标题**：`LLM Wiki`  
**目标**：把文章中的核心模式沉淀成 Beacon 可持续复用的研究笔记，供后续在 knowledge plane、research materials、schema governance、query/writeback 等方向反复引用。

---

## 1. 一句话结论

这篇文章最重要的不是“如何做 RAG”，而是提出了一个更强的中间层：

> 让 LLM 持续维护一个持久化、结构化、可交叉引用的 markdown wiki，使知识以可演化资产的形式累积，而不是在每次问答里重新临时拼装。

如果把 RAG 理解成“按需检索原材料”，那么 `LLM Wiki` 更接近：

```text
raw sources
→ LLM 持续编译
→ interlinked markdown wiki
→ 查询 / 对比 / 洞察 / 新页面反写
→ 再次累积
```

它本质上是一种 **knowledge compilation** 模式，而不是单次 retrieval 模式。

---

## 2. 调研对象的第一性原理

文章把常见 LLM 文档问答系统的问题指出得很明确：

1. 传统文件上传 / RAG 会在每次提问时重新发现知识
2. 多文档综合能力虽然存在，但每次都要重新拼接
3. 之前已经发现的联系、冲突、结论不会自动沉淀
4. 问答本身常常消失在聊天记录里，无法复利

`LLM Wiki` 的第一性原理是：

1. **原始资料不直接作为主要查询面**
2. **LLM 先把资料“编译”为 wiki**
3. **wiki 才是稳定的工作面和查询面**
4. **问答也可以反写成新页面**
5. **知识库通过持续维护而增值**

换句话说：

> 目标不是让模型“每次都更聪明地找资料”，而是让模型“把已有阅读结果维护成越来越有组织的知识结构”。

---

## 3. 文章里的系统形态

文章把系统分成三层。

### 3.1 Raw sources

- 文章、论文、图片、数据文件等原始材料
- 只读，不修改
- 作为事实源与审计源

### 3.2 Wiki

- 一组由 LLM 维护的 markdown 页面
- 包括摘要页、实体页、概念页、比较页、综合页
- 页面之间通过链接形成结构
- 用户主要读这一层，LLM 主要写这一层

### 3.3 Schema

- 由 `AGENTS.md` / `CLAUDE.md` 一类文件承载
- 规定 wiki 的目录结构、页面规范、更新流程、命名方式、索引和日志策略
- 它让 LLM 从通用聊天模型变成“纪律化的 wiki 维护者”

文章的关键不是某个具体工具，而是这三层分离：

```text
事实源
≠ 知识层
≠ 维护协议
```

这对 Beacon 很重要，因为 Beacon 当前也在处理类似分层：

- requirement materials
- machine/runtime artifacts
- execution/schema/governance rules

---

## 4. 三个核心操作

文章把长期知识维护收敛成三个主操作。

### 4.1 Ingest

当新增一个资料时，LLM 不只是“记住它”，而是要：

1. 阅读资料
2. 与人讨论重点
3. 写 summary page
4. 更新 index
5. 更新相关 entity / concept pages
6. 记录日志

一个 source 可能触达很多现有页面。

这说明 ingest 的本质是：

> 新证据进入系统后，不是挂在外面等以后检索，而是立即进入已有知识结构并修改其局部真相。

### 4.2 Query

问答并不是对原始资料的临时检索，而是对 wiki 的再综合。

更关键的是：

- 比较结果
- 新洞察
- 主题汇总
- 图表 / deck / canvas

这些都可以反写成新页面，变成未来查询的输入，而不是留在聊天历史中蒸发。

### 4.3 Lint

文章建议定期做 wiki 健康检查，检查：

- 页面冲突
- 过时结论
- 孤儿页
- 缺失的核心概念页
- 缺少 cross-reference 的地方
- 需要补充外部搜索的数据空洞

这相当于把“知识维护”当成一种持续性 QA，而不是文档整理的尾活。

---

## 5. 两个关键辅助文件

文章特别强调两个文件。

### 5.1 `index.md`

它是内容索引，不是时间线。

典型职责：

- 列出页面
- 给出一句话摘要
- 可附带日期 / source 数量 / 标签
- 先帮助 LLM 找到该读哪些页面

作者认为在中等规模下，仅靠这个文件就足以支撑相当多的知识导航。

### 5.2 `log.md`

它是时间线日志，不是内容目录。

典型职责：

- 记录 ingest
- 记录 query
- 记录 lint
- 保留系统演化轨迹

文章提到一个很实用的点：如果日志头统一，可被简单 shell 工具解析。

这意味着 `log.md` 不只是给人读，也是在给 agent 留操作记忆。

---

## 6. 为什么这个模式成立

文章的核心论证不是“LLM 更懂知识”，而是：

1. 维护知识库最痛苦的部分不是阅读，而是 bookkeeping
2. 人类不愿长期维护 cross-references、摘要同步、冲突更新
3. LLM 擅长这种大规模、重复性、结构化维护工作
4. 因为维护成本下降，wiki 才真正能持续增长

所以人的角色是：

- 选资料
- 定方向
- 提问题
- 做判断

LLM 的角色是：

- 总结
- 链接
- 重组
- 更新
- 维持一致性

文章把这件事描述为：

```text
Obsidian 是 IDE
LLM 是程序员
Wiki 是代码库
```

这是全文最值得长期保留的认知框架之一。

---

## 7. 这篇文章对 Beacon 最有价值的 7 个启发

## 7.1 Beacon 不应只维护“流程状态”，还应维护“知识中间层”

Beacon 当前强项在：

- requirement chain
- QA / gate / release evidence
- machine-readable delivery materials

但从 `LLM Wiki` 模式看，Beacon 还可以更明确地区分：

1. **raw materials**
2. **compiled knowledge artifacts**
3. **governance / schema contracts**

如果没有中间的 compiled knowledge 层，很多 research / design / policy 判断会反复从原始文档重建，无法复利。

## 7.2 `docs/beacon/<version>/` 本质上已经接近 wiki，但还不够显式

Beacon 的版本包已经有：

- `SUMMARY.md`
- `research/`
- `user-story/`
- `prd/`
- `qa/test-cases/`
- `execution/`
- `.machine/`

这已经很像编译后的知识树。

但 `LLM Wiki` 提醒我们：

- 需要更强的 cross-page navigation
- 需要更明确的 index/log 机制
- 需要把 query 结果反写纳入正式流程
- 需要更主动的 lint/health-check 机制

## 7.3 `schema` 在这里不是附属物，而是核心产品面

文章中 `AGENTS.md` / `CLAUDE.md` 不只是说明文件，而是维护协议。

这对 Beacon 的启发是：

> Beacon 的真正产品价值，不只是生成材料，而是提供“如何让 agent 稳定维护知识/需求/证据系统”的协议层。

也就是说，Beacon 的 schema/guidance 本身可以被视为一等交付物。

## 7.4 ingest / query / lint 可以映射到 Beacon 的长期能力面

`LLM Wiki` 的三操作可以直接映射：

- `ingest`
  - 新需求 / 新研究 / 新外部参考 / 新项目上下文进入 Beacon
- `query`
  - 基于既有 materials 生成比较、分析、设计 judgement、implementation guidance
- `lint`
  - 扫描 materials 的冲突、漂移、孤儿页、缺链路、过时 claim、未闭环 evidence

这说明 Beacon 完全可以把“知识维护”视为正式 runtime surface，而不是隐含在 workflow 各阶段里的副作用。

## 7.5 query 结果应该能正式反写，而不是只停在 chat

文章一个很强的观点是：

> 一个好的回答，本身就是未来知识库的输入。

这和 Beacon 的现状高度相关。很多调研、对比、判断、验收解释，如果不反写到 docs，最后会丢失在会话里。

因此对 Beacon 的稳定启发是：

- 重要 query 应可写回 `research/` 或 `execution/`
- 重要 review judgement 应可写回 `release/` 或 `qa/`
- 重要 comparative analysis 应成为可引用材料，而不是一次性聊天内容

## 7.6 `index` 与 `log` 对 agent 很重要，不只是对人友好

文章说明：

- `index.md` 解决“先读哪里”
- `log.md` 解决“最近做了什么”

Beacon 当前虽然有大量 artifacts，但跨文档导航和时间线理解仍然偏隐式。

长期看可以考虑：

- 顶层研究索引
- 版本线知识索引
- 运行日志到正式 docs 的受控提升机制

## 7.7 lint 说明 Beacon 应该有“知识健康检查”

文章里的 lint 不只是格式检查，而是知识一致性检查。

对 Beacon 可转译成：

- 是否存在互相冲突的 PRD / user-story / QA 断言
- 是否存在只被提到但没有正式页面的核心概念
- 是否存在孤立 research 结论，没有进入 execution / release
- 是否存在新版本已覆盖旧说法，但旧文档未标 stale

这类能力比单纯语法检查更接近 Beacon 的核心价值。

---

## 8. Beacon 不应误读这篇文章的地方

## 8.1 不是在鼓励“让 agent 自由写一堆笔记”

文章强调的是有 schema、有结构、有持续维护纪律的 wiki。

因此对 Beacon 的正确翻译不是：

- 多生成一点 markdown

而是：

- 生成可维护、可导航、可复用、可持续修正的知识结构

## 8.2 不是把 RAG 全盘否定掉

文章的意思不是不要 retrieval，而是 retrieval 不应是唯一机制。

对于 Beacon：

- raw materials 仍然重要
- source-of-truth 仍要保留
- 但中间必须有编译层

## 8.3 不是让知识库替代版本治理

Beacon 的版本线、release line、machine artifacts 仍然必须正式存在。

`LLM Wiki` 模式增强的是：

- 长期知识积累
- 判断沉淀
- 研究复利

而不是替代 release governance。

---

## 9. 对 Beacon 的长期可执行建议

## 9.1 把 `docs/beacon/research/` 明确成跨版本知识层

这个目录最适合承载：

- 跨版本持续有效的方法研究
- 外部参考模式分析
- 不绑定单个 release line 的长期设计原则

建议这里的文档偏：

- 模式
- 结构
- 长期启发

而不是单次 feature 交付说明。

## 9.2 未来可补一个 research `index.md`

随着 `docs/beacon/research/` 增长，可增加：

- 文档索引
- 一句话摘要
- 适用范围
- 与哪个版本线或哪个 execution problem 最相关

## 9.3 未来可补一个 research `log.md`

记录：

- 新增哪些研究
- 哪些研究被后续版本吸收
- 哪些结论已转化成 PRD / execution / release artifact

这样研究本身也有演化轨迹。

## 9.4 把 “ingest/query/lint” 变成 Beacon 长期知识操作词汇

后续设计 knowledge plane 时，可以直接复用这三词：

- ingest new material
- query compiled knowledge
- lint knowledge graph / material consistency

这三个词比泛泛地说“读文档、回答问题、整理资料”更清晰。

## 9.5 把“回答可反写”纳入 Beacon 的默认习惯

如果某次回答具备以下特征，应考虑转成正式文档：

- 对后续版本仍有效
- 解释了一个关键模式
- 提供了长期判断标准
- 解决了经常重复出现的问题

这正是把 chat 资产化的最直接方式。

---

## 10. 建议保留的长期引用语义

后续如果在 Beacon 中再次引用这篇文章，可优先复用以下语义，而不是回到“RAG vs wiki”的泛泛讨论：

1. **Persistent, compounding artifact**
2. **Knowledge should be compiled, not repeatedly rediscovered**
3. **Schema turns a generic LLM into a disciplined maintainer**
4. **Query outputs can become future inputs**
5. **Lint is knowledge QA, not just formatting**
6. **The wiki is the codebase; the LLM is the maintainer**

---

## 11. 最终结论

这篇文章对 Beacon 的最大价值，不在具体工具，而在一个非常稳的产品判断：

> 长期有效的 agent 系统，不应只会在原始资料上临时回答问题；它还必须把阅读、综合、判断和问答结果持续沉淀为可维护的中间知识层。

对 Beacon 来说，这意味着：

- requirement materials 不只是阶段产物
- research 不只是背景附件
- query 不只是聊天回答
- schema 不只是提示词

它们都可以成为一个持续增长的知识系统的一部分。

因此，这篇文章适合作为 Beacon 后续设计以下能力时的长期参考：

- research plane
- compiled knowledge layer
- cross-version knowledge index
- query-to-doc writeback
- knowledge lint / consistency review
- schema-as-product governance

