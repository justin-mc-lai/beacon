# User Story: beacon-v1.3.3-minimal-hud-scenarios-and-implementation

## Story

**As a** Beacon 人类操作者,  
**I want** 在 `help/status`、Codex 输入框下固定 HUD、以及 implement 运行中看到同源极简 HUD（阶段、阻断、下一步）,  
**So that** 我可以在 3 秒内做出下一步决策，并在阻断时用单一推荐命令恢复流程。

## Acceptance Criteria

- AC-001 S1-S6 场景渲染稳定：`help/status` 可稳定覆盖主链空闲、single、team、ralph、warn、blocked/trip 六类场景。
- AC-002 HUD 行数预算受控：正常场景最多 2 行，仅 warn/blocked 允许第 3 行。
- AC-003 最小决策字段完整：必须包含 `stage`、执行摘要（single/team/ralph）、`next_action`，阻断时包含 `recommended_command`。
- AC-004 Ralph HUD 可观测闭环：输出含 `phase`、`round_count`、`stop_state`、`next_action`、`current_blocker`、`failure_streak`、`no_delta_streak`。
- AC-005 Team HUD 可观测执行摘要：输出含 `team_state`、`terminal_status`、`review_gates`、`fix_loops` 与角色最新事件摘要。
- AC-006 命令面不扩张且兼容：不新增公开一级命令；`help/status --json` 保持向后兼容（仅增字段不删字段）。
- AC-007 阻断恢复一致性：compatibility 阻断统一推荐 `beacon doctor migrate-compat ...`；机器侧仍保留完整 JSON/artifacts。
- AC-008 Codex 固定 HUD 注入：hook 输出必须通过 `hookSpecificOutput.additionalContext` 返回 1-3 行 HUD，且文本来自 `minimal_hud` 同一渲染契约。
- AC-009 自动注入事件覆盖：必须覆盖 `UserPromptSubmit`，并支持会话刷新事件（`SessionStart/SessionResume/SessionRefresh` 至少其一可配置）。
- AC-010 Hook 治理与降级：hook 安装/校验必须走 `beacon doctor`；hook 失败不得阻断主输入流程，必须降级并写 debug 证据。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 5 |
| Status | ready-for-implementation |
| Created | 2026-04-17T11:52:38.595220 |
| Memory Context | HUD minimal contract v1.3.3 + codex fixed hud hook |
