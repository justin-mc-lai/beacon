---
slug: beacon-qa-business-state-machine-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-qa-business-state-machine-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：QA Business State Machine v1.6.4

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-business-state-machine-v164/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.4/features/beacon-qa-business-state-machine-v164/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-business-state-machine-v164/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define + acceptance | truth.md | draft |
| R1 truth.coverage | tests.md | draft |

## Source refs

- program feature-graph：docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 3)
- depends_on: beacon-qa-coverage-confidence-chain-v164 (Phase 2 frozen, confidence_chain interface)

## Diagnostic evidence（gap baseline）

- state_machine reviewer 仅在 planner 层（qa_evo_deep / planner_review_runtime），qa 层无 FSM 提取
- 无 state_machine_coverage 字段
- 无 truth→FSM→边界用例 管道

## Implementation/QA evidence

由下游 `beacon-gen-implement` / `beacon-eval-qa` 阶段填充（truth 阶段不留 placeholder）。
