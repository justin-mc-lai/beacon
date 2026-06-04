# Test Cases: Beacon v1.3.8 Post-Freeze Team-Ralph Sequencing and Host Prompt Trace

**Feature**: `beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | 冻结后的多服务交付通过公开 implement surface 启动 | integration | Beacon 能表达 `team -> ralph` 的 formal execution contract。 |
| TC-002 | AC-002 | 宿主提示词驱动一次冻结后交付 | integration | 系统能记录 `host prompt -> mapped command -> produced artifact` 链路。 |
| TC-003 | AC-003 | 查询一个处于 team 或 ralph 阶段的 feature | integration | `status` / HUD 显示 team/ralph phase、stop_state 与 next_action。 |
| TC-004 | AC-004 | 多服务 feature 存在 branch mismatch 与 dirty worktree | integration | branch preflight 返回服务级风险与推荐动作。 |
| TC-005 | AC-005 | 查看 execution docs、payloads 或 status | docs | `team reviewer/tester` 与 `ralph` 职责边界清晰可见。 |

## Execution Notes

- version: `v1.3.8`
- execution contract、evidence contract、phase projection 三层都必须验证。
