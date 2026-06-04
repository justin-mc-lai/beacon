# Beacon v1.3.8 Archive Governance and Historical Requirement Isolation Analysis

**Date**: 2026-04-24  
**Method**: 基于 Beacon 当前 `v1.3.7` truth/gate 架构、版本文档树现状、以及真实项目迭代中“历史需求继续影响当前实现”的使用痛点做收敛分析  
**Purpose**: 判断 Beacon 是否应在 `v1.3.8` 新增 archive governance，把“当前有效 truth”与“历史已过期/已 superseded 需求”正式隔离。

---

## 1. Summary

这条调研的核心结论是：

- Beacon 现在已经有 `revision superseded`、`release line`、`change`、`technical archive`、`implementation summary` 等局部能力。
- 但系统仍然缺少一条面向“整版需求资产”的 archive governance 线。
- 结果是：历史版本文档、历史 feature truth、历史 change、历史 raw evidence 仍容易在后续 brainstorming、implement、QA、memory 分析中继续被误读为当前有效输入。
- `v1.3.8` 最值得新增的，不是简单“把旧文档移走”，而是建立一套正式的 archive contract：
  - 当前版本 truth 是什么
  - 哪些 feature/revision 已 superseded
  - 哪些 requirement 仅供历史追溯，不能再参与当前实现决策
  - 哪些技术归档是可学习输入，哪些只是历史记录

一句话：

> `v1.3.8` 应该把“历史存在”和“当前有效”分开管理，让 Beacon 能保留历史证据，但不让历史需求继续污染当前交付。

---

## 2. Problem Statement

当前 Beacon 有两个强项：

1. 强 truth discipline
2. 强 gate / release closure

但还缺一个中间治理层：

- 历史 requirement package 如何退出当前决策面
- 历史 feature artifacts 如何进入 archive 面，而不是继续留在 active truth 面
- memory/friction/evolution 在读取历史材料时，如何知道它是在“学习历史模式”，还是在“引用当前正式 truth”

真实风险不是“文档太多”，而是：

- 历史 PRD / user-story / test-case 继续被当成当前参考
- 历史 feature change 继续影响当前实现判断
- 历史 release line 与 current release line 在阅读时混淆
- 历史技术归档和当前 formal truth 没有清晰状态标识

---

## 3. Current Baseline

### 3.1 Beacon 已经有的能力

- `docs/beacon/<version>/` 版本化文档树
- `change/` 与 `.machine/change/`
- `technical-implementation-*.md/.json`
- `implementation-summary-*.md/.json`
- `revision_state` 中的 `superseded_by`
- `status` / `release_scorecard` 对 revision superseded 的识别
- current runtime release line 与 historical release line 的区分

### 3.2 Beacon 还缺的能力

- 没有一个正式 archive plan 指出：
  - 哪些 feature truth 仍 active
  - 哪些 feature truth 已 archived
  - 哪些 artifacts 属于 learnable archive
  - 哪些 artifacts 仅允许追溯，不允许再参与当前实现面
- 没有一个版本级 archive index 帮人和 LLM 明确知道：
  - 当前版本应该读什么
  - 历史版本何时只读
  - 历史需求如何停止影响当前迭代
- gate 现在擅长校验一致性，但不擅长校验“历史隔离是否已完成”。

---

## 4. Evidence and Trigger Signals

### 4.1 用户显式提出的需求

用户要求：

- 基于最新版本需求和历史需求，按功能实现为基线做整体归档
- 避免后续迭代过程中历史过期需求继续影响项目

这说明问题已经不是局部 feature 设计，而是 Beacon 自身缺少“历史失效隔离”能力。

### 4.2 当前仓库状态带来的系统性信号

- `docs/beacon/` 下保留了大量版本目录。
- `v1.3.7` 的 change 文档仍可引用 `v1.3.6` 的旧线材料。
- 历史 technical archive 会被 learning/rewrite 继续利用，但缺少 active/archive 语义边界。
- memory/friction 分析天然会扫历史 `.beacon` 状态与 docs，如果没有 archive contract，就容易把旧线问题和当前线输入混在一起。

### 4.3 与 `v1.3.7` truth discipline 的关系

`v1.3.7` 已经解决了：

- frozen truth 和 canonical implementation baseline 的单向投影关系

但它没有正式解决：

- truth 在时间轴上的退场机制

也就是说，`v1.3.7` 解决了“同一时间点谁是真相”，`v1.3.8` 需要解决“旧真相何时退出当前生效面”。

---

## 5. Research Direction

### 5.1 方向 A: 只保留现有 superseded 语义，不新增 archive governance

优点：

- 改动最小
- 不引入新的主概念

缺点：

- `superseded_by` 只能覆盖 revision 关系，不能覆盖整版 requirement asset 的治理
- 无法明确区分：
  - current truth
  - historical reference
  - learnable archive
- 无法阻止旧需求继续进入新一轮 brainstorming / implement 输入

结论：

- 不够。

### 5.2 方向 B: 增加版本级 archive plan 和 feature-level archive status

优点：

- 能从“功能实现闭环完成”这个时点出发，正式把需求资产归档
- 能把历史可读、可学、可执行三种状态拆开
- 能为 help/status/memory/gate 提供统一 archive truth

缺点：

- 需要在 docs、machine artifacts、status、memory 消费面新增状态语义

结论：

- 推荐。

### 5.3 方向 C: 做自动搬迁归档，不做显式 archive contract

优点：

- 表面上使用更省事

缺点：

- 没有 contract，就无法解释“为什么这份材料不再是当前 truth”
- 自动移动文件无法替代 formal status
- 容易破坏追溯链和历史证据引用

结论：

- 不推荐。

---

## 6. Proposed v1.3.8 Scope

### 6.1 Version Archive Plan

新增版本级归档材料，至少表达：

- current version truth root
- archived version roots
- active feature set
- archived feature set
- learnable archive refs
- excluded-from-current-delivery refs

### 6.2 Feature Archive Status

针对每个 feature 增加正式 archive state，至少区分：

- `active`
- `superseded`
- `archived-learnable`
- `archived-reference-only`

### 6.3 Archive Boundary Consumption

让以下消费面读取 archive boundary：

- `status`
- `help`
- `memory-friction-evolution`
- `brainstorm`
- `implement`
- `gate`

目标不是让它们都阻断，而是让它们知道：

- 当前应该优先读什么
- 什么只能作为历史背景
- 什么根本不应再进入当前实现面

### 6.4 Archive Trigger

归档不应由人工随意触发，而应绑定到正式闭环时点，例如：

- feature release accepted
- version release promoted
- revision superseded and closure accepted

---

## 7. Suggested Artifact Model

推荐新增下列 artifact：

- `docs/beacon/<version>/execution/archive-plan.md`
- `docs/beacon/<version>/.machine/execution/archive-plan.json`
- `docs/beacon/<version>/execution/archive-index.md`
- feature-level archive metadata beside revision / implementation summary

推荐最小字段：

- `archive_status`
- `archive_reason`
- `archived_at`
- `supersedes`
- `superseded_by`
- `active_for_delivery`
- `active_for_learning`
- `active_for_reference`

---

## 8. Boundaries

`v1.3.8` 的 archive governance 不应：

- 破坏历史文档可追溯性
- 物理删除历史 truth
- 改写已冻结 requirement 内容
- 把 archive 变成新的主生命周期 stage

`v1.3.8` 的 archive governance 应：

- 明确哪些历史材料仍可学习
- 明确哪些历史材料不可再作为当前实现 truth
- 保证 LLM 在读历史时带着 archive 状态

---

## 9. Preliminary Conclusion

`v1.3.8` 值得新增 archive governance，而且它应该被定义成：

- 一条版本级治理能力
- 一个 machine-readable contract
- 一个对 LLM 特别重要的 truth filter

这样 Beacon 才能真正做到：

```text
保留全部历史
!=
允许全部历史继续影响当前实现
```

## 10. Recommended Next Step

基于这份调研，下一步适合起一条正式 feature：

- `beacon-v1.3.8-archive-governance-and-historical-requirement-isolation`

并继续进入：

- PRD
- user-story
- test-case

## Source Refs

- `docs/beacon/v1.3.7/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.7/execution/boundaries.md`
- `docs/beacon/v1.3.7/release/v1.3.7.md`
- `beacon/utils/revision_state.py`
- `beacon/utils/release_scorecard.py`
- `beacon/commands/status.py`
- `beacon/utils/memory.py`
