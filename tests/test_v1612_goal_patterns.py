"""CAP-5 canary: pattern catalog, incidents archive, ready-score (AC-005)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.goal_ready import goal_ready_score

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "skills" / "beacon" / "beacon-goal" / "references" / "patterns" / "INDEX.md"
INCIDENTS = ROOT / "skills" / "beacon" / "beacon-goal" / "references" / "incidents" / "INDEX.md"


def test_pattern_catalog_contains_required_ip_patterns() -> None:
    text = PATTERNS.read_text(encoding="utf-8")
    for ip in ("IP-001", "IP-002", "IP-003", "IP-013", "IP-016"):
        assert ip in text, ip
    assert "canary_test" in text or "canary" in text


def test_incidents_archive_contains_five_lessons() -> None:
    text = INCIDENTS.read_text(encoding="utf-8")
    for key in ("outcome-floor", "planner-review", "monitor-only", "user-gate", "authorization"):
        assert key in text, key


def test_ready_score_blocks_with_concrete_checks() -> None:
    score = goal_ready_score(
        {
            "truth_frozen": True,
            "workspace_admission": False,
            "quota_configured": True,
            "evidence_fresh": True,
        }
    )
    assert score["ready"] is False
    assert score["blocked_checks"] == ["workspace_admission"]


def test_ready_score_all_checks_pass() -> None:
    score = goal_ready_score(
        {
            "truth_frozen": True,
            "workspace_admission": True,
            "quota_configured": True,
            "evidence_fresh": True,
        }
    )
    assert score["ready"] is True
    assert score["blocked_checks"] == []
