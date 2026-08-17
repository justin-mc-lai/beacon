# Beacon Revision Delta

- feature: `beacon-loop-goal-v166`
- version: `v1.6.6`
- revision_id: `R6`
- source_revision_id: `R5`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `2`
- added_requirement_count: `6`

## Removed Requirement Surfaces
- `AC-007` Release 阶段永远需要人工确认；即使 `auto_decide=true`，`current_stage=release_gate` 时编排器停在人工输入门
- `AC-014` 当 review decision packet 存在 P0/P1、`user_decision_required=true`，或推荐 route 指向 `beacon-gen-truth` / `beacon-gen-change` / `beacon-gen-refreeze` 时，loop-goal 不得自动进入 `implement_routing`，必须停在对应 route 或 error recovery

## Added Requirement Surfaces
- `AC-002` **不可覆盖**
- `AC-001` `--human-gate` 可强制停
- `AC-027` Auto-decide 表必须与 AC-007/AC-014 对齐：默认人类急停仅 release + review blocking 集合；P1-only 默认续跑；`--human-gate` 可把 P1 升为停；release 永远不可 auto 覆盖（**Must**）
- `AC-030` state/status 必须暴露 `human_stops_per_run`、`stop_reason` 分布、`p1_continue_count`；假性卡死（pseudo_stall）在可判定时计数（**Should**）
- `AC-029` 必须提供 `beacon status loop-goal --resume`（或等价），按 state 文件返回 `current_stage` + next skill + reason_code；禁止无状态变更的 no-op 打印充当 resume（**Must**）
- `AC-028` public SKILL.md 决策树必须声明：输出 next route 后**同会话立即加载**下一 skill；禁止以「仅打印下一步」结束编排回合（**Must**）
