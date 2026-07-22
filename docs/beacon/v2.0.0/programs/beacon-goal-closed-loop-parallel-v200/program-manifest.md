---
program_slug: beacon-goal-closed-loop-parallel-v200
version: v2.0.0
plan_mode: interactive
status: support_advisory
brand: Loom
authority: beacon-plan
research_ref: docs/beacon/v2.0.0/research/goal-closed-loop-program-parallel-subagent-pln.md
related_program: beacon-v2-product-goal-parallel-v200
---

# Program Manifest — Goal Closed-Loop Parallel (v2.0.0 / Loom)

## Intent

同 v1.6.9：Goal 内 program 图驱动并行子代理闭环。实现上 **强化既有湖** 优先于新建 slug。

## Lakes (strengthen existing)

| Lake | Action |
|------|--------|
| beacon-v2-product-goal-orchestrator | graph → parallel_plan.v2 |
| beacon-v2-main-star-satellite-pool | merge 真落地 |
| loom-goal-optional-subagent | ready_set spawn 真执行 |
| beacon-v2-goal-durable-longrun | 边界：单湖长跑 ≠ 多湖并行 |
| loom-git-worktree-implement-harness | leaf admit 执行卫生 |

## Non-Goals

- multi-version ops as default
- replace beacon-v2-product-goal-parallel-v200 entirely (compose, don't fork)

## Next

User ack → beacon-gen-change on the three strengthen lakes + axis regenerate.
