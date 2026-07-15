# Beacon Revision Delta

- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- revision_id: `R10`
- source_revision_id: `R9`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `1`
- added_requirement_count: `1`

## Removed Requirement Surfaces
- `AC-125` **：`TraceSpine.v1` 是 run 级 append-only authority；`lifecycle_events`、read model、evidence manifest、loop-readiness 均为 projection，不得作为唯一权威源。

## Added Requirement Surfaces
- `AC-030` R7 refreeze：TraceSpine.v1 / TraceContext.v1 成为 run authority；loop/implement/qa-evidence/release 绑定 trace completeness；stagnation/remediation 报告绑定 trace event range；truth/change/refreeze 只能在 canonical truth branch 执行；阻断 reason-only/machine-only refreeze 与 revision narrative drift（AC-131–137）
