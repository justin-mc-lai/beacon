# User Story: Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking

## Story

作为在 Beacon 内推进 requirement、变更与后续演进的操作者，我希望 Beacon 自身拥有一个内建的 `beacon-brainstorm` 子 skill，能够基于 `docs/beacon/<version>/` 的正式材料继续头暴、补齐缺口并收敛方向，这样我就不需要在正式 requirement 写作、静态代码分析和外部通用 brainstorming 之间来回切换。

## Requirement Description

`v1.3.7` 需要一个新的内建 sidecar：

- 名称固定：`beacon-brainstorm`
- 基于 version 文档继续头暴和补齐
- 支持项目演进方向探索
- 支持第一性原理、苏格拉底提问、奥卡姆剃刀
- 不改 truth
- 不直接执行 implement

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | built-in-skill | 存在一个 Beacon 内建的 `beacon-brainstorm` 子 skill，定位为 host-visible 但非主流程。 |
| AC-002 | version-grounding | 该 skill 能基于 `docs/beacon/<version>/` 的正式材料继续头暴、补齐和收敛。 |
| AC-003 | working-modes | 该 skill 至少支持 requirement convergence、frozen-truth delta、evolution exploration、redundancy pruning 四类模式。 |
| AC-004 | thinking-protocols | 该 skill 的输出显式体现第一性原理、苏格拉底提问、奥卡姆剃刀三类思考协议。 |
| AC-005 | boundary-and-artifact | 该 skill 只做思考与建议，不直接改 truth、不直接执行 implement，并能生成单一 Markdown 产物。 |

## Metadata

- version: `v1.3.7`
- feature: `Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking`
- status: `draft`
