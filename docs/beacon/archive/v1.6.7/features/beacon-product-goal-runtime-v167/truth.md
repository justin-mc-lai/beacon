---
slug: beacon-product-goal-runtime-v167
version: v1.6.7
status: frozen
revision_id: R3
language: zh
change_reason: "R3 - single public entry beacon-goal (or beacon run); loop-goal is support discovery only; 30s UX"
canonical_refs:
  truth: docs/beacon/archive/v1.6.7/features/beacon-product-goal-runtime-v167/truth.md
  tests: docs/beacon/archive/v1.6.7/features/beacon-product-goal-runtime-v167/tests.md
  tasks: docs/beacon/archive/v1.6.7/features/beacon-product-goal-runtime-v167/tasks.md
  evidence: docs/beacon/archive/v1.6.7/features/beacon-product-goal-runtime-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: Product Goal Runtime v1.6.7 (R3)

## Overview

**对用户只有一个入口：`beacon-goal`（CLI 等价 `beacon goal run` / 可选别名 `beacon run`）。**

一句话目标 → 自动拆解需求、编排执行、持续验收，直到 `done_when` 通过（release 仍可人工确认）。

内部模块可以拆（discover / finish / ralph / program），**不得**要求用户先调 loop 再调 goal。

## Public call surface（Must — 调用侧简单）

| 入口 | 可见性 | 用户是否需要记 |
|------|--------|----------------|
| **`$beacon-goal` / `beacon goal run "<目标>"`** | **唯一主编排入口** | **只要记这一个** |
| `beacon run "<目标>"` | 可选别名 → goal run | 可选 |
| `$beacon-loop-goal` | **support / internal discovery** | **默认不出现在主文档调用路径** |
| `$beacon-pln-program*` | planner 支持面 | 仅调试/显式拆海时 |
| `$beacon-gen-implement --mode ralph` | implement 子控制器 | 由 goal 委托，用户不手点 |

### 用户本意映射

```text
用户：做一个 X，验收通过
     ↓
唯一入口：beacon-goal
     ↓ 内部（对用户不可见）
  pln-program? → gen-truth → gen-implement(ralph?) → eval-qa → release_gate
  可选：loop-goal 只写 queue / 心跳发现
```

## User Intent（一行）

一句话目标，Beacon 自动拆需求、编排到验收；调用侧不暴露双主编排。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-PGR-001 | Goal 单位 | **产品交付单位 / lake-feature** |
| UD-PGR-002 | Done | **domain_fsm + evidence_chain + continuous qa** |
| UD-PGR-003 | Host parity | **create_goal/update_goal/blocked≥3** |
| UD-PGR-004 | Inner | **可委托 loop 子步骤、ralph implement** |
| UD-PGR-005 | Release | **human gate** |
| UD-PGR-006 | **Public entry** | **唯一：`beacon-goal`（+ CLI `beacon goal run` / 可选 `beacon run`）** |
| UD-PGR-007 | Loop skill | **`beacon-loop-goal` = support discovery only，非并列主编排** |
| UD-PGR-008 | Progressive load | **按阶段加载 skill，默认不全量** |
| UD-PGR-009 | Sub-agent | **意图/program 声明时可并行** |
| UD-PGR-010 | Worktree | **`single_worktree` \| `main_star_satellite_pool`** |
| UD-PGR-011 | Docs | **主文档/examples 只教单入口 30 秒用法** |
| UD-PGR-012 | v2 | **v2 同构：单入口 + support loop** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-PGR-001 | single-entry | 用户主路径只需 `beacon-goal` / `beacon goal run`（**Must**） |
| AC-PGR-002 | no-dual-call | 主文档与 host router **不得**要求「先 loop 后 goal」（**Must**） |
| AC-PGR-003 | facade | `beacon-goal` 门面内完成：拆解→truth→implement→qa→（release 门）（**Must**） |
| AC-PGR-004 | loop-support | `beacon-loop-goal` 元数据/描述标 support；inventory 可保留但路由为 support（**Must**） |
| AC-PGR-005 | alias | `beacon run` 可映射到 `beacon goal run`（**Should**） |
| AC-PGR-006 | progressive | 阶段 skill 渐进加载（**Must**） |
| AC-PGR-007 | parallel | parallel_plan + 主星卫星 pool（**Must**，承 R2） |
| AC-PGR-008 | done-audit | complete 需 verifier（**Must**） |
| AC-PGR-009 | example-30s | `skills/beacon/examples/goal-one-shot-30s.md` 存在且只教单入口（**Must**） |
| AC-PGR-010 | host-router | `skills/beacon/SKILL.md` 标明 goal 为一句话交付入口（**Must**） |
| AC-PGR-011 | v2-parity | v2 orchestrator 合同同步单入口（**Must**） |

## Non-Goals

- 不强迫用户理解 discover/finish 两个按钮
- 不删除 loop-goal 实现能力，只降调用层级

## Dependencies

- domain-fsm-authority, loop-discover-goal-finish (support role), git-scope-graph
