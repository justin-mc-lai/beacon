---
slug: loom-implement-lane-enforcement-v200
version: v2.0.0
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO 2026-07-20: UD-ENF 全接受 — main 禁业务 commit + git hooks + goal/release 挂钩; dual v2.0.0"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-implement-lane-enforcement-v200/truth.md
  tests: docs/beacon/v2.0.0/features/loom-implement-lane-enforcement-v200/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-implement-lane-enforcement-v200/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-implement-lane-enforcement-v200/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
ux_required: false
design_deferral: "No product UI; doctor + git hooks"
---

## 人话

禁止在 main 上直接 commit 业务实现路径；pre-commit/pre-push + doctor setup-git-hooks；goal implement 与 release 挂钩 admission 证据。

# Requirement Truth: Implement Lane Enforcement

## Intent

关闭「agent/人在 main checkout 直改 beacon/** 并 commit」漏洞：Git 硬闸 + Goal 硬闸加固 + release/doctor 复检。紧急旁路仅 env + evidence 文件。

## UD

| ID | Value |
|----|-------|
| UD-ENF-001 | main/master 上 staged 命中业务路径默认 **reject commit** |
| UD-ENF-002 | 紧急旁路：`BEACON_ALLOW_MAIN_IMPLEMENT=1` + `.beacon/evidence/main-implement-exception.json` |
| UD-ENF-003 | goal implement 无 admission → blocked（加固） |
| UD-ENF-004 | dual version 意图无双轨 admit plan → blocked（soft→记录） |
| UD-ENF-005 | release check 对缺 admission/pool 证据 **WARN**（本湖不硬挡全仓历史） |
| UD-ENF-006 | `beacon doctor setup-git-hooks` / `verify-git-hooks` / `verify-implement-lane` |

## Business path denylist (main)

- `beacon/**`
- `packages/**`
- `tests/test_*.py`（业务单测）

## Allowlist on main

- `docs/beacon/**`
- `skills/**`
- 顶层 `*.md` / 配置（不含 beacon 包代码）

## AC

| ID | Description |
|----|-------------|
| AC-ENF-001 | main + staged beacon/foo.py → pre-commit blocked |
| AC-ENF-002 | main + only docs → pass |
| AC-ENF-003 | env allow + exception evidence → pass with reason |
| AC-ENF-004 | setup-git-hooks writes pre-commit + pre-push |
| AC-ENF-005 | verify-git-hooks detects missing/mismatch |
| AC-ENF-006 | verify-implement-lane flags dirty main with business paths |
| AC-ENF-007 | dual feature packages v169+v200 |
| AC-ENF-008 | release advisory includes implement_lane check (non-fatal WARN) |

## Non-goals

- 阻止所有未 save 的编辑器缓冲（仅 git 与 CLI 路径）
- 改写已 push 历史
- 本湖强制所有历史 feature 补 worktree
