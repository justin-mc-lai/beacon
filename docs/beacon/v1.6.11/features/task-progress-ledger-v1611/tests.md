---
slug: task-progress-ledger-v1611
version: v1.6.11
revision_id: R2
materials_status: current
---

# Tests: L5 Task Progress Ledger

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-LED-001 | AC-LED-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k task_attempt_fields --tb=no` | task attempts contain required fields |
| TC-LED-002 | AC-LED-002 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k feedback_append_only --tb=no` | feedback history is append-only |
| TC-LED-003 | AC-LED-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k path_progress --tb=no` | all path counters reconcile |
| TC-LED-004 | AC-LED-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k progress_revision --tb=no` | graph change stales old snapshot |
| TC-LED-005 | AC-LED-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k goal_run_lifecycle_trace --tb=no` | events bind run_id, internal state, public 1+6 stage and agent_trace.v1 refs |
| TC-LED-006 | AC-LED-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k trace_append_fail_closed --tb=no` | trace append failure cannot silently commit the state transition |
| TC-LED-007 | AC-LED-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k fill_transaction_progress_replay --tb=no` | all fill-chain steps append sequence/hash/status/feedback and retries remain replayable |
| TC-LED-ILLEGAL | AC-LED-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k ledger_illegal_transition --tb=no` | illegal current state with sequence gap, stale snapshot or failed trace append is rejected |
