---
slug: beacon-ecosystem-discovery-sync-drift-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：Ecosystem Discovery & Sync Drift Repair v1.6.3

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md |
| tests.md | test_truth | docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/tests.md |
| tasks.md | requirement_truth | docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/tasks.md |

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

- pytest junit：`tests/test_v163_ecosystem_discovery_sync_drift.py` 7 TC，7 passed
- 实现：
  - `beacon/utils/manifest.py` sync_manifest 对 ≥v1.5.2 额外扫 `features/<slug>/`
  - `beacon/utils/material_sync.py` sync_project_requirement_materials 对 package-authoritative 调 rebuild_machine_json
  - `beacon/commands/freeze.py` _freeze_impl 调 rebuild_machine_json
- 回归：78 预存在失败均为旧包状态债（stash 对照 0 回归）
- 实测：manifest sync 自动扫到 5 包（无需手动 add-feature）；sync-materials 后 4 包 truth-map verify pass

## QA 阶段证据（qa 后追加）

- `beacon-eval-qa` verdict
