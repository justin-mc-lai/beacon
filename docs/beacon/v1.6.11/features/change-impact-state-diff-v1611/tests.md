---
slug: change-impact-state-diff-v1611
version: v1.6.11
revision_id: D2
materials_status: current
---

# Tests: L3 Change Impact and State Diff

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-DIF-001 | AC-DIF-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k five_surface_diff --tb=no` | all five surfaces emitted |
| TC-DIF-002 | AC-DIF-002 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k fsm_diff --tb=no` | state and edge delta complete |
| TC-DIF-003 | AC-DIF-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k diff_traceability --tb=no` | intent/code/TC bindings present |
| TC-DIF-004 | AC-DIF-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k destructive_diff_review --tb=no` | high-risk diff requires human ack |
| TC-DIF-005 | AC-DIF-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k inherited_surface_diff --tb=no` | lifecycle, delegation, admission, trace, Goal ownership and no-compat surfaces are present |
| TC-DIF-ILLEGAL | AC-DIF-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k diff_illegal_transition --tb=no` | illegal approval with missing surface or human ack is rejected |
