from __future__ import annotations

from beacon.utils.minimal_hud import build_minimal_hud


def _payload(*, stage: str, mode: str = "", blocker_level: str = "none", circuit_status: str = "ok") -> dict:
    return {
        "beacon_version": "v1.3.3",
        "docs_version": "v1.3.3",
        "feature": "feature-x",
        "stage": stage,
        "execution": {
            "mode": mode,
            "elapsed": "30s",
            "progress": {"done": 1, "total": 3, "round": 2},
            "circuit_status": circuit_status,
        },
        "blocker": {
            "level": blocker_level,
            "reason": "needs_manual_fix",
            "recommended_command": "beacon doctor migrate-compat --project-root . --version v1.3.3",
        },
        "next_action": "implement",
    }


def test_s1_idle_should_render_one_line() -> None:
    hud = build_minimal_hud(_payload(stage="prd"))
    assert hud["scenario"] == "S1"
    assert len(hud["lines"]) == 1


def test_s2_single_should_render_two_lines() -> None:
    hud = build_minimal_hud(_payload(stage="implement", mode="single"))
    assert hud["scenario"] == "S2"
    assert len(hud["lines"]) == 2


def test_s3_team_should_render_two_lines() -> None:
    hud = build_minimal_hud(_payload(stage="implement", mode="team"))
    assert hud["scenario"] == "S3"
    assert len(hud["lines"]) == 2


def test_s4_ralph_should_render_two_lines() -> None:
    hud = build_minimal_hud(_payload(stage="implement", mode="ralph"))
    assert hud["scenario"] == "S4"
    assert len(hud["lines"]) == 2


def test_s5_warn_should_render_three_lines() -> None:
    hud = build_minimal_hud(_payload(stage="implement", mode="ralph", blocker_level="warn", circuit_status="warn"))
    assert hud["scenario"] == "S5"
    assert len(hud["lines"]) == 3


def test_s6_blocked_should_render_three_lines() -> None:
    hud = build_minimal_hud(_payload(stage="qa", blocker_level="blocked", circuit_status="trip"))
    assert hud["scenario"] == "S6"
    assert len(hud["lines"]) == 3


def test_lines_should_not_exceed_120_chars() -> None:
    long_reason = "x" * 400
    payload = _payload(stage="implement", mode="ralph", blocker_level="warn", circuit_status="warn")
    payload["feature"] = "feature-with-very-long-name-" + ("y" * 300)
    payload["blocker"]["reason"] = long_reason
    hud = build_minimal_hud(payload)
    assert hud["lines"]
    assert all(len(line) <= 120 for line in hud["lines"])

