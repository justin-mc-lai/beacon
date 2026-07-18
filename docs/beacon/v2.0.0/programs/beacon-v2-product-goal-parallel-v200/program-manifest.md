---
program_slug: beacon-v2-product-goal-parallel-v200
version: v2.0.0
plan_mode: interactive
scope_mode: full_parity
lake_or_ocean: 海拆湖
program_phase: P0
p4_ack: true
upstream_version: v1.6.7
upstream_program: beacon-product-goal-domain-delivery-v167
promotion_ref: planner-review:pln-review-20260717t073750z+user-decisions-20260717
user_decisions:
  UD-V2-PG-001: rust_orchestrator_owns_product_goal_runtime
  UD-V2-PG-002: dual_skills_loop_vs_goal_parity_with_v167
  UD-V2-PG-003: parallel_subagent_main_star_satellite_pool
  UD-V2-PG-004: progressive_skill_load_in_operator_spine
  UD-V2-PG-005: python_compat_shim_preserves_cli_surface
  UD-V2-PG-006: domain_truth_chain_merged_into_this_program_option_a
  UD-V2-PG-007: full_inherit_v167_ui_state_matrix_ship_hard_gate
  UD-V2-PG-008: reject_early_default_beacon_v2_until_w4
---

# Program Manifest — v2 Product Goal Parallel + Domain Truth Chain

## User Intent

v2 Rust kernel 实现与 v1.6.7 同构的 **Loop 发现 / Goal 完成** 双 skill 语义，并原生支持：
并行 sub-agent、渐进 skill 加载、主星/卫星 worktree pool；
**同时并入 Domain 真值链**（Option A）：domain-fsm 硬门、golden 夹具、QA 业务序、**完整继承** ui-state-matrix ship 门、Ralph implement-only 边界。

## Locked Decisions (2026-07-17)

| ID | Decision |
|----|----------|
| DEF-SE-001 | Domain 真值链 **Option A**：并入本 program，不另建独立 program |
| V2SE-006 | v2 ship **完整继承** v1.6.7 `ui-state-matrix` 硬门（非仅 design_primitives 弱对齐） |
| DEF-SE-004 | **拒绝** W4 完成前默认 `BEACON_V2=1` |

## Topology (7 lakes)

1. `beacon-v2-product-goal-orchestrator`
2. `beacon-v2-main-star-satellite-pool`
3. `beacon-v2-domain-fsm-authority`
4. `beacon-v2-golden-commerce-fixture-parity`
5. `beacon-v2-domain-fsm-qa-gate`
6. `beacon-v2-ui-state-matrix-ship-gate`
7. `beacon-v2-ralph-implement-boundary`
8. `beacon-v2-goal-durable-longrun`  # one-shot agent longrun + v1.6.7 durable parity

## Upstream (v1.6.7 contracts to honor)

- beacon-product-goal-runtime-v167 R3
- beacon-loop-discover-goal-finish-v167 R3
- beacon-git-scope-graph-v167
- beacon-domain-fsm-authority-v167
- beacon-golden-commerce-fixture-v167
- beacon-domain-fsm-qa-gate-v167
- beacon-ui-design-ship-gate-v167（**full inherit**）
- beacon-ralph-implement-boundary-v167
- beacon-goal-durable-supervisor-v167  # durable heartbeat/resume/tick-exec

## Migration waves (binding)

See `docs/beacon/v2.0.0/execution/v1.6-to-v2-migration-roadmap.md` Wave W0–W5 and
`docs/beacon/v2.0.0/execution/v2-software-engineering-standards.md` (SE-V2-*).

## Non-Goals

- 不把具体业务 Domain FSM 内嵌 `beacon-core`
- 不 1:1 克隆 v1 Python 巨石模块结构
- 不静默 fallback v1↔v2
- 不在 W4 前默认切换 `BEACON_V2=1`

## Additive (2026-07-18)

| ID | Decision |
|----|----------|
| UD-V2-PG-009 | Goal durable longrun AgentDriver one-shot (`--longrun`) on single public entry |
| UD-V2-PG-010 | Inherit v1.6.7 durable supervisor (120s heartbeat, append log, resume-pack, tick --execute) |

Lake: `beacon-v2-goal-durable-longrun` — see `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md`.

## Additive lakes (User GO 2026-07-18 — Loom)

9. `loom-brand-surface` — dual-install brand Loom
10. `loom-goal-optional-subagent` — true opt-in subagent fan-out
11. `loom-goal-trace-bundle` — driver ↔ agent_trace

User decisions: brand Loom; parallel install; no default replace beacon.

