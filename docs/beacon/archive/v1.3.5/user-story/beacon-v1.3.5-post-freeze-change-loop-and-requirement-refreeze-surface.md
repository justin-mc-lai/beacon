# User Story: beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface

## Story

**As a** Beacon 产品负责人或实现负责人,  
**I want** 在需求已经冻结后，通过一个克制的宿主子 skill 进入需求调整再闭环,  
**So that** 我可以不打破 `7+3` 主链，就完成 reopen、增量补文档、重新冻结、增量实现、增量验收与 re-release。

## Acceptance Criteria

- [ ] AC-001 Beacon 不新增新的一级主命令，但新增一个宿主可见 `beacon-change` 子 skill 草案，并明确其不是新主阶段。
- [ ] AC-002 冻结后的 feature 能走通 `change intake -> reopen -> prd revise -> user-story refresh -> test-case refresh -> prototype refresh -> re-freeze -> implement fix -> qa delta-run -> release recheck`。
- [ ] AC-003 系统能提供一份文档化生命周期状态机，明确状态、迁移条件、阻断条件与产物边界。
- [ ] AC-004 变更后的 implement / qa / release 都绑定最新 frozen revision，不允许继续沿用旧 baseline。
- [ ] AC-005 `help/status` 在识别到冻结后需求调整时，稳定推荐 `beacon-change` 或等价 change loop。
- [ ] AC-006 `release` 能区分 initial delivery、revised delivery、hotfix delivery 的语义与 gate 对象。

## Story Breakdown

### Story 1: 宿主路由补齐

作为使用 Beacon 的操作者，我希望通过自然语言稳定进入冻结后变更闭环，而不是自己记忆隐藏命令。

- 对应 AC: `AC-001`, `AC-005`

### Story 2: Requirement Re-freeze 主链成立

作为 requirement owner，我希望 feature 冻结后仍能在正式 revision 语义下 reopen、增量补文档并重新冻结。

- 对应 AC: `AC-002`, `AC-004`

### Story 3: 状态机与交付语义可审计

作为 release reviewer，我希望看到清晰的生命周期状态机和 revised delivery 语义，避免旧 baseline 混入新交付。

- 对应 AC: `AC-003`, `AC-006`

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | frozen-pending-implementation |
| Created | 2026-04-20T14:34:54.721629+00:00 |
| Updated | 2026-04-20T22:40:00+08:00 |
| Memory Context | post-freeze change loop |
