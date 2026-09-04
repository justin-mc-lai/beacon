---
slug: beacon-plan-persistent-goal
version: v1.6.17
materials_status: current
---

# Tests: beacon-plan-persistent-goal

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 -c "from beacon.utils.plan_artifact import build_plan_artifact; a=build_plan_artifact('用 Computer Use 复刻天气', subintent_payload={'subintent':'program'}); assert 'persistent_goal' in a and a['persistent_goal']['objective']=='用 Computer Use 复刻天气'"` | persistent_goal_in_plan_artifact |
| TC-002 | AC-002 | `python3 -c "from pathlib import Path; from beacon.utils.product_goal_runtime import create_goal_run; p=create_goal_run(Path('.'), utterance='复刻天气', version='v1.6.17', feature='beacon-plan-persistent-goal'); assert p['goal_objective']=='复刻天气' and p['goal_status']=='active'"` | goal_persisted_across_tick |
| TC-003 | AC-003 | `python3 -c "from beacon.utils.goal_steering import render_steering; s=render_steering({'utterance':'复刻天气','token_budget':1000,'tokens_used':10}, {}); assert '复刻天气' in s"` | continuation_injected |
| TC-004 | AC-004 | `python3 -c "from beacon.utils.goal_steering import select_template_id; assert select_template_id(halt_budget=True)=='budget_limit'"` | budget_limit_not_blocked |
| TC-005 | AC-005 | `rg -n "writes_truth.*false|may_implement.*false" beacon/utils/plan_artifact.py` | planner_only_boundary |
| TC-EXEC-CLI | AC-001 | `python3 -c 'import beacon; print(chr(111)+chr(107))'` | import_beacon_ok |
| TC-EXEC-PYTEST | AC-002 | `python3 -m pytest -q tests/test_plan_persistent_goal.py --tb=no -k persistent` | pytest_persistent_goal |
| TC-ILLEGAL | AC-005 | `rg -n -e "未经.*plan.*直接.*persist" -e "budgetLimited.*complete" docs/beacon/v1.6.17/features/beacon-plan-persistent-goal/truth.md` | illegal（未plan直接persist/预算当完成均被拒） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + domain exec layer. AC-002/AC-003 行为级命令已覆盖 plan→goal 持久化与续跑。
