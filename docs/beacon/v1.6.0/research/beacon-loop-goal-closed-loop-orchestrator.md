---
slug: beacon-loop-goal-closed-loop-orchestrator
version: v1.6.0
authority: support_advisory
status: promoted
source: user-confirmed-architecture-session
created: 2026-06-10
updated: 2026-06-10
truth_refs:
  - docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md
  - docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md
  - docs/beacon/v1.6.0/execution/boundaries.md
source_refs:
  - packages/beacon-loop/src/runner/run.ts
  - beacon/utils/planner_review_runtime.py
  - beacon/utils/intent_router.py
  - /Users/apple/Developer/Personal/oss-sync/automation/autoresearch/openspec
  - /Users/apple/Developer/Personal/oss-sync/pm/pm/spec-kit
  - /Users/apple/Developer/Personal/oss-sync/agents/agent-skills/compound-engineering-plugin
  - /Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack
evidence_refs:
  - docs/beacon/v1.6.0/change/beacon-loop-goal-closed-loop-orchestrator.md
user_decision: accepted
promotion_ref: docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md
---

# Research: Beacon Loop Goal Closed-Loop Orchestrator

## Support Advisory Contract

- authority: `support_advisory`
- status: `promoted`
- feature_slug: `beacon-loop-goal-closed-loop-orchestrator`
- prd_refs: docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md
- user_story_refs: docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md
- test_case_refs: docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md
- coverage_notes: AC-031..AC-039 map to TC-031..TC-039; parent AC-003..AC-005, AC-016, AC-021..AC-022, AC-025 map to TC-034/TC-040/TC-041 regression and integration coverage; AC-001..AC-030 bulk regression via TC-040.
- out_of_scope_notes: No new public lifecycle stage; loop does not write package truth or formal QA/release verdicts; parent feature remains frozen; parallel review lanes (D-009) deferred to Phase H.
- outcome: 将 `beacon-loop goal "<utterance>"` 升级为 Delivery Orchestrator：原话意图 → 自动 review → truth 补齐 → implement loop → qa → release，且不漂移、不自证 verdict。
- lake_or_ocean: 海。触及 intent engine、planner subprocess、generator truth_fill 编排、delivery state machine、evaluator 回灌、与 parent runner 的状态合成。
- truth_gap: 本 research 已晋升为 `features/.../truth.md` 草案；冻结前不得作为 implementation closure authority。
- recommended_route: `beacon-gen-change` → refreeze → `beacon-gen-implement` Phase E-H

## Decision Summary

```text
beacon-loop goal "<utterance>"
  → intent_capture + intent_contract (deterministic)
  → planner_review_runtime (multi-agent, runtime evidence only)
  → truth_gap_scan → truth_fill (beacon gen-* CLI) → freeze gate
  → implement_loop (parent orchestrator)
  → import_evidence → beacon qa → beacon release
  → terminal_closed (Beacon evaluator only)
```

## OSS Pattern Borrowing

| Source | Borrow |
|--------|--------|
| OpenSpec | change delta + specs 单真值；CLI 治理 delivery-state |
| Spec Kit | phase-gated truth 补齐顺序 |
| Compound | reviewer lanes + finding synthesis + autofix route |
| gstack | plan/execute 分离；scope 模式；delivery vs review-only |
| manage-oss-sync | query/show/diagnose 分桶（parent AC-022..023） |

## Non-goals

- 替代 Beacon truth-map resolver
- loop 直接写 `features/*/truth.md`
- loop 产出 QA pass / release ready verdict
- 新增 Beacon 主生命周期 stage
