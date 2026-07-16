# Change Record: beacon-loop-native-runner-and-automation-retirement

- feature: `beacon-loop-native-runner-and-automation-retirement`
- version: `v1.6.0`
- change_reason: `full-parity-gnhf-and-oss-sync-harness-via-beacon-lifecycle`
- artifact_role: `change_record_not_requirement_truth`
- truth_source: `false`

## Rationale

Planner review (`beacon-pln-review`) 判定：原 frozen truth 与实现仅为 MVP 骨架（单 iteration、stub resume/stop、仅 codex），与用户要求的 **gnhf 完整 runner 能力** 和 **manage-oss-sync 级 harness 成熟度**（统一 CLI、机器可读索引、query/show、diagnose、runtime 追踪、站外 learn/analyze）不一致。

用户明确要求通过 `beacon-gen-change` 重开需求包，写入 parity matrix 与 State Model，并重新冻结。

## Scope Change

| Before | After |
|--------|-------|
| `scope_mode` 隐式 MVP / 「第一版核心能力」 | 明示 `full_parity`（Beacon lifecycle 边界不变） |
| AC-001..AC-015 MVP 契约 | 保留并扩展 AC-016..AC-030 |
| 无 State Model 落点 | 必填 State Model + illegal transition 测试义务 |
| 无 parity matrix 落点 | 必填 gnhf + oss-sync harness parity matrix |
| tasks 全勾选完成 | 重开 Phase A/B/C 实现任务 |

## Accepted Deferrals

| ID | Capability | Decision | Revisit |
|----|------------|----------|---------|
| D-005 | TUI / live terminal title | `accepted` defer | v1.6.x patch |
| D-006 | Anonymous telemetry | `accepted` defer | v1.6.x patch |
| D-007 | prevent-sleep OS integration | `accepted` defer | v1.6.x patch |
| D-008 | stdin prompt + interactive prompt conflict UX | `accepted` defer | v1.6.x patch |

## Non-Deferrals (must land in this change truth)

- Multi-iteration orchestrator loop
- True resume / graceful+force stop
- gnhf failure/backoff/consecutive-failure semantics
- manage-oss-sync harness patterns: run ledger, query/show, diagnose, runtime tracking, analyze/learn 站外产物
- Multi-agent adapters (phased delivery: codex Phase A full loop; claude + acp Phase B minimum)
- Beacon closed loop unchanged

## Promotion Diff

进入 `features/.../truth.md` 的新增承诺：

- `Scope Mode`、`State Model`、`Source Capability Inventory`、`Parity Matrix`、`Deferral Ledger`、`Delivery Phases`
- AC-016..AC-030 与对应 tests/tasks

## Next Route

`beacon-gen-implement` after refreeze complete.
