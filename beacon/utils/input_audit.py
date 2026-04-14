"""Structured user input audit trail helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def user_input_audit_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "input-audit" / "events.jsonl"


def append_user_input_audit(project_root: Path, event: dict[str, Any]) -> Path:
    path = user_input_audit_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


def load_user_input_audit(
    project_root: Path,
    *,
    limit: int = 0,
    source: str = "",
    hook_event_name: str = "",
) -> list[dict[str, Any]]:
    path = user_input_audit_path(project_root)
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    source_filter = str(source or "").strip()
    hook_filter = str(hook_event_name or "").strip()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(payload, dict):
            continue
        if source_filter and str(payload.get("source", "")).strip() != source_filter:
            continue
        if hook_filter and str(payload.get("hook_event_name", "")).strip() != hook_filter:
            continue
        rows.append(payload)

    if limit > 0:
        return rows[-limit:]
    return rows
