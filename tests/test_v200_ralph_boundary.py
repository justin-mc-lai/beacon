"""v2.0.0 Ralph implement boundary tests."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.product_goal_runtime import delegate_implement_to_ralph, run_goal_facade
from beacon.utils.ralph_boundary import (
    ralph_boundary_contract,
    sanitize_ralph_state,
    validate_handoff_route,
)
from beacon.utils.ralph_runtime import initialize_ralph_state, load_ralph_state, save_ralph_state


def test_no_qa_verdict(tmp_path: Path) -> None:
    initialize_ralph_state(tmp_path, feature="demo", version="v2.0.0", run_id="r1", host_runtime="test", runner="native")
    dirty = load_ralph_state(tmp_path, feature="demo")
    dirty["qa_verdict"] = "pass"
    dirty["product_complete"] = True
    save_ralph_state(tmp_path, feature="demo", payload=dirty)
    cleaned = load_ralph_state(tmp_path, feature="demo")
    assert "qa_verdict" not in cleaned
    assert cleaned.get("product_complete") is False
    again = sanitize_ralph_state({"qa_verdict": "pass", "release_verdict": "ready"})
    assert "qa_verdict" not in again
    assert "release_verdict" not in again


def test_handoff_routes() -> None:
    for route in ("implement", "qa", "human_review"):
        assert validate_handoff_route(route)["allowed"] is True
    assert validate_handoff_route("write_truth")["allowed"] is False


def test_finalize_not_complete(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="impl", version="v2.0.0", feature="lake-a")
    updated = delegate_implement_to_ralph(tmp_path, run["run_id"], feature="lake-a")
    assert updated.get("implement_delegate") == "ralph"
    contract = ralph_boundary_contract()
    assert contract["may_mark_product_complete"] is False
    assert contract.get("ralph_finalize_is_product_complete") is False or contract["may_mark_product_complete"] is False
