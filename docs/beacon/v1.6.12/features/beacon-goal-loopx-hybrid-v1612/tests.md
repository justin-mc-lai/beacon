| TC ID | AC ID | Command | Assertion |
|----|----|----|----|
| TC-001 | AC-001 | `python3 -m pytest -q tests/test_v1612_goal_quota.py --tb=no` | exit 0 |
| TC-002 | AC-002 | `python3 -m pytest -q tests/test_v1612_goal_todos.py --tb=no` | exit 0 |
| TC-003 | AC-003 | `python3 -m pytest -q tests/test_v1612_goal_gates.py --tb=no` | exit 0 |
| TC-004 | AC-004 | `python3 -m pytest -q tests/test_v1612_goal_budget.py --tb=no` | exit 0 |
| TC-005 | AC-005 | `python3 -m pytest -q tests/test_v1612_goal_patterns.py --tb=no` | exit 0 |
| TC-006 | AC-006 | `python3 -m pytest -q tests/test_doctor_context_commands.py tests/test_v169_version_defaults_dual_axis.py --tb=no` | 无新增失败（生命周期护栏） |
| TC-007 | AC-006 | `python3 -c "import json; s=json.load(open('.beacon/state/loop-goal/pgr-0dd73fcf5c9f.verification-bundle.json')); print('ok')"` | 旧状态文件可读（向后兼容） |
| TC-008 | AC-003 | `python3 -m pytest -q tests/test_v1612_goal_gates.py -k gate_resolve --tb=no` | illegal transition（gate 未 resolve 直接推进）被拒绝 |
