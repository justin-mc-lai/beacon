"""Debug feedback helpers for prompt/event capture and memory assimilation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.memory import append_memory_entry
from beacon.utils.runtime import append_jsonl, now_iso, utc_compact_ts, write_json

DEBUG_MODE_STATE_FILE = "debug-mode.json"


def debug_mode_state_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / DEBUG_MODE_STATE_FILE


def load_debug_mode_state(project_root: Path) -> dict[str, Any]:
    path = debug_mode_state_path(project_root)
    if not path.exists():
        return {
            "schema_version": "1.0",
            "enabled": False,
            "run_id": "",
            "updated_at": "",
            "source": "",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    return {
        "schema_version": "1.0",
        "enabled": bool(payload.get("enabled", False)),
        "run_id": str(payload.get("run_id", "") or ""),
        "updated_at": str(payload.get("updated_at", "") or ""),
        "source": str(payload.get("source", "") or ""),
    }


def save_debug_mode_state(
    project_root: Path,
    *,
    enabled: bool,
    run_id: str = "",
    source: str = "debug",
) -> dict[str, Any]:
    state = {
        "schema_version": "1.0",
        "enabled": bool(enabled),
        "run_id": str(run_id or "").strip(),
        "updated_at": now_iso(),
        "source": str(source or "").strip(),
    }
    write_json(debug_mode_state_path(project_root), state)
    return state


def is_debug_mode_enabled(project_root: Path) -> bool:
    return bool(load_debug_mode_state(project_root).get("enabled", False))


def resolve_debug_run_id(project_root: Path, run_id: str | None = None) -> str:
    explicit = str(run_id or "").strip()
    if explicit:
        return explicit
    state = load_debug_mode_state(project_root)
    saved = str(state.get("run_id", "") or "").strip()
    if saved:
        return saved
    return f"debug-{utc_compact_ts()}"


def debug_feedback_path(project_root: Path, run_id: str) -> Path:
    return project_root / ".beacon" / "state" / "debug-feedback" / f"{run_id}.jsonl"


def append_debug_feedback_event(
    project_root: Path,
    *,
    source: str,
    goal: str,
    intent: str,
    confidence: float,
    boundary_state: str,
    block_reason: str = "",
    recommended_command: str = "",
    executed: bool = False,
    exit_code: int | None = None,
    note: str = "",
    run_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> tuple[str, Path, dict[str, Any]]:
    target_run_id = resolve_debug_run_id(project_root, run_id=run_id)
    out_path = debug_feedback_path(project_root, target_run_id)
    payload: dict[str, Any] = {
        "ts": now_iso(),
        "run_id": target_run_id,
        "source": str(source or "").strip() or "unknown",
        "goal": str(goal or ""),
        "intent": str(intent or "").strip(),
        "confidence": float(confidence or 0.0),
        "boundary_state": str(boundary_state or "").strip() or "unknown",
        "block_reason": str(block_reason or "").strip(),
        "recommended_command": str(recommended_command or "").strip(),
        "executed": bool(executed),
        "exit_code": exit_code,
        "note": str(note or "").strip(),
    }
    if isinstance(extra, dict) and extra:
        payload["extra"] = extra
    append_jsonl(out_path, payload)
    return target_run_id, out_path, payload


def append_debug_event_memory(
    project_root: Path,
    *,
    run_id: str,
    event_payload: dict[str, Any],
    evidence_path: Path,
    source: str,
) -> dict[str, Any]:
    goal = str(event_payload.get("goal", "")).strip()
    intent = str(event_payload.get("intent", "")).strip() or "unknown"
    boundary_state = str(event_payload.get("boundary_state", "")).strip() or "unknown"
    confidence = float(event_payload.get("confidence", 0.0) or 0.0)
    block_reason = str(event_payload.get("block_reason", "")).strip()

    tags = ["debug-feedback", "prompt", intent, boundary_state]
    reason_codes: list[str] = []
    if block_reason:
        reason_codes.append(block_reason)
    if confidence < 0.62:
        reason_codes.append("low-confidence")

    text = f"[debug.prompt] {goal} | intent={intent} | confidence={round(confidence, 2)} | boundary={boundary_state}"
    return append_memory_entry(
        project_root=project_root,
        mem_type="insight",
        text=text,
        source_session_id=f"debug:{run_id}",
        source=source,
        evidence_ref=[str(evidence_path.relative_to(project_root))],
        confidence=max(0.0, min(1.0, confidence if confidence > 0 else 0.5)),
        tags=tags,
        reason_codes=reason_codes,
        upsert=True,
    )
