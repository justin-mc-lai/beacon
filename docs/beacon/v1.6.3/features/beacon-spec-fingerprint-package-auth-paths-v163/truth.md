---
slug: beacon-spec-fingerprint-package-auth-paths-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 修复 spec fingerprint 对 package-authoritative 包只反映 test_case 层的路径残留
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/truth.md
  user_story: docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/truth.md
  test_case: docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Spec Fingerprint Package-Auth Paths v1.6.3

## 概述

`beacon-spec-fingerprint-package-auth-paths-v163` 修复 spec fingerprint 对 package-authoritative（≥v1.5.2）包的路径残留：`_find_layer_files`（`beacon/utils/v110_baseline.py:20`）只扫 legacy `user-story/`、`prd/`、`qa/test-cases/` 目录，不扫 `features/<slug>/`。

**后果**：package-auth 包的 fingerprint `user_story`/`prd` 层 count=0、hash 为空——spec fingerprint 只反映 `test_case` 层（`.machine/qa/*.ac-test-matrix.json`），**忽略 truth.md/tests.md 主体内容**。这意味着：
- truth.md 改动不改变 fingerprint（只要 test_case matrix 不变）→ spec_impl_drift 检测对 truth 漂移失效
- fingerprint 不能真实代表 package-auth 包的需求真相状态

**根因**：与 P0-3 / truth-format-skip 同类——legacy 路径假设未随 package-authoritative 模型迁移。`_find_layer_files` 是 v1.1.0 引入的 fingerprint 层文件发现，仍用旧目录。

**P0 交付（Must）：**

1. **`_find_layer_files` 对 package-auth 扫 features/** — ≥v1.5.2 版本 user_story 层扫 `features/<slug>/truth.md`，prd 层扫 `features/<slug>/truth.md`（package-auth truth.md 承担 prd+user_story 角色），test_case 层扫 `features/<slug>/tests.md` + 保留 `.machine/qa/*.ac-test-matrix.json`。
2. **fingerprint 反映 truth/tests 主体** — package-auth 包 fingerprint 的 user_story/prd/test_case 层 count>0，truth.md 改动改变 fingerprint。
3. **legacy 兼容** — <v1.5.2 版本 `_find_layer_files` 行为不变。

**不**改 `generate_spec_fingerprint` 的 hash 算法；**不**改 fingerprint schema；**不**新增 lifecycle stage。

## User Intent（一行）

spec fingerprint 对 package-authoritative 包扫描 features/<slug>/truth.md 与 tests.md，让 fingerprint 真实反映 truth 主体内容，使 spec_impl_drift 检测对 truth 漂移有效。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | _find_layer_files 只扫旧目录，package-auth 包 fingerprint 忽略 truth 主体，spec drift 检测失效，需扫 features/ |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`fingerprint_layer_path_alignment`** |
| 强度词 | 扫 features/、反映 truth 主体、drift 检测有效、legacy 兼容 |
| 非协商边界 | hash 算法**不**改；fingerprint schema**不**改；legacy 兼容 |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | user_story 层 | ≥v1.5.2 扫 `features/<slug>/truth.md`；<v1.5.2 扫 `user-story/<slug>.md` |
| UD-002 | prd 层 | ≥v1.5.2 扫 `features/<slug>/truth.md`（package-auth truth.md 承担 prd 角色）；<v1.5.2 扫 `prd/<slug>.md` |
| UD-003 | test_case 层 | ≥v1.5.2 扫 `features/<slug>/tests.md` + 保留 `.machine/qa/*.ac-test-matrix.json`；<v1.5.2 保持 |
| UD-004 | hash 算法不变 | `generate_spec_fingerprint` 的 sha256(merged_parts) 不改 |
| UD-005 | legacy 兼容 | <v1.5.2 `_find_layer_files` 行为不变 |
| UD-006 | 实现位置 | `beacon/utils/v110_baseline.py _find_layer_files` |

## Problem Statement

| 现象 | 根因 |
|------|------|
| package-auth 包 fingerprint user_story/prd 层 count=0 | `_find_layer_files` 只扫旧目录 |
| truth.md 改动不改变 fingerprint | 主体内容不在扫描范围 |
| spec_impl_drift 对 truth 漂移失效 | fingerprint 不反映 truth |

## Non-Goals

- 改 `generate_spec_fingerprint` hash 算法
- 改 fingerprint schema / layers 结构
- 重构 v110_baseline.py god-file
- 改 `.machine/qa/*.ac-test-matrix.json` 的 test_case 层扫描

## 受影响代码面

| 位置 | 当前 | 目标 |
|------|------|------|
| `beacon/utils/v110_baseline.py:20 _find_layer_files` | 只扫 user-story/prd/qa-test-cases | ≥v1.5.2 扫 features/<slug>/{truth,tests}.md |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | fingerprint-user-story-layer | ≥v1.5.2 包 fingerprint user_story 层 count>0（扫 features/<slug>/truth.md）（**Must**） |
| AC-002 | fingerprint-prd-layer | ≥v1.5.2 包 fingerprint prd 层 count>0（**Must**） |
| AC-003 | truth-change-detected | 改 truth.md 后 fingerprint hash 改变（spec drift 检测对 truth 有效）（**Must**） |
| AC-004 | legacy-compat | <v1.5.2 `_find_layer_files` 行为不变（**Must**） |
| AC-005 | test-case-layer-preserved | test_case 层仍扫 `.machine/qa/*.ac-test-matrix.json`（**Must**） |
| AC-006 | no-regression-v163-release | v1.6.3 release gate 修复后仍 pass（fingerprint 重生成后 expected=actual）（**Must**） |
| AC-007 | no-regression-v162 | v1.6.2 fingerprint 行为不变（**Must**） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | v110_baseline.py god-file 拆分 | 另开技术债 feature |
| DEF-002 | fingerprint layers schema 对 package-auth 的重新定义（truth/tests 而非 prd/user_story/test_case） | 另开 feature |
| DEF-003 | qa.py:626 / release_scorecard.py:548 非阻断旧路径文案清理 | 另开 feature |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | prd 层扫 truth.md（package-auth 无独立 prd，truth.md 承担）（UD-002） |
| OQ-002 | hash 算法不改，仅改层文件发现（UD-004） |
| OQ-003 | test_case 层保留 .machine/qa matrix 扫描（UD-003） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 4–7 煮干后 freeze。
