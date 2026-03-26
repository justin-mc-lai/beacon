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


def write_qa_status(project_root: Path, payload: dict[str, Any]) -> dict[str, str]:
    """Write canonical QA status and legacy auto-test mirror."""
    canonical = qa_status_path(project_root)
    legacy = legacy_auto_test_status_path(project_root)
    payload = dict(payload)
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("updated_at", now_iso())
    write_json(canonical, payload)
    write_json(legacy, payload)
    return {
        "canonical": str(canonical.relative_to(project_root)),
        "legacy": str(legacy.relative_to(project_root)),
    }


def load_qa_status(project_root: Path) -> dict[str, Any]:
    """Load QA status preferring canonical v1.1.8 location."""
    for path in (qa_status_path(project_root), legacy_auto_test_status_path(project_root)):
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            payload = {}
        if isinstance(payload, dict):
            return payload
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
