---
slug: beacon-ecosystem-discovery-sync-drift-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 修复 feature 发现与 .machine 同步的 3 处生态漂移（闭环 v1.6.3 时暴露）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md
  user_story: docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md
  test_case: docs/beacon/archive/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Ecosystem Discovery & Sync Drift Repair v1.6.3

## 概述

`beacon-ecosystem-discovery-sync-drift-v163` 修复 Beacon 免疫系统生态的 3 处漂移。这些漂移在闭环 v1.6.3 release 时暴露——feature 包能冻结、能验证，但**管线发现不了、同步不对、freeze 后不重物化**，导致每个新 feature 都要手动 workaround。与 P0-3（gate 检查器）同类：旧 truth 模型残留，未随 package-authoritative 迁移。

**3 处漂移：**

1. **`manifest sync` 不扫 package-authoritative 路径** — `beacon/utils/manifest.py:222 sync_manifest` 只扫 `("prd", "user-story", "qa/test-cases")` 旧目录，不扫 `features/<slug>/`。v1.5.2+ feature 包在 `features/` 下，sync 永远返回 0 features，需手动 `add-feature`。`_discover_features`（material_sync.py:23）同样依赖 manifest，连锁失效。

2. **`sync-materials` 不重算 source hash** — `doctor_registry.py:153 _materials_sync` → `sync_project_requirement_materials` → `sync_feature_requirement_materials`（legacy 分支，不调 `rebuild_machine_json`）。而 `sync_change_loop_requirement_materials:175` 才调 rebuild。`beacon doctor sync-materials` 命令走前者，写出的 `.machine` source hash 过期，`truth-map verify` 报 `machine_json_source_hash_stale`。需直接 `rebuild_machine_json` 才对。

3. **freeze 后改 truth 不自动重物化 .machine** — `beacon/commands/freeze.py` freeze 时调 `materialize_revision_delta` 但**不调 `rebuild_machine_json`**。freeze 后若 truth/tests 内容变更（如修 parser_contract），`.machine` 镜像 hash 过期，无自动同步，需手动 rebuild。

**P0 交付（Must）：**

1. **manifest sync 扫 features/** — `sync_manifest` 对 v1.5.2+ 版本额外扫 `features/<slug>/` 目录，发现 package-authoritative feature 包。
2. **sync-materials 走 rebuild** — `_materials_sync`/`sync_project_requirement_materials` 对 package-authoritative 版本调 `rebuild_machine_json`，写出正确 source hash。
3. **freeze 自动重物化** — `freeze` 完成后调 `rebuild_machine_json`，保证 `.machine` 镜像与 frozen truth hash 一致。

**不**改 package-authoritative 模型语义；**不**删 legacy 扫描（旧版本兼容）；**不**新增 lifecycle stage。

## User Intent（一行）

feature 发现与 .machine 同步对齐 package-authoritative 模型：manifest sync 扫 features/、sync-materials 走 rebuild、freeze 后自动重物化，让每个新 feature 无需手动 workaround 即可被管线识别与验证。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | 闭环 v1.6.3 时 manifest sync 扫不到 feature、sync-materials hash 过期、freeze 后 .machine 不同步，需修这 3 处生态裂缝 |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`discovery_sync_model_alignment`** |
| 强度词 | 扫 features/、走 rebuild、自动重物化、无需 workaround |
| 非协商边界 | legacy 扫描**不**删（旧版本兼容）；package-authoritative 模型语义**不**改 |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | manifest sync 扫 features/ | `sync_manifest` 对 ≥v1.5.2 版本额外扫 `features/<slug>/`，发现 package-authoritative 包 |
| UD-002 | sync-materials 走 rebuild | `_materials_sync`/`sync_project_requirement_materials` 对 package-authoritative 版本调 `rebuild_machine_json` |
| UD-003 | freeze 自动重物化 | `freeze` 完成后调 `rebuild_machine_json`，`.machine` hash 与 frozen truth 一致 |
| UD-004 | legacy 兼容 | <v1.5.2 版本保持原扫描/sync 行为不变 |
| UD-005 | 实现位置 | `beacon/utils/manifest.py` + `beacon/utils/material_sync.py` + `beacon/commands/freeze.py` |
| UD-006 | 不改模型 | package-authoritative 模型语义、feature_paths 计算不变 |

## Problem Statement

| 现象 | 根因 |
|------|------|
| `manifest sync` 返回 0 features | `:222` 只扫旧目录，不扫 features/ |
| `sync-materials` 后 hash 仍 stale | 走 legacy 分支不 rebuild |
| freeze 后改 truth，.machine 过期 | freeze 不调 rebuild_machine_json |
| 每个新 feature 需手动 add-feature + rebuild | 3 处漂移连锁 |

## Non-Goals

- 重构 manifest.py / material_sync.py god-file
- 改 `rebuild_machine_json` 内部逻辑
- 修复 P0-1/P0-2/P0-3（已修）
- 改 feature_paths / package_paths 计算

## 受影响代码面

| 位置 | 当前 | 目标 |
|------|------|------|
| `beacon/utils/manifest.py:222 sync_manifest` | 只扫 prd/user-story/qa-test-cases | ≥v1.5.2 额外扫 features/<slug>/ |
| `beacon/utils/material_sync.py:139 sync_project_requirement_materials` | 调 legacy sync_feature_requirement_materials | package-authoritative 版本调 rebuild_machine_json |
| `beacon/commands/freeze.py _freeze_impl` | 不调 rebuild_machine_json | freeze 后调 rebuild_machine_json |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | manifest-sync-discovers-features | `manifest sync` 对 ≥v1.5.2 版本扫到 `features/<slug>/` 下的 feature 包，无需手动 add-feature（**Must**） |
| AC-002 | sync-materials-rebuilds-hash | `beacon doctor sync-materials` 后 `truth-map verify` 无 `machine_json_source_hash_stale`（**Must**） |
| AC-003 | freeze-rebuilds-machine | `beacon freeze` 后 `.machine` source hash 与 frozen truth 一致，`truth-map verify` pass（**Must**） |
| AC-004 | legacy-compat | <v1.5.2 版本 manifest sync / sync-materials 行为不变（**Must**） |
| AC-005 | no-regression-v162 | v1.6.2 已有 feature 包修复后仍 pass（**Must**） |
| AC-006 | no-regression-v163-packages | v1.6.3 四个已 frozen 包修复后 truth-map verify pass（**Must**） |
| AC-007 | discover-features-material-sync | `_discover_features`（material_sync）对 ≥v1.5.2 经 manifest 正确发现 features/ 包（**Must**） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | manifest.py / material_sync.py god-file 拆分 | 另开技术债 feature |
| DEF-002 | sync-materials 走 rebuild 的性能（大版本多 feature） | 另开 feature（当前正确性优先） |
| DEF-003 | freeze 后 .machine 重物化的增量同步 | 另开 feature |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | manifest sync 额外扫 features/，不删 legacy 扫描（UD-001/004） |
| OQ-002 | sync-materials 走 rebuild，不保留 legacy hash 写法（UD-002） |
| OQ-003 | freeze 自动重物化，不另开命令（UD-003） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 4–7 煮干后 freeze。
