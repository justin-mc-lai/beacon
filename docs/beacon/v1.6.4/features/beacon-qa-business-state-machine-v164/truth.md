---
slug: beacon-qa-business-state-machine-v164
version: v1.6.4
status: frozen
revision_id: R1
language: zh
change_reason: R1 — truth→业务状态机→边界用例 QA 管道（FSM 提取 + 状态覆盖 + 不可达态拒绝）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.4/features/beacon-qa-business-state-machine-v164/truth.md
  user_story: docs/beacon/v1.6.4/features/beacon-qa-business-state-machine-v164/truth.md
  test_case: docs/beacon/v1.6.4/features/beacon-qa-business-state-machine-v164/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：QA Business State Machine v1.6.4

## 概述

beacon 的 state_machine reviewer 仅在 planner 层（审查 truth 是否含状态机），**qa 层无 truth→FSM→边界用例 管道**。用户要求"从需求真相、系统业务状态机进行有效的边界 QA 验证"——需从 truth.md 的 AC 提取业务 FSM（状态集 + 转换集 + 边界态 + 不可达态），生成状态覆盖用例，纳入 qa 验收。

本 feature 建立 truth→FSM 提取 + 状态覆盖 QA 模型，边界态/不可达态 fail-closed，并接入 Phase 2 的 confidence_chain（状态覆盖是置信度输入）。

## User Intent（一行）

从 truth AC 提取业务状态机，边界态/不可达态覆盖可见，不可达态拒绝 fail-closed。

## User Intent Snapshot

- user_prompt: "从需求真相、系统业务状态机进行有效的边界 QA 验证"
- lake_or_ocean: 湖（海级程序已拆，本 feature 单点 FSM 管道，scope 清晰）
- scope_mode: brownfield_takeover（既有 state_machine planner reviewer，做 qa 层落地）
- silent_scope_change_allowed: false
- program_ref: docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 3)
- depends_on: beacon-qa-coverage-confidence-chain-v164 (Phase 2, state coverage 接入 confidence_chain)

## User Decisions（locked）

- UD-001 FSM 来源：从 truth.md 的 State Machine 段落 + AC 提取（非独立 FSM 文件，复用 truth 既有结构）
- UD-002 不可达态处置：fail-closed 拒绝（不可达态被触达 → block，非警告）
- UD-003 边界态定义：状态转换的边界值（初始态/终态/非法转换目标）

## Problem Statement

1. state_machine reviewer 仅在 planner 层审查 truth，qa 层无 FSM 提取。
2. 无状态覆盖模型（转换覆盖 / 边界态覆盖 / 不可达态拒绝）。
3. 无 `state_machine_coverage` 字段。
4. 边界用例无自动推导（从 FSM 生成边界 TC 缺失）。
5. 状态覆盖未接入 confidence_chain（Phase 2 预留接口待填）。

## Non-Goals

- 不重定义 truth.md State Machine 段落格式（复用既有，UD-001）。
- 不做置信度链本身（Phase 2 范围，本 feature 仅接入）。
- 不做 defect 路由（Phase 4 范围）。
- 不做 FSM 形式化验证工具（如 TLA+，仅覆盖模型）。

## 受影响代码面

- `beacon/utils/qa_acceptance.py`：新增 `state_machine_coverage` 字段 + FSM 覆盖计算。
- `beacon/utils/`：新增 `qa_state_machine.py`（truth→FSM 提取 + 边界用例推导 + 不可达态检测）。
- `beacon/utils/coverage.py`：状态覆盖接入 confidence_chain（Phase 2 接口）。
- `tests/test_v164_qa_business_state_machine.py`：TC-SM-001..006。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | fsm-extract | 从 truth.md State Machine 段落 + AC 提取 FSM（状态集 + 转换集 + 边界态 + 不可达态）；提取失败时 block（reason_code `fsm_extract_failed`）（**Must**，UD-001） |
| AC-002 | state-coverage-model | 状态覆盖模型：转换覆盖（每条转换至少 1 TC）+ 边界态覆盖（初始/终态/非法转换目标）（**Must**，UD-003） |
| AC-003 | state-machine-coverage-field | `build_qa_profile_completeness` 输出含 `state_machine_coverage`（转换覆盖率 + 边界态覆盖 + 不可达态列表 + gap）；projection 同步（**Must**） |
| AC-004 | boundary-coverage | 边界态用例自动推导：从 FSM 生成边界 TC（初始态进入 / 终态退出 / 非法转换拒绝）；边界态未覆盖 → 标记 `boundary_gap`（**Must**） |
| AC-005 | unreachable-reject | 不可达态被触达 → fail-closed block（reason_code `unreachable_state_reached`），不记 pass（**Must**，UD-002） |
| AC-006 | confidence-chain-integration | 状态覆盖接入 Phase 2 `confidence_chain`：状态覆盖缺口削弱对应层置信度（`state_machine_gap` 标记）（**Must**，UD-003 from Phase 2） |

## Deferral Ledger

| ID | 项 | user_decision |
|---|---|---|
| UD-001 | FSM 从 truth State Machine 段落提取 | accepted |
| UD-002 | 不可达态 fail-closed 拒绝 | accepted（preamble §4） |
| UD-003 | 边界态 = 初始/终态/非法转换目标 | accepted |
| UD-004 | FSM 形式化验证工具（TLA+ 等） | accepted（延后，仅覆盖模型） |

## State Machine

```
[truth.md State Machine + AC] --AC-001提取--> [FSM: states + transitions + boundary + unreachable]
[FSM] --AC-002/004--> [边界 TC: 转换 / 边界态 / 非法转换]
[边界 TC] --AC-003--> [state_machine_coverage verdict]
[verdict] --AC-005--> [不可达态触达 → block]
[verdict] --AC-006--> [接入 confidence_chain (Phase 2)]
```

## Closed Questions

FSM 来源：truth State Machine 段落（UD-001）。不可达态：block（UD-002）。边界态定义：初始/终态/非法目标（UD-003）。形式化验证：延后（UD-004）。

## Downstream Routes（post-freeze）

- `beacon-gen-implement`：实现 AC-001..006（FSM 提取 + 覆盖模型 + 字段 + 边界推导 + 不可达拒绝 + 链集成）。
- `beacon-eval-qa`：用真实 truth FSM 验证状态覆盖 + 不可达态拒绝。
- Phase 4（defect-repair-loop）依赖本 feature 的 state_machine_coverage finding。
