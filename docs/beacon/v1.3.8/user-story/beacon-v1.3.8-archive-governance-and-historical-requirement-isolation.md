# User Story: Beacon v1.3.8 Archive Governance and Historical Requirement Isolation

**Feature**: `beacon-v1.3.8-archive-governance-and-historical-requirement-isolation`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Story

作为长期维护 Beacon 版本线与历史需求资产的治理者，我希望 Beacon 提供显式的 `archive` support command 和对应的 `beacon:beacon-archive` skill 来执行归档治理，这样我既能追溯历史，也不会让历史需求继续污染当前交付。

## Requirement Description

本线聚焦 `truth retirement`：

- 定义 archive status model
- 把 archive 落成 `beacon archive` support command
- 提供 `beacon:beacon-archive` skill 路由面
- 产出 version archive plan / archive index 与 feature archive metadata
- 让主要消费面读取 archive boundary
- 保持 `beacon-brainstorm` 只负责归档前策略讨论

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | archive-status | Beacon 存在 machine-readable archive status model。 |
| AC-002 | support-command | Beacon 对外存在 `beacon archive plan/apply/status/explain`，并明确归属 support command，而非新 lifecycle stage。 |
| AC-003 | skill-routing | Beacon 对外存在 `beacon:beacon-archive` skill，负责 archive 命令路由。 |
| AC-004 | archive-consumption | Beacon 存在版本级 archive plan / archive index、feature-level archive metadata，且 `help` / `status` / `brainstorm` / `memory-friction-evolution` / `implement` / `gate` 能识别 archive boundary。 |
| AC-005 | boundary-and-isolation | `beacon-brainstorm` 只负责归档前策略讨论；历史 requirement 与历史 truth 可追溯，但不会继续默认进入当前 active delivery plane。 |

## Metadata

- version: `v1.3.8`
- feature: `Beacon v1.3.8 archive governance and historical requirement isolation`
- status: `draft`
