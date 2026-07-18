---
slug: loom-goal-optional-subagent
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-18: true optional subagent parallel for Loom/goal; parity checklist vs omx/omc"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-goal-optional-subagent/truth.md
  tests: docs/beacon/v2.0.0/features/loom-goal-optional-subagent/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-goal-optional-subagent/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-goal-optional-subagent/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
ux_required: false
design_deferral: "CLI/runtime orchestration; no marketing UI"
---

# Requirement Truth: Loom Goal Optional Subagent (R1)

## Overview

在 **product goal** 主路径上实现 **可选** 子代理并行，闭合今日缺口：

- 今日：`build_parallel_plan` **只产计划**；`spawn_tmux_workers` 仅 QA/implement team
- 目标：`loom goal` / `beacon goal`（compat）在 **opt-in** 下真正：建卫星 worktree → spawn → 回收结果 → **只合并回主星**

对标 **oh-my-codex / oh-my-claude**：**行为清单 parity**，不 1:1 抄壳。

## User Intent

用户说「并行/subagent/多湖」或传 `--subagent` 时，goal **可选**拉起子代理分湖干，而不是只生成 JSON 计划。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-SA-001 | Opt-in | **默认 off**；意图词或 `--subagent` / `--worktree-mode main_star_satellite_pool` 才启用 spawn |
| UD-LOOM-SA-002 | Plan reuse | 复用/强化 `build_parallel_plan`；一湖一卫星 |
| UD-LOOM-SA-003 | Deps | **未满足 depends_on 的湖不 fan-out**（AC-V2-PGO-004） |
| UD-LOOM-SA-004 | Truth write | 卫星 **禁止**写主轨 truth；只合主星 |
| UD-LOOM-SA-005 | Spawn backend | Phase-1：**tmux 或 BEACON_HOST_GOAL_BRIDGE_CMD**；Phase-2 host-native |
| UD-LOOM-SA-006 | OMX/OMC | **行为清单**对齐，非产品克隆 |
| UD-LOOM-SA-007 | Fallback | 无 runtime 时 **显式** single_process + reason；禁止谎称 parallel |
| UD-LOOM-SA-008 | Entry | 挂在 `$loom-goal` / compat `beacon goal`；非第二公共哲学入口 |
| UD-LOOM-SA-009 | Complete | 子代理结果 **不能** 自证 complete/release |

## OMX/OMC 行为清单（Must parity 目标）

| # | Behavior | Loom 要求 |
|---|----------|-----------|
| B1 | 可 opt-in 并行 | UD-LOOM-SA-001 |
| B2 | 每 worker 隔离上下文/目录 | satellite worktree + spec |
| B3 | 明确 ownership | 一湖一卫星 + role |
| B4 | 结果回写主 orchestrator | merge_to_star only |
| B5 | 失败可见 | worker result + execution log |
| B6 | 不伪造并行 | fallback reason 必填 |

## Domain FSM — SubagentSession

| State | Meaning |
|-------|---------|
| idle | 未 opt-in |
| planned | parallel_plan 已生成 |
| arming | 创建 worktree / 写 worker spec |
| running | spawn active |
| collecting | wait results |
| merging | merge to main_star |
| halted | budget/error/user stop |
| done | 本轮 fan-out 结束（非 product complete） |

### Illegal

| From | To | Why |
|------|-----|-----|
| collecting | product completed | 无 verifier |
| satellite | write main truth | I-LOOM-SA-001 |
| idle | running | 无 opt-in |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-LOOM-SA-001 | opt-in | 默认不 spawn；flag/意图才 spawn（**Must**） |
| AC-LOOM-SA-002 | plan-exec | parallel_plan 驱动真实 worktree 创建（**Must**） |
| AC-LOOM-SA-003 | one-lake | 一湖一卫星（**Must**） |
| AC-LOOM-SA-004 | deps | 尊重 feature-graph depends_on（**Must**） |
| AC-LOOM-SA-005 | no-truth-write | 卫星禁写主 truth（**Must**） |
| AC-LOOM-SA-006 | merge-star | 只合并回主星（**Must**） |
| AC-LOOM-SA-007 | spawn | tmux 或 bridge 至少一种可测（**Must**） |
| AC-LOOM-SA-008 | fallback | 无 runtime 时 single_process + reason（**Must**） |
| AC-LOOM-SA-009 | omx-checklist | tests 覆盖 B1–B6（**Must**） |
| AC-LOOM-SA-010 | no-self-cert | fan-out 结束 ≠ complete（**Must**） |
| AC-LOOM-SA-011 | log | spawn/merge 写入 execution.jsonl（**Must**） |
| AC-LOOM-SA-012 | legal-illegal | tests 含 legal/illegal（**Must**） |

## Non-Goals

- 变成通用多代理 OS
- 默认全量并行（费钱/乱写）
- 1:1 复制 omx/omc UI/品牌

## Dependencies

- loom-brand-surface
- beacon-v2-main-star-satellite-pool
- beacon-v2-product-goal-orchestrator
- existing: beacon/utils/subagent_runtime.py, product_goal_runtime.build_parallel_plan

## As-is gap（audit）

- plan only on goal path; spawn used by qa/implement team only
