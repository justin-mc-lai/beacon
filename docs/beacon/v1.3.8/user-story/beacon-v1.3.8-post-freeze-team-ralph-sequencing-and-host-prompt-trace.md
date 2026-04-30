# User Story: Beacon v1.3.8 Post-Freeze Team-Ralph Sequencing and Host Prompt Trace

**Feature**: `beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Story

作为在真实多服务项目中使用 Beacon 的操作者，我希望冻结后的 `team -> ralph` 顺序和宿主提示词驱动面都能进入 formal execution truth，这样我不需要反复解释执行顺序，系统也能学习我真实的工作模式。

## Requirement Description

本线聚焦 `truth execution`：

- `team -> ralph` 顺序产品化
- host prompt trace 结构化留证
- phase 状态投影到 `status` / HUD
- branch preflight 输出服务级动作

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | execution-sequence | 冻结后的 `team -> ralph` 顺序可以被 Beacon 公开表达为 execution contract。 |
| AC-002 | host-prompt-trace | 宿主提示词到命令、产物的映射可被结构化记录。 |
| AC-003 | phase-projection | `status` / HUD 能显示 freeze/team/ralph phase、stop_state 与 next_action。 |
| AC-004 | branch-actionability | branch preflight 能指出具体服务、当前分支、目标分支、脏工作树风险与推荐操作。 |
| AC-005 | role-semantics | `team reviewer/tester` 与 `ralph` 的职责边界在 docs 与状态面中清晰可见。 |

## Metadata

- version: `v1.3.8`
- feature: `Beacon v1.3.8 post-freeze team ralph sequencing and host prompt trace`
- status: `draft`
