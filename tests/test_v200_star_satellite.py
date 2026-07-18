"""v2.0.0 main-star / satellite pool tests."""

from __future__ import annotations

from beacon.utils.product_goal_runtime import build_parallel_plan


def test_modes() -> None:
    single = build_parallel_plan(lakes=["a"], mode="single_worktree")
    assert single["mode"] == "single_worktree"
    assert single["satellites"] == []
    pool = build_parallel_plan(lakes=["x", "y"], mode="main_star_satellite_pool")
    assert pool["mode"] == "main_star_satellite_pool"


def test_one_lake_one_satellite() -> None:
    pool = build_parallel_plan(lakes=["l1", "l2", "l3"], mode="main_star_satellite_pool")
    assert pool["one_lake_one_satellite"] is True
    assert len(pool["satellites"]) == 3
    lakes = {s["lake"] for s in pool["satellites"]}
    assert lakes == {"l1", "l2", "l3"}


def test_merge_to_star_only() -> None:
    pool = build_parallel_plan(lakes=["a"], mode="main_star_satellite_pool")
    assert pool["main_star"]["merge_policy"] == "satellites_merge_to_star_only"
    assert all(s.get("merge_target") == "main_star" for s in pool["satellites"])


def test_satellite_cannot_write_truth() -> None:
    pool = build_parallel_plan(lakes=["a"], mode="main_star_satellite_pool")
    assert all(s.get("may_write_truth_on_main") is False for s in pool["satellites"])
