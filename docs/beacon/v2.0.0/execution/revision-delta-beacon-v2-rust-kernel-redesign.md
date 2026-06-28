# Beacon Revision Delta

- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- revision_id: `R2`
- source_revision_id: `R1`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `2`
- added_requirement_count: `6`

## Removed Requirement Surfaces
- `AC-018` 无 placeholder；worktree+implement 不 defer
- `AC-025` planner review 选项 A：AC-042–046 真集成；Diagram Truth Layer；AC 重编号至 098；禁止 placeholder AC

## Added Requirement Surfaces
- `AC-018` 无空壳 AC；worktree+implement 不 defer
- `AC-024` TIG + planner multi-agent + doctor 路由
- `AC-025` beacon-rs scaffold 已完成
- `AC-098` **（P3）：`beacon doctor verify-truth-integrity` 在 v2 路由到 gate 或 PyO3 compat；`--mode block` exit code 与 v1.6 一致。
- `AC-028` **）
- `AC-027` planner review 选项 A：AC-042–046 真集成；Diagram Truth Layer；AC 重编号至 098；禁止空壳 AC
