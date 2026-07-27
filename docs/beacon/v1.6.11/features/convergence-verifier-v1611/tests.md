---
slug: convergence-verifier-v1611
version: v1.6.11
revision_id: D2
materials_status: current
---

# Tests: L8 Convergence Verifier

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-CNV-001 | AC-CNV-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k closure_matrix --tb=no` | six layers are bidirectionally traceable |
| TC-CNV-002 | AC-CNV-002 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k goal_completion --tb=no` | any open required layer blocks pass |
| TC-CNV-003 | AC-CNV-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k stale_blocks --tb=no` | stale truth/graph/material/evidence blocks |
| TC-CNV-004 | AC-CNV-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k goal_owner --tb=no` | subagent completion rejected |
| TC-CNV-005 | AC-CNV-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k minimal_gap_route --tb=no` | fail reports minimal gaps and routes |
| TC-CNV-006 | AC-CNV-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k goal_run_required_refs --tb=no` | missing or stale program/graph/truth/ready/decision/admission/trace/verifier refs block complete |
| TC-CNV-007 | AC-CNV-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k public_lifecycle_boundary --tb=no` | no new public harness appears and only Goal owner completes after verifier pass |
| TC-CNV-ILLEGAL | AC-CNV-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k convergence_illegal_transition --tb=no` | illegal completion by child, stale verdict or new public harness is rejected |
