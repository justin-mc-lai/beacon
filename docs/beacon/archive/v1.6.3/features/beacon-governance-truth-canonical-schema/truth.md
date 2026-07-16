---
slug: beacon-governance-truth-canonical-schema
version: v1.6.3
status: frozen
revision_id: R1
language: zh
change_reason: R1 — governance contract schema 字段化 truth_canonical/runtime_mirror，消除 per_service_canonical_branch 与 global-boundaries §4.2 truth-on-main 的主动矛盾，解除 git-alignment blocked
source_revision_id: null
canonical_refs:
  prd: docs/beacon/archive/v1.6.3/features/beacon-governance-truth-canonical-schema/truth.md
  user_story: docs/beacon/archive/v1.6.3/features/beacon-governance-truth-canonical-schema/truth.md
  test_case: docs/beacon/archive/v1.6.3/features/beacon-governance-truth-canonical-schema/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：Governance Truth-Canonical Schema v1.6.3

## 概述

governance 契约（`docs/beacon/governance/project-version-governance.md`）当前用单值 `per_service_canonical_branch: beacon/v<x>` 表达版本 canonical 分支，与 `global-boundaries §4.2`（truth-on-main：truth 在 `main` 编写冻结、`beacon/v<x>` 仅为 runtime mirror）主动矛盾。该矛盾在 delivery gate 层落地为 `doctor verify-delivery` 的 `git-alignment` artifact `blocked=true`（reason_codes: `git_branch_target_mismatch` / `git_branch_prefix_mismatch` / `git_version_ref_not_satisfied`），阻断 v2.0.0 delivery seal。

本 feature 在 governance contract schema 层引入 `truth_canonical` 与 `runtime_mirror` 双字段，使契约能表达 §4.2 已声明的 truth-on-main 职责分离，并让 `doctor branch-governance` / `git-alignment` resolver 按 §4.2 接受 `main` 为 truth canonical。

## User Intent（一行）

governance 契约 schema 能表达 §4.2 的 truth-on-main 职责分离，解除 git-alignment blocked，使 delivery gate 不再因 contract 与 truth 矛盾而误阻断。

## User Intent Snapshot

- user_prompt: "governance contract 区分 truth_canonical=main / runtime_mirror=beacon/v<x>，消除与 §4.2 矛盾，解除 git-alignment 阻断"
- lake_or_ocean: 湖（bounded 治理 schema 对齐，scope 清晰，非开放式功能）
- scope_mode: brownfield_takeover（既有 governance contract 既有 §4.2，做 schema 对齐）
- silent_scope_change_allowed: false

## User Decisions（locked）

- UD-001 scope 边界：本 feature 仅冻结 governance contract schema 字段化（`truth_canonical`/`runtime_mirror`）+ resolver 按 §4.2 接受 main。09735ee5 的 UD-020 admission merge-main 裸码收口**不纳入**本 feature，另开 feature/queue item 处理。
- UD-002 resolver 兼容策略：保留 `per_service_canonical_branch` 字段（向后兼容），新增 `truth_canonical` / `runtime_mirror` 双字段。resolver 优先读新字段，旧字段保留不破坏现有 doctor/worktree 流向。

## Problem Statement

1. `project_governance.py` 的 `_assign_version_kv` 是固定白名单，无 `truth_canonical`/`runtime_mirror`——未知 key 被静默丢弃，契约无法表达 truth-on-main。
2. `doctor branch-governance` / `git-alignment` resolver 按 `per_service_canonical_branch`（= `beacon/v<x>`）解析 base/target，而 §4.2 truth 在 `main` → repair/implement 在 main 跑时 git-alignment 全 mismatch → `blocked=true`。
3. v2.0.0 delivery 因 git-alignment blocked 无法 seal。

## Non-Goals

- 不修订 v1.6.2 admission R4 truth 的既有 acceptance（R4 已 frozen，scope 为文档层；本 feature 不触碰 R4 的任何 acceptance criteria）。
- 不收口 09735ee5 的 UD-020 admission merge-main 裸码（UD-001，另开）。
- 不改 §4.2 global-boundaries 本身（§4.2 是 cross-version canonical 约束源头，本 feature 对齐它，不改它）。
- 不重构 worktree admission 流向（UD-002 保留旧字段兼容）。
- monorepo 场景的 truth 分支策略（§4.2 明示另定）。

## 受影响代码面

- `beacon/utils/project_governance.py`：`_assign_version_kv` 白名单 + `_parse_version_contracts` + `render_governance_markdown` + `commit_governance_payload`/`_sync_sqlite_projection`。
- `beacon/utils/` git-alignment / branch-governance resolver（doctor `verify-git-alignment`、`branch-governance show/verify`）。
- `docs/beacon/governance/project-version-governance.md`：v1.6.3 / v2.0.0 contract 增补双字段（由 `commit_governance_payload` transaction 写入）。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | schema-parse | `_assign_version_kv` 识别并持久化 `truth_canonical` / `runtime_mirror` 两个新 key，不再静默丢弃；`_parse_version_contracts` 正确解析双字段到 contract payload（**Must**） |
| AC-002 | schema-render | `render_governance_markdown` 将双字段正确回写到 governance MD；`commit_governance_payload` 重算 transaction_id/source_hash 并 sync sqlite projection（**Must**） |
| AC-003 | resolver-truth-canonical | `doctor branch-governance` / `git-alignment` resolver 在 contract 含 `truth_canonical: main` 时，按 §4.2 接受 `main` 为 truth canonical base，不再因 current_branch=main 报 `git_branch_target_mismatch`（**Must**） |
| AC-004 | backward-compat | contract 仅含旧 `per_service_canonical_branch`（无双字段）时，resolver 行为不变（向后兼容，UD-002）（**Must**） |
| AC-005 | git-alignment-unblock | v1.6.3 contract 补双字段（`truth_canonical: main` / `runtime_mirror: beacon/v1.6.3`）后，`doctor verify-git-alignment` / `doctor verify-delivery --version v1.6.3` 的 git-alignment 不再因 current_branch=main 报 `blocked=true`（reason_codes 清空或转为可解释的 non-blocked 状态）。本 AC 验证对象限定 v1.6.3 单版本（**Must**，UD-003） |
| AC-006 | no-flow-break | 现有 v1.6.3 worktree admission / branch-governance 流向不破坏（`beacon workspace admit` / `doctor branch-governance verify` 在双字段 contract 下行为可解释且不误阻断）（**Must**） |

## Deferral Ledger

| ID | 项 | user_decision |
|---|---|---|
| UD-001 | 09735ee5 UD-020 admission merge-main 裸码收口 | accepted（另开 feature，不纳入本包） |
| UD-002 | monorepo truth 分支策略 | accepted（§4.2 明示另定，延后） |
| UD-003 | v2.0.0 contract 补双字段 + delivery unblock | accepted（缩到 v1.6.3 单版本；v2.0.0 contract 应用作为 implement 阶段下游动作，不改 v2.0.0 truth，本包不验证 v2.0.0） |

## State Machine

```
[contract 无双字段] --AC-001/002--> [contract 含双字段]
[contract 含双字段] --AC-003--> [resolver 接受 main 为 truth canonical]
[resolver 接受 main] --AC-005--> [git-alignment unblocked]
[git-alignment unblocked] --> 解锁 v2.0.0 delivery seal（下游，非本包闭环）
```

## Closed Questions

是否替换 `per_service_canonical_branch`：否（UD-002，保留兼容）。是否纳入 UD-020 裸码收口：否（UD-001，另开）。

## Downstream Routes（post-freeze）

- `beacon-gen-implement`：实现 AC-001..006 代码（schema + resolver）。
- `beacon-eval-qa`：验证 git-alignment unblocked + 向后兼容 + 不破坏流向。
- v2.0.0 delivery seal（F4）在本 feature 实现后解锁，属独立下游闭环。
