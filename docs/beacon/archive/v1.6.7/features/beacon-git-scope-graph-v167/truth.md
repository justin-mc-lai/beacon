---
slug: beacon-git-scope-graph-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: GitScopeGraph unified topology for single_repo/monorepo/multi_git_workspace; promotion_ref friction:2e306f7acea7
canonical_refs:
  truth: docs/beacon/archive/v1.6.7/features/beacon-git-scope-graph-v167/truth.md
  tests: docs/beacon/archive/v1.6.7/features/beacon-git-scope-graph-v167/tests.md
  tasks: docs/beacon/archive/v1.6.7/features/beacon-git-scope-graph-v167/tasks.md
  evidence: docs/beacon/archive/v1.6.7/features/beacon-git-scope-graph-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.7/programs/beacon-unified-topology-loop-goal-v167/feature-graph.json
---

# Requirement Truth: Git Scope Graph v1.6.7

## Overview

本 feature 定义 Beacon 统一的 **Git 拓扑合同**：在单仓、monorepo（单 git 根多 service）、多 git workspace（主仓 + 卫星仓）三种场景下，用一张 **`GitScopeGraph`** 管理 admission、dirty policy 与 `topology_gate`，供 `beacon-loop-goal` R7 与 v2 `BranchContext.v1` 消费。

## User Intent（一行）

主仓 + 卫星仓一张图，单项目与多 git monorepo 统一 admission / topology_gate，让 loop-goal precheck 可 fail-closed 且可续跑。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-GSG-001 | 拓扑模型 | **GitScopeGraph.v1** |
| UD-GSG-002 | ProjectTopology | `single_repo` \| `monorepo` \| `multi_git_workspace` |
| UD-GSG-003 | Admission | 每 scope 独立 admission；汇总 `topology_gate_status` |
| UD-GSG-004 | program-level 兼容 | v1.6.2 program-level profile 是 GitScopeGraph 的一种 profile |
| UD-GSG-005 | monorepo dirty | 单 git 根；writable services dirty policy 来自 governance |
| UD-GSG-006 | v2 parity | `GitScopeGraph` 字段对齐 v2 `BranchContext.v1` |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-GSG-001 | schema | 必须定义并写出 `git-scope-graph.v1` schema；含 scopes[] 与 topology_gate_status（**Must**） |
| AC-GSG-002 | single-repo | `single_repo` 仅 1 primary scope；行为与 v1.6.6 单 admission 回归等价（**Must**） |
| AC-GSG-003 | monorepo | `monorepo` 单 git 根；writable service dirty 违反时 topology_gate blocked（**Must**） |
| AC-GSG-004 | multi-git | `multi_git_workspace` 含 satellite scope；任 scope blocked → 汇总 blocked（**Must**） |
| AC-GSG-005 | program-level-profile | `branch_resolution_mode=program-level` 映射为单 scope profile；SidePilot fixture 回归（**Must**） |
| AC-GSG-006 | topology-resolve-cli | `beacon workspace topology-resolve` 写 artifact 并返回 JSON（**Must**） |
| AC-GSG-007 | precheck-bundle | standard execution verification bundle 增加 `topology_gate` 检查项（**Must**） |
| AC-GSG-008 | loop-goal-consume | loop-goal `record_standard_execution_precheck` 拒绝无 topology_gate_ref 的 pass（**Must**） |
| AC-GSG-009 | v2-branch-context-parity | v1 GitScopeGraph fixture 可被 v2 BranchContext parity test 加载（**Must**） |
| AC-GSG-010 | sqlite-ledger-ref | friction/git scope 事件可写入 runtime-ledger `git_scopes` 投影（**Should**） |
