"""Prompt router history helpers shared by prompt/debug/hook flows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def prompt_router_history_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "memory" / "prompt-router-history.jsonl"


def append_prompt_router_history(project_root: Path, event: dict[str, Any]) -> Path:
    history_path = prompt_router_history_path(project_root)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return history_path


def load_prompt_router_history(project_root: Path, *, limit: int = 0) -> list[dict[str, Any]]:
    history_path = prompt_router_history_path(project_root)
    if not history_path.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(row, dict):
            rows.append(row)

    if limit > 0:
        return rows[-limit:]
    return rows
