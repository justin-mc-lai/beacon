---
slug: beacon-freeze-integrity-drift-repair-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：Freeze Integrity Drift Repair v1.6.3

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/tasks.md |

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

- pytest junit：`tests/test_v163_freeze_integrity_drift_repair.py` 12 TC，12 passed
- 实现：
  - `beacon/utils/feature_package.py` `ALLOWED_PARSER_CONTRACTS`（v1+v2）、forbidden field key 声明 + authority 列值匹配、authority 错误 `allowed_authorities`/`required_columns`
  - `beacon/utils/truth_integrity.py` `_HARD_TEST_MARKERS_RE` 增加 pytest
- 回归：0 回归；71 预存在失败均为 v1.5.0/v1.4.x 旧包状态债（stash 对照确认）
- dogfooding 验证：两个 v1.6.3 frozen 包 + v1.6.2 包 verify-closure 全 pass

## QA 阶段证据（qa 后追加）

- `beacon-eval-qa` verdict
