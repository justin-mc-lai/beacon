# PRD: Beacon v1.3.8 PRD Executable Diagram Truth Layer

**Feature**: `beacon-v1.3.8-prd-executable-diagram-truth-layer`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Context

- Parent line:
  - `docs/beacon/archive/v1.3.8/prd/beacon-v1.3.8-truth-lifecycle-governance.md`
- Research anchor:
  - `docs/beacon/archive/v1.3.8/research/beacon-v1.3.8-prd-executable-diagram-truth-layer-analysis.md`
- Brainstorm anchor:
  - `docs/brainstorms/2026-04-24-beacon-v1-3-8-truth-lifecycle-brainstorm.md`

## 1. Problem

复杂业务 feature 只靠 narrative PRD 不够稳定。

当一个 feature 同时牵涉：

- 多状态轴
- 多服务联调
- 资格与归属切换
- 奖励或结算口径切换

纯段落描述会带来这些结果：

- 后端压缩字段语义
- 前端根据文案反推逻辑
- QA 无法稳定覆盖状态迁移与分支树
- freeze 后仍靠口头解释维持一致

所以 `v1.3.8` 需要把 PRD 从“可读说明书”升级为“可执行真相面”。

## 2. Goals

### 2.1 Primary Goal

让复杂业务 feature 在 freeze 前具备最小可执行 diagram truth layer：

```text
narrative requirements
+ branch-flow
+ state-machine
+ decision-priority
+ state axes
```

### 2.2 Expected Result

本线完成后，Beacon 应满足：

1. 对复杂业务 feature，`prd create` 能推荐或生成 diagram truth layer。
2. freeze readiness / brainstorm convergence 能识别缺失图层的风险。
3. implement plan 能吸收 diagram 节点，而不是只读 acceptance text。
4. QA 能按图中的 branch / transition 派生覆盖骨架。

## 3. Non-goals

- 不要求所有 feature 都强制画复杂图
- 不把 Mermaid 图层当作装饰性文档
- 不只改 PRD 而不改 implement / QA 传导

## 4. Core Product Semantics

### 4.1 Diagram Truth Layer

对满足复杂业务判定条件的 feature，PRD 推荐至少支持：

- `branch-flow`
- `state-machine`
- `decision-priority`

### 4.2 State Axis Modeling

PRD / user-story 应允许显式表达多条状态轴，而不是把语义塞进一个状态字段。

典型例子：

- relation
- sale
- ownership
- eligibility

### 4.3 Propagation Contract

Diagram 不是只给人看，还要传导到：

- freeze readiness
- implementation plan
- QA coverage

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon 必须在复杂业务 feature 上支持或推荐 `branch-flow`、`state-machine`、`decision-priority` 三类 diagram truth layer。 |
| FR-002 | AC-002 | Beacon 必须支持在 PRD / user-story 中显式建模多条 state axis，而不是默认压缩成单字段状态。 |
| FR-003 | AC-003 | `beacon-brainstorm` 或 freeze readiness 必须能识别“缺少 diagram truth layer 的复杂业务 feature”，并给出明确提示或阻断。 |
| FR-004 | AC-004 | implementation plan 编译必须能够吸收 diagram 中的关键分支、关键状态节点、关键转移，转化为 task / review gate。 |
| FR-005 | AC-005 | QA / test-case 生成必须能够覆盖 diagram 中的主要分支与状态迁移，而不是仅覆盖 narrative acceptance text。 |

## 6. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | diagram-layer | 复杂业务 feature 的 PRD 可以正式承载 `branch-flow`、`state-machine`、`decision-priority`。 |
| AC-002 | state-axis | PRD / user-story 能显式表达多条 state axis，而不是依赖隐式段落语义。 |
| AC-003 | freeze-readiness | freeze readiness 或 brainstorm convergence 能识别 diagram truth layer 缺失风险。 |
| AC-004 | plan-propagation | implementation plan 能吸收 diagram truth layer，生成可执行 task 与 review gate。 |
| AC-005 | qa-propagation | QA / test-case 能按 diagram 的 branch / transition 建立覆盖骨架。 |

## 7. Freeze Deliverables

- `docs/beacon/archive/v1.3.8/research/beacon-v1.3.8-prd-executable-diagram-truth-layer-analysis.md`
- `docs/beacon/archive/v1.3.8/prd/beacon-v1.3.8-prd-executable-diagram-truth-layer.md`
- `docs/beacon/archive/v1.3.8/user-story/beacon-v1.3.8-prd-executable-diagram-truth-layer.md`
- `docs/beacon/archive/v1.3.8/qa/test-cases/beacon-v1.3.8-prd-executable-diagram-truth-layer.md`

## 8. Risks

- 如果复杂业务识别规则过弱，系统仍会让 narrative PRD 进入 freeze。
- 如果 diagram 只存在于 PRD 层，不会真正进入 implement / QA。

## 9. Release Guard

- 本 requirement line 的冻结前提是：
  - requirement clarity 无 unresolved findings
  - PRD / user-story / test-case 对 AC-001 到 AC-005 一一映射
