---
slug: beacon-v2-product-goal-orchestrator
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: v2 product goal parallel + main-star satellite; parity with v1.6.7 R2
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

# Requirement Truth: v2 Product Goal Orchestrator


## Overview

Rust Operator Spine 实现 Product Goal Runtime：

- host skill **`beacon-goal`** + CLI `beacon goal`
- 与 **`beacon-loop-goal`** 双 skill 分工（发现 vs 完成）
- **渐进式 skill 加载**（阶段映射）
- 用户意图 / program graph 触发 **并行 sub-agent**
- done_when / blocked≥3 / release human gate 与 v1.6.7 R2 同构

## User Decisions

| ID | Value |
|----|-------|
| UD-V2-PGO-001 | Rust orchestrator is source of runtime truth; Python is compat shim |
| UD-V2-PGO-002 | Progressive skill load map is data-driven JSON in ~/.beacon or project .beacon |
| UD-V2-PGO-003 | Sub-agent fan-out only for lakes without unmet depends_on |


## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-PGO-001 | parity | 加载 v1.6.7 product-goal-state schema fixture 并通过 parity test（**Must**） |
| AC-V2-PGO-002 | skill | 暴露 beacon-goal host skill + CLI（**Must**） |
| AC-V2-PGO-003 | progressive | 阶段 skill map 可配置且默认不全量加载（**Must**） |
| AC-V2-PGO-004 | subagent | parallel_plan 驱动 sub-agent；尊重 feature-graph 依赖（**Must**） |
| AC-V2-PGO-005 | done | complete 需 verifier；禁止自述（**Must**） |
| AC-V2-PGO-006 | compat | Python CLI 入口保持 `beacon goal`（**Must**） |
