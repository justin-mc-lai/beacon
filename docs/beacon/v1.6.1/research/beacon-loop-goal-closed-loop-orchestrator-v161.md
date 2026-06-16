---
feature_slug: beacon-loop-goal-closed-loop-orchestrator-v161
version: v1.6.1
authority: support_advisory
promotion_ref: docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md
---

# Research: Beacon Loop Goal Closed-Loop Orchestrator v1.6.1

## outcome

v1.6.1 统一长任务入口 `beacon-loop goal`、湖/海 scope 分类、海级 program 外层 FSM（P0–P6）、opt-in eval supplement；upstream v1.6.0 loop R10 frozen 不 reopen。

## lake_or_ocean

**湖**（本 package）；运行时面向 **湖 | 海** utterance。

## truth_refs

- `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`（frozen R10）
- `docs/beacon/v1.6.1/features/beacon-harness-program-plan-v161/truth.md`（R3 program handoff）
- `docs/beacon/v1.6.1/features/beacon-agent-eval-v161/truth.md`（eval supplement）

## source_refs

- 对话：路线 A — v1.6.1 + pre-main；不在 v1.6.0 开 R11
- Planner review：`pln-review-20260616t023732z`
- 详细 closure：`docs/beacon/v1.6.1/research/beacon-loop-goal-closed-loop-orchestrator.md`

## user_decision

promoted

## promotion_ref

`docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md`

## prd_refs

docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md

## user_story_refs

docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md

## test_case_refs

docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/tests.md

## coverage_notes

v1.6.1 delta AC-072..075；AC-031/068/069/071 由 upstream v1.6.0 R10 覆盖（tests 标注 upstream-delegated）。

## out_of_scope_notes

不 reopen v1.6.0 loop package；不新增主 lifecycle stage。
