---
slug: beacon-v2-main-star-satellite-pool
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: v2 product goal parallel + main-star satellite; parity with v1.6.7 R2
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-main-star-satellite-pool/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-main-star-satellite-pool/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-main-star-satellite-pool/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-main-star-satellite-pool/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
---

# Requirement Truth: v2 Main-Star Satellite Worktree Pool


## Overview

实现 **主星 / 卫星** worktree pool：

- **主星（main-star）**：integration 分支；负责合入、跨湖回归、QA、release 协调
- **卫星（satellite）**：每个可并行 **湖（feature）** 一个 worktree + 子代理
- 卫星完成局部 implement 验证后 **merge 回主星**，不得直写 truth_canonical 需求真相

## Modes

| Mode | Behavior |
|------|----------|
| `single_worktree` | 串行，一 goal 一 worktree |
| `main_star_satellite_pool` | 主星 + N 卫星并行 |

## User Decisions

| ID | Value |
|----|-------|
| UD-V2-MSS-001 | BranchContext 记录 star vs satellite role |
| UD-V2-MSS-002 | topology_gate 对每个 satellite scope 独立 admission |
| UD-V2-MSS-003 | Merge target = main-star integration branch only |


## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-MSS-001 | modes | 支持 single_worktree 与 main_star_satellite_pool（**Must**） |
| AC-V2-MSS-002 | allocate | 一湖一卫星 worktree；依赖未满足不分配（**Must**） |
| AC-V2-MSS-003 | merge | 卫星 merge 仅到主星 integration；冲突可判定 blocked（**Must**） |
| AC-V2-MSS-004 | truth | 卫星禁止写 docs/beacon feature truth 权威（**Must**） |
| AC-V2-MSS-005 | branch-context | v2 BranchContext 含 star/satellite + lake slug（**Must**） |
| AC-V2-MSS-006 | topology | 复用/扩展 GitScopeGraph topology_gate（**Must**） |
