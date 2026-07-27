---
slug: drift-padding-review-gate-v1611
version: v1.6.11
revision_id: R2
materials_status: current
---

# Tests: L6 Drift and Padding Review Gate

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-REV-001 | AC-REV-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k drift_kinds --tb=no` | all required finding kinds detected |
| TC-REV-002 | AC-REV-002 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k drift_pause --tb=no` | mandatory finding pauses execution |
| TC-REV-003 | AC-REV-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k human_choices --tb=no` | only five choices accepted |
| TC-REV-004 | AC-REV-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k decision_ref --tb=no` | transition without decision_ref rejected |
| TC-REV-005 | AC-REV-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k advisory_finding_sources --tb=no` | hook and subagent findings cannot directly change canonical task or Goal state |
| TC-REV-006 | AC-REV-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k canonical_human_gate_owner --tb=no` | Beacon policy persists the decision and only parent scheduler applies it |
| TC-REV-007 | AC-REV-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k hollow_fill_review_gate --tb=no` | placeholder, hollow domain, orphan, hanging FSM, padding, evidence/hash drift force governed human choice |
| TC-REV-ILLEGAL | AC-REV-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k review_gate_illegal_transition --tb=no` | illegal resume, cancel or clear without canonical decision_ref is rejected |
