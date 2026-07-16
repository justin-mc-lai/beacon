---
slug: beacon-loop-discover-goal-finish-v167
version: v1.6.7
status: frozen
revision_id: R3
language: zh
change_reason: "R3 - beacon-loop-goal is support/internal discovery only; not co-equal public entry"
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

# Requirement Truth: Loop as Support Discovery v1.6.7 (R3)

## Overview

**用户不需要「两个主编排」。**

| Skill | 调用层级 | 职责 |
|-------|----------|------|
| **`beacon-goal`** | **唯一公共入口** | 一句话目标 → 验收 |
| **`beacon-loop-goal`** | **support / internal** | 发现、分拣、写 queue；可被 goal 内部调用或定时心跳 |
| `beacon-pln-program*` | support planner | 显式拆海时用 |

`beacon-loop-goal` **可以保留 host 目录**（兼容、调试），但：

1. description 必须标明 **support**
2. 主路由 / 30 秒用法 **不得** 要求用户先调它
3. 不得 mark product complete

## User Intent（一行）

Loop 降为发现支持面；Goal 独占用户侧一句话交付入口。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LDG-001 | Public entry | **仅 beacon-goal** |
| UD-LDG-002 | Loop tier | **support/internal discovery** |
| UD-LDG-003 | Handoff | **goal-queue；由 goal 消费** |
| UD-LDG-004 | Docs | **主路径不展示双 skill 流水线** |
| UD-LDG-005 | Compatibility | **旧 `$beacon-loop-goal` 调用仍可用，但应 redirect/说明改用 goal 做交付** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-LDG-001 | support-meta | loop-goal skill frontmatter/description 含 support 语义（**Must**） |
| AC-LDG-002 | no-coequal | program/SUMMARY/examples 不把 loop 与 goal 并列为两主编排入口（**Must**） |
| AC-LDG-003 | queue | 仍可写 goal-queue 供 goal 消费（**Must**） |
| AC-LDG-004 | no-complete | loop 不得 product complete（**Must**） |
| AC-LDG-005 | redirect | loop skill 正文指向「交付请用 beacon-goal」（**Must**） |

## Non-Goals

- 不删除 loop-goal 代码路径
- 不禁止高级用户显式调用 support 面
