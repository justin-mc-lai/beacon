"""Shared runtime helpers for Beacon CLI commands."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_compact_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return fallback


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def runs_dir(project_root: Path) -> Path:
    d = project_root / ".beacon" / "runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def generate_run_id(project_root: Path) -> str:
    return f"run-{utc_compact_ts()}-{secrets.token_hex(2)}"


def newest_run_id(project_root: Path) -> str | None:
    directory = runs_dir(project_root)
    candidates = [p.name for p in directory.iterdir() if p.is_dir() and (p / "state.json").exists()]
    if not candidates:
        return None
    return sorted(candidates)[-1]


def load_run_state(project_root: Path, run_id: str) -> dict[str, Any] | None:
    path = runs_dir(project_root) / run_id / "state.json"
    if not path.exists():
        return None
    data = read_json(path, {})
    return data if isinstance(data, dict) else None


def save_run_state(project_root: Path, run_id: str, payload: dict[str, Any]) -> Path:
    path = runs_dir(project_root) / run_id / "state.json"
    write_json(path, payload)
    return path


def run_events_path(project_root: Path, run_id: str) -> Path:
    return runs_dir(project_root) / run_id / "events.jsonl"

