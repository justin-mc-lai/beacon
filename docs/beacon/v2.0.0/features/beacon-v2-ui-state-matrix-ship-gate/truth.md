---
slug: beacon-v2-ui-state-matrix-ship-gate
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "V2SE-006 locked - full inherit v1.6.7 ui-state-matrix ship hard gate (not design_primitives-only)"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-ui-state-matrix-ship-gate/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-ui-state-matrix-ship-gate/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-ui-state-matrix-ship-gate/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-ui-state-matrix-ship-gate/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
upstream_ref: docs/beacon/v1.6.7/features/beacon-ui-design-ship-gate-v167/truth.md
---

# Requirement Truth: v2 UI State Matrix Ship Gate (R1)

## Overview

**完整继承** v1.6.7 UI Design Philosophy Ship Gate：  
UX/视觉交付必须绑定 **DESIGN + ui-state-matrix.v1（业务态→UI 表面）**，并进入 freeze/ship/release 硬门。

与 redesign `design_primitives.v1` 的关系：

- `design_primitives` 是实现前绑定原语（必要但不充分）
- **ui-state-matrix.v1 是 v2 ship 硬合同**（V2SE-006 locked）
- 仅有 design_primitives、无 ui-state-matrix → **不得** release_ready（UX feature）

## User Intent（一行）

有 UX 的 v2 交付必须设计哲学与 domain FSM 态一致，才可 ship。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-V2-UID-001 | DESIGN 权威 | DESIGN.md 或 docs/beacon/<v>/design/* 为绑定合同 |
| UD-V2-UID-002 | State matrix | **业务态→UI 表面矩阵必填（domain UX 特征）** |
| UD-V2-UID-003 | Ship gate | 缺矩阵/设计基线 → release_ready fail-closed |
| UD-V2-UID-004 | Full inherit | **完整继承** v1.6.7 AC-UID-001..006 语义，不得降级为 primitives-only |
| UD-V2-UID-005 | Implement | implement 必须读 DESIGN；禁止硬编码覆盖 token |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-UID-001 | matrix-schema | ui-state-matrix.v1 绑定 domain-fsm 状态（**Must**） |
| AC-V2-UID-002 | design-required | UX feature 无 DESIGN 且无 deferral → freeze/ship block（**Must**） |
| AC-V2-UID-003 | ship-gate | release scorecard 含 design_alignment **与** ui_state_matrix（**Must**） |
| AC-V2-UID-004 | not-primitives-only | 仅 design_primitives 不足以致 release_ready（UX）（**Must**） |
| AC-V2-UID-005 | implement-read | implement precheck 记录 DESIGN 已读证据（**Should**） |
| AC-V2-UID-006 | qa-visual | QA 可索引态徽章/视觉一致性（**Should**） |
| AC-V2-UID-007 | golden-link | golden commerce 含最小 state matrix（**Must**） |
| AC-V2-UID-008 | parity | v1.6.7 ui ship-gate fixture/语义可被 v2 加载对照（**Must**） |

## Non-Goals

- 不强制无 UX 的纯 kernel 湖也填 ui-state-matrix（`design_required=false` 时豁免）
- 不替代 domain-fsm-authority

## Alignment Surface

本 lake 完成定义来自上表；不得用「有 DESIGN 文字」代替 matrix 门禁。
