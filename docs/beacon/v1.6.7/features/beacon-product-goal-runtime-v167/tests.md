---
slug: beacon-product-goal-runtime-v167
version: v1.6.7
status: draft
revision_id: R2
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Product Goal Runtime R2

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-PGR-001 | TC-PGR-001 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_state_schema_parallel_worktree -q` | state 含 parallel_plan/worktree_mode |
| AC-PGR-003 | TC-PGR-002 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_beacon_goal_skill_present -q` | skills/beacon/beacon-goal 存在 |
| AC-PGR-004 | TC-PGR-003 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_loop_vs_goal_skills_split -q` | 两 skill 边界文案 |
| AC-PGR-005 | TC-PGR-004 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_progressive_skill_load_map -q` | 阶段→skill 映射 |
| AC-PGR-006 | TC-PGR-005 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_intent_parses_subagent -q` | 意图解析 parallel |
| AC-PGR-009 | TC-PGR-006 | integration | `python3 -m pytest tests/test_v167_product_goal.py::test_main_star_satellite_pool -q` | 主星卫星 pool |
| AC-PGR-010 | TC-PGR-007 | integration | `python3 -m pytest tests/test_v167_product_goal.py::test_satellite_merge_to_star -q` | merge 回主星 |
| AC-PGR-011 | TC-PGR-008 | negative | `python3 -m pytest tests/test_v167_product_goal.py::test_complete_requires_verifier -q` | 无 verifier 不可 complete |
| AC-PGR-014 | TC-PGR-009 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_v2_schema_fixture_parity -q` | v2 fixture 可加载 |
