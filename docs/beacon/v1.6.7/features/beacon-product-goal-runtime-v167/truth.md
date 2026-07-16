---
slug: beacon-product-goal-runtime-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: P1 product goal runtime full lifecycle
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: Product Goal Runtime v1.6.7

## Overview

定义 **Product Goal Runtime**：跨 truth→implement→qa→release 的 run-until-done 完成机。对接宿主 Codex/Claude create_goal/update_goal 语义；完成条件包含 domain-fsm、证据链、持续验收，而不是阶段打卡。Ralph/loop-goal 是其内部控制器，不是 Goal 本身。

## User Intent（一行）

Goal 能跨越全生命周期跑到可验证交付，而不是停在 implement 长跑。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-PGR-001 | Goal 单位 | **产品交付单位 / lake-feature，非单次 prompt** |
| UD-PGR-002 | Done | **done_when 含 domain_fsm + evidence_chain + qa continuous** |
| UD-PGR-003 | Host parity | **对齐 create_goal/update_goal/blocked≥3** |
| UD-PGR-004 | Inner routers | **loop-goal 路由阶段；Ralph 仅 implement** |
| UD-PGR-005 | Release | **release 仍 human gate** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-PGR-001 | state-schema | 定义 product-goal-state.v1（objective/done_when/budget/status/stage_pointer）（**Must**） |
| AC-PGR-002 | cli-surface | beacon goal start|status|pause|resume|complete|tick CLI 合同（**Must**） |
| AC-PGR-003 | host-parity | host /goal 与 CLI 共享或可映射同一 state（**Must**） |
| AC-PGR-004 | done-audit | complete 前必须 CLI verifier（tests/qa/domain）；禁止自述完成（**Must**） |
| AC-PGR-005 | blocked-audit | 同一 blocker 连续 ≥3 goal turn 才可 blocked（**Must**） |
| AC-PGR-006 | lifecycle-span | goal 状态可指向 truth/implement/qa/release_gate 阶段（**Must**） |
| AC-PGR-007 | budget | token/turn budget + pause（**Should**） |
| AC-PGR-008 | intent-queue | 可消费 intent/goal-queue 顶项（**Should**） |

## Non-Goals

- 不把 support checklist 当作已强制门禁
- 不在本 lake 内替代其他 harness 职责
- 不交付与本 lake 无关的业务产品实现

## Alignment Surface

本 lake 的完成定义来自上表 AC；implement/QA/release 不得用「文档写了」代替 CLI 门禁与证据。

## Dependencies

- program: `beacon-product-goal-domain-delivery-v167`
- topology: 见 feature-graph.json
