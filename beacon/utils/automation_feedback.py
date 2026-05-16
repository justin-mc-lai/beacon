"""Automation feedback ledger and queue update helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.automation_runtime import (
    bounded_runtime_round_summary,
    derive_bounded_runtime_from_qa,
)
from beacon.utils.automation_queue import default_queue_path, load_automation_queue
from beacon.utils.qa_feature import load_feature_qa_status
from beacon.utils.qa_precision import load_feature_qa_scorecard
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug


def automation_feedback_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "automation"


def qa_feedback_ledger_path(project_root: Path) -> Path:
    return automation_feedback_root(project_root) / "qa-feedback-ledger.json"


def load_qa_feedback_ledger(project_root: Path) -> dict[str, Any]:
    payload = read_json(qa_feedback_ledger_path(project_root), {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("generated_at", "")
    payload.setdefault("entries", [])
    return payload


def _extract_feedback_entry(project_root: Path, *, feature: str) -> dict[str, Any]:
    status = load_feature_qa_status(project_root, feature=feature)
    scorecard = load_feature_qa_scorecard(project_root, feature=feature)
    feature_scorecard = status.get("feature_scorecard") if isinstance(status.get("feature_scorecard"), dict) else scorecard
    repair_handoff = feature_scorecard.get("repair_handoff") if isinstance(feature_scorecard.get("repair_handoff"), dict) else {}
    stop_reasons = feature_scorecard.get("stop_reasons") if isinstance(feature_scorecard.get("stop_reasons"), list) else []
    coverage_current = feature_scorecard.get("coverage_current") if isinstance(feature_scorecard.get("coverage_current"), dict) else {}
    bounded_runtime = derive_bounded_runtime_from_qa(project_root, feature=feature, status=status, scorecard=feature_scorecard)
    return {
        "feature": str(status.get("feature") or feature),
        "feature_slug": feature_slug(feature),
        "version": str(status.get("version") or ""),
        "run_id": str(status.get("run_id") or ""),
        "status": str(status.get("status") or "unknown"),
        "release_ready": bool(status.get("release_ready", False)),
        "evidence_done": bool(status.get("evidence_done", False)),
        "execution_mode": str(status.get("execution_mode") or ""),
        "targeted_layers": list(status.get("targeted_rerun", {}).get("targeted_layers") or status.get("targeted_layers") or []),
        "targeted_tc_ids": list(status.get("targeted_rerun", {}).get("targeted_tc_ids") or status.get("targeted_tc_ids") or []),
        "targeted_scenario_ids": list(status.get("targeted_rerun", {}).get("targeted_scenario_ids") or status.get("targeted_scenario_ids") or []),
        "stop_reasons": [str(item).strip() for item in stop_reasons if str(item).strip()],
        "continue_decision": str(feature_scorecard.get("continue_decision") or ""),
        "resume_command": str(feature_scorecard.get("resume_command") or ""),
        "repair_route": str(repair_handoff.get("action") or ""),
        "repair_command": str(repair_handoff.get("command") or ""),
        "coverage_rate": float(coverage_current.get("coverage_rate") or 0.0),
        "coverage_executed_scenarios": int(coverage_current.get("executed_scenarios") or 0),
        "coverage_required_scenarios": int(coverage_current.get("required_scenarios") or 0),
        "closure_state": str(bounded_runtime.get("closure_state") or ""),
        "next_route": str(bounded_runtime.get("next_route") or ""),
        "terminal_signal": str(bounded_runtime.get("terminal_signal") or ""),
        "round_number": int(bounded_runtime.get("round_number") or 0),
        "previous_round_ref": str(bounded_runtime.get("previous_round_ref") or ""),
        "current_round_ref": str(bounded_runtime.get("current_round_ref") or ""),
        "human_takeover_required": bool(bounded_runtime.get("human_takeover_required", False)),
        "active_issue_register": bounded_runtime.get("active_issue_register") if isinstance(bounded_runtime.get("active_issue_register"), dict) else {},
        "bounded_runtime": bounded_runtime,
        "runtime_summary": bounded_runtime_round_summary(bounded_runtime),
        "feature_status_path": str((project_root / ".beacon" / "qa" / "features" / feature_slug(feature) / "status.json").relative_to(project_root)),
        "scorecard_path": str((project_root / ".beacon" / "qa" / "features" / feature_slug(feature) / "scorecard.json").relative_to(project_root)),
        "updated_at": now_iso(),
    }


def refresh_qa_feedback_ledger(project_root: Path, *, features: list[str] | None = None) -> dict[str, Any]:
    target_features: list[str] = []
    if features:
        target_features = [str(item).strip() for item in features if str(item).strip()]
    else:
        feature_root = project_root / ".beacon" / "qa" / "features"
        if feature_root.exists():
            target_features = sorted(path.name for path in feature_root.iterdir() if path.is_dir())
    entries = [_extract_feedback_entry(project_root, feature=item) for item in target_features]
    payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "entry_count": len(entries),
        "entries": entries,
    }
    write_json(qa_feedback_ledger_path(project_root), payload)
    return payload


def _entry_needs_repair(entry: dict[str, Any]) -> bool:
    continue_decision = str(entry.get("continue_decision") or "").strip()
    next_route = str(entry.get("next_route") or "").strip()
    terminal_signal = str(entry.get("terminal_signal") or "").strip()
    repair_route = str(entry.get("repair_route") or "").strip()
    stop_reasons = {str(item).strip() for item in (entry.get("stop_reasons") or []) if str(item).strip()}
    return bool(
        continue_decision == "stop_for_repair"
        or next_route == "implement"
        or terminal_signal == "qa_route_implement_repair"
        or repair_route == "implement-repair"
        or stop_reasons
    )


def update_automation_queue_from_feedback(
    project_root: Path,
    *,
    queue_path: Path | None = None,
    expected_revision: int | None = None,
) -> dict[str, Any]:
    path = queue_path or default_queue_path(project_root)
    queue = load_automation_queue(path)
    queue_revision_before = int(queue.get("queue_revision") or 0)
    if expected_revision is not None and int(expected_revision) != queue_revision_before:
        return {
            "schema_version": "1.0",
            "status": "stale_writer_rejected",
            "queue_path": str(path),
            "ledger_path": str(qa_feedback_ledger_path(project_root)),
            "queue_revision_before": queue_revision_before,
            "queue_revision_after": queue_revision_before,
            "update_count": 0,
            "updates": [],
        }
    ledger = load_qa_feedback_ledger(project_root)
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), list) else []
    by_feature = {
        str(item.get("feature") or item.get("feature_slug") or "").strip(): item
        for item in entries
        if isinstance(item, dict) and str(item.get("feature") or item.get("feature_slug") or "").strip()
    }
    updates: list[dict[str, Any]] = []
    jobs = queue.get("jobs") if isinstance(queue.get("jobs"), list) else []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        job_kind = str(job.get("job_kind") or "").strip()
        selector = job.get("feature_selector") if isinstance(job.get("feature_selector"), dict) else {}
        features = selector.get("features") if isinstance(selector.get("features"), list) else []
        if job_kind == "qa":
            next_features: list[str] = []
            for feature in features:
                feature_name = str(feature).strip()
                if not feature_name:
                    continue
                entry = by_feature.get(feature_name) or by_feature.get(feature_slug(feature_name))
                if not isinstance(entry, dict):
                    next_features.append(feature_name)
                    continue
                if _entry_needs_repair(entry):
                    next_features.append(feature_name)
                    continue
                closure_state = str(entry.get("closure_state") or "").strip().lower()
                if closure_state in {"release_ready", "closed"} or str(entry.get("status") or "").strip().lower() == "passed":
                    updates.append({"job_id": str(job.get("job_id") or ""), "feature": feature_name, "action": "removed_from_qa_queue", "reason": "qa_passed"})
                    continue
                next_features.append(feature_name)
            selector["features"] = next_features
            job["feature_selector"] = selector
        if job_kind == "implement":
            current = {str(item).strip() for item in features if str(item).strip()}
            for feature_name, entry in by_feature.items():
                if not isinstance(entry, dict):
                    continue
                if _entry_needs_repair(entry):
                    canonical = str(entry.get("feature") or feature_name).strip()
                    if canonical and canonical not in current:
                        current.add(canonical)
                        updates.append({"job_id": str(job.get("job_id") or ""), "feature": canonical, "action": "added_to_implement_queue", "reason": "qa_repair_needed"})
            selector["features"] = sorted(current)
            job["feature_selector"] = selector
    queue["jobs"] = jobs
    queue["queue_revision"] = queue_revision_before + 1
    queue["last_feedback_sync_at"] = now_iso()
    write_json(path, queue)
    return {
        "schema_version": "1.0",
        "status": "updated",
        "queue_path": str(path),
        "ledger_path": str(qa_feedback_ledger_path(project_root)),
        "queue_revision_before": queue_revision_before,
        "queue_revision_after": int(queue.get("queue_revision") or 0),
        "update_count": len(updates),
        "updates": updates,
    }
