"""Minimal human HUD renderer for v1.3.3."""

from __future__ import annotations

from typing import Any


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _clip(line: str, limit: int = 120) -> str:
    text = str(line or "").strip()
    if len(text) <= limit:
        return text
    if limit <= 1:
        return text[:limit]
    return text[: limit - 1] + "…"


def _scenario(stage: str, mode: str, blocker_level: str, circuit_status: str) -> str:
    blocked = blocker_level == "blocked" or circuit_status == "trip"
    warned = blocker_level == "warn"
    if blocked:
        return "S6"
    if warned:
        return "S5"
    if stage == "implement" and mode == "single":
        return "S2"
    if stage == "implement" and mode == "team":
        return "S3"
    if stage == "implement" and mode == "ralph":
        return "S4"
    return "S1"


def build_minimal_hud(payload: dict[str, Any]) -> dict[str, Any]:
    """Build 1-3 line minimal HUD from normalized payload."""
    beacon_version = _text(payload.get("beacon_version"), "N/A")
    docs_version = _text(payload.get("docs_version"), "N/A")
    feature = _text(payload.get("feature"), "unknown-feature")
    stage = _text(payload.get("stage"), "draft")
    execution = payload.get("execution") if isinstance(payload.get("execution"), dict) else {}
    blocker = payload.get("blocker") if isinstance(payload.get("blocker"), dict) else {}
    next_action = _text(payload.get("next_action"), "none")

    mode = _text(execution.get("mode"), "")
    elapsed = _text(execution.get("elapsed"), "N/A")
    progress = execution.get("progress") if isinstance(execution.get("progress"), dict) else {}
    done = int(progress.get("done", 0) or 0)
    total = int(progress.get("total", 0) or 0)
    round_count = int(progress.get("round", 0) or 0)
    circuit_status = _text(execution.get("circuit_status"), "ok").lower()

    blocker_level = _text(blocker.get("level"), "none").lower()
    blocker_reason = _text(blocker.get("reason"), "")
    blocker_command = _text(blocker.get("recommended_command"), "")

    scenario = _scenario(stage, mode, blocker_level, circuit_status)

    stage_view = f"{stage}:{mode}" if stage == "implement" and mode else stage
    blocked = scenario == "S6"
    line1 = (
        f"[beacon:{beacon_version}] docs:{docs_version} | {feature} | [{stage_view}] | blocked"
        if blocked
        else f"[beacon:{beacon_version}] docs:{docs_version} | {feature} | [{stage_view}] | next:{next_action}"
    )
    lines = [_clip(line1)]

    if scenario in {"S2", "S3", "S4", "S5", "S6"}:
        if mode == "ralph":
            line2 = f"▸ round:{round_count} circuit:{circuit_status} elapsed:{elapsed}"
        elif mode in {"single", "team"}:
            line2 = f"▸ progress:{done}/{total} elapsed:{elapsed}"
        else:
            line2 = f"▸ state:{circuit_status} elapsed:{elapsed}"
        lines.append(_clip(line2))

    if scenario in {"S5", "S6"}:
        level_prefix = "⛔" if scenario == "S6" else "⚠"
        reason = blocker_reason or "unknown_blocker"
        command = blocker_command or "N/A"
        lines.append(_clip(f"{level_prefix} blocker:{reason} | cmd:{command}"))

    return {
        "schema_version": "1.0",
        "scenario": scenario,
        "line_budget": len(lines),
        "lines": lines,
    }


def build_minimal_hud_lines(payload: dict[str, Any]) -> list[str]:
    result = build_minimal_hud(payload)
    lines = result.get("lines")
    return list(lines) if isinstance(lines, list) else []

