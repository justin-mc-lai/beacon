# PRD: Beacon v1.4.5 guidance surface family and cross-industry positioning

**Feature**: `beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning`  
**Version**: `v1.4.5`  
**Date**: `2026-05-12`  
**Status**: `freeze-ready`  
**Track**: `support-surface-governance + product-positioning`  
**Scenario**: `cross-industry-guidance-without-mainline-expansion`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Prior version summaries:
  - `docs/beacon/v1.4.3/SUMMARY.md`
  - `docs/beacon/v1.4.4/SUMMARY.md`
- Current public guidance surfaces:
  - `skills/beacon/beacon-brainstorm/SKILL.md`
  - `skills/beacon/beacon-ceo-review/SKILL.md`
  - `skills/beacon/beacon-design-review/SKILL.md`
  - `skills/beacon/beacon-deep/SKILL.md`
- Product tension:
  - Beacon already exposes guidance/review surfaces, but its product narrative and docs topology still overfit software delivery.

## Overview

Beacon needs a stable guidance-surface family and a product narrative that explains those surfaces as part of a general decision loop, not as software-only side features. This feature freezes that framing without expanding the main lifecycle.

## Scope

- Formalize `ceo-review`, `brainstorm`, `design-review`, and `deep` as one guidance family
- Freeze the non-truth and non-gate boundary for guidance surfaces
- Define software delivery as one domain materialization of Beacon's broader loop
- Align help, status, and docs language around that model
- Exclude new top-level lifecycle stages, new top-level commands, and implementation details for external skill registration

## 1. 问题

### 1.1 Beacon 的能力边界已经变宽，但产品定义还停留在编码治理

Beacon 已经不只是：

- `prd -> implement -> qa` 的冻结工具
- coding-only 的 no-drift enforcement shell

它已经开始拥有更广的 guidance surface：

- `ceo-review` 做方向挑战与 scope challenge
- `brainstorm` 做 requirement convergence 与 evolution exploration
- `design-review` 做 UX/interaction 方向判断
- `deep` 做 route explainability 与 evidence gap support

但当前 docs 和产品表述还没有把这些表面整合为一个稳定家族，结果是：

- 用户仍把 Beacon 理解成“写代码前冻结需求”的系统
- 非软件行业场景很难自然映射进 Beacon
- 支持面看起来像零散增强，而不是统一产品面

### 1.2 需要的是“通用闭环 + 行业 materialization”，不是新增主生命周期

Beacon 的主公开生命周期仍然应该是：

`prd -> user-story -> test-case -> prototype -> implement -> qa -> release`

但它的更底层产品闭环应表达为：

`define -> challenge -> freeze -> execute -> verify -> learn`

软件开发只是其中一个 materialization。

如果不把这个抽象正式冻结：

- Beacon 未来每进入一个行业，都容易被迫新增一套命令面
- `ceo-review` / `brainstorm` 会持续处于“有能力，但没有清晰角色”的状态
- 文档结构与帮助信息会继续围绕 coding-first 组织，削弱跨行业指导能力

## 2. 目标

### 2.1 主要目标

1. 冻结 Beacon 的 guidance surface family 定义
2. 把 Beacon 的产品定位提升为“通用决策闭环 + domain materialization”
3. 保持现有主生命周期不扩张
4. 为非软件行业分析、内容生产、运营编排提供正式解释入口

### 2.2 非目标

- 不新增一级主命令
- 不新增 `strategy`, `analysis`, `industry`, `content` 等新的公开 stage
- 不削弱软件开发主线
- 不让 support surface 直接冻结 truth 或给出 gate verdict

## 3. 设计原则

### 3.1 guidance surface 是 family，不是零散特例

以下 surfaces 必须被正式归为一类：

- `ceo-review`
- `brainstorm`
- `design-review`
- `deep`

### 3.2 guidance 只能 challenge / explain / route

guidance surface 可以：

- challenge framing
- surface tradeoffs
- explain route
- identify evidence gaps

但不能：

- 直接冻结 truth
- 直接替代 `change`
- 直接变成 `qa/release` gate

### 3.3 产品抽象必须先于行业扩展

Beacon 面向跨行业扩展时，必须先冻结：

- 通用闭环
- support family
- truth/guidance boundary

而不是直接为每个行业造目录或命令。

### 3.4 Skill 设计必须优先校准策略哲学，而不是过度指定步骤

Beacon 在更强模型条件下，默认 skill 设计原则必须偏向：

- `Agent 策略哲学`
- `最小完备工具集`
- `必要事实说明`

而不是把 prompt/skill 设计成对 Agent 的逐步动作脚本。

这意味着 Beacon 在 guidance surface 中更应该：

- 校准问题 framing
- 补足缺失工具
- 提前声明模型显然未必稳定记得的事实与边界

而不是把每一步 how-to 都硬编码到 skill。

## 4. 范围

### In scope

- guidance surface family contract
- product positioning language
- cross-industry mapping semantics
- help/status/docs 解释面的统一口径

### Out of scope

- 具体外部 skill 注册实现
- docs 目录重构实现细节
- learning/registry schema 细节

## 5. 功能需求

### FR-001 Beacon 必须冻结 guidance surface family

Beacon 必须把以下 surfaces 正式定义为 support/guidance family：

- `ceo-review`
- `brainstorm`
- `design-review`
- `deep`

### FR-002 Beacon 必须冻结 guidance surface family 的统一边界

每个 guidance surface 必须统一遵守：

- not truth source
- not gate source
- not new lifecycle stage
- must route back to `change` / `prd` / `user-story` / `test-case` / `implement`

### FR-003 Beacon 必须表达通用闭环

Beacon 必须在 docs/help 中正式表达通用闭环：

`define -> challenge -> freeze -> execute -> verify -> learn`

### FR-004 软件开发生命周期必须被定义为 domain materialization

当前软件生命周期必须被解释为 Beacon 通用闭环的一种 domain-specific projection，而不是 Beacon 唯一有效形态。

### FR-005 Beacon 必须允许非软件行业场景使用 guidance surface

Beacon 必须支持把内容生产、运营分析、行业策略等场景映射到 guidance family，而不要求用户先声明编码型中间实现。

### FR-006 guidance surface 的 route explainability 必须统一

`help / status / deep / brainstorm / ceo-review` 至少要能解释：

- 当前处于闭环哪一层
- 还缺什么证据
- 下一步应回到哪个 truth 或 delivery surface

### FR-007 Beacon 必须冻结 guidance-oriented skill philosophy

Beacon 必须明确 guidance family 的 skill 设计默认偏向：

- strategy philosophy calibration
- minimum complete toolset
- necessary factual grounding

并避免把 skill 写成对强模型的过度步骤约束。

### FR-008 support-surface requirement 默认不得被自动抬升为 browser QA

当 requirement 文本描述的是：

- guidance surface family
- support surface
- non-software routing
- route explainability

这类 support-surface / decision-surface 语义时，Beacon 的默认 QA9 自动映射必须优先落到 deterministic non-browser layers（如 `unit` / `contract`），而不是因为宽泛文本命中把它们自动抬升为 `functional` / browser execution。

只有当 requirement 明确声明了 UI、browser、page、form、click、screen 等交互语义时，才允许默认映射到 browser-oriented QA 类型。

## 6. 验收标准

| AC ID | 说明 |
| --- | --- |
| AC-001 | guidance surface family 被正式定义且成员固定 |
| AC-002 | support surfaces 的 non-truth / non-gate 边界被正式冻结 |
| AC-003 | Beacon docs/help 中能表达通用闭环 |
| AC-004 | 软件开发生命周期被定义为 domain materialization |
| AC-005 | 非软件行业场景可以使用 guidance family 获得 routeable 分析 |
| AC-006 | route explainability 在 guidance family 中口径一致 |
| AC-007 | guidance family 的 skill philosophy 被定义为策略校准优先，而不是步骤脚本优先 |
| AC-008 | support-surface requirement 默认映射到 deterministic non-browser QA layers，除非 requirement 明确声明 UI/browser 交互语义 |
