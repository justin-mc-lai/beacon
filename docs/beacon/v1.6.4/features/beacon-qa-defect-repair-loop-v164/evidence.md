---
slug: beacon-qa-defect-repair-loop-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-qa-defect-repair-loop-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：QA Defect Repair Loop v1.6.4

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-defect-repair-loop-v164/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.4/features/beacon-qa-defect-repair-loop-v164/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-defect-repair-loop-v164/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define + acceptance | truth.md | draft |
| R1 truth.coverage | tests.md | draft |

## Source refs

- program feature-graph：docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 4)
- depends_on: beacon-qa-coverage-confidence-chain-v164 + beacon-qa-business-state-machine-v164 (Phase 2/3 frozen)

## Diagnostic evidence（gap baseline）

- `ROUTE_RECOMMENDATIONS` (qa_attribution.py) 已有单向路由：implementation_gap→implement, truth_drift→change, coverage_gap→test-case, execution_lapse→qa, skill_defect→change, runner_admission_blocker→blocked, evidence_insufficient→qa
- `RELEASE_BLOCKING_FAMILIES` = {implementation_gap, truth_drift, coverage_gap}
- 缺：repair_route/defect_classification 字段、修复后回归 QA 触发、闭环 evidence 链

## Implementation/QA evidence

由下游 `beacon-gen-implement` / `beacon-eval-qa` 阶段填充（truth 阶段不留 placeholder）。
