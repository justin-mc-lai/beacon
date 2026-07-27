---
slug: atomic-task-graph-compiler-v1611
version: v1.6.11
revision_id: D2
materials_status: current
---

# Tests: L4 Atomic Task Graph Compiler

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-DAG-001 | AC-DAG-001 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k atomic_compile --tb=no` | each node is independently verifiable |
| TC-DAG-002 | AC-DAG-002 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k task_trace_bindings --tb=no` | all seven bindings present |
| TC-DAG-003 | AC-DAG-003 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k dag_ready_set --tb=no` | cycle and unmet dependency fail closed |
| TC-DAG-004 | AC-DAG-004 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k orphan_padding --tb=no` | orphan/padding blocks graph |
| TC-DAG-005 | AC-DAG-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k graph_scale --tb=no` | 100+ nodes supported without count KPI |
| TC-DAG-006 | AC-DAG-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k task_delegation_contract --tb=no` | delegated nodes declare mode, role, reason and evidence while child completion authority is rejected |
| TC-DAG-007 | AC-DAG-007 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k honest_subagent_fallback --tb=no` | intent gate controls host lanes and unavailable runtime records honest fallback |
| TC-DAG-008 | AC-DAG-008 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k implementation_worktree_admission --tb=no` | implementation dispatch requires service/admission/real-worktree/cwd/HEAD bindings |
| TC-DAG-ILLEGAL | AC-DAG-008 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k task_graph_illegal_transition --tb=no` | illegal dispatch with cycle, orphan, stale graph or missing worktree admission is rejected |
