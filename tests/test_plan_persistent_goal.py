"""AC coverage for beacon-plan-persistent-goal — ponytail minimal."""

from pathlib import Path
from beacon.utils.plan_artifact import build_plan_artifact
from beacon.utils.product_goal_runtime import create_goal_run, load_goal_run, tick_goal_run
from beacon.utils.goal_steering import render_steering, select_template_id

def test_persistent_goal_in_plan():
    a = build_plan_artifact("用 Computer Use 复刻天气", subintent_payload={"subintent": "program"})
    assert "persistent_goal" in a
    pg = a["persistent_goal"]
    assert pg["objective"] == "用 Computer Use 复刻天气"
    assert pg["status"] == "active"
    assert pg["source"] == "plan_artifact.v1"
    assert len(pg["objective_fingerprint"]) == 12

def test_goal_persisted_across_tick(tmp_path=None):
    root = Path("/tmp/beacon-test-persistent-goal") if tmp_path is None else Path(tmp_path)
    root.mkdir(parents=True, exist_ok=True)
    # ensure version dir exists for goal run
    p = create_goal_run(root, utterance="复刻天气", version="v1.6.17", feature="beacon-plan-persistent-goal")
    assert p["goal_objective"] == "复刻天气"
    assert p["goal_status"] == "active"
    run_id = p["run_id"]
    # tick should preserve
    p2 = tick_goal_run(root, run_id, note="test", execute=False)
    assert p2["goal_objective"] == "复刻天气"

def test_continuation_injected():
    from beacon.utils.goal_steering import budget_fields
    bf = budget_fields({"utterance": "复刻天气", "token_budget": 1000, "tokens_used": 10}, {})
    assert bf["token_budget"] == "1000"
    assert "remaining" in bf or "tokens_used" in str(bf)

def test_budget_limit_not_blocked():
    assert select_template_id(halt_budget=True) == "budget_limit"
    assert select_template_id(halt_budget=False) == "continuation"

def test_planner_only_boundary():
    # plan_artifact must declare it does not write truth
    a = build_plan_artifact("hello")
    assert a["writes_truth"] is False
    assert a["may_implement"] is False
