---
slug: beacon-runtime-release-alignment-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 修复 release gate 不要求 runtime==docs + post-release hook 不 bump runtime，导致 skills/runtime 撕裂
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/truth.md
  user_story: docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/truth.md
  test_case: docs/beacon/v1.6.3/features/beacon-runtime-release-alignment-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Runtime Release Alignment v1.6.3

## 概述

`beacon-runtime-release-alignment-v163` 修复 beacon 发布模型的 runtime/skills 撕裂：**release gate 不要求 runtime==docs，post-release hook 不 bump runtime**，导致发布后 skills 是 v1.6.3 内容但 `beacon --version` 仍报旧 runtime——半发布。

**两处根因：**

1. **release gate 不查 runtime==docs drift** — `beacon/commands/gate.py` 的 release 阶段无 `runtime_docs_version_drift` 检查。P0-1（`project_hooks.py:497`）的 drift 守卫只在 post-release hook 算 `informational`（UD-006 不阻断），release gate 完全不查。后果：runtime v1.6.1 / docs v1.6.3 时 release gate 仍能 Pass，发布撕裂版本。

2. **post-release hook 不 bump runtime** — `_run_beacon_post_release_local_install`（`project_hooks.py`）不调 `sync-version-surfaces` / 不写 `__toolkit_version__` / 不装包。hook 只装 skills + launcher，runtime 保持在旧版本。用户跑 hook "发布到本机 agent" 后，`beacon --version` 仍报旧版本。

**深层意图**：发布一个 beacon 版本到本机 agent = skills 文档 + runtime CLI 一起到该版本。当前 hook 只做一半，违背"发布"语义。

**P0 交付（Must）：**

1. **release gate 要求 runtime==docs** — release 阶段加 `runtime_docs_release_drift` 检查：runtime_version ≠ docs target version → critical block。开发期（非 release stage）仍允许 drift（双版本模型开发期合法）。
2. **hook 显式路由 runtime bump** — post-release hook 加 `runtime_alignment` 步骤：检测 runtime≠docs 时，路由 `beacon doctor sync-version-surfaces`（写 `__toolkit_version__`/`__version__`/pyproject）+ 提示重装包；hook payload 含 `runtime_alignment` 字段。
3. **drift 在 release 阻断，开发期 informational** — 修正 P0-1 的 UD-006：drift 在 release gate 阻断；在 post-release hook 仍 informational 但路由修复；开发期（plan/truth/implement/qa stage）不阻断。

**不**改 `sync-version-surfaces` 内部逻辑；**不**强制开发期 runtime==docs；**不**自动 pip install（hook 提示，不静默装包）；**不**新增 lifecycle stage。

## User Intent（一行）

发布 beacon 版本到本机 agent 时 skills 与 runtime 一起到该版本：release gate 阻断 runtime≠docs 的发布，post-release hook 显式路由 sync-version-surfaces 修复 runtime，消除半发布撕裂。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | 发布就该 skills+runtime 一起，hook 不 bump runtime 是半发布，release gate 该阻断 runtime≠docs |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`runtime_release_alignment`** |
| 强度词 | release 阻断 drift、hook 路由 bump、开发期允许、不静默装包 |
| 非协商边界 | 开发期 runtime≠docs **仍合法**；`sync-version-surfaces` 逻辑**不**改；hook 不自动 pip install |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | release gate drift 阻断 | release stage 加 `runtime_docs_release_drift` 检查；runtime≠docs target → critical block |
| UD-002 | hook 路由 runtime bump | post-release hook 加 `runtime_alignment` 步骤：runtime≠docs 时路由 `beacon doctor sync-version-surfaces`，payload 含 `runtime_alignment` |
| UD-003 | 开发期不阻断 | plan/truth/implement/qa stage 不查 runtime==docs（双版本开发期合法） |
| UD-004 | hook 不自动 pip install | hook 检测 runtime≠docs 时提示 operator 重装（`pip install -e .`），不静默执行 |
| UD-005 | P0-1 守卫修正 | `project_hooks.py:497` drift 仍 informational（hook 不阻断），但 release gate 阻断（UD-001） |
| UD-006 | 实现位置 | `beacon/commands/gate.py`（新 release 检查）+ `beacon/utils/project_hooks.py`（hook runtime_alignment） |

## Problem Statement

| 现象 | 根因 |
|------|------|
| release gate Pass 但 runtime≠docs | gate release 阶段不查 drift |
| hook 跑完 `beacon --version` 仍旧 | hook 不 bump runtime |
| skills v1.6.3 跑在 runtime v1.6.1 | 半发布撕裂 |

## Non-Goals

- 改 `sync-version-surfaces` 内部逻辑
- 开发期强制 runtime==docs
- hook 自动 pip install（只提示）
- 重构 gate.py / project_hooks.py god-file
- 改 P0-1 的 `_resolve_eval_version` 逻辑

## 受影响代码面

| 位置 | 当前 | 目标 |
|------|------|------|
| `beacon/commands/gate.py` release 检查 | 无 runtime==docs 检查 | 加 `check_runtime_release_alignment`（release stage，runtime≠docs → block） |
| `beacon/utils/project_hooks.py` hook | 不调 sync-version-surfaces | 加 `runtime_alignment` 步骤（检测+路由修复+payload 字段） |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | release-gate-drift-block | release stage runtime≠docs target → critical block，reason_code `runtime_docs_release_drift`（**Must**） |
| AC-002 | release-gate-pass-when-aligned | runtime==docs 时 release gate 不因 drift block（**Must**） |
| AC-003 | hook-runtime-alignment-step | post-release hook payload 含 `runtime_alignment` 字段（runtime_version/docs_version/aligned/recommended_command）（**Must**） |
| AC-004 | hook-routes-sync-version-surfaces | runtime≠docs 时 hook `runtime_alignment.recommended_command` 含 `beacon doctor sync-version-surfaces`（**Must**） |
| AC-005 | dev-stages-no-block | plan/truth/implement/qa stage 不因 runtime≠docs block（开发期合法）（**Must**） |
| AC-006 | no-auto-pip-install | hook 不执行 pip install，只提示（**Must**，UD-004） |
| AC-007 | no-regression-p01 | P0-1 的 `_resolve_eval_version` + resolve failure fail-closed 仍生效（**Must**） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | gate.py / project_hooks.py god-file 拆分 | 另开技术债 feature |
| DEF-002 | hook 自动 pip install（需用户授权机制） | 另开 feature |
| DEF-003 | runtime bump 的 pipx/独立 venv 支持 | 另开 feature |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | release 阻断 drift，开发期允许（UD-001/003） |
| OQ-002 | hook 路由 sync-version-surfaces，不自动 pip install（UD-002/004） |
| OQ-003 | P0-1 hook 守卫仍 informational（UD-005） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 4–7 煮干后 freeze。
