---
slug: beacon-loop-discover-goal-finish-v167
version: v1.6.7
status: draft
revision_id: R3
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-loop-discover-goal-finish-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Support Role R3

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-LDG-001 | TC-LDG-R3-001 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_loop_skill_support_meta -q` | support 元数据 |
| AC-LDG-002 | TC-LDG-R3-002 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_no_coequal_entry_in_examples -q` | 示例无并列入口 |
| AC-LDG-004 | TC-LDG-R3-003 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_loop_cannot_mark_complete -q` | 不能 complete |
| AC-LDG-005 | TC-LDG-R3-004 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_loop_points_to_goal -q` | 指向 beacon-goal |
