# User Story: Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope

## Story

作为在 Codex / Claude 内推进 Beacon 版本实现的操作者，我希望在目标版本 requirement truth 已冻结后，直接通过 `beacon-implement + version + prompt` 进入实现，同时由系统自动核实 prompt 是否仍落在 frozen scope 内，以便我不用重复准备流程，也不会误把新需求混进已冻结实现。

## Requirement Description

`v1.3.7` 的 `implement` 极简入口必须建立在冻结 requirement truth 之上：

- prompt 只作为实现意图输入和 frozen-truth verification 输入
- prompt 不是新的 truth source
- 超出 frozen scope 的请求必须阻断并回到 requirement change / refreeze
- `implement plan` 前必须先生成 canonical delivery baseline envelope
- 所有实现前置 artifacts 都必须由 canonical envelope 单向投影生成

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | minimal-entry | 对应版本的 `prd / user-story / test-case` 已冻结时，用户可以在 Codex / Claude 内通过 `beacon-implement + version + prompt` 直接进入实现前核实流程。 |
| AC-002 | prompt-boundary | 系统能将 prompt 明确分类为 `in_scope_implementation`、`clarification_within_scope`、`requirement_change`、`truth_conflict`，并且只允许前两类继续。 |
| AC-003 | stop-and-reroute | 当 prompt 被判定为 requirement 变更或 truth 冲突时，系统必须阻断 implement，并给出 requirement change / refreeze 路由。 |
| AC-004 | canonical-source | `implement plan` 必须先生成 canonical 的 `implementation delivery baseline envelope`，再投影 `architecture-blueprint`、deterministic contract、git workflow 与 implementation plan。 |
| AC-005 | consistency-gate | gate 必须以 canonical envelope 为唯一对齐源，对 `baseline_id`、事务元数据和 service/branch/worktree 关键信息做一致性校验；发现漂移必须阻断。 |

## Metadata

- version: `v1.3.7`
- feature: `Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope`
- status: `draft`
