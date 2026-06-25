---
slug: beacon-gate-truth-model-alignment-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 任务账本：Gate Truth Model Alignment v1.6.3

## Phase A — 实现 check_formal_version_package_closure 分流

- [x] TC-GT-001..007 测试文件 `tests/test_v163_gate_model_alignment.py` 创建
- [x] `beacon/commands/gate.py:2308` 加 semver 分流：`<v1.5.2` 走原契约，`≥v1.5.2` 走 feature 包闭环
- [x] 新 reason_code `feature_package_closure_missing`（≥v1.5.2 无 feature 包时）
- [x] version-line 材料（SUMMARY/execution/boundaries/source-architecture/release）校验保留

## Phase B — review.py 同步

- [x] N/A：`beacon/commands/review.py:747` 走 `build_material_audit`，非同一硬编码，无需同步

## Phase C — 回归验证

- [x] AC-006 本项目 v1.6.2 gate check release 不再因顶层目录 block（closure 检查 0 issues）
- [x] AC-003 v1.4.10 旧版本契约不 break（TC-GT-003 pass）
- [x] 7/7 TC pass；65 个现有 gate 测试无回归
- [x] release gate blocked_count 65 → 4（P0-3 blocker 消除）

## checkbox 不自证 closure

checkbox 仅追踪实现进度；closure 以 tests.md 的 TC 全 pass + `beacon-eval-qa` verdict 为准。
