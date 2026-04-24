# PRD: Beacon v1.3.8 Post-Freeze Team-Ralph Sequencing and Host Prompt Trace

**Feature**: `beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Context

- Parent line:
  - `docs/beacon/v1.3.8/prd/beacon-v1.3.8-truth-lifecycle-governance.md`
- Research anchor:
  - `docs/beacon/v1.3.8/research/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace-analysis.md`

## 1. Problem

在真实多服务交付中，冻结后的工作顺序已经稳定表现为：

```text
freeze
-> implement team
-> implement ralph
-> qa
-> release
```

但当前 Beacon 仍有四个缺口：

1. `team -> ralph` 只是人工说明，不是 formal execution contract
2. 宿主提示词才是真实驱动面，但没有 formal trace
3. `status` / HUD 不能完整展示 phase
4. branch preflight 更像 generic blocker，不够 action-oriented

## 2. Goals

### 2.1 Primary Goal

把冻结后的真实交付顺序与宿主驱动面写入 Beacon 的 execution truth。

### 2.2 Expected Result

本线完成后，Beacon 应满足：

1. `team -> ralph` 顺序可以被显式表达为 execution contract。
2. `host prompt -> mapped command -> produced artifact` 可被结构化记录。
3. `status` / HUD 能展示 team/ralph phase 与 next action。
4. branch preflight 提供服务级推荐动作。

## 3. Non-goals

- 不新增新的公开一级主生命周期 stage
- 不让 `team` 与 `ralph` 使用不同 requirement truth
- 不用 prompt trace 替代 formal implement / QA / release evidence

## 4. Core Product Semantics

### 4.1 Explicit Execution Sequence

Beacon 应支持显式表达：

```text
freeze pass
-> implement team-plan
-> implement team-run
-> implement ralph
-> qa
-> release
```

### 4.2 Host Prompt Trace

推荐至少记录：

- original host prompt
- inferred surface
- mapped command
- generated artifacts
- route success or blocked

### 4.3 Phase Projection

`status` / HUD 至少应展示：

- freeze status
- team phase
- ralph pending or active
- stop_state
- next_action

### 4.4 Branch Actionability

branch preflight 应输出：

- affected service
- current branch
- expected branch
- dirty worktree state
- recommended safe relocation action

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon 必须支持把冻结后的 `team -> ralph` 顺序表达为正式 execution contract。 |
| FR-002 | AC-002 | Beacon 必须把宿主提示词到命令、产物的映射记录为结构化 host prompt trace。 |
| FR-003 | AC-003 | `status` / HUD 必须能显示 freeze/team/ralph phase、stop_state 与 next_action。 |
| FR-004 | AC-004 | branch preflight 必须输出服务级 branch mismatch 与推荐安全迁移动作。 |
| FR-005 | AC-005 | `team reviewer/tester` 与 `ralph` 的职责语义必须在 docs / payloads / status 上清晰区分。 |

## 6. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | execution-sequence | 冻结后的 `team -> ralph` 顺序可以被 Beacon 公开表达为 execution contract。 |
| AC-002 | host-prompt-trace | 宿主提示词到命令、产物的映射可被结构化记录。 |
| AC-003 | phase-projection | `status` / HUD 能显示 freeze/team/ralph phase、stop_state 与 next_action。 |
| AC-004 | branch-actionability | branch preflight 能指出具体服务、当前分支、目标分支、脏工作树风险与推荐操作。 |
| AC-005 | role-semantics | `team reviewer/tester` 与 `ralph` 的职责边界在 docs 与状态面中清晰可见。 |

## 7. Freeze Deliverables

- `docs/beacon/v1.3.8/research/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace-analysis.md`
- `docs/beacon/v1.3.8/prd/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace.md`
- `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace.md`
- `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace.md`

## 8. Risks

- 如果只记录命令，不记录宿主提示词，memory 仍然学不到真实交付行为。
- 如果 phase 只存在实现内部，不暴露到 status / HUD，用户仍会靠聊天补状态。

## 9. Release Guard

- 本 requirement line 的冻结前提是：
  - requirement clarity 无 unresolved findings
  - PRD / user-story / test-case 对 AC-001 到 AC-005 一一映射
