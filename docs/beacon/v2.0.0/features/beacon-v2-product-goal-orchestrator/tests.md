---
slug: beacon-v2-product-goal-orchestrator
version: v2.0.0
status: draft
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: v2 Product Goal Orchestrator

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V2-PGO-001 | TC-V2-PGO-001 | contract | `python3 -m pytest tests/test_v200_product_goal.py::test_v167_schema_parity -q` | v167 fixture parity |
| AC-V2-PGO-003 | TC-V2-PGO-002 | contract | `python3 -m pytest tests/test_v200_product_goal.py::test_progressive_load_default -q` | 默认不全量加载 |
| AC-V2-PGO-004 | TC-V2-PGO-003 | contract | `python3 -m pytest tests/test_v200_product_goal.py::test_parallel_respects_deps -q` | 依赖边约束 |
