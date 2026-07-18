---
slug: beacon-v2-domain-fsm-qa-gate
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "W3 domain FSM QA enforcement parity with v1.6.7"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-qa-gate/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-qa-gate/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-qa-gate/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-qa-gate/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
upstream_ref: docs/beacon/v1.6.7/features/beacon-domain-fsm-qa-gate-v167/truth.md
---

# Requirement Truth: v2 Domain FSM QA Gate (R1)

## Overview

v2 QA/evaluator 在 domain 特征上 **强制** 合法路径 walk 与非法转移拒绝；QA pass 绑定 domain_fsm_coverage 阈值，低于阈值不得 release_ready。

## User Intent（一行）

QA 必须验业务序，不能只验接口绿。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-V2-FQA-001 | 合法 walk | QA 矩阵 ≥1 合法 FSM 全路径 |
| UD-V2-FQA-002 | 非法拒绝 | ≥1 非法/无前置期望失败 |
| UD-V2-FQA-003 | Score | domain_fsm_coverage 进 scorecard；低于阈值不得 release_ready |
| UD-V2-FQA-004 | Golden | 消费 golden commerce 负例 |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-FQA-001 | matrix-legal | domain 特征 QA 强制 legal walk 行（**Must**） |
| AC-V2-FQA-002 | matrix-illegal | domain 特征 QA 强制 illegal/precedence 行（**Must**） |
| AC-V2-FQA-003 | fail-closed | 缺 domain_fsm_coverage → qa/release_ready fail-closed（**Must**） |
| AC-V2-FQA-004 | golden-bind | golden 负例被 QA 消费并期望 fail（**Must**） |
| AC-V2-FQA-005 | deep-route | 组合爆炸推荐 qa-deep（**Should**） |
| AC-V2-FQA-006 | evidence-index | evidence 可索引 FSM walk 工件（**Should**） |

## Non-Goals

- 不把 checklist 当强制门禁
- 不替代 freeze 侧 domain-fsm-authority
