from __future__ import annotations

from pathlib import Path

from beacon.utils.protected_paths import build_protected_path_block, planner_protected_path_advisory, protected_path_match
from beacon.utils.workspace_admission import hook_should_deny_write


def test_global_boundaries_contains_protected_path_principle() -> None:
    text = Path("docs/beacon/global-boundaries.md").read_text(encoding="utf-8")
    assert "Protected Path Denylist" in text
    assert "planner/research" in text
    assert "reason_code=protected_path_denylist" in text


def test_protected_path_matcher_patterns() -> None:
    assert protected_path_match(".env")["match_type"] == "exact"
    assert protected_path_match("secrets/api.txt")["match_type"] == "glob"
    assert protected_path_match("certs/prod.pem")["match_type"] == "extension"
    assert protected_path_match("src/auth/session.py")["match_type"] == "segment"
    assert protected_path_match("src/app.py")["matched"] is False


def test_write_guard_blocks_protected_path(tmp_path: Path) -> None:
    (tmp_path / "docs/beacon/global-boundaries.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/beacon/global-boundaries.md").write_text("x\n", encoding="utf-8")
    deny, reason = hook_should_deny_write(tmp_path, target_path=".env")
    assert deny is True
    assert reason == "protected_path_denylist"


def test_planner_risk_is_advisory() -> None:
    payload = planner_protected_path_advisory("payments/stripe.py")
    assert payload["status"] == "advisory"
    assert payload["blocked"] is False


def test_block_payload_contains_human_route() -> None:
    payload = build_protected_path_block("credentials/prod.json")
    assert payload["blocked"] is True
    assert payload["reason_code"] == "protected_path_denylist"
    assert "human" in payload["route_recommendation"].lower()
