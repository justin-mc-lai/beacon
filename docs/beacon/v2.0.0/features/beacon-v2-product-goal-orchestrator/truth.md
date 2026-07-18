---
slug: beacon-v2-product-goal-orchestrator
version: v2.0.0
status: frozen
revision_id: R3
language: zh
change_reason: "R3 - lock user decisions 2026-07-17: Option A domain chain program merge; full ui-state-matrix inherit; reject early BEACON_V2 default; SE-V2 binding"
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

# Requirement Truth: v2 Product Goal Orchestrator (R3)

## Overview

Rust Operator Spine 实现 Product Goal Runtime，**调用侧与 v1.6.7 R3 相同：唯一入口 `beacon-goal`**。

R3 将 planner 确认的迁移场景与用户三决策写入合同：Domain 真值链并入本 program（Option A）；ui-state-matrix 完整继承；拒绝 W4 前默认 `BEACON_V2=1`。

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
| UD-V2-PGO-006 | Domain truth chain lakes merge into program Option A（DEF-SE-001） |
| UD-V2-PGO-007 | Done_when includes domain_fsm + evidence_chain + continuous qa when domain-bearing |
| UD-V2-PGO-008 | UX ship requires full ui-state-matrix inherit（V2SE-006）；design_primitives 不足 |
| UD-V2-PGO-009 | Reject default `BEACON_V2=1` before Wave W4 exit（DEF-SE-004） |
| UD-V2-PGO-010 | SE standards binding: `docs/beacon/v2.0.0/execution/v2-software-engineering-standards.md` |

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
| AC-V2-PGO-009 | program-merge | program topology 含 domain 真值链 5 lakes（Option A）（**Must**） |
| AC-V2-PGO-010 | done-domain | domain-bearing goal 的 done_when 绑定 domain_fsm_coverage（**Must**） |
| AC-V2-PGO-011 | no-early-default | 发布材料与 runtime 不得在 W4 前宣称默认 BEACON_V2=1（**Must**） |
| AC-V2-PGO-012 | se-binding | gate/orchestrator 变更不得违反 SE-V2-00..13（**Must**） |

## Non-Goals

- 不在本 lake 实现 domain-fsm schema 细节（见 domain-fsm-authority）
- 不默认切换全局 v2 runtime

## Dependencies

- program lakes: main-star, domain-fsm-authority, golden, domain-fsm-qa-gate, ui-state-matrix-ship-gate, ralph-boundary

## Related lake (additive 2026-07-18)

Long-run AgentDriver and durable supervisor parity live in **`beacon-v2-goal-durable-longrun`** (not this lake’s non-goals). Orchestrator must expose hooks for:

- `--longrun` / longrun intent
- AgentDriver requeue
- resume-pack injection

See `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md`.

