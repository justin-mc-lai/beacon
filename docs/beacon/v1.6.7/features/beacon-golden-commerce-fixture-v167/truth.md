---
slug: beacon-golden-commerce-fixture-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: P0 golden commerce fixture positive+negative
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-golden-commerce-fixture-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-golden-commerce-fixture-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-golden-commerce-fixture-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-golden-commerce-fixture-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: Golden Commerce Fixture v1.6.7

## Overview

提供 **canonical golden fixture**：可冻结的迷你电商结账域（Product→Cart→Order FSM），作为 skill/agent 的完整示范；并包含 **负例**（无商品直接下单）必须在 freeze 或 QA 失败。本 lake 交付 fixture 与文档示范，不交付真实电商业务系统。

## User Intent（一行）

冻结一份正例+坏例的完整业务产品示范，消灭 skill 无样板问题。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-GOLD-001 | Fixture 路径 | **docs/beacon/v1.6.7/fixtures/golden-commerce-checkout/** |
| UD-GOLD-002 | 负例 | **order_without_product 必须 fail freeze 或 fail QA** |
| UD-GOLD-003 | Skill 引用 | **beacon-gen-truth / examples 必须指向本 fixture 为推荐完整示范** |
| UD-GOLD-004 | 范围 | **示范与门禁夹具，非生产电商** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-GOLD-001 | positive-package | 正例 fixture 含 truth/tests/tasks/evidence + domain-fsm + entity-precedence（**Must**） |
| AC-GOLD-002 | negative-package | 坏例 fixture 或负例矩阵：无 Product 创建 Order 必须失败（**Must**） |
| AC-GOLD-003 | fsm-content | 至少覆盖 Product 与 Order 两聚合根状态与合法/非法转移（**Must**） |
| AC-GOLD-004 | skill-pointer | skills/beacon/examples 增加指向本 fixture 的完整示范入口（**Must**） |
| AC-GOLD-005 | agent-readable | fixture 可作为 materialize/validate 的可读输入（**Should**） |
| AC-GOLD-006 | design-stub | 含最小 DESIGN.md 或 UI state matrix stub 绑定订单态徽章（**Should**） |

## Non-Goals

- 不把 support checklist 当作已强制门禁
- 不在本 lake 内替代其他 harness 职责
- 不交付与本 lake 无关的业务产品实现

## Alignment Surface

本 lake 的完成定义来自上表 AC；implement/QA/release 不得用「文档写了」代替 CLI 门禁与证据。

## Dependencies

- program: `beacon-product-goal-domain-delivery-v167`
- topology: 见 feature-graph.json
