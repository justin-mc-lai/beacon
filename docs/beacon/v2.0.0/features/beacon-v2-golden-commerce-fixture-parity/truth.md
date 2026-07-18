---
slug: beacon-v2-golden-commerce-fixture-parity
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "W3 golden commerce positive+negative parity clamps from v1.6.7"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-golden-commerce-fixture-parity/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-golden-commerce-fixture-parity/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-golden-commerce-fixture-parity/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-golden-commerce-fixture-parity/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
upstream_ref: docs/beacon/v1.6.7/features/beacon-golden-commerce-fixture-v167/truth.md
---

# Requirement Truth: v2 Golden Commerce Fixture Parity (R1)

## Overview

把 v1.6.7 **golden commerce checkout** 正例 + 负例（无商品直接下单）作为 v2 平台 **parity 夹具权威**。  
本 lake 交付 fixture 索引、加载合同与门禁消费，不交付真实电商系统。

## User Intent（一行）

v2 必须能用同一套正/负业务夹具证明 domain 门禁不是空转。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-V2-GOLD-001 | Fixture 源 | 优先引用 `docs/beacon/v1.6.7/fixtures/golden-commerce-checkout/`；v2 可镜像索引于 `docs/beacon/v2.0.0/fixtures/parity-v167/` |
| UD-V2-GOLD-002 | 负例 | order_without_product 必须 fail freeze 或 fail QA |
| UD-V2-GOLD-003 | 范围 | 示范与门禁夹具，非生产电商 |
| UD-V2-GOLD-004 | 消费方 | domain-fsm freeze/QA + ui-state-matrix golden-link |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-GOLD-001 | positive | 正例含 truth/tests/tasks/evidence + domain-fsm + entity-precedence（**Must**） |
| AC-V2-GOLD-002 | negative | 坏例：无 Product 创建 Order 必须失败（**Must**） |
| AC-V2-GOLD-003 | fsm-content | 覆盖 Product 与 Order 聚合根合法/非法转移（**Must**） |
| AC-V2-GOLD-004 | v2-index | v2 fixtures/parity-v167 索引指向可加载路径（**Must**） |
| AC-V2-GOLD-005 | gate-consume | v2 freeze/QA 路径可消费夹具（**Must**） |
| AC-V2-GOLD-006 | design-stub | 含最小 ui-state-matrix / DESIGN stub（**Should**） |

## Non-Goals

- 不实现真实电商业务
- 不替代 domain-fsm-authority schema 定义
