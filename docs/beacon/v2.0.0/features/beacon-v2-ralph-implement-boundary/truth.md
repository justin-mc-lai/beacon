---
slug: beacon-v2-ralph-implement-boundary
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "W3 Ralph implement-only boundary under Product Goal; parity v1.6.7"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-ralph-implement-boundary/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-ralph-implement-boundary/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-ralph-implement-boundary/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-ralph-implement-boundary/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
upstream_ref: docs/beacon/v1.6.7/features/beacon-ralph-implement-boundary-v167/truth.md
---

# Requirement Truth: v2 Ralph Implement Boundary (R1)

## Overview

合同化：**Ralph 仅是 implement 子控制器**。  
不得替代 truth/QA/release，不得作为 product goal 完成权威。  
Product Goal 可在 implement 阶段委托 Ralph 多轮，但 done_when 仍在 Goal + evaluator。

## User Intent（一行）

防止用实现长跑冒充产品交付完成。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-V2-RLP-001 | 范围 | 仅 implement mode=ralph / implement-loop 子控制器 |
| UD-V2-RLP-002 | 禁止 | 不得写 truth、不得发 QA/release verdict |
| UD-V2-RLP-003 | 委托 | Product Goal 可 delegate implement rounds to Ralph |
| UD-V2-RLP-004 | 完成 | Ralph finalize ≠ product complete |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-RLP-001 | skill-contract | implement-ralph / skill 明示边界（**Must**） |
| AC-V2-RLP-002 | runtime-guard | ralph runtime 不得设置 qa_verdict/release_verdict（**Must**） |
| AC-V2-RLP-003 | goal-delegate | product-goal state 可记录 implement_delegate=ralph（**Must**） |
| AC-V2-RLP-004 | handoff | ralph handoff 仅到 qa/review/repair routes（**Must**） |
| AC-V2-RLP-005 | tests | contract tests 锁边界（**Must**） |
| AC-V2-RLP-006 | no-default-v2 | 与 DEF-SE-004 一致：不得用 Ralph 长跑作为切默认 BEACON_V2 的证据（**Must**） |

## Non-Goals

- 不删除 Ralph 能力
- 不禁止 Goal 委托 implement rounds
