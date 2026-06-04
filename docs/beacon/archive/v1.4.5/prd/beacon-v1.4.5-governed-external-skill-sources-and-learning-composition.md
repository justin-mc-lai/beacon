# PRD: Beacon v1.4.5 governed external skill sources and learning composition

**Feature**: `beacon-v1.4.5-governed-external-skill-sources-and-learning-composition`  
**Version**: `v1.4.5`  
**Date**: `2026-05-12`  
**Status**: `freeze-ready`  
**Track**: `external-capability-governance + learning-composition`  
**Scenario**: `non-software-domain-capability-orchestration`

## Context

- Version summary: `docs/beacon/archive/v1.4.5/SUMMARY.md`
- Friction evidence:
  - `.beacon/analysis/friction-intake-fit-20260512T030800Z.md`
  - `.beacon/debug/friction-captures/2cbbfad443f2.json`
- Canonical external sample:
  - `oss-sync` mirror `core-skills/baoyu-skills`
- Product intent:
  - Beacon should guide users by business outcome and result shape, not force them to predeclare implementation chain.

## 1. 问题

Beacon 当前更擅长：

- 消费内置 surface
- 在软件开发流程中维持 truth 与 implementation alignment

但它还不擅长：

- 把外部开源 skill 作为一等 capability source
- 在内容型、运营型、行业分析型任务中由模型自主设计 capability composition
- 基于历史结果学习 task-type -> skill-chain -> output-shape

这导致 Beacon 很难自然支持：

- 票务政策内容整理
- 出行提醒内容编排
- 报价承接文章骨架生成
- 面向行业的长任务分析与内容生产

## 2. 目标

1. 把外部 skill source 提升为 Beacon 的可治理一等能力源
2. 允许用户只声明业务目标与期望结果
3. 允许 Beacon 选择合适 skill source、skill chain、output shape
4. 把成功组合、失败回退、模板偏好与人工采纳结果回写为 learning evidence

## 3. 设计原则

### 3.1 外部 skill 是 capability source，不是旁路 hack

外部 skill 不能只通过人工安装说明存在，而要进入 Beacon 的治理与解释面。

### 3.2 用户声明结果，不声明中间实现

用户优先表达：

- 业务目标
- 目标受众
- 结果形态

而不是被要求先写死 skill chain。

### 3.3 学习只能优化选择，不能替代 truth

learning 可以：

- 推荐已验证组合
- 提供 prior pattern
- 给出 fallback hint

但不能直接变成 pass/fail truth。

### 3.4 外部 skill 设计应优先吸收“哲学 + 工具 + 事实”而不是流程脚本

Beacon 接入外部 skill 时，默认应优先吸收：

- 对应场景的 agent strategy philosophy
- 为完成任务真正缺失的最小工具集
- 模型显然未必稳定记得的必要事实说明

而不是把外部 skill 简化为僵硬的流程脚本或过长的步骤指令。

## 4. 范围

### In scope

- external skill source governance model
- canonical sample source `baoyu-skills`
- task-type -> skill-chain -> output-shape learning contract
- success/failure/adoption writeback semantics

### Out of scope

- 通用公网 skill marketplace
- 任意远程仓库即时执行
- 无治理的开放式 skill 下载

## 5. 功能需求

### FR-001 Beacon 必须允许外部 skill source 成为一等 capability source

Beacon 必须能表达：

- source identity
- source governance status
- source compatibility
- source intended domains

### FR-002 Beacon 必须支持 canonical external sample source

`core-skills/baoyu-skills` 必须作为首个正式样例源，用于验证 Beacon 的 external capability contract。

### FR-003 用户必须可以只声明业务目标与目标结果

对于内容型或非软件行业任务，用户不应被强制要求先声明 skill chain。

### FR-004 Beacon 必须能做 capability selection 与 composition

Beacon 至少要能选择：

- task type
- candidate skill source
- skill chain
- output shape

### FR-005 Beacon 必须记录 success/failure/adoption learning

至少需要支持记录：

- successful chain
- failed chain
- fallback path
- preferred template/output shape
- human adoption / rejection

### FR-006 learning 必须形成可回用 mapping

Beacon 必须能够学习并复用：

- `task-type -> skill-chain -> output-shape`

### FR-007 外部 source 治理必须保持边界清楚

external capability source 的引入不能：

- 绕过 truth/guidance boundary
- 绕过 host/runtime compatibility checks
- 直接成为未治理的 runtime dependency

### FR-008 Beacon 必须支持对外部 skill 做 philosophy-first admission

Beacon 在治理外部 skill source 时，必须能够区分并优先吸收：

- strategy philosophy
- minimum complete tools
- necessary factual grounding

而不是只看静态安装信息或逐步流程说明。

## 6. 验收标准

| AC ID | 说明 |
| --- | --- |
| AC-001 | 外部 skill source 被正式定义为一等 capability source |
| AC-002 | `baoyu-skills` 作为 canonical sample 被正式纳入 |
| AC-003 | 用户可以只声明业务目标与结果，而不是先声明 chain |
| AC-004 | Beacon 能表达 capability selection 与 composition contract |
| AC-005 | success/failure/adoption learning 被正式记录 |
| AC-006 | `task-type -> skill-chain -> output-shape` 映射被定义为 learning asset |
| AC-007 | 外部 source 接入不破坏原有 truth/guidance/runtime 边界 |
| AC-008 | 外部 skill 的接入能优先保留其策略哲学、最小工具与必要事实，而不是退化成流程脚本 |
