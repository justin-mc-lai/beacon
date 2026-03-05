"""Memory utilities for Beacon PTK-aligned memory envelope."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

MEMORY_FILE_MAP: dict[str, tuple[str, str, str]] = {
    "insight": ("project-insights.json", "insights", "content"),
    "decision": ("decisions.json", "decisions", "decision"),
    "vocabulary": ("vocabulary.json", "terms", "term"),
    "feedback": ("feedback.json", "items", "content"),
}
MEMORY_V1_FILE = "memory-v1.json"


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
        "fb": "feedback",
    }
    mapped = alias.get(raw, raw)
    if mapped not in MEMORY_FILE_MAP:
        raise ValueError(f"unsupported memory type: {value}")
    return mapped


def memory_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "memory"


def memory_v1_path(project_root: Path) -> Path:
    return memory_dir(project_root) / MEMORY_V1_FILE


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


def _normalize_reason_codes(values: Iterable[str] | None) -> list[str]:
    if not values:
        return []
    normalized = []
    for value in values:
        text = str(value or "").strip()
        if text:
            normalized.append(text)
    return sorted(set(normalized))


def _content_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _load_memory_v1(project_root: Path) -> dict[str, Any]:
    path = memory_v1_path(project_root)
    payload = _read_json(path, {"schema_version": "1.0", "items": [], "updated_at": now_iso()})
    if not isinstance(payload.get("items"), list):
        payload["items"] = []
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("updated_at", now_iso())
    return payload


def _save_memory_v1(project_root: Path, payload: dict[str, Any]) -> None:
    path = memory_v1_path(project_root)
    payload["schema_version"] = "1.0"
    payload["updated_at"] = now_iso()
    _write_json(path, payload)


def _load_legacy_entries(project_root: Path, mem_type: str | None = None) -> list[dict[str, Any]]:
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
            normalized["type"] = t
            normalized["content"] = str(normalized.get("content", normalized.get(content_key, "")))
            result.append(normalized)
    return result


def _migrate_legacy_to_v1_if_needed(project_root: Path) -> dict[str, Any]:
    path = memory_v1_path(project_root)
    if path.exists():
        return _load_memory_v1(project_root)

    legacy_rows = _load_legacy_entries(project_root)
    payload = {"schema_version": "1.0", "items": [], "updated_at": now_iso()}
    for row in legacy_rows:
        content = str(row.get("content", "")).strip()
        created_at = str(row.get("created_at", "") or now_iso())
        updated_at = str(row.get("updated_at", "") or created_at)
        entry: dict[str, Any] = {
            "memory_id": str(row.get("memory_id", "") or str(uuid.uuid4())),
            "type": normalize_memory_type(str(row.get("type", "insight"))),
            "status": str(row.get("status", "active") or "active"),
            "content": content,
            "content_hash": str(row.get("content_hash", "") or _content_hash(content)),
            "source_session_id": str(row.get("source_session_id", "manual") or "manual"),
            "source": str(row.get("source", "remember") or "remember"),
            "evidence_ref": [str(x) for x in (row.get("evidence_ref") or []) if str(x).strip()],
            "reason_codes": _normalize_reason_codes(row.get("reason_codes") or []),
            "confidence": max(0.0, min(1.0, float(row.get("confidence", 0.8) or 0.8))),
            "tags": sorted(set(str(x) for x in (row.get("tags") or []) if str(x).strip())),
            "created_at": created_at,
            "updated_at": updated_at,
        }
        if row.get("revision_of"):
            entry["revision_of"] = str(row.get("revision_of"))
        if row.get("superseded_by"):
            entry["superseded_by"] = str(row.get("superseded_by"))
        payload["items"].append(entry)
    _save_memory_v1(project_root, payload)
    return payload


def _write_legacy_projection(project_root: Path, items: list[dict[str, Any]]) -> None:
    grouped: dict[str, list[dict[str, Any]]] = {key: [] for key in MEMORY_FILE_MAP}
    for item in items:
        if not isinstance(item, dict):
            continue
        mem_type = normalize_memory_type(str(item.get("type", "insight")))
        grouped[mem_type].append(item)

    for mem_type, rows in grouped.items():
        filename, array_key, content_key = MEMORY_FILE_MAP[mem_type]
        projected: list[dict[str, Any]] = []
        for row in rows:
            content = str(row.get("content", ""))
            payload = {
                "memory_id": str(row.get("memory_id", "")),
                "type": mem_type,
                "status": str(row.get("status", "active") or "active"),
                "source_session_id": str(row.get("source_session_id", "manual") or "manual"),
                "source": str(row.get("source", "remember") or "remember"),
                "evidence_ref": [str(x) for x in (row.get("evidence_ref") or []) if str(x).strip()],
                "reason_codes": _normalize_reason_codes(row.get("reason_codes") or []),
                "confidence": max(0.0, min(1.0, float(row.get("confidence", 0.8) or 0.8))),
                "tags": sorted(set(str(x) for x in (row.get("tags") or []) if str(x).strip())),
                "created_at": str(row.get("created_at", "") or now_iso()),
                "updated_at": str(row.get("updated_at", "") or now_iso()),
                "content": content,
                "content_hash": str(row.get("content_hash", "") or _content_hash(content)),
            }
            if row.get("revision_of"):
                payload["revision_of"] = str(row.get("revision_of"))
            if row.get("superseded_by"):
                payload["superseded_by"] = str(row.get("superseded_by"))
            payload[content_key] = content
            projected.append(payload)
        _write_json(
            memory_dir(project_root) / filename,
            {"schema_version": "3.0", array_key: projected, "updated_at": now_iso()},
        )


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
    revision_of: str | None = None,
    reason_codes: list[str] | None = None,
    status: str = "active",
    upsert: bool = False,
) -> dict[str, Any]:
    normalized = normalize_memory_type(mem_type)
    payload = _migrate_legacy_to_v1_if_needed(project_root)
    items = payload.get("items")
    if not isinstance(items, list):
        items = []
        payload["items"] = items

    content = str(text or "")
    content_hash = _content_hash(content)
    refs = [str(x) for x in (evidence_ref or []) if str(x).strip()]
    normalized_reason_codes = _normalize_reason_codes(reason_codes)
    normalized_tags = sorted(set(str(x) for x in (tags or []) if str(x).strip()))
    now = now_iso()

    if upsert:
        for row in reversed(items):
            if not isinstance(row, dict):
                continue
            if normalize_memory_type(str(row.get("type", ""))) != normalized:
                continue
            if str(row.get("content_hash", "")) != content_hash:
                continue
            if str(row.get("source_session_id", "")) != str(source_session_id or "manual"):
                continue
            if str(row.get("source", "")) != str(source or "remember"):
                continue
            if str(row.get("status", "active")) == "archived":
                continue
            row["status"] = "active"
            row["evidence_ref"] = sorted(set(list(row.get("evidence_ref", [])) + refs))
            row["reason_codes"] = sorted(set(list(row.get("reason_codes", [])) + normalized_reason_codes))
            row["tags"] = sorted(set(list(row.get("tags", [])) + normalized_tags))
            row["updated_at"] = now
            row["confidence"] = max(
                0.0,
                min(1.0, float(max(float(row.get("confidence", 0.0) or 0.0), float(confidence)))),
            )
            _save_memory_v1(project_root, payload)
            _write_legacy_projection(project_root, payload["items"])
            return row

    created_at = now
    entry: dict[str, Any] = {
        "memory_id": str(uuid.uuid4()),
        "type": normalized,
        "status": str(status or "active"),
        "content": content,
        "content_hash": content_hash,
        "source_session_id": source_session_id or "manual",
        "source": source or "remember",
        "evidence_ref": refs,
        "reason_codes": normalized_reason_codes,
        "confidence": max(0.0, min(1.0, float(confidence))),
        "tags": normalized_tags,
        "created_at": created_at,
        "updated_at": created_at,
    }
    if normalized == "decision":
        entry["decision"] = content
    elif normalized == "vocabulary":
        entry["term"] = content
    if revision_of:
        entry["revision_of"] = str(revision_of)
        for row in items:
            if not isinstance(row, dict):
                continue
            if str(row.get("memory_id", "")) != str(revision_of):
                continue
            row["status"] = "superseded"
            row["superseded_by"] = entry["memory_id"]
            row["updated_at"] = created_at
            break

    items.append(entry)
    _save_memory_v1(project_root, payload)
    _write_legacy_projection(project_root, payload["items"])
    return entry


def load_memory_entries(project_root: Path, mem_type: str | None = None) -> list[dict[str, Any]]:
    payload = _migrate_legacy_to_v1_if_needed(project_root)
    items = payload.get("items")
    if not isinstance(items, list):
        items = []
    target_type = normalize_memory_type(mem_type) if mem_type else None
    result: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized = dict(item)
        normalized["type"] = normalize_memory_type(str(normalized.get("type", "insight")))
        if target_type and normalized["type"] != target_type:
            continue
        normalized["content"] = str(normalized.get("content", ""))
        if normalized["type"] == "decision" and "decision" not in normalized:
            normalized["decision"] = normalized["content"]
        if normalized["type"] == "vocabulary" and "term" not in normalized:
            normalized["term"] = normalized["content"]
        normalized["reason_codes"] = _normalize_reason_codes(normalized.get("reason_codes") or [])
        normalized["tags"] = sorted(set(str(x) for x in (normalized.get("tags") or []) if str(x).strip()))
        normalized["status"] = str(normalized.get("status", "active") or "active")
        if "content_hash" not in normalized:
            normalized["content_hash"] = _content_hash(normalized["content"])
        result.append(normalized)
    result.sort(key=lambda x: str(x.get("updated_at", x.get("created_at", ""))), reverse=True)
    return result


def _shape_memory_layer(item: dict[str, Any], *, layer: str) -> dict[str, Any]:
    if layer == "index":
        return {
            "memory_id": item.get("memory_id"),
            "type": item.get("type"),
            "status": item.get("status", "active"),
            "summary": str(item.get("content", ""))[:120],
            "reason_codes": item.get("reason_codes", []),
            "tags": item.get("tags", []),
            "updated_at": item.get("updated_at"),
        }
    if layer == "timeline":
        return {
            "memory_id": item.get("memory_id"),
            "type": item.get("type"),
            "status": item.get("status", "active"),
            "content": item.get("content", ""),
            "source_session_id": item.get("source_session_id", "manual"),
            "source": item.get("source", "remember"),
            "reason_codes": item.get("reason_codes", []),
            "tags": item.get("tags", []),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
        }
    return dict(item)


def search_memory_entries(
    project_root: Path,
    query: str,
    *,
    mem_type: str | None = None,
    limit: int = 10,
    mode: str = "hybrid",
    layer: str = "detail",
    ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    effective_mode = str(mode or "hybrid").strip().lower()
    if effective_mode not in {"keyword", "semantic", "hybrid"}:
        effective_mode = "hybrid"
    effective_layer = str(layer or "detail").strip().lower()
    if effective_layer not in {"index", "timeline", "detail"}:
        effective_layer = "detail"

    all_items = load_memory_entries(project_root, mem_type=mem_type)
    id_filter = {str(x).strip() for x in (ids or []) if str(x).strip()}
    if id_filter:
        all_items = [item for item in all_items if str(item.get("memory_id", "")) in id_filter]
    if not q and not id_filter:
        return [_shape_memory_layer(item, layer=effective_layer) for item in all_items[: max(0, limit)]]

    out: list[tuple[float, dict[str, Any]]] = []
    query_terms = [term for term in q.replace("-", " ").split() if term]
    for item in all_items:
        content = str(item.get("content", "")).lower()
        source = str(item.get("source", "")).lower()
        tags = [str(x).lower() for x in (item.get("tags") or []) if str(x).strip()]
        direct_match = not q or q in content or q in source or any(q in tag for tag in tags)
        overlap = 0.0
        if query_terms:
            corpus = " ".join([content, source, " ".join(tags)])
            hits = sum(1 for term in query_terms if term in corpus)
            overlap = float(hits) / float(len(query_terms))
        semantic_match = overlap >= 0.34
        if effective_mode == "keyword":
            matched = direct_match
            score = 1.0 if direct_match else 0.0
        elif effective_mode == "semantic":
            matched = semantic_match
            score = overlap
        else:
            matched = direct_match or semantic_match
            score = 1.0 if direct_match else overlap
        if matched:
            out.append((score, item))
    out.sort(key=lambda row: (row[0], str(row[1].get("updated_at", ""))), reverse=True)
    return [_shape_memory_layer(row[1], layer=effective_layer) for row in out[: max(0, limit)]]


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
