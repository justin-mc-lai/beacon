---
slug: beacon-ui-design-ship-gate-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: P1 UI design philosophy ship gate
canonical_refs:
  truth: docs/beacon/archive/v1.6.7/features/beacon-ui-design-ship-gate-v167/truth.md
  tests: docs/beacon/archive/v1.6.7/features/beacon-ui-design-ship-gate-v167/tests.md
  tasks: docs/beacon/archive/v1.6.7/features/beacon-ui-design-ship-gate-v167/tasks.md
  evidence: docs/beacon/archive/v1.6.7/features/beacon-ui-design-ship-gate-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: UI Design Philosophy Ship Gate v1.6.7

## Overview

将 UI 视觉交付与 **软件设计哲学**（DESIGN.md / design contracts / UI state matrix）绑定到 ship/release 门。每个业务态必须有对应 UI 表面；禁止「页面能打开」代替设计对齐。

## User Intent（一行）

有 UX 的交付必须设计哲学与 FSM 态一致，才可 ship。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-UID-001 | DESIGN 权威 | **存在 DESIGN.md 或 docs/beacon/<v>/design/* 时为绑定合同** |
| UD-UID-002 | State matrix | **业务态→UI 表面矩阵必填（domain 特征）** |
| UD-UID-003 | Ship gate | **缺矩阵/设计基线 → release_ready fail-closed（UX feature）** |
| UD-UID-004 | Implement | **implement 必须读 DESIGN，禁止硬编码覆盖 token** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-UID-001 | matrix-schema | ui-state-matrix.v1 绑定 domain-fsm 状态（**Must**） |
| AC-UID-002 | design-required | UX feature 无 DESIGN 且无 deferral → freeze/ship block（**Must**） |
| AC-UID-003 | ship-gate | release scorecard 增加 design_alignment / ui_state_matrix 检查（**Must**） |
| AC-UID-004 | implement-read | implement skill/CLI precheck 记录 DESIGN 已读证据（**Should**） |
| AC-UID-005 | qa-visual | QA 可索引视觉/态徽章一致性检查（**Should**） |
| AC-UID-006 | golden-link | golden commerce 含最小 state matrix（**Must**） |

## Non-Goals

- 不把 support checklist 当作已强制门禁
- 不在本 lake 内替代其他 harness 职责
- 不交付与本 lake 无关的业务产品实现

## Alignment Surface

本 lake 的完成定义来自上表 AC；implement/QA/release 不得用「文档写了」代替 CLI 门禁与证据。

## Dependencies

- program: `beacon-product-goal-domain-delivery-v167`
- topology: 见 feature-graph.json
