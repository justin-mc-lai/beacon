---
slug: beacon-truth-format-package-auth-skip-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 修复 truth_format 校验与 feature paths 对 package-authoritative 的连环漂移（C 方向）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md
  user_story: docs/beacon/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md
  test_case: docs/beacon/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Truth Format Package-Auth Skip v1.6.3

## 概述

`beacon-truth-format-package-auth-skip-v163` 修复一组连环漂移：legacy `truth_format` 校验器（v1.4.12 引入，针对 prd/user-story/test-case 旧模型）被错误地套用到 package-authoritative（≥v1.5.2）feature 包上，且被 `compute_feature_paths` 返回旧路径、manifest status 误判两处裂缝**自我掩盖**——旧路径不存在导致校验跳过→假 pass。修路径会激活校验→所有 package-auth 包 fail。

**4 处连环裂缝：**

1. **`compute_feature_paths` 返回旧路径** — `beacon/utils/manifest.py:63` 对所有版本返回 `prd/<slug>.md`、`user-story/<slug>.md`、`qa/test-cases/<slug>.md`，但 ≥v1.5.2 truth 在 `features/<slug>/{truth,tests,tasks,evidence}.md`。manifest 的 truth_paths 指向不存在的旧路径。
2. **manifest status 误判为 template** — `sync_manifest:248` 从 `.machine/requirement/<slug>.freeze-state.json` 读 status，但 package-auth 包无此文件（frozen 状态在 truth.md frontmatter `status: frozen`）。导致所有 package-auth 包 manifest status 恒为 `template`。
3. **truth_format 校验器要求旧格式** — `beacon/utils/truth_format.py:287 validate_test_case_format` 要求 `Outline/Coverage Matrix/Explicit Non Coverage` 章节 + `Planned Command`/`Evidence Path` 列 + `Feature/Status/Date/Language` frontmatter。package-auth 的 tests.md 用不同格式（`覆盖矩阵` + `Command/Assertion` 列 + `slug/version/status` frontmatter），过不了。
4. **校验靠"路径不存在"跳过** — `material_audit.py:1083 if _path.exists()`：旧路径不存在→校验跳过→假 pass。修裂缝1会激活裂缝3，所有 package-auth 包 fail。

**根因**：legacy `truth_format` 校验器是 v1.4.12 prd/user-story/test-case 模型的产物，package-authoritative 模型有自己的格式校验（`feature_package.validate_feature_package` + `verify-closure`，已用且 package-auth 包都过）。legacy 校验器不应套用到 package-auth 版本——正如 P0-3 `formal_package_closure` 对 ≥v1.5.2 改用 feature 包校验。

**P0 交付（Must，C 方向）：**

1. **compute_feature_paths 对 package-auth 返回 features/ 路径** — ≥v1.5.2 版本 truth_paths 指向 `features/<slug>/{truth,tests}.md`。
2. **manifest status 从 truth.md frontmatter 读** — package-auth 包 status 取自 `truth.md` frontmatter `status`，非 freeze-state.json。
3. **truth_format 校验对 package-auth 跳过** — `material_audit.py` truth_format 校验对 ≥v1.5.2 版本跳过（package-auth 用 `feature_package.validate` 替代）；<v1.5.2 保持原校验。
4. **不删 legacy truth_format 校验器** — 旧版本仍用，仅对 package-auth 版本跳过。

**不**改 package-authoritative 模型语义；**不**删 `truth_format.py`；**不**新增 lifecycle stage。

## User Intent（一行）

legacy truth_format 校验对 package-authoritative 版本跳过（由 feature_package.validate 替代），feature paths 与 manifest status 对齐 features/ 模型，消除路径-校验连环掩盖，让 package-auth 包格式校验走正确的 feature_package.validate 通道。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | truth_format 旧校验被路径错误掩盖，修路径会激活旧校验全 fail，应对 package-auth 跳过 legacy 校验，走 feature_package.validate |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`legacy_validator_package_auth_skip`** |
| 强度词 | 跳过 legacy、走 feature_package.validate、路径对齐、status 从 frontmatter、不删 |
| 非协商边界 | legacy truth_format 校验器**不**删（旧版本用）；package-auth 模型语义**不**改 |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | compute_feature_paths 分流 | ≥v1.5.2 truth_paths 指向 `features/<slug>/{truth,tests,tasks,evidence}.md`；<v1.5.2 保持旧路径 |
| UD-002 | manifest status 来源 | package-auth 包 status 取自 `truth.md` frontmatter `status`；无 frontmatter 默认 template |
| UD-003 | truth_format 跳过 | `material_audit.py` truth_format 校验对 ≥v1.5.2 版本跳过；<v1.5.2 保持 |
| UD-004 | 替代校验 | package-auth 格式校验由 `feature_package.validate_feature_package` + `verify-closure` 承担（已存在） |
| UD-005 | 不删 legacy | `truth_format.py` 及其校验器保留，旧版本仍用 |
| UD-006 | 实现位置 | `beacon/utils/manifest.py` + `beacon/utils/material_audit.py` |

## Problem Statement

| 现象 | 根因 |
|------|------|
| package-auth 包 manifest truth_paths 指向不存在旧路径 | compute_feature_paths 不分流 |
| package-auth 包 manifest status 恒 template | sync_manifest 读 freeze-state.json，package-auth 无此文件 |
| 修路径后 package-auth 包 truth_format 全 fail | legacy 校验器要求旧格式，被路径错误掩盖 |
| v1.6.2 假 pass | 路径不存在→校验跳过 |

## Non-Goals

- 删除或重写 truth_format.py legacy 校验器
- 改 feature_package.validate_feature_package 逻辑
- 改 package-authoritative tests.md 格式规范
- 重构 manifest.py / material_audit.py god-file

## 受影响代码面

| 位置 | 当前 | 目标 |
|------|------|------|
| `beacon/utils/manifest.py:63 compute_feature_paths` | 所有版本旧路径 | ≥v1.5.2 返回 features/ 路径 |
| `beacon/utils/manifest.py:248 sync_manifest status` | 读 freeze-state.json | package-auth 读 truth.md frontmatter |
| `beacon/utils/material_audit.py:1064 truth_format 校验` | ≥v1.4.12 全校验 | ≥v1.5.2 跳过 |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | feature-paths-package-auth | `compute_feature_paths` 对 ≥v1.5.2 返回 `features/<slug>/{truth,tests}.md` 路径（**Must**） |
| AC-002 | manifest-status-from-frontmatter | package-auth 包 manifest status 取自 truth.md frontmatter `status`（frozen 包显示 frozen）（**Must**） |
| AC-003 | truth-format-skip-package-auth | `build_requirement_package_gate` 对 ≥v1.5.2 包不报 `truth_format_non_compliant_*`（**Must**） |
| AC-004 | legacy-truth-format-preserved | <v1.5.2 版本 truth_format 校验行为不变（**Must**） |
| AC-005 | implement-qa-unblocked-format | v1.6.3 frozen 包 `implement run`/`qa run` 不再因 `truth_format_non_compliant` blocked（**Must**） |
| AC-006 | no-regression-v162 | v1.6.2 包修复后 `build_requirement_package_gate` 仍 pass（不因路径修复而 break）（**Must**） |
| AC-007 | feature-package-validate-still-runs | package-auth 包仍经 `feature_package.validate_feature_package` 校验（未绕过真校验）（**Must**） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | manifest.py / material_audit.py god-file 拆分 | 另开技术债 feature |
| DEF-002 | truth_format.py legacy 校验器的废弃时间表 | 另开 feature |
| DEF-003 | package-auth tests.md 格式规范的正式文档 | 另开 feature |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | 跳过 legacy truth_format，不删（UD-005） |
| OQ-002 | package-auth 由 feature_package.validate 替代（UD-004） |
| OQ-003 | manifest status 从 truth.md frontmatter，不另建 freeze-state（UD-002） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 4–7 煮干后 freeze。
