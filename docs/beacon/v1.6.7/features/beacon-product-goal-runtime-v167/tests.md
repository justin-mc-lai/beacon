---
slug: beacon-product-goal-runtime-v167
version: v1.6.7
status: draft
revision_id: R3
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Product Goal Runtime R3

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-PGR-001 | TC-PGR-R3-001 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_single_public_entry -q` | 单入口合同 |
| AC-PGR-002 | TC-PGR-R3-002 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_docs_no_dual_call_path -q` | 主文档无双调用 |
| AC-PGR-003 | TC-PGR-R3-008 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_facade_stage_plan -q` | facade 阶段齐全 |
| AC-PGR-004 | TC-PGR-R3-003 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_loop_goal_marked_support -q` | loop 标 support |
| AC-PGR-006 | TC-PGR-R3-009 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_progressive_skill_load -q` | 渐进 skill 加载 |
| AC-PGR-007 | TC-PGR-R3-006 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_main_star_satellite_pool -q` | 主星卫星 |
| AC-PGR-008 | TC-PGR-R3-007 | negative | `python3 -m pytest tests/test_v167_product_goal.py::test_complete_requires_verifier -q` | 无 verifier 不可 complete |
| AC-PGR-009 | TC-PGR-R3-004 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_30s_example_exists -q` | 30s 示例存在 |
| AC-PGR-010 | TC-PGR-R3-005 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_host_router_mentions_goal_entry -q` | host router 指向 goal |
| AC-PGR-011 | TC-PGR-R3-010 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_v2_parity_program_exists -q` | v2 合同存在 |

## Verification Notes

- Contract tests under `tests/test_v167_product_goal.py`.
