---
slug: cancel-replan-next-ready-v1611
version: v1.6.11
revision_id: R2
materials_status: current
---

# Tests: L7 Cancel, Replan and Next Ready

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-RPL-001 | AC-RPL-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k replan_choices --tb=no` | each choice emits correct disposition (legal walk / happy path) |
| TC-RPL-002 | AC-RPL-002 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k required_cancel --tb=no` | missing replacement blocks downstream |
| TC-RPL-003 | AC-RPL-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k ready_recompute --tb=no` | ready set recomputed atomically |
| TC-RPL-004 | AC-RPL-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k evidence_reuse --tb=no` | evidence retained or staled correctly |
| TC-RPL-005 | AC-RPL-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k illegal_terminal_transition --tb=no` | cancelled/superseded/blocked cannot become done |
| TC-RPL-006 | AC-RPL-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k goal_scheduler_shared_admission --tb=no` | Goal scheduler dispatch records shared admission and real-worktree bindings across all implement routes |
| TC-RPL-007 | AC-RPL-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k refreeze_invalidates_dispatch --tb=no` | refreeze stales graph, ready set and admission until main reconciliation |
| TC-RPL-008 | AC-RPL-008 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k fill_task_failure_recovery --tb=no` | timeout/retryable/non-retryable/human-reject paths stop self-spinning and emit governed routes |
| TC-RPL-009 | AC-RPL-009 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k no_open_work_closure_ready --tb=no` | empty ready set distinguishes blocked open work from closure-ready no-open-work |
| TC-RPL-ILLEGAL | AC-RPL-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k replan_illegal_transition --tb=no` | illegal done/ready/dispatch after cancel or refreeze is rejected |
