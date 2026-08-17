"""Contract tests for beacon-ralph-implement-boundary-v167."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.product_goal_runtime import delegate_implement_to_ralph, run_goal_facade
from beacon.utils.ralph_boundary import (
    ALLOWED_HANDOFF_ROUTES,
    ralph_boundary_contract,
    sanitize_ralph_state,
    skill_boundary_text_ok,
    validate_handoff_route,
)
from beacon.utils.ralph_runtime import initialize_ralph_state, load_ralph_state, save_ralph_state

ROOT = Path(__file__).resolve().parents[1]


def test_skill_boundary_text() -> None:
    text = (ROOT / "skills/beacon/beacon-implement/references/gen-implement/implement-ralph.md").read_text(encoding="utf-8")
    result = skill_boundary_text_ok(text)
    assert result["status"] == "pass", result["checks"]
    # also host skill mentions ralph is subcontroller via boundary ref
    skill = (ROOT / "skills/beacon/beacon-implement/SKILL.md").read_text(encoding="utf-8")
    assert "ralph" in skill.lower()


def test_ralph_state_no_qa_verdict(tmp_path: Path) -> None:
    initialize_ralph_state(
        tmp_path,
        feature="demo",
        version="v1.6.7",
        run_id="r1",
        host_runtime="test",
        runner="native",
    )
    dirty = load_ralph_state(tmp_path, feature="demo")
    dirty["qa_verdict"] = "pass"
    dirty["release_verdict"] = "ready"
    dirty["product_complete"] = True
    save_ralph_state(tmp_path, feature="demo", payload=dirty)
    cleaned = load_ralph_state(tmp_path, feature="demo")
    # load returns raw file; sanitize via save already cleaned
    assert "qa_verdict" not in cleaned
    assert "release_verdict" not in cleaned
    assert cleaned.get("product_complete") is False
    assert cleaned.get("may_issue_qa_verdict") is False
    assert cleaned.get("ralph_finalize_is_product_complete") is False
    # direct sanitize
    again = sanitize_ralph_state({"qa_verdict": "pass", "next_action": "hack_truth"})
    assert "qa_verdict" not in again
    assert again["next_action"] == "human_review"


def test_goal_delegate_field(tmp_path: Path) -> None:
    run = run_goal_facade(tmp_path, utterance="实现某湖", version="v1.6.7", feature="lake-a")
    updated = delegate_implement_to_ralph(tmp_path, run["run_id"], feature="lake-a")
    assert updated.get("implement_delegate") == "ralph"
    contract = ralph_boundary_contract()
    assert contract["goal_delegate_field"] == "implement_delegate"
    assert contract["goal_delegate_value"] == "ralph"
    assert contract["may_mark_product_complete"] is False


def test_handoff_routes() -> None:
    for route in ("implement", "qa", "review_quality", "verify", "human_review", "repair"):
        assert validate_handoff_route(route)["allowed"] is True
    bad = validate_handoff_route("write_truth")
    assert bad["allowed"] is False
    assert "qa" in ALLOWED_HANDOFF_ROUTES
    assert "release" in ALLOWED_HANDOFF_ROUTES  # route suggestion only
    contract = ralph_boundary_contract()
    assert contract["may_issue_release_verdict"] is False


def test_contract_suite_locks_boundary() -> None:
    """AC-RLP-005: dedicated contract tests module locks Ralph boundary."""
    path = Path(__file__).resolve()
    assert path.name == "test_v167_ralph_boundary.py"
    src = path.read_text(encoding="utf-8")
    for name in ("test_skill_boundary_text", "test_ralph_state_no_qa_verdict", "test_goal_delegate_field", "test_handoff_routes"):
        assert f"def {name}" in src
