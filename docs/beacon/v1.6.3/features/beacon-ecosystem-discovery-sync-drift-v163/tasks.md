---
slug: beacon-ecosystem-discovery-sync-drift-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 任务账本：Ecosystem Discovery & Sync Drift Repair v1.6.3

## Phase A — manifest sync 扫 features/

- [x] TC-EC-001..007 测试文件 `tests/test_v163_ecosystem_discovery_sync_drift.py` 创建（7 TC）
- [x] `beacon/utils/manifest.py sync_manifest` 对 ≥v1.5.2 额外扫 `features/<slug>/`

## Phase B — sync-materials 走 rebuild

- [x] `beacon/utils/material_sync.py` sync_project_requirement_materials 对 package-authoritative 调 rebuild_machine_json
- [x] TC-EC-002 sync-materials 后无 hash stale

## Phase C — freeze 自动重物化

- [x] `beacon/commands/freeze.py _freeze_impl` 调 rebuild_machine_json
- [x] TC-EC-003 freeze 后 hash 一致

## Phase D — 回归

- [x] TC-EC-004 legacy 兼容
- [x] TC-EC-005 v1.6.2 无回归
- [x] TC-EC-006 v1.6.3 四包无回归
- [x] TC-EC-007 _discover_features 正确
- [x] 7/7 TC pass；78 预存在失败均为旧包状态债（stash 对照 0 回归）
- [x] 实测：manifest sync 自动扫到 5 包；sync-materials 后 4 包 verify pass

## checkbox 不自证 closure

checkbox 仅追踪实现进度；closure 以 tests.md 的 TC 全 pass + `beacon-eval-qa` verdict 为准。
