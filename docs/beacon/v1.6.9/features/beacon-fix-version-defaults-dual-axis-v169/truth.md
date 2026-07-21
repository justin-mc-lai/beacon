---
slug: beacon-fix-version-defaults-dual-axis-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO: dual-axis version — runtime screwdriver vs project docs serial; greenfield v0.0.1; record in global-boundaries"
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
ux_required: false
design_deferral: "CLI/runtime + global-boundaries; no product UI"
---

## 人话

Runtime=螺丝刀型号；项目交付线=工件编号。新项目从 v0.0.1 起，不从 Beacon v1.6.9 起。

## UD

| ID | Value |
|----|-------|
| UD-VER-AXIS-001 | 强制双轴 runtime_version ≠ project_docs_version |
| UD-VER-EXT-001 | external greenfield 无版本 → v0.0.1 |
| UD-VER-EXT-002 | external existing 无版本新功能 → 相对**项目**基线 patch+1 |
| UD-VER-SELF-001 | monorepo self 才可用 toolkit planning/patch 规则 |
| UD-VER-HF-001 | hotfix baseline=项目生产基线；self 才用 current_runtime_release_line |
| UD-VER-003 | 禁止 silent major/minor bump |
| UD-VER-NORM-001 | 写入 global-boundaries 永久原则，防再跑偏 |

## AC

| ID | Description |
|----|-------------|
| AC-AXIS-001 | classify_project: beacon_self / external_greenfield / external_existing |
| AC-AXIS-002 | empty tmp project → default_target v0.0.1 |
| AC-AXIS-003 | external with docs v0.2.3 → default_target v0.2.4 |
| AC-AXIS-004 | beacon_self monorepo → not forced to v0.0.1 |
| AC-AXIS-005 | hotfix external uses project baseline not toolkit when project release known |
| AC-AXIS-006 | global-boundaries contains dual-axis principle |
| AC-AXIS-007 | skill version-default + beacon-goal text match dual-axis |
| AC-AXIS-008 | dual package v169+v200 |

## Non-goals

- 改变 toolkit 自身 semver 发布节奏
- 自动创建 git tag
