---
slug: beacon-gate-truth-model-alignment-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：Gate Truth Model Alignment v1.6.3

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/archive/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md |
| tests.md | test_truth | docs/beacon/archive/v1.6.3/features/beacon-gate-truth-model-alignment-v163/tests.md |
| tasks.md | requirement_truth | docs/beacon/archive/v1.6.3/features/beacon-gate-truth-model-alignment-v163/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define | truth.md | draft |
| R1 truth.coverage | tests.md | draft |
| R4 weak-assertion 扫描 | soft_tc_scan | pass |
| R5 deferral 扫描 | deferral_scan | pass |
| R5 verify-closure | closure_allowed | pass |
| R6 sync-requirement-clarity | blocked | none |
| R7 freeze | status | frozen |

## Implement 阶段证据（已发生）

- pytest junit：`tests/test_v163_gate_model_alignment.py` 7 TC，7 passed
- 实现：`beacon/commands/gate.py` `check_formal_version_package_closure` semver 分流 + `_PACKAGE_AUTHORITATIVE_CUTOVER=(1,5,2)` 常量
- 回归：65 个现有 gate 测试无 break
- v1.6.2 回归：release gate `formal_package_closure_missing` 顶层目录阻断消除；blocked_count 65 → 4

## QA 阶段证据（qa 后追加）

- `beacon-eval-qa` verdict
