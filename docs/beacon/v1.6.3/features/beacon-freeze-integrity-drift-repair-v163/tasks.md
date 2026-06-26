---
slug: beacon-freeze-integrity-drift-repair-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 任务账本：Freeze Integrity Drift Repair v1.6.3

## Phase A — parser_contract 单一源

- [x] TC-FI-001..003 测试文件 `tests/test_v163_freeze_integrity_drift_repair.py` 创建
- [x] `beacon/utils/feature_package.py:448` 接受 resolver 声明的 v1/v2（`ALLOWED_PARSER_CONTRACTS`），未知版本仍 mismatch

## Phase B — forbidden field 词边界

- [x] TC-FI-010..011
- [x] `beacon/utils/feature_package.py` forbidden field 改为 key 声明（`field:`）+ authority 列值匹配，不再子串误伤

## Phase C — hard markers + integration

- [x] TC-FI-020..021
- [x] `beacon/utils/truth_integrity.py:60` `_HARD_TEST_MARKERS_RE` 增加 pytest
- [x] integration 行有 hard command 时不判软（复用现有 `_HARD_TEST_MARKERS_RE.search(line)`）

## Phase D — 错误自描述

- [x] TC-FI-030..031
- [x] `beacon/utils/feature_package.py` authority 错误 diagnostics 含 `allowed_authorities` + `required_columns`

## Phase E — 回归

- [x] TC-FI-040 v1.6.2 包兼容（verify-closure pass）
- [x] TC-FI-050 P0-3 包无回归（verify-closure pass）
- [x] TC-FI-060 真实违规仍 block（TC-FI-060 pass）
- [x] 12/12 TC pass；v150 gate_truth 语义保持；0 回归（71 预存在失败均为旧包状态债）

## checkbox 不自证 closure

checkbox 仅追踪实现进度；closure 以 tests.md 的 TC 全 pass + `beacon-eval-qa` verdict 为准。
