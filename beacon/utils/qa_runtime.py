"""QA runtime status/session helpers for Beacon v1.1.8."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json


def qa_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "qa"


def qa_status_path(project_root: Path) -> Path:
    return qa_root(project_root) / "status.json"


def legacy_auto_test_status_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "auto-test-status.json"


def qa_legacy_admission_path(project_root: Path) -> Path:
    return qa_root(project_root) / "compatibility" / "legacy-auto-test-status-admission.json"


def _qa_summary(payload: dict[str, Any]) -> dict[str, Any]:
    feature_scorecard = payload.get("feature_scorecard") if isinstance(payload.get("feature_scorecard"), dict) else {}
    reconciliation = payload.get("reconciliation") if isinstance(payload.get("reconciliation"), dict) else (
        feature_scorecard.get("reconciliation") if isinstance(feature_scorecard.get("reconciliation"), dict) else {}
    )
    repair_handoff = feature_scorecard.get("repair_handoff") if isinstance(feature_scorecard.get("repair_handoff"), dict) else {}
    stop_reasons = [str(item).strip() for item in (feature_scorecard.get("stop_reasons") or payload.get("reason_codes") or []) if str(item).strip()]
    return {
        "feature": str(payload.get("feature") or ""),
        "version": str(payload.get("version") or ""),
        "status": str(payload.get("status") or "unknown"),
        "release_ready": bool(payload.get("release_ready", False)),
        "continue_decision": str(feature_scorecard.get("continue_decision") or ""),
        "stop_reasons": stop_reasons,
        "reconciliation_required": bool(reconciliation.get("required", False)),
        "reconciliation_reason_code": str(reconciliation.get("reason_code") or ""),
        "reconciliation_artifact_path": str(reconciliation.get("artifact_path") or ""),
        "reconciliation_reprojection_targets": list(((reconciliation.get("artifact") or {}).get("reprojection_targets")) or []),
        "repair_action": str(repair_handoff.get("action") or ""),
        "repair_command": str(repair_handoff.get("command") or ""),
    }


def write_qa_status(project_root: Path, payload: dict[str, Any]) -> dict[str, str]:
    """Write canonical QA status and legacy auto-test mirror."""
    canonical = qa_status_path(project_root)
    legacy = legacy_auto_test_status_path(project_root)
    payload = dict(payload)
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("updated_at", now_iso())
    payload["summary"] = _qa_summary(payload)
    write_json(canonical, payload)
    write_json(legacy, payload)
    return {
        "canonical": str(canonical.relative_to(project_root)),
        "legacy": str(legacy.relative_to(project_root)),
    }


def _load_json_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def write_qa_legacy_admission(project_root: Path, *, reason: str = "explicit_legacy_qa_admission") -> dict[str, Any]:
    payload = {
        "schema_version": "1.0",
        "compat_id": "qa-auto-test-status-legacy-mirror",
        "source": str(legacy_auto_test_status_path(project_root).relative_to(project_root)),
        "role": "historical_evidence",
        "reason": reason,
        "admitted_at": now_iso(),
    }
    path = qa_legacy_admission_path(project_root)
    write_json(path, payload)
    return {
        **payload,
        "path": str(path.relative_to(project_root)),
    }


def load_qa_status(project_root: Path, *, allow_legacy: bool = False, admission_reason: str = "explicit_legacy_qa_admission") -> dict[str, Any]:
    """Load current QA status.

    By default this reads only the canonical v1.1.8+ QA status. Legacy
    auto-test status is compatibility evidence and requires explicit admission.
    """
    canonical = _load_json_payload(qa_status_path(project_root))
    if canonical:
        canonical.setdefault("qa_status_source", "canonical")
        return canonical
    if not allow_legacy:
        return {}
    legacy = _load_json_payload(legacy_auto_test_status_path(project_root))
    if legacy:
        admission = write_qa_legacy_admission(project_root, reason=admission_reason)
        legacy = dict(legacy)
        legacy["qa_status_source"] = "legacy_admitted"
        legacy["compatibility_evidence"] = {
            "compat_id": "qa-auto-test-status-legacy-mirror",
            "role": "historical_evidence",
            "admission_ref": admission["path"],
        }
        return legacy
    return {}


def qa_sessions_root(project_root: Path) -> Path:
    return qa_root(project_root) / "sessions"


def qa_session_manifest_path(project_root: Path, session_id: str) -> Path:
    return qa_sessions_root(project_root) / session_id / "manifest.json"


def qa_current_session_path(project_root: Path) -> Path:
    return qa_root(project_root) / "current-session.json"


def write_qa_session(project_root: Path, session_id: str, payload: dict[str, Any]) -> dict[str, str]:
    session_root = qa_sessions_root(project_root) / session_id
    session_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1.0",
        "session_id": session_id,
        **payload,
        "updated_at": now_iso(),
    }
    manifest_path = session_root / "manifest.json"
    write_json(manifest_path, manifest)
    return {
        "manifest": str(manifest_path.relative_to(project_root)),
        "session_root": str(session_root.relative_to(project_root)),
    }


def load_qa_session(project_root: Path, session_id: str) -> dict[str, Any]:
    path = qa_session_manifest_path(project_root, session_id)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        payload = {}
    return payload if isinstance(payload, dict) else {}


def list_qa_sessions(project_root: Path) -> list[dict[str, Any]]:
    root = qa_sessions_root(project_root)
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for manifest in sorted(root.glob("*/manifest.json")):
        payload = load_qa_session(project_root, manifest.parent.name)
        if payload:
            rows.append(payload)
    return rows


def set_current_qa_session(project_root: Path, session_id: str) -> dict[str, str]:
    payload = {
        "schema_version": "1.0",
        "session_id": session_id,
        "updated_at": now_iso(),
    }
    path = qa_current_session_path(project_root)
    write_json(path, payload)
    return {"current_session": str(path.relative_to(project_root))}


def load_current_qa_session(project_root: Path) -> dict[str, Any]:
    path = qa_current_session_path(project_root)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        payload = {}
    return payload if isinstance(payload, dict) else {}
