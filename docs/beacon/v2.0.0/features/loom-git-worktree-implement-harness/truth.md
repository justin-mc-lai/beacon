---
slug: loom-git-worktree-implement-harness
version: v2.0.0
status: frozen
revision_id: R2
language: zh
change_reason: "R2 - branch ref hierarchy hard gate: leaf-only lanes; admit fail never implements on main; user GO 1A/2A/3A 2026-07-20"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/truth.md
  tests: docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-git-worktree-implement-harness/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/feature-graph.json
parent_kernel: beacon-v2-rust-kernel-redesign
upstream_acs: ["AC-099", "AC-100"]
wave: W1
priority: P0
ux_required: false
design_deferral: "kernel/CLI; no product marketing UI"
display_name: "Loom Git Worktree + Implement Harness"
brand: Loom
---

# Requirement Truth: 真 git worktree + ImplementHarness 一轮 (W1)

## 人话

进化轨在隔离 git worktree 上真实现一轮，禁止 mkdir/subprocess 冒充。

实现 lane 永远是 **leaf 分支**（`beacon/<version>/<feature>`）；禁止因 `beacon/<version>` 与子路径冲突而退回 **main** 写实现。

本湖是 Loom（Beacon 进化品牌）内核补齐的一部分；**不**把生产 `beacon` 默认切走。

## Overview

| Wave | Priority | Upstream AC |
|------|----------|-------------|
| W1 | P0 | AC-099, AC-100 |

Depends on: （无）

## User Intent

进化轨在隔离 git worktree 上真实现一轮，禁止 mkdir/subprocess 冒充。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-W1-001 | git_worktree_add | worktree 模式必须 git worktree add（或等价） |
| UD-LOOM-W1-002 | modes | worktree | current-branch | run-branch；非法组合 fail-closed |
| UD-LOOM-W1-003 | cwd | harness/agent project-root == admitted worktree cwd |
| UD-LOOM-W1-004 | implement_harness | ImplementHarnessBackend 调真实 implement 面一轮 |
| UD-LOOM-W1-005 | no_fake | 禁止 subprocess-only 冒充 harness；禁止 zero-assertion TC |
| UD-LOOM-W1-006 | cli_brand | 用户面 CLI 为 loom（非 loom-v2 产品名） |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-099 | worktree-modes | Git worktree 全模式 parity：worktree/current-branch/run-branch；非法组合 fail-closed；cwd 对齐（Must） |
| AC-100 | implement-harness | ImplementHarnessBackend 在 admitted worktree 内真一轮；IterationResult schema AC-042；非 subprocess 冒充（Must） |
| AC-LOOM-W1-001 | git-real | temp fixture 上可执行 git worktree add 并检出（Must） |
| AC-LOOM-W1-002 | artifact | 成功 iterate 写入 artifact_refs/iteration_result（Must） |
| AC-LOOM-W1-003 | legal-illegal | tests 含合法 walk + 非法组合（Must） |

## Illegal

| ID | Illegal |
|----|---------|
| I-W1-001 | mkdir-only 冒充 worktree |
| I-W1-002 | subprocess echo JSON 冒充 ImplementHarness |
| I-W1-003 | current-branch + isolated 通过 |


## User Decisions — branch ref hierarchy (R2, user GO 1A/2A/3A)

| ID | Decision | Value |
|----|----------|-------|
| UD-BR-001 | hierarchy | 禁止任意 prefix `P` 与 `P/*` 同时作为 git branch ref；create 前 preflight |
| UD-BR-002 | namespace≠leaf | program aggregation（如 `beacon/<version>`）是**命名空间/策略 key**，不是必须存在的 leaf checkout branch |
| UD-BR-003 | default lane | **Always leaf** `beacon/<version>/<feature-slug>`；worktree `.beacon/worktrees/<version>/<feature-slug>`（方案 A） |
| UD-BR-004 | admit fail | admit blocked ⇒ **硬停** implement/goal 实现写路径；禁止 soft fallback 到 main |
| UD-BR-005 | materialize | collision 时 rewrite 到 leaf 或 `branch_ref_hierarchy_collision` 阻断；**禁止**创建 parent while children exist |
| UD-BR-006 | debt | 已有 `beacon/<version>/*` children 合法；不得再创建 parent `beacon/<version>` leaf |

## Acceptance Criteria — R2

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-BR-001 | leaf-only | workspace admit 物化的 `feature_branch` **必须**是 leaf（含 feature-slug）；不得仅为 `beacon/<version>`（**Must**） |
| AC-BR-002 | preflight | create/switch 前 hierarchy preflight；父子冲突 → `branch_ref_hierarchy_collision`（**Must**） |
| AC-BR-003 | program-level | program-level 模式保留 aggregation 元数据，但 checkout 仍用 leaf feature branch（**Must**） |
| AC-BR-004 | no-main-fallback | admit fail 后 implement/goal 不得在 truth_canonical（main/master）写业务实现（**Must**） |
| AC-BR-005 | reason-codes | 暴露 `branch_ref_hierarchy_collision`、`workspace_admission_worktree_failed`、`implement_on_canonical_without_admission`（**Must**） |
| AC-BR-006 | tests | 含 collision fixture + leaf rewrite + no main soft fallback（**Must**） |

## Illegal — R2

| ID | Illegal |
|----|---------|
| I-BR-001 | 创建 `beacon/<version>` parent leaf 当 `beacon/<version>/*` children 已存在 |
| I-BR-002 | admit failed 后在 main 继续 implement |
| I-BR-003 | program-level 把 aggregation branch 当作唯一 checkout target 且忽略 feature slug |
| I-BR-004 | soft-warn 后继续在未 admit 工作区写实现 |

## Domain note — Git ref tree

Git refs 是前缀树：`P` 与 `P/child` 互斥。Beacon 必须在 materialize 前检测并 **rewrite 到 leaf** 或 fail-closed。


## Non-Goals

- 默认 `BEACON_V2=1` / loom 覆盖 beacon
- 本湖单独宣称整个 v2.0.0 release 完成
- feature slug 全量路径 rename

## Alignment Surface

完成定义以上表 AC 为准；implement/QA 须 integration tier 行为证据与可执行 TC。
