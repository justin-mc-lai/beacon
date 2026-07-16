---
slug: beacon-v2-product-goal-orchestrator
version: v2.0.0
status: frozen
revision_id: R2
language: zh
change_reason: R2 single public entry beacon-goal; loop support-only; parity v1.6.7 R3
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
---

# Requirement Truth: v2 Product Goal Orchestrator (R2)

## Overview

Rust Operator Spine 实现 Product Goal Runtime，**调用侧与 v1.6.7 R3 相同：唯一入口 `beacon-goal`**。

## Public entry

| 入口 | 层级 |
|------|------|
| `beacon-goal` / `beacon goal run` | **唯一公共交付入口** |
| `beacon run` | 可选别名 |
| `beacon-loop-goal` | support discovery only |

## User Decisions

| ID | Value |
|----|-------|
| UD-V2-PGO-001 | Rust orchestrator is runtime source; Python compat shim |
| UD-V2-PGO-002 | Progressive skill load map data-driven |
| UD-V2-PGO-003 | Sub-agent fan-out only for lakes without unmet depends_on |
| UD-V2-PGO-004 | Single public facade `beacon-goal` |
| UD-V2-PGO-005 | loop-goal support tier only |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-PGO-001 | parity | 加载 v1.6.7 product-goal-state schema fixture 并通过 parity test（**Must**） |
| AC-V2-PGO-002 | skill | 暴露 beacon-goal host skill + CLI（**Must**） |
| AC-V2-PGO-003 | progressive | 阶段 skill map 可配置且默认不全量加载（**Must**） |
| AC-V2-PGO-004 | subagent | parallel_plan 驱动 sub-agent；尊重 feature-graph 依赖（**Must**） |
| AC-V2-PGO-005 | done | complete 需 verifier；禁止自述（**Must**） |
| AC-V2-PGO-006 | compat | Python CLI 入口保持 `beacon goal`（**Must**） |
| AC-V2-PGO-007 | single-entry | 用户主路径仅 beacon-goal；loop 为 support（**Must**） |
| AC-V2-PGO-008 | docs | 30s 用法与 v1 同构引用（**Must**） |
