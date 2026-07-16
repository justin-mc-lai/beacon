---
feature_slug: beacon-harness-program-plan-v161
version: v1.6.1
authority: support_advisory
promotion_ref: docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md
---

# Research: Beacon Harness Program Plan v1.6.1

## outcome

定义版本级「书籍真相」program harness：海级 utterance（如完整复刻 OSS）→ program 目录/大纲/feature 湖切分 → 每湖 gen-truth 七轮煮干 → program freeze gate；change 时 plan review + 保留 change 意图 + refreeze。

## lake_or_ocean

**海**（program 运行时面向海级 utterance）；本 feature package 自身为 **湖**（冻结 harness 契约）。

## truth_refs

- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md`
- `docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md`
- `docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md`
- `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`

## source_refs

- 对话上下文：OSS 一句话复刻、湖海、书籍目录章节、LLM 防糊弄治理、change 闭环

## evidence_refs

- v1.6.0 TIG + Truth Freeze Intent Loop 七轮

## truth_gap

v1.6.1 此前无 program 级 artifact；本 research promote 至 feature package。

## test_gap

tests.md 映射 AC-PBP-001..028；Phase B–F CLI 用 BLOCKED 标注直至实现。

## implementation_risk

- 假 inventory 若全自动抽取
- program freeze 与多湖 TIG 汇总复杂度

## verification_risk

- maker-checker 需 machine-readable 每湖 frozen 证据

## recommended_route

truth.define → TIG → freeze → Phase B–F implement

## user_decision

promoted

## promotion_ref

`docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md`

## Version Projection Truth Binding

- prd_refs: docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md
- user_story_refs: docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md
- test_case_refs: docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/tests.md
- coverage_notes: AC-PBP-001..030 map TC-PBP-001..030；Phase B–G integration 允许 BLOCKED:Phase-* 直至 CLI/FSM 落地；R3 收紧 AC-PBP-016、新增 AC-PBP-029/030。
- out_of_scope_notes: 不实现被复刻 OSS 产品代码；PB-001..003 为 Phased Backlog；program artifact 须 promote 才成 package truth。

## Decision Summary

```text
utterance (full_parity + source URL)
  → program_intent_capture
  → program_plan P0–P4 (inventory, module-map, feature-graph, user ack)
  → for each lake (topo): pln-review → gen-truth rounds 0–7 → TIG → freeze
  → program_freeze_gate
  → beacon-run generate/evaluate per lake

change utterance
  → change-intent-log
  → beacon-gen-change + pln-review + promotion_diff
  → user ack → update graph or single-lake truth → refreeze + TIG
```
