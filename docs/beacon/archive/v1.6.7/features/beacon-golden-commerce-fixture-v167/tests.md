---
slug: beacon-golden-commerce-fixture-v167
version: v1.6.7
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.7/features/beacon-golden-commerce-fixture-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Golden Commerce Fixture v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-GOLD-001 | TC-GOLD-001 | contract | `python3 -m pytest tests/test_v167_golden_commerce.py::test_positive_package_present -q` | 正例 package 存在且可解析 |
| AC-GOLD-002 | TC-GOLD-002 | negative | `python3 -m pytest tests/test_v167_golden_commerce.py::test_order_without_product_fails -q` | 无商品下单失败 |
| AC-GOLD-003 | TC-GOLD-003 | contract | `python3 -m pytest tests/test_v167_golden_commerce.py::test_fsm_covers_product_and_order -q` | FSM 覆盖两聚合根 |
| AC-GOLD-004 | TC-GOLD-004 | contract | `python3 -m pytest tests/test_v167_golden_commerce.py::test_skill_example_points_to_fixture -q` | skill 示例指向 fixture |

## Verification Notes

- Contract tests may land under `tests/test_v167_product_goal_domain.py` (or per-feature modules).
- Negative fixtures must fail closed (freeze or QA).
