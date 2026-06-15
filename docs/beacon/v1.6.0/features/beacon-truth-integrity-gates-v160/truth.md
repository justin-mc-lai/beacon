---
slug: beacon-truth-integrity-gates-v160
version: v1.6.0
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md
  user_story: docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md
  test_case: docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：Beacon Truth Integrity Gates v1.6.0

## 概述

`beacon-truth-integrity-gates-v160` 在 v1.6.0 冻结/refreeze 路径上引入 **Truth Integrity Gate（TIG）**，统一阻断占位 AC、软 TC、未拍板 deferral、假交付语义与 feature package validation 失败。

`scope_mode` = smoke（本包为治理内核，非海级 feature）。

## User Intent（一行）

冻结前必须由机器 gate 证明 feature package 可执行闭环，禁止占位 truth 进入 frozen baseline。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-TIG-001 | 单一阻断源 | `build_truth_integrity_gate` 为 `beacon freeze` 与 `change_refreeze` 冻结前唯一 hard block 源（含 clarity + fake_delivery + package validation）。 |
| AC-TIG-002 | 占位检测 | 占位 AC、软 TC、未拍板 deferral 必须产生带 `repair_route` 的 line-level findings。 |
| AC-TIG-003 | verify-closure 对齐 | `beacon skill package verify-closure` 与 TIG `fake_delivery` 切片结果一致。 |
| AC-TIG-004 | prose AC | prose AC 与 hardened tests 可通过 `validate_feature_package`（不再仅认 AC 表格）。 |
| AC-TIG-005 | 金样例 pytest | `tests/test_truth_integrity.py` 覆盖好包 pass、坏包 block（≥6 fixtures）。 |

## 边界

- 已 frozen 历史包默认 `--mode audit` 只报告不阻断；新冻/refreeze 走 `mode=block`。
- TIG 不替代 formal QA/release verdict。
