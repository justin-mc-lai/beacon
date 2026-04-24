# PRD: Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking

**Feature**: `beacon-v1.3.7-beacon-brainstorm-built-in-convergence-and-evolution-thinking`  
**Version**: `v1.3.7`  
**Status**: `planning`  
**Date**: `2026-04-23`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Previous brainstorm gap analysis:
  - `docs/brainstorms/2026-04-23-beacon-human-surface-closure-and-feature-intent-brainstorm-gap.md`
- Human-surface gap lighthouse:
  - `docs/beacon/v1.3.7/execution/beacon-toolkit-lighthouse-beacon-human-surface-closure-and-feature-intent-gap.md`
- Related v1.3.7 implement line:
  - `docs/beacon/v1.3.7/prd/beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope.md`

## 1. Problem

Beacon 当前的人类主面已经有 canonical lifecycle，也有 requirement 与代码分析能力：

```text
prd
-> user-story
-> test-case
-> prototype
-> implement
-> qa
-> release
+ help / status / doctor
```

以及 sidecar：

- `beacon-change`
- `beacon-prd-bootstrap`
- `beacon-toolkit-lighthouse`
- `beacon-memory-friction-evolution`

但还缺一个 Beacon 内置、面向“继续思考与收敛”的头暴子 skill。

当前缺口不只是：

- frozen truth 下的 implement/change 路由判断

还包括：

- 基于 `docs/beacon/<version>/` 正式材料继续头暴补齐
- 对已存在 requirement 做进一步收敛
- 对项目下一阶段演进给出思路
- 用严格的思考方法持续去假设、验前提、砍冗余

现在这些工作只能分散落在：

- `beacon-prd`
- `beacon-change`
- `beacon-toolkit-lighthouse`
- 通用外部 brainstorming skill

这会带来三个问题：

1. Beacon 没有自己的内建思考层，继续头暴时容易回退到通用外部流程。
2. `beacon-toolkit-lighthouse` 擅长静态分析，但不负责交互式补齐与收敛。
3. `beacon-prd` 负责正式 requirement 写作，不适合吸收所有前置/中途思考过程。

## 2. Goals

### 2.1 Primary Goal

在 Beacon 内置一个可见但非主流程的子 skill：

- 名称固定为 `beacon-brainstorm`

它用于：

- 读取 Beacon version 材料
- 基于正式需求继续头暴
- 暴露隐含假设
- 追问关键边界
- 收敛可执行方向
- 为后续 requirement / change / implement / evolution 给出建议

### 2.2 Expected Result

本线完成后，Beacon 应满足：

1. 存在一个 Beacon 内建的 `beacon-brainstorm` 子 skill，专门承担继续头暴、补齐、收敛与演进思考。
2. 它能够读取 `docs/beacon/<version>/` 正式材料，并以这些材料为思考起点，而不是脱离 version truth 发散。
3. 它支持至少三类工作：
   - requirement convergence
   - frozen material supplement / delta thinking
   - project evolution exploration
4. 它内置三套思维协议：
   - 第一性原理
   - 苏格拉底提问
   - 奥卡姆剃刀
5. 它只做思考、澄清、收敛、建议，不直接改写 requirement truth，不直接执行实现。

## 3. Non-goals

本 PRD 不承担：

- 不新增新的公开一级主命令
- 不把 `beacon-brainstorm` 升格成 canonical lifecycle stage
- 不让它替代 `beacon-prd`
- 不让它替代 `beacon-toolkit-lighthouse`
- 不让它直接改写 frozen `prd / user-story / test-case`
- 不让它直接执行 `implement`

## 4. Core Product Semantics

### 4.1 Skill Positioning

`beacon-brainstorm` 是：

- Beacon 内建
- host-visible
- sidecar
- thinking / convergence layer

它不是：

- 新主流程 stage
- requirement truth writer
- code executor

### 4.2 Required Inputs

该 skill 至少支持以下输入：

- `version`
- `prompt`
- optional `feature`
- version docs refs:
  - `SUMMARY.md`
  - `execution/`
  - `prd/`
  - `user-story/`
  - `qa/test-cases/`

可选输入：

- `prototype`
- current code context
- previous brainstorm docs
- evolution targets

### 4.3 Required Modes

该 skill 至少支持以下模式：

1. `requirement-convergence`
   - 对当前 version 的 requirement 材料继续头暴补齐并收敛
2. `frozen-truth-delta`
   - 判断新想法与 frozen truth 的差异、影响和变更方向
3. `evolution-exploration`
   - 对项目后续演进路径给出方向判断
4. `redundancy-pruning`
   - 找出冗余流程、冗余抽象、冗余假设，并给出精简建议

### 4.4 Thinking Protocols

该 skill 必须内置以下思考协议：

- 第一性原理
  - 拆解目标、约束、不变量、必要条件
- 苏格拉底提问
  - 一次一问地暴露假设、证据、边界和反例
- 奥卡姆剃刀
  - 删除不能证明必要的复杂度，优先保留最小闭环方案

### 4.5 Required Output Contract

该 skill 必须输出单一收敛结果，至少包含：

1. `prompt_summary`
2. `version_material_refs`
3. `confirmed_facts`
4. `assumptions_under_test`
5. `first_principles_breakdown`
6. `socratic_questions`
7. `redundancy_cuts`
8. `converged_recommendation`
9. `next_route`

### 4.6 Artifact Rule

该 skill 必须能生成单一 Markdown 产物。

推荐落点：

- 默认：`docs/brainstorms/`
- 可选：`.beacon/analysis/`
- 对 Beacon 源迭代：允许同步写入 `docs/beacon/<version>/execution/`

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon 必须提供一个内建、可见、非主流程的 `beacon-brainstorm` 子 skill，作为 thinking / convergence layer。 |
| FR-002 | AC-002 | `beacon-brainstorm` 必须能够读取 `docs/beacon/<version>/` 正式材料，并基于 version truth 继续头暴与补齐，而不是脱离文档发散。 |
| FR-003 | AC-003 | `beacon-brainstorm` 必须至少支持 `requirement-convergence`、`frozen-truth-delta`、`evolution-exploration`、`redundancy-pruning` 四类工作模式。 |
| FR-004 | AC-004 | `beacon-brainstorm` 必须内置第一性原理、苏格拉底提问、奥卡姆剃刀三类思考协议，并把它们显式用于结论收敛。 |
| FR-005 | AC-005 | `beacon-brainstorm` 必须只做思考、收敛和建议，不直接改写 requirement truth，不直接执行 implement；同时能生成单一 Markdown 产物。 |

## 6. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | built-in-skill | 存在一个 Beacon 内建的 `beacon-brainstorm` 子 skill，定位为 host-visible 但非主流程。 |
| AC-002 | version-grounding | 该 skill 能基于 `docs/beacon/<version>/` 的正式材料继续头暴、补齐和收敛。 |
| AC-003 | working-modes | 该 skill 至少支持 requirement convergence、frozen-truth delta、evolution exploration、redundancy pruning 四类模式。 |
| AC-004 | thinking-protocols | 该 skill 的输出显式体现第一性原理、苏格拉底提问、奥卡姆剃刀三类思考协议。 |
| AC-005 | boundary-and-artifact | 该 skill 只做思考与建议，不直接改 truth、不直接执行 implement，并能生成单一 Markdown 产物。 |

## 7. Risks

- 如果继续依赖通用外部 brainstorming skill，Beacon 的思考层会长期外置，无法与 version truth 稳定对齐。
- 如果把该能力并入 `beacon-prd`，会让正式 requirement 写作与前置/中途思考混在一起。
- 如果把该能力并入 `beacon-toolkit-lighthouse`，会让静态分析与交互式收敛混在一起。
- 如果不给它明确边界，它会膨胀成新的主流程 stage。

## 8. Release Guard

- 只有当 AC-001 到 AC-005 对应测试全部通过，且 `beacon-brainstorm` 的输出能稳定体现 version grounding、thinking protocol 与 boundary contract 时，才允许进入 release 评审。
