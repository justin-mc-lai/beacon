"""Memory utilities for Beacon PTK-aligned memory envelope."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MEMORY_FILE_MAP: dict[str, tuple[str, str, str]] = {
    "insight": ("project-insights.json", "insights", "content"),
    "decision": ("decisions.json", "decisions", "decision"),
    "vocabulary": ("vocabulary.json", "terms", "term"),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_memory_type(value: str) -> str:
    raw = (value or "").strip().lower()
    alias = {
        "insights": "insight",
        "project-insight": "insight",
        "project-insights": "insight",
        "decisions": "decision",
        "vocab": "vocabulary",
        "term": "vocabulary",
        "terms": "vocabulary",
    }
    mapped = alias.get(raw, raw)
    if mapped not in MEMORY_FILE_MAP:
        raise ValueError(f"unsupported memory type: {value}")
    return mapped


def memory_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "memory"


def _memory_file_info(mem_type: str) -> tuple[Path, str, str]:
    normalized = normalize_memory_type(mem_type)
    filename, array_key, content_key = MEMORY_FILE_MAP[normalized]
    return Path(filename), array_key, content_key


def _read_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return fallback


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_memory_entry(
    project_root: Path,
    mem_type: str,
    text: str,
    *,
    source_session_id: str = "manual",
    source: str = "remember",
    evidence_ref: list[str] | None = None,
    confidence: float = 0.8,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    normalized = normalize_memory_type(mem_type)
    filename, array_key, content_key = MEMORY_FILE_MAP[normalized]
    path = memory_dir(project_root) / filename
    data = _read_json(path, {"schema_version": "3.0", array_key: [], "updated_at": now_iso()})

    entries = data.get(array_key)
    if not isinstance(entries, list):
        entries = []

    created_at = now_iso()
    entry: dict[str, Any] = {
        "memory_id": str(uuid.uuid4()),
        "type": normalized,
        "source_session_id": source_session_id or "manual",
        "source": source or "remember",
        "evidence_ref": [x for x in (evidence_ref or []) if x],
        "confidence": max(0.0, min(1.0, float(confidence))),
        "tags": sorted(set([x for x in (tags or []) if x])),
        "created_at": created_at,
        "updated_at": created_at,
        content_key: text,
    }
    # 兼容通用查询字段
    entry["content"] = text

    entries.append(entry)
    data[array_key] = entries
    data["schema_version"] = "3.0"
    data["updated_at"] = now_iso()
    _write_json(path, data)
    return entry


def load_memory_entries(project_root: Path, mem_type: str | None = None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    target_types = [normalize_memory_type(mem_type)] if mem_type else list(MEMORY_FILE_MAP.keys())
    for t in target_types:
        filename, array_key, content_key = MEMORY_FILE_MAP[t]
        path = memory_dir(project_root) / filename
        data = _read_json(path, {"schema_version": "3.0", array_key: []})
        arr = data.get(array_key)
        if not isinstance(arr, list):
            continue
        for item in arr:
            if not isinstance(item, dict):
                continue
            normalized = dict(item)
            if not isinstance(normalized.get("type"), str):
                normalized["type"] = t
            if not isinstance(normalized.get("content"), str):
                normalized["content"] = str(normalized.get(content_key, ""))
            result.append(normalized)
    result.sort(key=lambda x: str(x.get("updated_at", x.get("created_at", ""))), reverse=True)
    return result


def search_memory_entries(
    project_root: Path,
    query: str,
    *,
    mem_type: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    all_items = load_memory_entries(project_root, mem_type=mem_type)
    if not q:
        return all_items[: max(0, limit)]

    out: list[dict[str, Any]] = []
    for item in all_items:
        content = str(item.get("content", "")).lower()
        source = str(item.get("source", "")).lower()
        tags = [str(x).lower() for x in (item.get("tags") or []) if str(x).strip()]
        if q in content or q in source or any(q in tag for tag in tags):
            out.append(item)
            if len(out) >= max(0, limit):
                break
    return out


def scope_memory_paths(project_root: Path) -> tuple[Path, Path]:
    root = memory_dir(project_root) / "scope"
    return root / "deviations.json", root / "confirmations.json"


def append_scope_items(
    project_root: Path,
    *,
    deviations: list[dict[str, Any]],
    confirmations: list[dict[str, Any]],
) -> None:
    deviations_path, confirmations_path = scope_memory_paths(project_root)

    old_deviations = _read_json(deviations_path, {"items": []}).get("items")
    if not isinstance(old_deviations, list):
        old_deviations = []
    old_deviations.extend(deviations)
    _write_json(deviations_path, {"items": old_deviations, "updated_at": now_iso()})

    old_confirmations = _read_json(confirmations_path, {"items": []}).get("items")
    if not isinstance(old_confirmations, list):
        old_confirmations = []
    old_confirmations.extend(confirmations)
    _write_json(confirmations_path, {"items": old_confirmations, "updated_at": now_iso()})
