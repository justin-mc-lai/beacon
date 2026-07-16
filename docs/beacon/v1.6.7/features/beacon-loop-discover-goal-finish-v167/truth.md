---
slug: beacon-loop-discover-goal-finish-v167
version: v1.6.7
status: frozen
revision_id: R2
language: zh
change_reason: "R2 - dual host skills: beacon-loop-goal (discover) vs beacon-goal (finish); queue handoff"
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-loop-discover-goal-finish-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-loop-discover-goal-finish-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-loop-discover-goal-finish-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-loop-discover-goal-finish-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: Loop Discover / Goal Finish Split v1.6.7 (R2)

## Overview

**两个 host-visible 编排 skill，不是一个。**

| Skill | 职责 | 不做什么 |
|-------|------|----------|
| **`beacon-loop-goal`** | 发现、分拣、写入 `goal-queue` / STATE；可定时/会话触发 | 不 mark product complete；不跑满 lifecycle 自证交付 |
| **`beacon-goal`** | 消费 queue 顶项，run-until-done（渐进加载阶段 skill） | 不做无目标的无限发现心跳 |

Program 拆海仍用 **`beacon-pln-program*`**（planner），产出 lakes 供 Goal 并行计划。

## User Intent（一行）

Loop 发现排队；Goal 啃到完成；skill 面一分为二且交接合同明确。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LDG-001 | Loop skill | **`beacon-loop-goal`（既有，角色收窄为 discover）** |
| UD-LDG-002 | Goal skill | **`beacon-goal`（新建，finish）** |
| UD-LDG-003 | Handoff | **`.beacon/state/goal-queue/*.json` + 可选 STATE.md** |
| UD-LDG-004 | Conflict | **同路径活跃 goal 时 loop 不抢写实现分支** |
| UD-LDG-005 | Inventory | **agent surface expected list 同时包含两 skill** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-LDG-001 | queue-schema | goal-queue.v1（**Must**） |
| AC-LDG-002 | loop-write-only | loop 只 append queue，不得 `goal.status=complete`（**Must**） |
| AC-LDG-003 | goal-consume | beacon-goal start 消费顶项（**Must**） |
| AC-LDG-004 | skill-docs | 两 skill SKILL.md 互指边界（**Must**） |
| AC-LDG-005 | inventory | skill inventory/count 接受 beacon-goal 为第 N 个 host skill（**Must**） |
| AC-LDG-006 | v2 | queue schema 进 v2 fixture（**Must**） |

## Non-Goals

- 不删除 beacon-loop-goal
- 不把 program planner 合并进 loop/goal
