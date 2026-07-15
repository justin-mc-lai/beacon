---
program_slug: v2-0-0-rust
version: v2.0.0
feature_slug: beacon-v2-rust-kernel-redesign
status: frozen_intent
scope_mode: full_parity
lake_or_ocean: 海
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md
phase_graph_ref: docs/beacon/v2.0.0/programs/v2-0-0-rust/phase-graph.md
admission_ref: docs/beacon/v2.0.0/programs/v2-0-0-rust/admission-gates.md
---

# v2.0.0 Rust Program Manifest

## Intent Snapshot

用户接受的 program intent：

> 现在开始完整实现 v2.0.0 rust 重构需求，确保可交付验收。

稳定解释：按 frozen v2 truth 完整实现 Rust 极简 Beacon harness，不降级 MVP；用 program 编排把 `truth -> design? -> implement -> qa-evidence -> release` 走成可恢复、可审计、可一键决策的闭环。

## Scope

- `scope_mode`: `full_parity`
- `lake_or_ocean`: `海`
- 不允许把 v2 Rust kernel closure 降级为单包 MVP、docs-only、stub-only 或 reason-only refreeze。
- program 只编排 truth 中已冻结的六能力 kernel contract；不新增第七个 public skill。

## Canonical Inputs

- Requirement truth: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md`
- Tests: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md`
- Tasks: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tasks.md`
- Evidence: `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/evidence.md`

## Program Outputs

- `intent_snapshot.v1`
- `prompt_snapshot` ledger with latest accepted pointer
- `decision_packet.v1`
- `BranchContext.v1`
- `TraceSpine.v1` and `TraceContext.v1`
- standard flow admission bundle
- phase exit evidence for P0, P1, P2, P3, P4 and P6

## Next Action

`program_phase:P0` remains the first executable action, but implementation admission must first prove:

- canonical truth branch refreeze is committed;
- feature branch contains the canonical truth baseline commit;
- workspace admission produced a valid `BranchContext.v1`;
- program phase graph and admission gates are present.
