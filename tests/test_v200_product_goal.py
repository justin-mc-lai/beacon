"""v2.0.0 Product Goal orchestrator contract tests."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.product_goal_runtime import (
    build_parallel_plan,
    progressive_skills_for_stage,
    public_entry_contract,
    run_goal_facade,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v167_schema_parity(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="v2 parity goal", version="v2.0.0", feature="demo")
    stages = [s.get("stage") for s in (run.get("stages") or []) if isinstance(s, dict)]
    assert "plan" in stages and "implement" in stages and "qa" in stages
    assert run.get("entry_contract", {}).get("single_entry") is True


def test_progressive_load_default() -> None:
    plan = progressive_skills_for_stage("plan")
    impl = progressive_skills_for_stage("implement")
    assert plan and impl
    assert set(plan) != set(impl)


def test_parallel_respects_deps() -> None:
    pool = build_parallel_plan(lakes=["a", "b"], mode="main_star_satellite_pool")
    assert pool["one_lake_one_satellite"] is True
    assert len(pool["satellites"]) == 2
    assert all(s.get("may_write_truth_on_main") is False for s in pool["satellites"])


def test_single_public_entry() -> None:
    c = public_entry_contract()
    assert c["single_entry"] is True
    assert c["public_primary"] == "beacon-goal"


def test_program_has_domain_lakes() -> None:
    axis = ROOT / "docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/goalrun-main-axis.md"
    text = axis.read_text(encoding="utf-8")
    for slug in (
        "beacon-v2-domain-fsm-authority",
        "beacon-v2-domain-fsm-qa-gate",
        "beacon-v2-product-goal-orchestrator",
    ):
        assert slug in text


def test_no_early_default_flag() -> None:
    # W4: no default BEACON_V2=1 in repo packaging claim
    summary = (ROOT / "docs/beacon/v2.0.0/SUMMARY.md").read_text(encoding="utf-8")
    assert "reject" in summary.lower() or "W4" in summary
    assert "BEACON_V2" in summary
