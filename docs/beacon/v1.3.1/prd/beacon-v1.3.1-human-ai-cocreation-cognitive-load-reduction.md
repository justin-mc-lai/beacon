# PRD：Beacon v1.3.1 人机共创心智包袱减重

**Feature**: `beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction`  
**Version**: `v1.3.1`  
**Date**: `2026-04-12`  
**Status**: `accepted supplement line`

## 1. 问题

Beacon 已经具备较强的阶段治理与 machine lane 能力，但人类操作者仍可能感受到以下负担：

1. 命令面过多，不知道自己到底该用哪些
2. `brainstorm`、team、learning、auto research 等内部能力和主交付链混在一起
3. `implement` 与 `qa` 虽然能力变强，但人类仍可能被迫理解内部多角色拆分
4. 源码升级后，旧项目的 machine 物料容易滞后
5. CLI 在人类视角下仍不够极简
6. 需求文档里经常残留未闭合的需求歧义与澄清债务，但当前没有被提升为正式冻结阻塞项
7. 每个版本进入实现前，git 分支、worktree、隔离环境、服务目录边界等实现面约束常常不够确定

## 2. 目标

让 Beacon 在人机共创场景里形成明确分层：

### 人类主面

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

### 机器协作面

- `brainstorm`
- `implement-team`
- `qa-team`
- learning
- auto research
- 版本物料同步 / doctor / help / status

机器面仍可以继续复杂，但人类只需围绕正式文档交付闭环工作。

## 3. 功能需求

### FR-001 人类可见主命令必须收敛

Beacon 对人类的主心智面必须控制在有限集合内。

当前目标集合为：

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

不要求人类长期记忆更多主命令。

### FR-002 `brainstorm` 必须嵌入 `prd -> user-story`

`brainstorm` 不应只是独立工具，而应成为 `prd -> user-story` 探索中的持续能力。

要求：

- 需求探索过程必须持续使用 brainstorm 做业务发散与闭环
- 最终沉淀必须回写到正式 `prd` / `user-story` 产物
- 人类主交互不应因 `brainstorm` 增加额外长期命令负担

### FR-003 `implement` 对人类保持单入口

对人类而言，`implement` 必须继续是唯一主入口。

对机器而言：

- Beacon 可自由决定是否启用 team 多代理
- 可继续使用 bounded team runtime
- 目标是把冻结需求快速实现为可交付结果

### FR-004 `qa` 对人类保持单入口

对人类而言，`qa` 必须继续是唯一主入口。

对机器而言：

- Beacon 可自由使用 `qa-team`
- 可穿插 learning / auto research
- 但必须围绕冻结用户故事提升覆盖率、发现新问题、澄清边界

### FR-005 每一轮 QA 都必须带来新的价值

QA 不能只是重复执行。

每一轮 QA 至少应实现以下之一：

- 新发现
- 新覆盖
- 新边界澄清
- 新 repair handoff

如果没有新增价值，则不应被视为有效 QA 进展。

### FR-006 learning / auto research 只能围绕冻结用户故事工作

learning / auto research 必须以冻结用户故事为边界：

- 不得偏离主需求包
- 不得自行扩 scope
- 只能用于提高 coverage、清晰度与业务闭环质量

### FR-007 旧文档物料必须支持按版本一键更新对齐

Beacon 源码更新后，旧项目必须支持按指定文档版本执行物料同步。

最低要求：

- 可指定 `docs version`
- 可同步 `.machine/user-story`
- 可同步 `.machine/qa`
- 动作可审计、可重复

### FR-008 探索极简 CLI

`v1.3.1` 必须探索 Beacon 的极简命令行。

核心原则：

- 人类主 CLI 服务六段闭环
- 机器内部 lane 不成为默认暴露面
- 复杂度通过 help/status/doctor 按需揭示

### FR-009 人类交付与机器协作必须分层

要求：

- 人类只需确保正式文档与交付闭环
- 机器间协作由 Beacon 自由制定
- 机器不能脱离人类冻结文档自行决定新的正式需求真相

### FR-010 需求审核未收口不得冻结

Beacon 必须把以下内容视为冻结前阻塞项：

- 未闭合的需求歧义
- 表述含混的验收边界
- 尚未落定的业务决策
- 未完成收口的澄清债务
- scope 解释仍可双向扩张的条目

只要这些问题仍存在：

- `prd` 不能 freeze
- `user-story` 不能 freeze
- 后续 `implement` 不应进入正式闭环

### FR-011 需求审核必须显式输出未决项清单

在 `brainstorm -> prd -> user-story` 过程中，Beacon 必须支持显式记录并收口：

- decisions_to_close
- unresolved_business_choices
- ambiguous_scope_edges
- acceptance_boundary_gaps

只有这些清单被清空或降级为非阻塞项，需求包才允许冻结。

### FR-012 每个版本必须先做技术评审

Beacon 必须把技术评审提升为每个版本进入实现前的正式前置动作。

技术评审至少必须给出：

- 目标 git 分支
- branch prefix / base branch
- 是否使用 worktree
- worktree 根目录
- 隔离开发环境要求
- 实际实现服务目录

### FR-013 monorepo / multi-service 项目必须给出确定性服务边界

对于 monorepo 或多服务项目，例如 `rolo` 一类 workspace：

技术评审不得只给抽象结论，必须明确：

- 需要改动的具体服务
- 只读参考服务
- gateway / BFF / downstream service 的责任边界
- 各服务的 branch / worktree / 环境隔离方式

### FR-014 技术评审未完成不得进入正式实现

如果版本级技术评审尚未明确实现面：

- 不得进入正式 `implement`
- 不得把不确定性留到编码期由机器临时决定
- 必须先补齐 deterministic implementation contract

### FR-015 极简 CLI 也必须覆盖需求审核与技术评审

即使人类主命令面收敛，也不能把以下动作做成“隐形漏项”：

- 需求审核与未决项收口
- 技术评审与实现面确定

也就是说，极简 CLI 不是去掉这些动作，而是把它们内嵌进主闭环而不是额外扩展命令负担。

### FR-016 同一版本必须支持多个并行 feature package

`v1.3.1` 必须正式承认：

- 同一个 `docs version` 下可以存在多份 `prd`
- 每份 `prd` 对应自己的 `user-story`
- 每份 `user-story` 对应自己的 `test-case`

要求：

- 通过共享 `feature slug` 维持一对一链路
- 不要求引入新的嵌套目录结构
- 不要求人类学习新的并行命令

### FR-017 交付必须产出独立 change 文档与版本演进图

Beacon 不能只留下 technical archive。

还必须有面向交付与 release 的独立 change 面，至少包含：

- 新增
- 删除 / 收敛
- 修复
- 追溯到哪些 feature package

同时必须存在版本演进图，说明：

- 相对上一版本新增了什么
- 删除 / 收敛了什么
- 修复 / 校正了什么
- 哪些能力被保留

## 4. 非功能约束

1. 不得削弱 `v1.3.0` 已落地的 team runtime。
2. 不得以“极简”为名删除必要的恢复/诊断能力。
3. 不得让 machine lane 失去 evidence-first 约束。
4. 不得让 learning / auto research 脱离冻结故事边界。
5. 不得在需求未清晰时冻结 PRD / user-story。
6. 不得在技术评审未明确 branch/worktree/service scope 时进入正式实现。

## 5. 成功标准

1. 人类主文档与帮助面明确收敛为六段闭环。
2. `brainstorm` 明确成为 `prd/user-story` 探索能力，而不是额外长期负担。
3. `implement` / `qa` 对人类是单入口，对机器允许内部自由协作。
4. 旧项目可以按版本一键同步 machine requirement materials。
5. `prd/user-story` 的冻结前审核阻塞规则被正式定义。
6. 每个版本进入实现前的技术评审与 deterministic implementation contract 被正式定义。
7. 极简 CLI 路线在文档层被清晰定义并可进一步实现。
8. 同一版本下多个 feature package 的并行一对一文档链被正式定义。
9. 版本级 `change` 文档与版本演进图成为正式交付面。
