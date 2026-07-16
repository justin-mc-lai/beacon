"""Contract tests for beacon-product-goal-runtime-v167 R3."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.product_goal_runtime import (
    REASON_VERIFIER_REQUIRED,
    attach_verifier,
    complete_goal_run,
    docs_forbid_dual_call,
    loop_goal_support_metadata,
    build_parallel_plan,
    public_entry_contract,
    run_goal_facade,
)

ROOT = Path(__file__).resolve().parents[1]


def test_single_public_entry() -> None:
    contract = public_entry_contract()
    assert contract["single_entry"] is True
    assert contract["public_primary"] == "beacon-goal"
    assert contract["dual_public_orchestration"] is False
    assert "beacon-loop-goal" in contract["support_only"]


def test_docs_no_dual_call_path() -> None:
    paths = [
        ROOT / "skills/beacon/SKILL.md",
        ROOT / "skills/beacon/beacon-goal/SKILL.md",
        ROOT / "skills/beacon/examples/goal-one-shot-30s.md",
    ]
    result = docs_forbid_dual_call(paths)
    assert result["status"] == "pass", result["violations"]


def test_loop_goal_marked_support() -> None:
    skill = ROOT / "skills/beacon/beacon-loop-goal/SKILL.md"
    text = skill.read_text(encoding="utf-8") if skill.exists() else ""
    meta = loop_goal_support_metadata(text)
    assert meta["marked_support"] is True, "beacon-loop-goal must be marked support"


def test_30s_example_exists() -> None:
    path = ROOT / "skills/beacon/examples/goal-one-shot-30s.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "beacon-goal" in text or "$beacon-goal" in text
    assert "不要先调" in text or "不要" in text


def test_host_router_mentions_goal_entry() -> None:
    text = (ROOT / "skills/beacon/SKILL.md").read_text(encoding="utf-8")
    assert "beacon-goal" in text or "$beacon-goal" in text
    assert "一句话" in text or "goal run" in text


def test_main_star_satellite_pool() -> None:
    single = build_parallel_plan(lakes=["a"], mode="single_worktree")
    assert single["mode"] == "single_worktree"
    assert single["satellites"] == []
    pool = build_parallel_plan(lakes=["lake-a", "lake-b"], mode="main_star_satellite_pool")
    assert pool["mode"] == "main_star_satellite_pool"
    assert pool["one_lake_one_satellite"] is True
    assert len(pool["satellites"]) == 2
    assert all(s["merge_target"] == "main_star" for s in pool["satellites"])
    assert all(s["may_write_truth_on_main"] is False for s in pool["satellites"])
    auto = build_parallel_plan(utterance="用并行 subagent 拆多湖", lakes=["x", "y"])
    assert auto["mode"] == "main_star_satellite_pool"


def test_complete_requires_verifier(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="做一个可下单迷你店", version="v1.6.7", feature="demo")
    run_id = run["run_id"]
    rejected = complete_goal_run(tmp_path, run_id)
    assert rejected["status"] != "completed"
    assert rejected["reason_code"] == REASON_VERIFIER_REQUIRED
    attach_verifier(tmp_path, run_id, refs=[".beacon/qa/features/demo/scorecard.json"], source="beacon-eval-qa")
    done = complete_goal_run(tmp_path, run_id)
    assert done["status"] == "completed"
    assert done["verifier"]["present"] is True
