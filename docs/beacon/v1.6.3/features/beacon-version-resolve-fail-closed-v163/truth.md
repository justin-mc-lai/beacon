---
slug: beacon-version-resolve-fail-closed-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 修复版本解析硬编码 fallback + 加 runtime↔docs 漂移 fail-closed 守卫（P0-1 免疫系统修复）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md
  user_story: docs/beacon/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md
  test_case: docs/beacon/v1.6.3/features/beacon-version-resolve-fail-closed-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Version Resolve Fail-Closed v1.6.3

## 概述

`beacon-version-resolve-fail-closed-v163` 修复 Beacon 免疫系统的 P0-1 漂移：版本解析绕过集中化 `resolve_target_version`，且无 runtime↔docs 漂移 fail-closed 守卫。

**根因（两处）：**

1. **硬编码 fallback** — `beacon/utils/project_hooks.py:543` `eval_version = version if version.startswith("v") else "v1.6.1"`。当传入的 `version` 非显式 `v` 前缀（如 `auto`/`latest`/空）时，静默降到硬编码 `v1.6.1`，绕过集中化 `resolve_target_version`（`beacon/utils/versioning.py:1015`）。docs target=v1.6.2/v1.6.3 时，agent eval release hook 仍走 v1.6.1 路径。
2. **无漂移守卫** — `project_hooks.py:532-540` 只校验 `beacon --version` == `__toolkit_version__`（runtime 自检），**无 runtime(docs_default_line) ↔ docs(实际 docs 版本) 漂移 fail-closed 守卫**。runtime v1.6.1 / docs v1.6.3 时静默放行。

**后果**：版本边界（trust boundary）不 fail-closed，自驱 loop 可能在错误版本路径上跑，违反 anti-inertia「边界 fail-closed」原则。

**P0 交付（Must）：**

1. **消除硬编码 fallback** — `project_hooks.py:543` 改用 `resolve_target_version(project_root, version)`，不再硬编码 `v1.6.1`。
2. **runtime↔docs 漂移守卫** — post-release hook 校验 runtime 版本（`__toolkit_version__`）与 docs 解析版本（`resolve_target_version`）一致；不一致 → fail-closed block，reason_code `runtime_docs_version_drift`。
3. **`agent_eval_kit.py:32 AGENT_EVAL_VERSION` 收敛** — 不再硬编码蔓延 11 处默认参数；运行时解析版本而非常量默认。

**不**改变 runtime/docs 双版本模型语义；**不**强制 runtime==docs（双版本可分别推进是合法的）；**不**新增 lifecycle stage。

## User Intent（一行）

版本边界 fail-closed：消除 v1.6.1 硬编码 fallback、用 resolve_target_version 解析、runtime↔docs 漂移时硬阻断，让自驱 loop 不在错误版本路径上跑。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | project_hooks 硬编码 v1.6.1 fallback 绕过版本解析，无 runtime/docs 漂移守卫，需 fail-closed |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`version_boundary_fail_closed`** |
| 强度词 | fail-closed、消除硬编码、漂移阻断、不静默降级 |
| 非协商边界 | 双版本模型语义**不**改；runtime≠docs 合法但**必须**显式记录不静默放行；不强制 runtime==docs |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | 消除硬编码 fallback | `project_hooks.py:543` 改 `resolve_target_version(project_root, version)` |
| UD-002 | 漂移守卫 | post-release hook 加 runtime(`__toolkit_version__`)↔docs(`resolve_target_version`) 一致性校验；不一致 → block `runtime_docs_version_drift` |
| UD-003 | 守卫语义 | runtime≠docs **合法**（双版本可分别推进），但 hook **必须**在 payload 显式记录 `runtime_version`/`docs_version`/`drift` 字段；仅当 `__toolkit_version__` 无法解析或解析失败时 fail-closed |
| UD-004 | AGENT_EVAL_VERSION 收敛 | `agent_eval_kit.py` 运行时用 resolve 的版本，常量仅作最终 fallback；默认参数不再硬编码蔓延 |
| UD-005 | 实现位置 | `beacon/utils/project_hooks.py` + `beacon/utils/agent_eval_kit.py` |
| UD-006 | 不强制相等 | 不要求 runtime==docs；drift 字段 informational，不因双版本合法推进而 block |

## Problem Statement

| 现象 | 根因 |
|------|------|
| docs v1.6.3 时 agent eval hook 走 v1.6.1 | `:543` 硬编码 fallback 绕过 resolve |
| runtime/docs 漂移静默放行 | `:532-540` 只自检 runtime，无 docs 对照 |
| 版本边界不 fail-closed | trust boundary 缺守卫 |

## Non-Goals

- 强制 runtime==docs（双版本模型合法）
- 改 `resolve_target_version` / `resolve_docs_version` 内部逻辑
- 修复 P0-2（completion gate）/ P0-3（已修）
- 重构 project_hooks.py / agent_eval_kit.py god-file

## 受影响代码面

| 位置 | 当前 | 目标 |
|------|------|------|
| `beacon/utils/project_hooks.py:543` | `version if version.startswith("v") else "v1.6.1"` | `resolve_target_version(project_root, version)` |
| `beacon/utils/project_hooks.py:532-540` | 仅 runtime 自检 | 加 docs 解析 + `runtime_version`/`docs_version`/`drift` 字段；解析失败 fail-closed |
| `beacon/utils/agent_eval_kit.py:32` | `AGENT_EVAL_VERSION="v1.6.1"` 蔓延 11 处默认 | 运行时 resolve，常量仅最终 fallback |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | no-hardcoded-fallback | `project_hooks.py:543` 不再含硬编码 `v1.6.1` 字面量；改用 `resolve_target_version`（**Must**） |
| AC-002 | docs-version-resolved | version=`auto`/空/`latest` 时 eval_version 解析为 docs 实际版本（如 v1.6.3），非 v1.6.1（**Must**） |
| AC-003 | drift-guard-field | post-release hook payload 含 `runtime_version`/`docs_version`/`drift` 字段（**Must**） |
| AC-004 | resolve-failure-fail-closed | `resolve_target_version` 解析失败/抛异常时 hook fail-closed block，reason_code `version_resolve_failed`（**Must**） |
| AC-005 | agent-eval-version-resolved | `agent_eval_kit.is_live_runner_admitted` 运行时用 resolve 版本，不依赖硬编码 `AGENT_EVAL_VERSION` 默认（**Must**） |
| AC-006 | no-regression-release-hook | 现有 post-release hook 在 runtime==docs（正常）场景仍 pass，不误 block（**Must**） |
| AC-007 | drift-not-blocked-legitimate | runtime≠docs（双版本合法推进）时 `drift=true` 但**不** block（仅记录）（**Must**，UD-006） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | project_hooks.py / agent_eval_kit.py god-file 拆分 | 另开技术债 feature |
| DEF-002 | 强制 runtime==docs 的 strict 模式 | 另开 feature（当前仅 informational） |
| DEF-003 | P0-2 completion gate | 另开 feature 包 |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | 不强制 runtime==docs（UD-006，双版本合法） |
| OQ-002 | 漂移 informational，解析失败才 fail-closed（UD-003/004） |
| OQ-003 | AGENT_EVAL_VERSION 常量保留作最终 fallback，不删（UD-004） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 4–7 煮干后 freeze。
