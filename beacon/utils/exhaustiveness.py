"""Scenario/exhaustiveness scoring helpers for Beacon v1.1.10 QA."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.control_plane import exhaustion_for_run
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug


def feature_exhaustiveness_report_path(project_root: Path, *, feature: str) -> Path:
    return project_root / ".beacon" / "qa" / "features" / feature_slug(feature) / "exhaustiveness-report.json"


def load_exhaustiveness_report(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(feature_exhaustiveness_report_path(project_root, feature=feature), {})
    return payload if isinstance(payload, dict) else {}


def _normalize_results(qa_status: dict[str, Any]) -> list[dict[str, Any]]:
    qa9 = qa_status.get("qa9") if isinstance(qa_status.get("qa9"), dict) else {}
    tc_results = qa9.get("tc_results") if isinstance(qa9.get("tc_results"), list) else []
    return [item for item in tc_results if isinstance(item, dict)]


def build_exhaustiveness_report(
    project_root: Path,
    *,
    feature: str,
    run_id: str,
    plan: dict[str, Any],
    qa_status: dict[str, Any],
) -> dict[str, Any]:
    tc_results = _normalize_results(qa_status)
    targeted_entries = plan.get("targeted_entries") if isinstance(plan.get("targeted_entries"), list) else []
    scenario_results = tc_results or [item for item in targeted_entries if isinstance(item, dict)]
    total = len(scenario_results)
    browser_results = [item for item in scenario_results if bool(item.get("browser_required"))]
    passed = [item for item in scenario_results if str(item.get("status") or "").strip().lower() == "passed"]
    required_families = sorted(
        {
            str(item.get("scenario_family") or "").strip()
            for item in browser_results
            if str(item.get("scenario_family") or "").strip()
        }
    )
    passed_families = sorted(
        {
            str(item.get("scenario_family") or "").strip()
            for item in passed
            if bool(item.get("browser_required")) and str(item.get("scenario_family") or "").strip()
        }
    )
    missing_axes = [family for family in required_families if family not in passed_families]
    replay_required = [
        item
        for item in browser_results
        if bool(item.get("replay_required"))
    ]
    missing_replay = [
        str(item.get("scenario_id") or item.get("tc_id") or "")
        for item in replay_required
        if not str(item.get("replay_ref") or "").strip()
    ]
    missing_browser_pack = [
        str(item.get("scenario_id") or item.get("tc_id") or "")
        for item in browser_results
        if not str(item.get("browser_evidence_pack_ref") or "").strip()
    ]
    if missing_replay:
        missing_axes.append("deterministic_replay")
    if missing_browser_pack:
        missing_axes.append("browser_evidence_pack")
    browser_required = bool(browser_results)
    scenario_pass_rate = float(len(passed)) / float(total or 1)
    family_rate = (
        float(len(passed_families)) / float(len(required_families) or 1)
        if browser_required
        else 1.0
    )
    replay_rate = (
        float(len(replay_required) - len(missing_replay)) / float(len(replay_required) or 1)
        if replay_required
        else 1.0
    )
    browser_evidence_rate = (
        float(len(browser_results) - len(missing_browser_pack)) / float(len(browser_results) or 1)
        if browser_required
        else 1.0
    )
    threshold = 0.8 if browser_required else 0.6
    score = round((scenario_pass_rate + family_rate + replay_rate + browser_evidence_rate) / 4.0, 4)
    control = exhaustion_for_run(project_root, run_id=run_id)
    required_next_action = str(control.get("required_next_action") or "").strip()
    if not required_next_action:
        required_next_action = "close_missing_axes" if missing_axes else "ready_for_gate"
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "run_id": run_id,
        "generated_at": now_iso(),
        "execution_mode": str(plan.get("execution_mode") or "feature-aware"),
        "scenario_count": total,
        "browser_scenario_count": len(browser_results),
        "required_families": required_families,
        "passed_families": passed_families,
        "missing_axes": list(dict.fromkeys([axis for axis in missing_axes if axis])),
        "missing_replay_scenarios": missing_replay,
        "missing_browser_evidence_scenarios": missing_browser_pack,
        "scenario_pass_rate": round(scenario_pass_rate, 4),
        "family_coverage_rate": round(family_rate, 4),
        "replay_coverage_rate": round(replay_rate, 4),
        "browser_evidence_rate": round(browser_evidence_rate, 4),
        "score": score,
        "threshold": threshold,
        "status": "passed" if score >= threshold and not missing_axes else "blocked",
        "required_next_action": required_next_action,
        "failure_streak": int(control.get("failure_streak", 0) or 0),
        "escalation_level": str(control.get("escalation_level") or "E0"),
    }


def write_exhaustiveness_report(project_root: Path, *, feature: str, payload: dict[str, Any]) -> Path:
    path = feature_exhaustiveness_report_path(project_root, feature=feature)
    write_json(path, payload)
    return path
