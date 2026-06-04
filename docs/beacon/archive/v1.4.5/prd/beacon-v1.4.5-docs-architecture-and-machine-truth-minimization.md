# PRD: Beacon v1.4.5 docs architecture and machine-truth minimization

**Feature**: `beacon-v1.4.5-docs-architecture-and-machine-truth-minimization`  
**Version**: `v1.4.5`  
**Date**: `2026-05-12`  
**Status**: `freeze-ready`  
**Track**: `docs-governance + artifact-minimization`  
**Scenario**: `simpler-truth-structure-with-less-duplicate-projection`

## Context

- Version summary: `docs/beacon/archive/v1.4.5/SUMMARY.md`
- Friction evidence:
  - `.beacon/analysis/friction-intake-fit-20260512T031031Z.md`
  - `.beacon/debug/friction-captures/fb4969c9d300.json`
- Existing version layout examples:
  - `docs/beacon/v1.4.3/`
  - `docs/beacon/v1.4.4/`

## 1. 问题

当前 Beacon docs 结构缺少强规划：

- version 根目录里混有 `prd / user-story / qa / execution / change / research / think / source-architecture / .machine`
- 结构更像历史演化痕迹，而不是稳定 contract
- human artifact 与 machine artifact 经常双写，但没有新增语义

尤其在 support surfaces 上，当前常见问题是：

- human markdown 只是 JSON 的浅投影
- `.machine` 与 human 文档默认成对出现
- 人类读者并不总是需要这些镜像

这会造成：

- docs 成本升高
- 浏览路径混乱
- 维护者很难判断哪个才是 canonical truth

## 2. 目标

1. 从 `v1.4.5` 开始冻结更稳定的 docs architecture
2. 把 `truth / guidance / delivery / evidence / .machine` 语义分层清楚
3. 明确 `.machine` 是 projection，而不是默认需要 human mirror
4. 消除无新增语义的 human/machine 双写
5. 保持 docs 结构轻量，只在真实消费时渐进式创建目录

## 3. 设计原则

### 3.1 结构必须表达语义，不只是文件归类

docs 目录必须让维护者一眼分清：

- 哪些是 truth
- 哪些是 guidance
- 哪些是 delivery artifact
- 哪些只是 machine projection

### 3.2 human artifact 必须是“有决策价值”的

只有当 human artifact 能：

- 改善浏览
- 改善维护
- 改善决策
- 改善 acceptance/closure

时，才值得存在。

### 3.3 `.machine` 必须降级为 projection layer

`.machine` 可以保留，但它不再自动要求：

- 一份同语义 markdown
- 一份平行 human narrative

### 3.4 目录结构必须渐进式物化

即使 Beacon 冻结了更完整的结构语义，也不应一次性在每个版本里生成全量目录树。

只有当某一层被真实使用时，才应创建对应目录、索引或投影。

这样可以避免：

- 空目录膨胀
- 版本模板过重
- 维护者把结构语义误解成必须全部落盘的清单

## 4. 范围

### In scope

- 新版 docs structure contract
- support-surface artifact minimization policy
- `.machine` layer role clarification
- version template guidance

### Out of scope

- 批量迁移全部历史版本
- 删除所有已有 machine artifact
- 一次性重写整个 `docs/beacon/` 历史树

## 5. 功能需求

### FR-001 Beacon 必须冻结新的 docs structure 语义

`v1.4.5` 起，版本目录必须能够表达：

- `context/`
- `truth/`
- `guidance/`
- `delivery/`
- `evidence/`
- `.machine/`

### FR-002 现有软件主线 truth 必须能映射到新结构

当前：

- `prd`
- `user-story`
- `test-case`
- `change`

必须明确映射到 `truth/`。

### FR-003 support surfaces 必须映射到 guidance

`ceo-review / brainstorm / design-review / deep` 的文档产出必须优先进入 `guidance/`，而不是混入 truth。

### FR-004 `implement / qa / release / prototype` 必须映射到 delivery/evidence

这些执行相关物料必须被更清晰地区分为：

- `delivery/`
- `evidence/`

### FR-005 Beacon 必须冻结 artifact minimization policy

当 human artifact 没有新增语义时，Beacon 不应默认生成 paired markdown。

### FR-006 Beacon 必须定义 machine-truth policy

`.machine` 层必须被解释为：

- machine-readable truth/projection
- internal automation input
- optional human companion only when needed

### FR-007 Beacon 必须保留版本兼容策略

历史版本允许继续存在旧结构，但 `v1.4.5` 之后的新线必须有清晰模板与迁移口径。

### FR-008 Beacon 必须默认渐进式创建目录与投影

对于 `truth / guidance / delivery / evidence / .machine` 各层，Beacon 必须支持“语义先冻结、目录后按需创建”的策略，而不是一开始全量物化。

## 6. 验收标准

| AC ID | 说明 |
| --- | --- |
| AC-001 | `v1.4.5` 冻结新的 docs structure 语义层 |
| AC-002 | 现有软件 truth 被明确映射到 `truth/` |
| AC-003 | guidance surfaces 的文档产出不再混入 truth |
| AC-004 | delivery 与 evidence 分层更清楚 |
| AC-005 | paired human/machine artifact 不再默认双写 |
| AC-006 | `.machine` 的角色与 human companion 条件被明确 |
| AC-007 | 历史版本兼容、新版本模板约束同时成立 |
| AC-008 | 新结构以渐进式创建为默认策略，而不是一次性全量建树 |
