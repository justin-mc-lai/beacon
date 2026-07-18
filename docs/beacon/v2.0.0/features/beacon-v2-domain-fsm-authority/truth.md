---
slug: beacon-v2-domain-fsm-authority
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "W3 Option A - domain FSM freeze hard gate parity with v1.6.7; planner user decisions 2026-07-17"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-authority/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-authority/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-authority/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-authority/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
upstream_ref: docs/beacon/v1.6.7/features/beacon-domain-fsm-authority-v167/truth.md
---

# Requirement Truth: v2 Domain FSM Authority (R1)

## Overview

将 **业务域有限状态机（domain-fsm）** 与 **实体前置序（entity-precedence）** 升级为 v2 feature package 一等权威，并在 freeze / requirement_clarity / truth integrity 路径 **fail-closed**。  
与 v1.6.7 `beacon-domain-fsm-authority-v167` **完成定义等价**；实现落在 Rust gate/core 类型 + MD resolver，**不**把具体业务 FSM 内嵌 `beacon-core`。

## User Intent（一行）

domain-fsm + entity-precedence 成为 v2 冻结硬门，杜绝无业务序的可绿交付。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-V2-DFSM-001 | 权威位置 | features/<slug>/truth.md 必含 Domain Model + Domain FSM 或等价 machine projection |
| UD-V2-DFSM-002 | Freeze 门 | 缺 FSM/前置/非法转移 → freeze blocked |
| UD-V2-DFSM-003 | 与编排分离 | lifecycle/orchestrator FSM ≠ 业务域 FSM |
| UD-V2-DFSM-004 | Program | Option A：本 lake 归属 `beacon-v2-product-goal-parallel-v200` |
| UD-V2-DFSM-005 | 非目标 | 禁止把具体电商/业务 FSM 写进 beacon-core |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-DFSM-001 | schema | domain-fsm.v1 与 entity-precedence.v1 字段合同（状态、转移、guard、非法转移、实体前置）（**Must**） |
| AC-V2-DFSM-002 | truth-section | feature package truth 可承载 Domain Model / Domain FSM；resolver 可读（**Must**） |
| AC-V2-DFSM-003 | freeze-hard-gate | 缺 FSM/前置/非法转移覆盖 → reason_code 阻断 freeze（**Must**） |
| AC-V2-DFSM-004 | clarity-hard | requirement_clarity 对 domain 特征 fail-closed（**Must**） |
| AC-V2-DFSM-005 | story-order | US/AC 须映射合法 FSM 路径；孤儿态/跳态 block（**Must**） |
| AC-V2-DFSM-006 | illegal-required | 每聚合根 ≥1 非法转移 TC 槽位（**Must**） |
| AC-V2-DFSM-007 | parity | v1.6.7 domain-fsm fixture 可被 v2 gate 加载并给出等价 blocked/pass 语义（**Must**） |
| AC-V2-DFSM-008 | machine-projection | 可选 .machine/domain-fsm.json 由 truth 单向投影，drift fail-closed（**Should**） |

## Non-Goals

- 不内嵌具体业务产品 FSM 到 beacon-core
- 不把 support checklist 当作已强制门禁
- 不替代 QA/release harness 职责

## Alignment Surface

完成定义来自上表 AC；implement/QA/release 不得用「文档写了」代替 CLI 门禁与证据。
