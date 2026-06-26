---
slug: beacon-gate-truth-model-alignment-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — gate release 检查器对齐 package-authoritative truth 模型（P0-3 免疫系统修复）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md
  user_story: docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md
  test_case: docs/beacon/v1.6.3/features/beacon-gate-truth-model-alignment-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Gate Truth Model Alignment v1.6.3

## 概述

`beacon-gate-truth-model-alignment-v163` 修复 Beacon 免疫系统的一个 P0 漂移：`gate check release` 的 `check_formal_version_package_closure`（`beacon/commands/gate.py:2308`）对所有版本硬性要求 `prd/`、`user-story/`、`qa/test-cases/` 顶层目录，但 v1.5.2+ 已迁到 **package-authoritative** 模型——需求真相位于 `features/<slug>/{truth,tests,tasks,evidence}.md`，旧顶层目录不再承载 truth。

**后果**：v1.6.2（及任何 ≥v1.5.2 版本）跑 `gate check release --strict` 时，`formal_package_closure_missing` 永远 critical block（65 项阻断之一），除非塞空目录糊弄。这是门禁标准未随 truth 模型迁移导致的**永久 block**——免疫系统对正确交付的版本误报为未闭环。

**P0 交付（Must）：**

1. **检查器分流** — `check_formal_version_package_closure` 按 semver 分流：`<v1.5.2` 保持原顶层目录契约；`≥v1.5.2` 改为校验 package-authoritative feature 包闭环。
2. **新契约语义** — `≥v1.5.2` 版本要求至少存在一个 frozen feature 包（`features/<slug>/` 含 `truth.md` + `tests.md`），且 version-line 共享材料（SUMMARY/execution/boundaries/source-architecture/release）仍校验，不因模型迁移而放松。
3. **回归修复** — v1.6.2 实测 `gate check release` 不再因顶层 `prd/user-story/qa/test-cases` 缺失而 `formal_package_closure_missing` block。

**不**删除旧版本兼容路径；**不**改变 version-line 共享材料契约；**不**新增 lifecycle stage；**不**把 feature 包校验降级为 warn。

## User Intent（一行）

gate release 检查器对 `≥v1.5.2` 版本校验 package-authoritative feature 包闭环而非旧顶层目录，让正确交付的版本能过 gate；`<v1.5.2` 保持原契约不 break。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | gate 检查器没随 truth 模型迁移，v1.6.2 永久 block，需对齐到 package-authoritative，旧版本保持兼容 |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`single_check_fn_alignment`** |
| 强度词 | fail-closed、对齐、兼容、不放松 |
| 非协商边界 | 旧版本 (`<v1.5.2`) 契约**不**改；feature 包校验**不**降级为 warn；**不**用空目录糊弄 |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | 分流阈值 | **`v1.5.2`**（package-authoritative cutover 版本） |
| UD-002 | 新契约校验对象 | `features/<slug>/` 下至少一个含 `truth.md`+`tests.md` 的 feature 包 |
| UD-003 | 旧版本兼容 | `<v1.5.2` 保持 `prd/`+`user-story/`+`qa/test-cases/` 顶层目录契约不变 |
| UD-004 | version-line 材料 | SUMMARY/execution/boundaries/source-architecture/release 校验**所有版本保留**，不随分流放松 |
| UD-005 | 缺 feature 包时语义 | `≥v1.5.2` 版本无任何 feature 包 → critical block，reason_code `feature_package_closure_missing`（**不**误报顶层目录缺失） |
| UD-006 | 实现位置 | `beacon/commands/gate.py` `check_formal_version_package_closure` 原地修改，复用 `_parse_semver_tuple` |
| UD-007 | 验收基准 | v1.6.2 回归：原 `formal_package_closure_missing`（missing prd/user-story/qa/test-cases）不再出现 |

## Problem Statement

| 现象 | 根因 |
|------|------|
| v1.6.2 `gate check release` 65 项 block | `formal_package_closure_missing` 误报顶层目录缺失 |
| ≥v1.5.2 版本永远过不了 release gate | 检查器仍要求旧顶层目录，但 truth 已迁 feature 包 |
| 空目录糊弄能绕过 | 检查器只判目录存在，不校验 feature 包闭环 |

## Non-Goals

- 重构 gate.py god-file（另开技术债 feature）
- 改 version-line 共享材料契约
- 新增 feature 包冻结流程（复用现有 `beacon freeze`）
- 修复 P0-1（版本守卫）/ P0-2（completion gate）—— 另开 feature 包

## 受影响代码面

| 位置 | 当前行为 | 目标行为 |
|------|---------|---------|
| `beacon/commands/gate.py:2308 check_formal_version_package_closure` | 所有版本统一要求 `prd/`+`user-story/`+`qa/test-cases/` | `<v1.5.2` 保持；`≥v1.5.2` 改校验 feature 包闭环 |
| `beacon/commands/gate.py:4114 _parse_semver_tuple` | 已存在，复用 | 复用，不改 |
| `beacon/commands/review.py:747` 同名检查 | review 阶段同类逻辑 | 同步分流（若存在相同硬编码） |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | semver-fork | `check_formal_version_package_closure` 对 `≥v1.5.2` 版本不再要求 `prd/`/`user-story/`/`qa/test-cases/` 顶层目录（**Must**） |
| AC-002 | feature-package-closure | `≥v1.5.2` 版本改为校验 `features/<slug>/` 下至少一个 feature 包含 `truth.md`+`tests.md`（**Must**） |
| AC-003 | legacy-compat | `<v1.5.2` 版本（如 v1.4.10）保持原 `prd/`+`user-story/`+`qa/test-cases/` 顶层目录契约不变（**Must**） |
| AC-004 | version-line-preserved | SUMMARY/execution/boundaries/source-architecture/release 校验对所有版本保留，不因分流放松（**Must**） |
| AC-005 | missing-feature-block | `≥v1.5.2` 版本无任何 feature 包 → critical block，reason_code `feature_package_closure_missing`，**不**误报顶层目录缺失（**Must**） |
| AC-006 | regression-v162 | v1.6.2 实测 `gate check release` 的 `formal_package_closure_missing` 不再因顶层目录缺失出现（**Must**，回归 P0-3） |
| AC-007 | no-empty-dir-bypass | 空目录（`prd/` 存在但无 `.md`）不再使 `≥v1.5.2` 版本通过；通过需真实 feature 包（**Must**） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | gate.py god-file 拆分（按版本注册表） | 另开技术债 feature |
| DEF-002 | review.py:747 同名检查的重构统一 | 本包仅同步分流逻辑，不重构 |
| DEF-003 | P0-1 版本守卫 / P0-2 completion gate | 另开 feature 包 |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | 分流阈值 = v1.5.2（UD-001，package-authoritative cutover） |
| OQ-002 | 缺 feature 包仍 critical block，不降级 warn（UD-005） |
| OQ-003 | 旧版本契约不改（UD-003） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 2–7 煮干后 freeze。
