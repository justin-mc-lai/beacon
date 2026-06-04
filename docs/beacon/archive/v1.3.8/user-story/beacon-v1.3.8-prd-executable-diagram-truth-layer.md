# User Story: Beacon v1.3.8 PRD Executable Diagram Truth Layer

**Feature**: `beacon-v1.3.8-prd-executable-diagram-truth-layer`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Story

作为在复杂业务 feature 上做需求冻结与实现协同的操作者，我希望 Beacon 能在 PRD 阶段把复杂业务从 narrative text 提升为 diagram-backed truth，这样多服务实现与 QA 才能共享同一套判定路径。

## Requirement Description

本线聚焦 `truth admission`：

- PRD 需要支持 branch-flow、state-machine、decision-priority
- user-story 需要支持 state axis 建模
- freeze readiness 需要识别 diagram truth layer 缺失
- implement plan 与 QA 需要继续吸收这些结构

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | diagram-layer | 复杂业务 feature 的 PRD 可以正式承载 `branch-flow`、`state-machine`、`decision-priority`。 |
| AC-002 | state-axis | PRD / user-story 能显式表达多条 state axis，而不是依赖隐式段落语义。 |
| AC-003 | freeze-readiness | freeze readiness 或 brainstorm convergence 能识别 diagram truth layer 缺失风险。 |
| AC-004 | plan-propagation | implementation plan 能吸收 diagram truth layer，生成可执行 task 与 review gate。 |
| AC-005 | qa-propagation | QA / test-case 能按 diagram 的 branch / transition 建立覆盖骨架。 |

## Metadata

- version: `v1.3.8`
- feature: `Beacon v1.3.8 PRD executable diagram truth layer`
- status: `draft`
