---
feature_slug: beacon-v2-rust-kernel-redesign
version: v2.0.0
authority: support_advisory
promotion_ref: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md
---

# Research：Beacon v2 Rust Kernel Redesign

## outcome

将 Beacon v1 Python/Node 双栈治理内核重写为 **Rust 核心 + Python 兼容层**，用编译期状态机、本机全局 SQLite、统一 orchestrator 与单一 Operator Spine 查询面，消除 v1 的架构级漂移与运行态散落。

## lake_or_ocean

**海** — 跨 crate、跨语言、跨 v1/v2 共存与迁移的全产品线重写；必须分 P0–P6 阶段交付，不得 silent MVP 裁剪核心合同。

## truth_refs

- `docs/plans/beacon-v2-redesign.md`（主计划）
- `docs/beacon/global-boundaries.md`（真相/投影边界）
- `docs/beacon/archive/v1.3.4/execution/architecture-blueprint.md`（Runtime Ledger 单库多项目）
- `docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md`（Spine 字段语义）

## source_refs

- `beacon/utils/runtime_projection_store.py`（v1 机器级 ledger）
- `packages/beacon-loop/`、`packages/beacon-run/`（v1 长任务编排）
- `beacon/utils/prototype_utils.py`（v1 巨型单文件反例）

## evidence_refs

- v1.6.0 closed-loop orchestrator QA 经验（worktree、harness、truth_freeze_gate）

## truth_gap

v2.0.0 此前无冻结 package truth；本 research 已 promote 至 `features/beacon-v2-rust-kernel-redesign/truth.md`。

## test_gap

tests.md 已按 plan §1–§10 全量映射 AC/TC（r4 Alignment Surface 行为级收紧）；Round 6 前需 requirement_clarity pass。

## implementation_risk

- PyO3 构建链与 CI wheel
- v1→v2 全局库 migration 数据无损
- P3 前 orchestrator 与 v1 beacon-loop 并存边界

## verification_risk

- 性能目标需 benchmark 证据，不能仅单元测试
- Gate reason_codes 与 v1 字节级兼容需回归夹具

## recommended_route

`truth.define` → `truth.coverage`（已完成草案）→ `requirement_clarity` → `freeze` → P0 `beacon-core`+`beacon-store`

## user_decision

promoted（由 operator 请求落地 v2.0.0 完整需求真相）

## promotion_ref

`docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md`

## Version Projection Truth Binding

package-authoritative v2.0.0 feature；research 仅 support_advisory，冻结 authority 在 feature package。

- prd_refs: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md
- user_story_refs: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md
- test_case_refs: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md
- coverage_notes: AC-001..AC-100 map 1:1 to TC-001..TC-100; Alignment Surface (Spine/projects/三层存储/orchestrator 真集成/worktree+implement/gate+migration) 行为级 TC r4 收紧；P6 bench (AC-051–058) phased；D-V2-001 accepted defer proto (AC-024/TC-089).
- out_of_scope_notes: 海级 scope 单包 truth 不等于全 plan 实现 closure；post-v2.0.0 beacon-proto/gRPC (D-V2-001)；P6 默认 BEACON_V2=1 与 benchmark 门禁；orchestrator 不裁决 QA/release；需求正文不进 DB。

## State Machine（Diagram Truth 投影）

truth.md `state_machine_required=true`：WorkflowStage + Delivery FSM（plan 主链 + runs.status 12 态压缩）+ Gate 轴；非法转换 fail-closed（AC-026–036）。v1.6 closed-loop 为 Alignment Surface 对照源。
