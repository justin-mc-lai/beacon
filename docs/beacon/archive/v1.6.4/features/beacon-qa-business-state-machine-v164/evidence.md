---
slug: beacon-qa-business-state-machine-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.4/features/beacon-qa-business-state-machine-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：QA Business State Machine v1.6.4

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/archive/v1.6.4/features/beacon-qa-business-state-machine-v164/truth.md |
| tests.md | test_truth | docs/beacon/archive/v1.6.4/features/beacon-qa-business-state-machine-v164/tests.md |
| tasks.md | requirement_truth | docs/beacon/archive/v1.6.4/features/beacon-qa-business-state-machine-v164/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define + acceptance | truth.md | draft |
| R1 truth.coverage | tests.md | draft |

## Source refs

- program feature-graph：docs/beacon/archive/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 3)
- depends_on: beacon-qa-coverage-confidence-chain-v164 (Phase 2 frozen, confidence_chain interface)

## Diagnostic evidence（gap baseline）

- state_machine reviewer 仅在 planner 层（qa_evo_deep / planner_review_runtime），qa 层无 FSM 提取
- 无 state_machine_coverage 字段
- 无 truth→FSM→边界用例 管道

## Implementation evidence (generator handoff)

| 项 | 值 |
|---|---|
| harness | beacon-gen-implement (Ralph round 1) |
| branch | beacon/v1.6.4/beacon-qa-chrome-extension-e2e-v164 |
| AC 覆盖 | AC-001..006 |
| contract tests | `tests/test_v164_qa_business_state_machine.py` |
| full suite | `python3 -m pytest tests/test_v164_qa_*.py -q` → 29 passed |
| changed surfaces | `beacon/utils/qa_state_machine.py`, `beacon/utils/qa_acceptance.py`, `beacon/utils/coverage.py`, `tests/test_v164_qa_business_state_machine.py` |
| ralph trace | docs/beacon/archive/v1.6.4/.machine/trace/ralph/beacon-qa-business-state-machine-v164/ |
| next route | `beacon-eval-qa`（按 feature 分别验收，禁止 generator 自证 QA pass） |
