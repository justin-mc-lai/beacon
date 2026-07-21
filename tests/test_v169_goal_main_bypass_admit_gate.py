"""goal-main-bypass-admit-gate: hooks + default require + create preflight."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.implement_lane_enforcement import _hook_script_body
from beacon.utils.product_goal_runtime import (
    create_goal_run,
    utterance_requests_implement_delivery,
)
from beacon.utils.workspace_admission import load_admission_contract


def test_hook_body_imports_installed_beacon_package() -> None:
    body = _hook_script_body(hook_kind="pre-commit")
    assert "import beacon.utils.implement_lane_enforcement" in body
    assert "If beacon package not importable from repo, skip soft" not in body or "installed" in body.lower()
    # must not soft-exit before trying installed package
    assert body.index("import beacon.utils.implement_lane_enforcement") < body.rindex("exit 0")


def test_product_0x_defaults_require_admission(tmp_path: Path) -> None:
    # empty project: no governance → v0.0.13 should require True under new default
    c = load_admission_contract(tmp_path, version="v0.0.13")
    assert c["require_workspace_admission"] is True


def test_utterance_implement_intent_detector() -> None:
    assert utterance_requests_implement_delivery("冻结真相并实现到交付") is True
    assert utterance_requests_implement_delivery("just plan the ocean") is False
    assert utterance_requests_implement_delivery("implement the lake") is True


def test_create_goal_run_preflight_warns_without_feature(tmp_path: Path) -> None:
    # minimal git root
    (tmp_path / ".git").mkdir()
    payload = create_goal_run(
        tmp_path,
        utterance="实现并交付 feature 到验收",
        version="v0.0.13",
        feature="",
    )
    assert payload.get("implement_intent") is True
    assert "feature" in str(payload.get("admission_preflight_warning") or "").lower() or any(
        e.get("reason_code") == "feature_required_for_admit"
        for e in (payload.get("history") or [])
        if isinstance(e, dict)
    )
