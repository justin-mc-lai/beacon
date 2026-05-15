"""Bounded automation runtime helpers for repeated QA/repair loops."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug

RUNTIME_SCHEMA_VERSION = "1.0"
RUNTIME_CLOSURE_STATES = {
    "active",
    "blocked",
    "release_ready",
    "closed",
    "human_escalation_required",
}
RUNTIME_NEXT_ROUTES = {"qa", "implement", "release", "human"}


def automation_runtime_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "automation" / "features"


def feature_automation_runtime_path(project_root: Path, *, feature: str) -> Path:
    return automation_runtime_root(project_root) / feature_slug(feature) / "runtime.json"


def load_feature_automation_runtime(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(feature_automation_runtime_path(project_root, feature=feature), {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schema_version", RUNTIME_SCHEMA_VERSION)
    payload.setdefault("feature", str(feature).strip())
    payload.setdefault("feature_slug", feature_slug(feature))
    payload.setdefault("round_number", 0)
    payload.setdefault("previous_round_ref", "")
    payload.setdefault("current_round_ref", "")
    payload.setdefault("closure_state", "active")
    payload.setdefault("next_route", "qa")
    payload.setdefault("terminal_signal", "")
    payload.setdefault("human_takeover_required", False)
    payload.setdefault("active_issue_register", {})
    return payload


def write_feature_automation_runtime(project_root: Path, *, feature: str, payload: dict[str, Any]) -> Path:
    path = feature_automation_runtime_path(project_root, feature=feature)
    write_json(path, payload)
    return path


def _fingerprint(parts: list[str]) -> str:
    text = "|".join(str(item or "").strip() for item in parts)
    if not text.strip("|"):
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _runtime_truth_hash(status: dict[str, Any], scorecard: dict[str, Any], *, feature: str, version: str) -> str:
    explicit = str(status.get("truth_hash") or scorecard.get("truth_hash") or "").strip()
    if explicit:
        return explicit
    return _fingerprint(
        [
            version,
            feature,
            str(status.get("story_revision") or ""),
            str(status.get("acceptance_revision") or ""),
        ]
    )


def _runtime_evidence_hash(status: dict[str, Any], scorecard: dict[str, Any]) -> str:
    explicit = str(status.get("implementation_evidence_hash") or scorecard.get("implementation_evidence_hash") or "").strip()
    if explicit:
        return explicit
    return _fingerprint(
        [
            str(status.get("run_id") or ""),
            str(status.get("status") or ""),
            str(scorecard.get("continue_decision") or ""),
            str(scorecard.get("resume_command") or ""),
        ]
    )


def _normalized_active_issue_register(
    *,
    previous: dict[str, Any],
    stop_reasons: list[str],
    targeted_layers: list[str],
    targeted_tc_ids: list[str],
    targeted_scenario_ids: list[str],
    latest_ref: str,
) -> dict[str, Any]:
    previous_register = previous.get("active_issue_register") if isinstance(previous.get("active_issue_register"), dict) else {}
    accepted_fixes = previous_register.get("accepted_fixes") if isinstance(previous_register.get("accepted_fixes"), list) else []
    return {
        "unresolved_stop_reasons": [str(item).strip() for item in stop_reasons if str(item).strip()],
        "accepted_fixes": [str(item).strip() for item in accepted_fixes if str(item).strip()],
        "targeted_rerun_hints": {
            "targeted_layers": [str(item).strip() for item in targeted_layers if str(item).strip()],
            "targeted_tc_ids": [str(item).strip() for item in targeted_tc_ids if str(item).strip()],
            "targeted_scenario_ids": [str(item).strip() for item in targeted_scenario_ids if str(item).strip()],
        },
        "latest_ref": latest_ref,
        "previous_round_ref": str(previous.get("current_round_ref") or ""),
    }


def _qa_route_from_status(
    *,
    qa_status: str,
    continue_decision: str,
    stop_reasons: list[str],
) -> tuple[str, str, str]:
    normalized_status = str(qa_status or "").strip().lower()
    normalized_continue = str(continue_decision or "").strip().lower()
    if normalized_status == "passed" or normalized_continue == "ready_for_release":
        return ("release_ready", "release", "qa_exit_ready_for_release")
    if normalized_continue == "stop_for_repair":
        return ("blocked", "implement", "qa_route_implement_repair")
    if normalized_continue in {"human_escalation", "route_human", "handoff_to_human"}:
        return ("human_escalation_required", "human", "qa_route_human_escalation")
    if normalized_status in {"blocked", "failed"} and stop_reasons:
        return ("human_escalation_required", "human", "qa_route_human_escalation")
    return ("active", "qa", "qa_observation_recorded")


def derive_bounded_runtime_from_qa(
    project_root: Path,
    *,
    feature: str,
    status: dict[str, Any],
    scorecard: dict[str, Any],
) -> dict[str, Any]:
    previous = load_feature_automation_runtime(project_root, feature=feature)
    feature_name = str(status.get("feature") or feature).strip() or str(feature).strip()
    feature_version = str(status.get("version") or scorecard.get("version") or "")
    continue_decision = str(scorecard.get("continue_decision") or status.get("feature_scorecard", {}).get("continue_decision") or "")
    stop_reasons = scorecard.get("stop_reasons") if isinstance(scorecard.get("stop_reasons"), list) else []
    targeted_rerun = status.get("targeted_rerun") if isinstance(status.get("targeted_rerun"), dict) else {}
    targeted_layers = list(targeted_rerun.get("targeted_layers") or status.get("targeted_layers") or [])
    targeted_tc_ids = list(targeted_rerun.get("targeted_tc_ids") or status.get("targeted_tc_ids") or [])
    targeted_scenario_ids = list(targeted_rerun.get("targeted_scenario_ids") or status.get("targeted_scenario_ids") or [])
    closure_state, next_route, terminal_signal = _qa_route_from_status(
        qa_status=str(status.get("status") or ""),
        continue_decision=continue_decision,
        stop_reasons=[str(item).strip() for item in stop_reasons if str(item).strip()],
    )
    run_id = str(status.get("run_id") or "").strip()
    current_round_ref = f"qa:{run_id or 'observation'}"
    previous_ref = str(previous.get("current_round_ref") or "")
    previous_run_ref = str(previous.get("source", {}).get("run_id") or "")
    round_number = int(previous.get("round_number") or 0)
    if not previous_ref:
        round_number = 0
    elif run_id and run_id != previous_run_ref:
        round_number = round_number + 1
    payload = {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "feature": feature_name,
        "feature_slug": feature_slug(feature_name),
        "version": feature_version,
        "closure_state": closure_state if closure_state in RUNTIME_CLOSURE_STATES else "active",
        "next_route": next_route if next_route in RUNTIME_NEXT_ROUTES else "qa",
        "terminal_signal": terminal_signal,
        "round_number": round_number,
        "previous_round_ref": previous_ref,
        "current_round_ref": current_round_ref,
        "truth_hash": _runtime_truth_hash(status, scorecard, feature=feature_name, version=feature_version),
        "implementation_evidence_hash": _runtime_evidence_hash(status, scorecard),
        "human_takeover_required": next_route == "human",
        "active_issue_register": _normalized_active_issue_register(
            previous=previous,
            stop_reasons=[str(item).strip() for item in stop_reasons if str(item).strip()],
            targeted_layers=targeted_layers,
            targeted_tc_ids=targeted_tc_ids,
            targeted_scenario_ids=targeted_scenario_ids,
            latest_ref=current_round_ref,
        ),
        "source": {
            "stage": "qa",
            "run_id": run_id,
            "status": str(status.get("status") or ""),
            "continue_decision": continue_decision,
        },
        "updated_at": now_iso(),
    }
    write_feature_automation_runtime(project_root, feature=feature_name, payload=payload)
    return payload


def record_implement_repair_round(
    project_root: Path,
    *,
    feature: str,
    accepted_fixes: list[str] | None = None,
    human_escalation: bool = False,
    outcome_ref: str = "",
) -> dict[str, Any]:
    previous = load_feature_automation_runtime(project_root, feature=feature)
    previous_register = previous.get("active_issue_register") if isinstance(previous.get("active_issue_register"), dict) else {}
    prior_fixes = previous_register.get("accepted_fixes") if isinstance(previous_register.get("accepted_fixes"), list) else []
    new_fixes = [str(item).strip() for item in (accepted_fixes or []) if str(item).strip()]
    accepted = list(dict.fromkeys([*prior_fixes, *new_fixes]))
    round_number = int(previous.get("round_number") or 0) + 1
    current_round_ref = str(outcome_ref or f"implement:round-{round_number}")
    next_route = "human" if human_escalation else "qa"
    terminal_signal = "implement_route_human_escalation" if human_escalation else "implement_exit_to_qa"
    closure_state = "human_escalation_required" if human_escalation else "active"
    payload = {
        **previous,
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "feature": str(previous.get("feature") or feature).strip() or str(feature).strip(),
        "feature_slug": feature_slug(str(previous.get("feature") or feature)),
        "closure_state": closure_state,
        "next_route": next_route,
        "terminal_signal": terminal_signal,
        "round_number": round_number,
        "previous_round_ref": str(previous.get("current_round_ref") or ""),
        "current_round_ref": current_round_ref,
        "human_takeover_required": human_escalation,
        "active_issue_register": {
            "unresolved_stop_reasons": list(previous_register.get("unresolved_stop_reasons") or []),
            "accepted_fixes": accepted,
            "targeted_rerun_hints": previous_register.get("targeted_rerun_hints") if isinstance(previous_register.get("targeted_rerun_hints"), dict) else {},
            "latest_ref": current_round_ref,
            "previous_round_ref": str(previous.get("current_round_ref") or ""),
        },
        "source": {
            "stage": "implement",
            "outcome_ref": current_round_ref,
        },
        "updated_at": now_iso(),
    }
    write_feature_automation_runtime(project_root, feature=str(previous.get("feature") or feature), payload=payload)
    return payload


def bounded_runtime_round_summary(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    payload = runtime_payload if isinstance(runtime_payload, dict) else {}
    return {
        "feature": str(payload.get("feature") or ""),
        "round_number": int(payload.get("round_number") or 0),
        "closure_state": str(payload.get("closure_state") or "active"),
        "next_route": str(payload.get("next_route") or "qa"),
        "terminal_signal": str(payload.get("terminal_signal") or ""),
        "human_takeover_required": bool(payload.get("human_takeover_required", False)),
        "current_round_ref": str(payload.get("current_round_ref") or ""),
        "previous_round_ref": str(payload.get("previous_round_ref") or ""),
    }
