---
slug: beacon-domain-fsm-qa-gate-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: P0 domain FSM QA enforcement
canonical_refs:
  truth: docs/beacon/archive/v1.6.7/features/beacon-domain-fsm-qa-gate-v167/truth.md
  tests: docs/beacon/archive/v1.6.7/features/beacon-domain-fsm-qa-gate-v167/tests.md
  tasks: docs/beacon/archive/v1.6.7/features/beacon-domain-fsm-qa-gate-v167/tasks.md
  evidence: docs/beacon/archive/v1.6.7/features/beacon-domain-fsm-qa-gate-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: Domain FSM QA Gate v1.6.7

## Overview

让 QA/evaluator 在 domain 特征上 **强制** 执行合法路径 walk 与非法转移拒绝，而不是仅跑功能切片 pytest。QA pass 必须绑定 domain-fsm 覆盖率阈值。

## User Intent（一行）

QA 必须验业务序，不能只验接口绿。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-FQA-001 | 合法 walk | **QA 矩阵必须含 ≥1 合法 FSM 全路径** |
| UD-FQA-002 | 非法拒绝 | **QA 矩阵必须含 ≥1 非法转移/无前置用例且期望失败** |
| UD-FQA-003 | Deep | **复杂组合路由 beacon-eval-qa-deep** |
| UD-FQA-004 | Score | **domain_fsm_coverage 进入 scorecard；低于阈值不得 release_ready** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-FQA-001 | matrix-legal | domain 特征 QA 矩阵强制 legal walk 行（**Must**） |
| AC-FQA-002 | matrix-illegal | domain 特征 QA 矩阵强制 illegal/precedence 行（**Must**） |
| AC-FQA-003 | fail-closed | 缺 domain_fsm_coverage 时 qa/release_ready fail-closed（**Must**） |
| AC-FQA-004 | golden-bind | golden commerce 负例被 QA 消费并期望 fail（**Must**） |
| AC-FQA-005 | deep-route | 组合爆炸时推荐 qa-deep（**Should**） |
| AC-FQA-006 | evidence-index | evidence 可索引 FSM walk 结果工件（**Should**） |

## Non-Goals

- 不把 support checklist 当作已强制门禁
- 不在本 lake 内替代其他 harness 职责
- 不交付与本 lake 无关的业务产品实现

## Alignment Surface

本 lake 的完成定义来自上表 AC；implement/QA/release 不得用「文档写了」代替 CLI 门禁与证据。

## Dependencies

- program: `beacon-product-goal-domain-delivery-v167`
- topology: 见 feature-graph.json
