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
promotion_ref: analysis:product-goal-domain-delivery-20260716
user_decisions:
  UD-V2-PG-001: rust_orchestrator_owns_product_goal_runtime
  UD-V2-PG-002: dual_skills_loop_vs_goal_parity_with_v167
  UD-V2-PG-003: parallel_subagent_main_star_satellite_pool
  UD-V2-PG-004: progressive_skill_load_in_operator_spine
  UD-V2-PG-005: python_compat_shim_preserves_cli_surface
---

# Program Manifest — v2 Product Goal Parallel Orchestration

## User Intent

v2 Rust kernel 实现与 v1.6.7 同构的 **Loop 发现 / Goal 完成** 双 skill，并原生支持：
并行 sub-agent、渐进 skill 加载、主星/卫星 worktree pool（一湖一卫星，合并回主星）。

## Topology

1. `beacon-v2-product-goal-orchestrator` — Goal runtime + skill progressive load + host/CLI
2. `beacon-v2-main-star-satellite-pool` — worktree pool + merge-to-star + BranchContext parity

## Upstream (v1.6.7 contracts to honor)

- beacon-product-goal-runtime-v167 R2
- beacon-loop-discover-goal-finish-v167 R2
- beacon-git-scope-graph-v167 (topology_gate)
