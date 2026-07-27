---
slug: intent-completeness-engine-v1611
version: v1.6.11
revision_id: R2
materials_status: current
---

# Tests: L2 Intent Completeness Engine

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-INT-001 | AC-INT-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k intent_dimensions --tb=no` | seven dimensions are represented |
| TC-INT-002 | AC-INT-002 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k missing_must --tb=no` | missing must blocks |
| TC-INT-003 | AC-INT-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k semantic_stop --tb=no` | count target cannot close recursion |
| TC-INT-004 | AC-INT-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k intent_human_decision --tb=no` | high-impact ambiguity requires decision_ref |
| TC-INT-005 | AC-INT-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k inherited_must_intents --tb=no` | inherited Goal/subagent/worktree/trace/no-compat capabilities remain must and have landings |
| TC-INT-006 | AC-INT-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k host_llm_full_package_fill --tb=no` | structured response covers L0, journeys, matrix, AC, model, FSM, illegal and projection inputs |
| TC-INT-007 | AC-INT-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k false_completeness_blocked --tb=no` | sentence splitting, domain skip, duplicates and missing exec-test inputs cannot pass completeness |
| TC-INT-ILLEGAL | AC-INT-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k intent_illegal_transition --tb=no` | illegal completion with missing must or missing decision_ref is rejected |
