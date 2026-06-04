# Beacon Revision Delta

- feature: `Beacon v1.3.8 archive governance and historical requirement isolation`
- version: `v1.3.8`
- revision_id: `R2`
- source_revision_id: `R1`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `4`
- added_requirement_count: `4`

## Removed Requirement Surfaces
- `AC-004` `help` / `status` / `brainstorm` / `memory-friction-evolution` / `implement` / `gate` 能识别 archive boundary。
- `AC-003` feature-level truth 能携带 archive metadata。
- `AC-005` 历史 requirement 与历史 truth 可追溯，但不会继续默认进入当前 active delivery plane。
- `AC-002` Beacon 存在版本级 archive plan / archive index。

## Added Requirement Surfaces
- `AC-004` Beacon 存在版本级 archive plan / archive index、feature-level archive metadata，且 `help` / `status` / `brainstorm` / `memory-friction-evolution` / `implement` / `gate` 能识别 archive boundary。
- `AC-005` `beacon-brainstorm` 只负责归档前策略讨论；历史 requirement 与历史 truth 可追溯，但不会继续默认进入当前 active delivery plane。
- `AC-003` Beacon 对外存在 `beacon:beacon-archive` skill，负责 archive 命令路由。
- `AC-002` Beacon 对外存在 `beacon archive plan/apply/status/explain`，并明确归属 support command，而非新 lifecycle stage。
