# Beacon Revision Delta

- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- revision_id: `R3`
- source_revision_id: `R2`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `3`
- added_requirement_count: `7`

## Removed Requirement Surfaces
- `AC-018` 无空壳 AC；worktree+implement 不 defer
- `AC-079` **：`runs`（id, feature_id, run_kind, status, iteration, started_at, ended_at, metadata_json）
- `AC-033` 存储三层（Plan §2.5）

## Added Requirement Surfaces
- `AC-001` Agent 写代码→跑 Eval→发现问题→修→再测，自动闭环
- `AC-002` 人看实现→修正 Spec→重新实现；人注入 AI 不知道的上下文
- `AC-005` acp:*>` CLI 直接选 agent 跑长任务编码落地；agent 选择映射到对应 AgentBackend；loop 在 CLI 进程内跑，checkpoint/resume/信号（SIGINT graceful stop）保证 host 稳定，**无 daemon**。
- `AC-073` **（P3）：Developer Feedback Loop 人注入 checkpoint——`beacon-v2 run --feedback-checkpoint` 在每 N iteration 后暂停 loop，等待人注入上下文修正（写入 `lifecycle_events` notes_injected），resume 后基于修正重新 iterate；人注入是 harness 接口，不绕过 truth（truth 变更仍走 change/refreeze）。
- `AC-074` **（P3）：Loop Engineering 三层 Loop 可观测——spine snapshot 含 `loop_layer` 字段（coding/developer/realworld），标注当前 run 在哪层 Loop；Coding Loop 内的 iteration + Developer Feedback 的 checkpoint + Real-world 的 research 都可追溯。
- `AC-031` （stop-when maker≠checker）→ v2 AC-105
- `AC-030` ，后者是 L1 MD / L2 SQLite / L3 Blob**）：
