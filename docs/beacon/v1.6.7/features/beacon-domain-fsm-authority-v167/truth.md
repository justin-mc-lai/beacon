---
slug: beacon-domain-fsm-authority-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: P0 domain FSM authority; cure empty-castle freeze
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-domain-fsm-authority-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-domain-fsm-authority-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-domain-fsm-authority-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-domain-fsm-authority-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: Domain FSM Authority v1.6.7

## Overview

将 **业务域有限状态机（domain-fsm）** 与 **实体前置序（entity-precedence）** 升级为 feature package 一等权威，并在 freeze / requirement_clarity / truth integrity 路径 **fail-closed**。解决「AC 可绿但业务世界不成立」的空中楼阁根因。完成定义：缺 domain-fsm、缺前置序、缺非法转移覆盖时，不得 freeze。

## User Intent（一行）

domain-fsm + entity-precedence 成为冻结硬门，杜绝无业务序的可绿交付。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-DFSM-001 | 权威位置 | **features/<slug>/truth.md 必含 Domain Model + Domain FSM 章节或等价 machine projection** |
| UD-DFSM-002 | Freeze 门 | **缺 FSM/前置/非法转移 → freeze blocked** |
| UD-DFSM-003 | 与编排状态机分离 | **lifecycle/orchestrator 状态机 ≠ 业务域 FSM** |
| UD-DFSM-004 | Story/TC 拓扑 | **US/TC 必须可映射到 FSM 合法路径；孤儿态/跳态 block** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-DFSM-001 | schema | 定义 domain-fsm.v1 与 entity-precedence.v1 字段合同（状态、转移、guard、非法转移、实体前置）（**Must**） |
| AC-DFSM-002 | truth-section | feature package truth 必须能承载 Domain Model / Domain FSM；resolver 可读（**Must**） |
| AC-DFSM-003 | freeze-hard-gate | freeze 在 complexity 或显式 domain 标记时，缺 FSM/前置/非法转移覆盖 → reason_code 阻断（**Must**） |
| AC-DFSM-004 | clarity-hard | requirement_clarity 对 domain 特征 fail-closed，不得仅 missing_sections 告警后放行（**Must**） |
| AC-DFSM-005 | story-order | user-story/AC 必须引用至少一条合法 FSM 路径；无前置的 AC 被诊断为 orphan（**Must**） |
| AC-DFSM-006 | illegal-required | 每个聚合根至少 1 条非法转移 TC 槽位（**Must**） |
| AC-DFSM-007 | checklist-noncanonical | references/*-checklist 保持 support-only，不得替代本权威（**Must**） |
| AC-DFSM-008 | machine-projection | 可选 .machine/domain-fsm.json 由 truth 投影，单向，drift fail-closed（**Should**） |

## Non-Goals

- 不把 support checklist 当作已强制门禁
- 不在本 lake 内替代其他 harness 职责
- 不交付与本 lake 无关的业务产品实现

## Alignment Surface

本 lake 的完成定义来自上表 AC；implement/QA/release 不得用「文档写了」代替 CLI 门禁与证据。

## Dependencies

- program: `beacon-product-goal-domain-delivery-v167`
- topology: 见 feature-graph.json
