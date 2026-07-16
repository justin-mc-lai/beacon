---
slug: beacon-loop-discover-goal-finish-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: P2 loop discovers goal finishes
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

# Requirement Truth: Loop Discover / Goal Finish Split v1.6.7

## Overview

对齐 loop-engineering：Loop 只做发现与 STATE/goal-queue 写入；Goal Runtime 负责跑到 done。禁止 loop-goal 继续冒充 product goal 完成机。

## User Intent（一行）

Loop 发现，Goal 完成；两者契约化分工。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LDG-001 | Loop 职责 | **discovery + triage + queue append** |
| UD-LDG-002 | Goal 职责 | **run-until-done on queue item** |
| UD-LDG-003 | Handoff | **STATE.md 或 .beacon/state/goal-queue 交接合同** |
| UD-LDG-004 | Conflict | **同文件活跃 goal 时 loop 暂停写冲突路径** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-LDG-001 | queue-schema | goal-queue.v1 字段合同（**Must**） |
| AC-LDG-002 | loop-write | loop heartbeat/triage 只写 queue/STATE，不标 complete（**Must**） |
| AC-LDG-003 | goal-consume | product-goal start 可消费 queue 顶项（**Must**） |
| AC-LDG-004 | boundary-docs | loop-goal skill 明示非 product goal（**Must**） |
| AC-LDG-005 | pause-on-conflict | 冲突路径 pause 语义（**Should**） |

## Non-Goals

- 不把 support checklist 当作已强制门禁
- 不在本 lake 内替代其他 harness 职责
- 不交付与本 lake 无关的业务产品实现

## Alignment Surface

本 lake 的完成定义来自上表 AC；implement/QA/release 不得用「文档写了」代替 CLI 门禁与证据。

## Dependencies

- program: `beacon-product-goal-domain-delivery-v167`
- topology: 见 feature-graph.json
