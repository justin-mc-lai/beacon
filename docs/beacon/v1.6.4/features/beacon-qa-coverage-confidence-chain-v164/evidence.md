---
slug: beacon-qa-coverage-confidence-chain-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-qa-coverage-confidence-chain-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：QA Coverage Confidence Chain v1.6.4

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-coverage-confidence-chain-v164/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.4/features/beacon-qa-coverage-confidence-chain-v164/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-coverage-confidence-chain-v164/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define + acceptance | truth.md | draft |
| R1 truth.coverage | tests.md | draft |

## Source refs

- program feature-graph：docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 2)
- depends_on: beacon-qa-chrome-extension-e2e-v164 (Phase 1 frozen)

## Diagnostic evidence（gap baseline）

- `build_qa_profile_completeness` 只统计 executed/skipped/blocked/missing，无层间依赖
- `coverage.py` 有 story/ac/tc metrics，无层间传递
- 无 `confidence_chain` 字段

## Implementation evidence (generator handoff)

| 项 | 值 |
|---|---|
| harness | beacon-gen-implement (Ralph round 1) |
| branch | beacon/v1.6.4/beacon-qa-chrome-extension-e2e-v164 |
| AC 覆盖 | AC-001..005 |
| contract tests | `tests/test_v164_qa_confidence_chain.py` |
| full suite | `python3 -m pytest tests/test_v164_qa_*.py -q` → 29 passed |
| changed surfaces | `beacon/utils/qa_confidence_chain.py`, `beacon/utils/qa_acceptance.py`, `beacon/utils/coverage.py`, `tests/test_v164_qa_confidence_chain.py` |
| ralph trace | docs/beacon/v1.6.4/.machine/trace/ralph/beacon-qa-coverage-confidence-chain-v164/ |
| next route | `beacon-eval-qa`（按 feature 分别验收，禁止 generator 自证 QA pass） |
