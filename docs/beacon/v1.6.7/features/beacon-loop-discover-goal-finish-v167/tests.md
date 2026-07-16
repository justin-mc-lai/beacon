---
slug: beacon-loop-discover-goal-finish-v167
version: v1.6.7
status: draft
revision_id: R2
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-loop-discover-goal-finish-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop/Goal Skill Split R2

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-LDG-001 | TC-LDG-001 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_queue_schema -q` | queue schema |
| AC-LDG-002 | TC-LDG-002 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_loop_cannot_mark_complete -q` | loop 不能 complete |
| AC-LDG-003 | TC-LDG-003 | integration | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_goal_consumes_queue -q` | goal 消费 queue |
| AC-LDG-004 | TC-LDG-004 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_dual_skill_boundary_docs -q` | 双 skill 边界 |
| AC-LDG-005 | TC-LDG-005 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_inventory_lists_beacon_goal -q` | inventory 含 beacon-goal |
