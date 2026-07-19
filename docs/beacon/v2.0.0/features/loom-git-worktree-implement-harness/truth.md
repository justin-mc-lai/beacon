---
slug: loom-git-worktree-implement-harness
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-19 option2: freeze W1-W5 kernel closure lakes under program loom-kernel-closure-w1w5-v200"
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

## Non-Goals

- 默认 `BEACON_V2=1` / loom 覆盖 beacon
- 本湖单独宣称整个 v2.0.0 release 完成
- feature slug 全量路径 rename

## Alignment Surface

完成定义以上表 AC 为准；implement/QA 须 integration tier 行为证据与可执行 TC。
