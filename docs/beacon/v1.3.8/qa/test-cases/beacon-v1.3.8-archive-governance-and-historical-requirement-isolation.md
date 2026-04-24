# Test Cases: Beacon v1.3.8 Archive Governance and Historical Requirement Isolation

**Feature**: `beacon-v1.3.8-archive-governance-and-historical-requirement-isolation`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | archive governance runtime 初始化 | integration | 系统存在 machine-readable archive status model。 |
| TC-002 | AC-002 | 人类查询 Beacon 的 support surface | cli | Beacon 暴露 `beacon archive plan/apply/status/explain`，并明确归属 support command，而不是新 lifecycle stage。 |
| TC-003 | AC-003 | 宿主通过 skill 面触发 archive 治理 | integration | `beacon:beacon-archive` 能将 archive 命令正确路由到正式 archive governance 能力。 |
| TC-004 | AC-004 | 读取 version archive plan / archive index、feature archive metadata，并由 `help` / `status` / `brainstorm` / `memory-friction-evolution` / `implement` / `gate` 消费 | integration | 主要消费面能识别 archive boundary，且可返回 archive status / reason / refs。 |
| TC-005 | AC-005 | 用户先用 `beacon-brainstorm` 做归档前讨论，再触发正式 archive 治理，并读取历史 truth | integration | `beacon-brainstorm` 保持 read-only 策略边界；历史资料仍可追溯，但不会默认进入当前 active delivery plane。 |

## Execution Notes

- version: `v1.3.8`
- 需同时验证 support command 暴露、skill routing、brainstorm 边界、以及“仍可追溯但不会污染当前实现面”。
