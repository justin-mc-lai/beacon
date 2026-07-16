---
slug: beacon-loop-discover-goal-finish-v167
version: v1.6.7
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-loop-discover-goal-finish-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Discover / Goal Finish Split v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-LDG-001 | TC-LDG-001 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_queue_schema -q` | queue schema |
| AC-LDG-002 | TC-LDG-002 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_loop_cannot_mark_complete -q` | loop 不能 complete |
| AC-LDG-003 | TC-LDG-003 | integration | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_goal_consumes_queue -q` | goal 消费 queue |
| AC-LDG-004 | TC-LDG-004 | contract | `python3 -m pytest tests/test_v167_loop_goal_split.py::test_loop_goal_skill_boundary_text -q` | skill 边界文案 |

## Verification Notes

- Contract tests may land under `tests/test_v167_product_goal_domain.py` (or per-feature modules).
- Negative fixtures must fail closed (freeze or QA).
