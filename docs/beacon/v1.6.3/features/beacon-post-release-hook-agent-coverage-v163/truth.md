---
slug: beacon-post-release-hook-agent-coverage-v163
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 修复 post-release hook 只覆盖 codex+claude、漏 cursor/windsurf/trae 的 agent 覆盖缺陷
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/truth.md
  user_story: docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/truth.md
  test_case: docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: false
upstream_feature: null
promotion_ref: null
---

# 需求真相：Post-Release Hook Agent Coverage v1.6.3

## 概述

`beacon-post-release-hook-agent-coverage-v163` 修复 post-release hook 的 agent 覆盖缺陷：`beacon/utils/project_hooks.py:520 _run_beacon_post_release_local_install` 的 agent 循环硬编码 `for agent in ("codex", "claude")`，**漏 cursor/windsurf/trae** 三个 agent。

**后果**：用户跑 `beacon hooks run beacon-post-release-local-install` 发布 v1.6.3 到本机 agent 时，cursor/windsurf/trae 的项目级 skills（`.cursor/skills`、`.windsurf/skills`、`.trae/skills`）**不会被 setup/verify**——skills 静默过期（缺 v1.6.2/v1.6.3 内容如 GIT_ADMISSION preamble），但 hook 不报 block。用户以为发布到本机 agent 成功，实际只覆盖 2/5 agent。

**根因**：hook 的 agent 循环是 v1.6.2 workspace admission 特性时写的硬编码，没复用 `agent_surface.py:987` 已有的全 agent 常量 `("trae", "claude", "codex", "cursor", "windsurf")`。与 P0-3/eco/truth-format 同类——局部硬编码未随统一面更新。

**P0 交付（Must）：**

1. **hook 循环覆盖全 5 agent** — `_run_beacon_post_release_local_install` 的 agent 循环改为 `("trae", "claude", "codex", "cursor", "windsurf")`，复用 agent_surface 常量。
2. **drift 真阻断** — hook 对每个 agent 跑 `setup(force=True)` + `verify(strict=True)`；verify 报 `host_visible_skills_drift` 时 hook block（现有 verify 已查 drift，覆盖全 agent 后即生效）。
3. **claude 全局仍单独处理** — `install_global_claude_beacon_skills` / `verify_global_claude_beacon_skills` 保留（claude 全局 symlinks 是 claude 专属）。
4. **agent_surfaces payload 含全 5 agent** — hook 返回的 `agent_surfaces` 字段含 5 个 agent 的 setup/verify 结果。

**不**改 `setup_agent_surface` / `verify_agent_surface` 逻辑；**不**改 agent 路径解析；**不**新增 lifecycle stage。

## User Intent（一行）

post-release hook 覆盖全 5 agent（trae/claude/codex/cursor/windsurf）的 setup+verify，让 v1.6.3 beacon skills 在所有本机 agent 正确安装且 drift 时阻断，发布到本机 agent 真正完整。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | hook 只覆盖 codex+claude，cursor/windsurf/trae 的 skills 静默过期，需覆盖全 5 agent 且 drift 阻断 |
| `lake_or_ocean` | **湖** |
| `scope_mode` | **`hook_agent_coverage_full`** |
| 强度词 | 全 5 agent、drift 阻断、复用常量、claude 全局保留 |
| 非协商边界 | setup/verify 逻辑**不**改；agent 路径解析**不**改；claude 全局**不**删 |

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | hook agent 循环 | 改为 `("trae", "claude", "codex", "cursor", "windsurf")`，复用 agent_surface 常量 |
| UD-002 | drift 阻断 | 每个agent `setup(force=True)` + `verify(strict=True)`；verify 非 PASS → hook block `{agent}_agent_surface_verify_failed` |
| UD-003 | claude 全局 | 保留 `install_global_claude_beacon_skills` + `verify_global_claude_beacon_skills`（claude 专属全局 symlinks） |
| UD-004 | payload | `agent_surfaces` 含全 5 agent 的 setup/verify 结果 |
| UD-005 | 实现位置 | `beacon/utils/project_hooks.py _run_beacon_post_release_local_install` |
| UD-006 | 不改 setup/verify | `setup_agent_surface` / `verify_agent_surface` 逻辑不变 |

## Problem Statement

| 现象 | 根因 |
|------|------|
| hook 跑后 cursor/windsurf/trae skills 不更新 | `:520` 只循环 codex/claude |
| skills drift 静默过期 | 3 agent 不跑 verify，drift 不被检测 |
| 用户误以为发布完整 | hook 报 pass 但实际 2/5 agent |

## Non-Goals

- 改 `setup_agent_surface` / `verify_agent_surface` 内部逻辑
- 改 `resolve_agent_surface_target` agent 路径
- 改 claude 全局安装逻辑
- 重构 project_hooks.py god-file
- 改 hook trigger_policy（仍 manual_confirmed）

## 受影响代码面

| 位置 | 当前 | 目标 |
|------|------|------|
| `beacon/utils/project_hooks.py:520` | `for agent in ("codex", "claude")` | `for agent in ("trae", "claude", "codex", "cursor", "windsurf")` |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | hook-covers-5-agents | `_run_beacon_post_release_local_install` 的 agent 循环含 trae/claude/codex/cursor/windsurf 全 5 个（**Must**） |
| AC-002 | all-agents-setup-verify | hook payload 的 `agent_surfaces` 含 5 个 agent 的 setup_status + verify_status（**Must**） |
| AC-003 | drift-blocks-hook | 任一 agent verify 报 `host_visible_skills_drift` 时 hook block，reason_code 含 `{agent}_agent_surface_verify_failed`（**Must**） |
| AC-004 | claude-global-preserved | hook 仍调 `install_global_claude_beacon_skills` + `verify_global_claude_beacon_skills`（**Must**） |
| AC-005 | no-regression-codex-claude | codex/claude 的 setup/verify 行为不变（仍 force=True + strict=True）（**Must**） |
| AC-006 | no-regression-block-reasons | 现有 block reason_codes（setup_failed/verify_failed）语义不变（**Must**） |
| AC-007 | agent-constant-reused | 循环复用 agent_surface 的全 agent 常量，不新增硬编码（**Must**） |

## Deferral Ledger

| ID | 项 | 目标 |
|----|-----|------|
| DEF-001 | project_hooks.py god-file 拆分 | 另开技术债 feature |
| DEF-002 | hook trigger_policy 改 auto_allowed | 另开 feature（当前仍 manual_confirmed） |
| DEF-003 | codex `.agents/skills` 路径特殊性加固 | 另开 feature（当前路径解析正确） |

## State Machine

```text
truth_draft -> truth_review -> freeze -> implement -> qa -> release
```

## Closed Questions

| ID | 决议 |
|----|------|
| OQ-001 | 循环用全 5 agent，不参数化（UD-001） |
| OQ-002 | drift 通过 verify strict 阻断，不另加检查（UD-002） |
| OQ-003 | claude 全局保留，不合并进循环（UD-003） |

## Downstream Routes（post-freeze）

| 阶段 | Route |
|------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |

---

**Status:** `draft` R1 — truth.define；待 Round 4–7 煮干后 freeze。
