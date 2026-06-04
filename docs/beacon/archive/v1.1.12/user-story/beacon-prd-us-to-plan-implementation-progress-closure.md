# User Story: Beacon PRD / User Story to Implementation Plan 进度闭环（v1.1.12）

**Feature**: `beacon-prd-us-to-plan-implementation-progress-closure`
**Version**: `v1.1.12`

## Story

**As a** 使用 Beacon 管理需求交付、实现执行与进度回写的 release owner / AI coding agent / 项目维护者
**I want** Beacon 在 `user-story + prd + test-case` 之后，先把需求编译成 implementation plan，再用该 plan 约束 implement 执行与进度写回
**So that** Beacon 不只是“能开始实现”，而是能把 PRD/用户故事稳定转成可执行计划、可追踪任务和可回写进度的闭环交付面

## Story Slices

### US-001: PRD/US 必须先编译成 implementation plan
作为 release owner，我希望 `user-story + prd + test-case` 先被编译成 implementation plan，而不是直接把文档路径塞进 implement prompt。

### US-002: implementation plan 必须是正式工件
作为审计方，我希望实现计划有明确的 machine-readable artifact 与 human-readable artifact，后续 implement / review / status 都能引用同一份计划。

### US-003: implement 前必须通过 plan gate
作为 AI coding agent，我希望 `implement run` 在真正开始编码前先确认 plan 已存在、已对齐冻结基线、已绑定当前版本与需求修订。

### US-004: plan 必须显式表达 task-level progress
作为项目维护者，我希望实现进度不是只有 stage 状态，而是能看到 task 级别的 pending / in_progress / blocked / done。

### US-005: AC/TEST 到实现任务必须可追踪
作为 release owner，我希望每个实现任务都能追踪它对应的 AC / TEST / source refs，避免实现、验证和回写彼此脱节。

### US-006: writeback 必须更新 plan progress
作为项目协作者，我希望 implement / verify / accept 的 writeback 不仅更新 story/revision，还能同步更新 implementation plan 的任务状态。

### US-007: status 必须展示计划级进度
作为使用者，我希望 `status` 能同时展示 workflow 阶段级进度与 implementation plan 任务级进度，而不是只看 run-level 摘要。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Plan Compiler | Beacon 必须存在 `prd-us-to-plan` 语义，把 `user-story + prd + test-case` 编译成 implementation plan |
| AC-002 | Plan Artifact | implementation plan 必须有 machine-readable artifact 与 human-readable artifact，且可被 implement / status / writeback 消费 |
| AC-003 | Baseline Binding | plan 必须绑定当前 version、revision_id 与 frozen baseline truth，未对齐时不得进入 implement |
| AC-004 | Pre-implement Gate | `implement run` 在 runner 启动前必须校验 plan readiness，不得跳过 plan gate 直接编码 |
| AC-005 | Task Progress Model | implementation plan 必须显式表达 task 级状态，包括 `pending`、`in_progress`、`blocked`、`done` |
| AC-006 | Traceability | 每个 task 必须可追踪其 source refs、mapped story ids、mapped AC ids、mapped TEST ids |
| AC-007 | Writeback Update | implement / verify / accept 的 writeback 必须同步更新 implementation plan progress |
| AC-008 | Status Visibility | `status` 必须能展示 plan-level progress，并能指出当前卡在哪个 task / 哪个 AC / 哪个 TEST |
| AC-009 | Progress Fidelity | 任务级进度不得被 run-level summary 或 stage-level progress 伪装或覆盖 |
| AC-010 | Closed-Loop Evidence | 已完成任务必须留下可回溯 evidence refs，便于 review / gate / recover 使用 |

## First-principles Loop

正确链路应是：

```text
user-story + prd + test-case
→ prd-us-to-plan compiler
→ implementation plan artifact
→ pre-implement plan gate
→ implement task execution
→ writeback updates task progress
→ status / review / gate consume plan truth
```

不是：

```text
user-story + prd
→ 直接丢给 implement prompt
→ 跑完再临时拼 progress
```

## Notes

- 这条线不是为了再造一个 workflow stage。
- 它的目标是把实现前的“计划编译”和实现中的“进度回写”统一成一条正式闭环。
- `autoresearch` 与 `navigator` 可以参考 plan truth，但不应直接替代 plan truth。
