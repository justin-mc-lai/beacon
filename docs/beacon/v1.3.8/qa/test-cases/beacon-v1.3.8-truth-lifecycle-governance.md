# Test Cases: Beacon v1.3.8 Truth Lifecycle Governance

**Feature**: `beacon-v1.3.8-truth-lifecycle-governance`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | 读取 `v1.3.8` requirement package | docs | 版本主题清晰表达为 `truth admission -> truth execution -> truth retirement`。 |
| TC-002 | AC-002 | 复杂业务 feature 进入 PRD 阶段 | product | PRD 能承载 branch-flow、state-machine、decision-priority 与 state axis，而不是只有 narrative paragraphs。 |
| TC-003 | AC-003 | freeze readiness 检查复杂业务 feature | integration | 系统能识别缺少 diagram truth layer 的 feature，并在冻结前给出明确提示或阻断。 |
| TC-004 | AC-004 | 冻结后的多服务交付启动 | integration | Beacon 能公开表达 `team -> ralph` 的 execution contract，而不需要用户重复手工说明顺序。 |
| TC-005 | AC-005 | 宿主提示词触发 Beacon workflow | integration | 系统能记录 `host prompt -> mapped command -> produced artifact` 的结构化链路。 |
| TC-006 | AC-006 | 查看冻结后 feature 的状态 | integration | `status` / HUD 能显示 freeze/team/ralph phase、`stop_state` 与 `next_action`。 |
| TC-007 | AC-007 | 多服务 feature 存在 branch mismatch 与 dirty worktree | integration | branch preflight 返回服务级风险与推荐安全迁移动作。 |
| TC-008 | AC-008 | 版本线进入 archive governance writeback | integration | 系统存在 machine-readable archive contract，并能区分 active、superseded、archived-learnable、archived-reference-only。 |
| TC-009 | AC-009 | help/status/brainstorm/memory/implement/gate 读取历史资料 | integration | 主要消费面能识别 archive 状态，不把历史 requirement 继续当成当前 active truth。 |

## Execution Notes

- version: `v1.3.8`
- AC-001 到 AC-009 都必须有至少一条明确测试覆盖。
- 测试时应区分：
  - truth admission correctness
  - truth execution evidence completeness
  - truth retirement isolation correctness
