"""Release scorecard aggregation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.exhaustiveness import load_exhaustiveness_report
from beacon.utils.learning_loop import load_latest_evo_experiment
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.versioning import resolve_target_version


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def build_release_scorecard(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    gate_report = _load_json(project_root / ".beacon" / "gate-report.json")
    qa_status = load_qa_status(project_root)
    feature = str(qa_status.get("feature") or "").strip()
    exhaustiveness = load_exhaustiveness_report(project_root, feature=feature) if feature else {}
    scorecard_state = _load_json(project_root / ".beacon" / "state" / "evo" / "scorecards" / "latest.json")
    latest_experiment = load_latest_evo_experiment(project_root)
    blocked_count = len(
        [item for item in gate_report.get("issues", []) if isinstance(item, dict) and bool(item.get("blocked"))]
    ) if isinstance(gate_report.get("issues"), list) else 0
    decision_summary = scorecard_state.get("counts") if isinstance(scorecard_state.get("counts"), dict) else {}
    release_ready = (
        str(gate_report.get("status") or "").strip().lower() == "pass"
        and str(qa_status.get("status") or "").strip().lower() == "passed"
        and bool(qa_status.get("evidence_done", False))
        and (not exhaustiveness or str(exhaustiveness.get("status") or "").strip().lower() == "passed")
    )
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "release_ready": release_ready,
        "gate": {
            "status": str(gate_report.get("status") or "unknown"),
            "blocked_count": blocked_count,
            "run_id": str(gate_report.get("run_id") or ""),
        },
        "qa": {
            "feature": feature,
            "status": str(qa_status.get("status") or "unknown"),
            "evidence_done": bool(qa_status.get("evidence_done", False)),
            "execution_mode": str(qa_status.get("execution_mode") or "feature-aware"),
        },
        "exhaustiveness": exhaustiveness if isinstance(exhaustiveness, dict) else {},
        "learning_scorecard": {
            "main_kpi": str(scorecard_state.get("main_kpi") or "false_complete_rate"),
            "decision_summary": decision_summary,
            "candidate_count": len(scorecard_state.get("candidates", [])) if isinstance(scorecard_state.get("candidates"), list) else 0,
        },
        "latest_experiment": latest_experiment if isinstance(latest_experiment, dict) else {},
    }


def summarize_release_scorecard(scorecard: dict[str, Any] | None) -> dict[str, Any]:
    payload = scorecard if isinstance(scorecard, dict) else {}
    gate = payload.get("gate") if isinstance(payload.get("gate"), dict) else {}
    qa = payload.get("qa") if isinstance(payload.get("qa"), dict) else {}
    exhaustiveness = payload.get("exhaustiveness") if isinstance(payload.get("exhaustiveness"), dict) else {}
    learning = payload.get("learning_scorecard") if isinstance(payload.get("learning_scorecard"), dict) else {}
    decisions = learning.get("decision_summary") if isinstance(learning.get("decision_summary"), dict) else {}
    latest_experiment = payload.get("latest_experiment") if isinstance(payload.get("latest_experiment"), dict) else {}
    return {
        "release_ready": bool(payload.get("release_ready", False)),
        "gate_status": str(gate.get("status") or "unknown"),
        "gate_blocked_count": int(gate.get("blocked_count") or 0),
        "qa_status": str(qa.get("status") or "unknown"),
        "qa_execution_mode": str(qa.get("execution_mode") or "feature-aware"),
        "qa_evidence_done": bool(qa.get("evidence_done", False)),
        "exhaustiveness_status": str(exhaustiveness.get("status") or ""),
        "exhaustiveness_score": exhaustiveness.get("score"),
        "exhaustiveness_threshold": exhaustiveness.get("threshold"),
        "main_kpi": str(learning.get("main_kpi") or "false_complete_rate"),
        "main_kpi_score": latest_experiment.get("main_kpi_score"),
        "decision_keep": int(decisions.get("keep") or 0),
        "decision_review": int(decisions.get("review") or 0),
        "decision_discard": int(decisions.get("discard") or 0),
        "candidate_count": int(learning.get("candidate_count") or 0),
    }
