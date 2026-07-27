---
slug: contract-baseline-convergence-v1611
version: v1.6.11
revision_id: D2
materials_status: current
---

# Tests: L0 Contract Baseline Convergence

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-BAS-001 | AC-BAS-001 | `beacon doctor verify-context --project-root . --strict --json` | status=pass |
| TC-BAS-002 | AC-BAS-002 | `git rev-parse HEAD` | equals bound baseline commit during review |
| TC-BAS-003 | AC-BAS-003 | `python3 -m pytest -q tests/test_v1610_plan_host_subagent_voltpack.py tests/test_v166_loop_goal.py --tb=no` | result is captured and every failure has disposition |
| TC-BAS-004 | AC-BAS-004 | `python3 -m pytest -q tests/test_v1610_truth_gen_template_and_gates.py -k stale --tb=no` | stale cascade contract passes |
| TC-BAS-005 | AC-BAS-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k package_shape_upgrade_required --tb=no` | old package/ledger shapes fail closed without compatibility bypass |
| TC-BAS-006 | AC-BAS-006 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k frozen_truth_lineage --tb=no` | old frozen truth stays immutable and inherited semantics require a new frozen revision |
| TC-BAS-ILLEGAL | AC-BAS-005 | `python3 -m pytest -q tests/test_v1611_plan_goal_task_closure.py -k baseline_illegal_transition --tb=no` | illegal old-shape or stale-evidence transition is rejected |
