"""Multi-version dual-track intent (v1.6.8\\v2.0.0)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.multi_version_intent import (
    build_multi_version_execution_plan,
    detect_multi_version_intent,
    extract_versions,
)
from beacon.utils.product_goal_runtime import create_goal_run, plan_multi_version

ROOT = Path(__file__).resolve().parents[1]


def test_extract_versions_backslash() -> None:
    assert extract_versions(r"v1.6.8\v2.0.0") == ["v1.6.8", "v2.0.0"]
    assert extract_versions("v1.6.8/v2.0.0") == ["v1.6.8", "v2.0.0"]
    assert extract_versions("fix v1.6.8 and v2.0.0") == ["v1.6.8", "v2.0.0"]


def test_detect_parallel_dual_track() -> None:
    d = detect_multi_version_intent(r"双轨 v1.6.8\v2.0.0 并行修复")
    assert d["detected"] is True
    assert d["parallel"] is True
    assert d["versions"] == ["v1.6.8", "v2.0.0"]
    assert d["confidence"] >= 75


def test_build_plan_assigns_lakes_per_track() -> None:
    plan = build_multi_version_execution_plan(ROOT, r"v1.6.8\v2.0.0 双轨")
    assert plan["parallel_tracks"] is True
    assert len(plan["tracks"]) == 2
    assert plan["tracks"][0]["version"] == "v1.6.8"
    assert plan["tracks"][1]["version"] == "v2.0.0"
    assert plan["tracks"][0]["public_entry"] == "beacon-goal"
    assert plan["tracks"][1]["public_entry"] == "loom-goal"
    assert "beacon-worktree-progressive-skill-flow-v168" in plan["tracks"][0]["lakes"]
    assert "loom-git-worktree-implement-harness" in plan["tracks"][1]["lakes"]
    assert plan["orchestration"]["admit_rule"].startswith("leaf_only")


def test_create_goal_run_attaches_multi_version() -> None:
    payload = create_goal_run(
        ROOT,
        utterance=r"需要 双轨并行 v1.6.8\v2.0.0 leaf-admit + InjectBundle",
        version="auto",
    )
    mv = payload.get("multi_version") or {}
    assert mv.get("enabled") is True
    assert mv.get("parallel") is True
    assert "v1.6.8" in (mv.get("versions") or [])
    assert "v2.0.0" in (mv.get("versions") or [])
    lakes = payload.get("lakes") or []
    assert any(str(x).startswith("v1.6.8::") for x in lakes)
    assert any(str(x).startswith("v2.0.0::") for x in lakes)
    plan = payload.get("multi_version_plan") or {}
    assert plan.get("orchestration", {}).get("mode") == "parallel_version_tracks"


def test_plan_multi_version_helper() -> None:
    plan = plan_multi_version(ROOT, r"v1.6.8+v2.0.0")
    assert len(plan.get("tracks") or []) == 2
