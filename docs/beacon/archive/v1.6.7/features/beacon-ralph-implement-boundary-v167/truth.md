---
slug: beacon-ralph-implement-boundary-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: P2 Ralph implement-only boundary under Product Goal
canonical_refs:
  truth: docs/beacon/archive/v1.6.7/features/beacon-ralph-implement-boundary-v167/truth.md
  tests: docs/beacon/archive/v1.6.7/features/beacon-ralph-implement-boundary-v167/tests.md
  tasks: docs/beacon/archive/v1.6.7/features/beacon-ralph-implement-boundary-v167/tasks.md
  evidence: docs/beacon/archive/v1.6.7/features/beacon-ralph-implement-boundary-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: Ralph Implement Boundary v1.6.7

## Overview

合同化：**Ralph 仅是 implement 子控制器**。不得替代 truth/QA/release，不得作为 product goal。Product Goal 可在 implement 阶段委托 Ralph 多轮修，但完成权威仍在 Goal done_when + evaluator。

## User Intent（一行）

明确 Ralph 边界，防止用实现长跑冒充产品交付完成。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-RLP-001 | 范围 | **仅 implement mode=ralph** |
| UD-RLP-002 | 禁止 | **不得写 truth、不得发 QA/release verdict** |
| UD-RLP-003 | 委托 | **Product Goal 可 delegate implement rounds to Ralph** |
| UD-RLP-004 | 完成 | **Ralph finalize ≠ product complete** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-RLP-001 | skill-contract | implement-ralph.md + skill 明示边界（**Must**） |
| AC-RLP-002 | runtime-guard | ralph_runtime 不得设置 qa_verdict/release_verdict（**Must**） |
| AC-RLP-003 | goal-delegate | product-goal state 可记录 implement_delegate=ralph（**Must**） |
| AC-RLP-004 | handoff | ralph handoff 仅到 qa/review/repair routes（**Must**） |
| AC-RLP-005 | tests | contract tests 锁边界（**Must**） |

## Non-Goals

- 不把 support checklist 当作已强制门禁
- 不在本 lake 内替代其他 harness 职责
- 不交付与本 lake 无关的业务产品实现

## Alignment Surface

本 lake 的完成定义来自上表 AC；implement/QA/release 不得用「文档写了」代替 CLI 门禁与证据。

## Dependencies

- program: `beacon-product-goal-domain-delivery-v167`
- topology: 见 feature-graph.json
