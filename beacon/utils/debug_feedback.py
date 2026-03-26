"""Debug feedback helpers for prompt/event capture and memory assimilation."""

from __future__ import annotations

import json
from collections import Counter
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


def debug_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "debug"


def debug_run_dir(project_root: Path, run_id: str) -> Path:
    return debug_root(project_root) / "runs" / run_id


def debug_run_events_path(project_root: Path, run_id: str) -> Path:
    return debug_run_dir(project_root, run_id) / "events.jsonl"


def debug_run_summary_path(project_root: Path, run_id: str) -> Path:
    return debug_run_dir(project_root, run_id) / "summary.json"


def debug_issues_dir(project_root: Path) -> Path:
    return debug_root(project_root) / "issues"


def debug_ideas_dir(project_root: Path) -> Path:
    return debug_root(project_root) / "ideas"


def debug_index_path(project_root: Path) -> Path:
    return debug_root(project_root) / "index.json"


def infer_feedback_target(source: str, extra: dict[str, Any] | None = None) -> str:
    explicit = str((extra or {}).get("feedback_target", "") or "").strip()
    if explicit:
        return explicit
    lowered = str(source or "").strip().lower()
    if "gate" in lowered or "workflow" in lowered or "prompt" in lowered or "run." in lowered:
        return "beacon-core"
    if "team" in lowered:
        return "beacon-skill"
    return "beacon-core"


def _infer_result(*, executed: bool, exit_code: int | None, block_reason: str, boundary_state: str) -> str:
    if executed and exit_code not in {None, 0}:
        return "failed"
    if block_reason or boundary_state not in {"", "in_scope"}:
        return "degraded" if not executed else "succeeded-with-friction"
    return "succeeded-with-friction" if executed else "improved"


def _write_canonical_debug_event(
    project_root: Path,
    *,
    run_id: str,
    payload: dict[str, Any],
) -> None:
    run_dir = debug_run_dir(project_root, run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    event_path = debug_run_events_path(project_root, run_id)
    event_payload = {
        "schema_version": "1.0",
        "ts": str(payload.get("ts", "") or now_iso()),
        "run_id": run_id,
        "project_name": project_root.name,
        "project_root": str(project_root),
        "feature_slug": str(payload.get("feature_slug", "") or ""),
        "workflow_stage": str(payload.get("workflow_stage", "") or ""),
        "beacon_command": str(payload.get("recommended_command", "") or ""),
        "skill_id": str(payload.get("skill_id", "") or ""),
        "profile_id": str(payload.get("profile_id", "") or ""),
        "feedback_target": infer_feedback_target(str(payload.get("source", "") or ""), payload.get("extra") if isinstance(payload.get("extra"), dict) else None),
        "severity": "high" if str(payload.get("block_reason", "") or "") else "medium",
        "reason_code": str(payload.get("block_reason", "") or "runtime_feedback"),
        "expected": str(payload.get("goal", "") or ""),
        "actual": str(payload.get("note", "") or "") or str(payload.get("recommended_command", "") or ""),
        "friction_summary": str(payload.get("goal", "") or ""),
        "workaround": str(payload.get("recommended_command", "") or ""),
        "artifact_refs": [str(debug_feedback_path(project_root, run_id).relative_to(project_root))],
        "source_refs": [],
        "suggested_capability": str(((payload.get("extra") or {}).get("suggested_capability", "")) if isinstance(payload.get("extra"), dict) else ""),
        "candidate_doc_slug": str(((payload.get("extra") or {}).get("candidate_doc_slug", "")) if isinstance(payload.get("extra"), dict) else ""),
        "result": _infer_result(
            executed=bool(payload.get("executed")),
            exit_code=payload.get("exit_code") if isinstance(payload.get("exit_code"), int) else None,
            block_reason=str(payload.get("block_reason", "") or ""),
            boundary_state=str(payload.get("boundary_state", "") or ""),
        ),
    }
    append_jsonl(event_path, event_payload)
    _refresh_debug_run_summary(project_root, run_id)
    _refresh_debug_index(project_root)


def _load_canonical_debug_events(project_root: Path, *, run_id: str | None = None) -> list[dict[str, Any]]:
    roots = [debug_run_events_path(project_root, run_id)] if run_id else sorted(debug_root(project_root).glob("runs/*/events.jsonl"))
    rows: list[dict[str, Any]] = []
    for path in roots:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def _refresh_debug_run_summary(project_root: Path, run_id: str) -> None:
    events = _load_canonical_debug_events(project_root, run_id=run_id)
    reasons = Counter(str(item.get("reason_code", "") or "runtime_feedback") for item in events)
    targets = Counter(str(item.get("feedback_target", "") or "beacon-core") for item in events)
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": now_iso(),
        "event_count": len(events),
        "reason_counts": dict(reasons),
        "feedback_target_counts": dict(targets),
        "latest_event_at": str(events[-1].get("ts", "") if events else ""),
    }
    write_json(debug_run_summary_path(project_root, run_id), payload)


def _refresh_debug_index(project_root: Path) -> None:
    runs_root = debug_root(project_root) / "runs"
    entries: list[dict[str, Any]] = []
    if runs_root.exists():
        for summary in sorted(runs_root.glob("*/summary.json")):
            try:
                payload = json.loads(summary.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                payload = {}
            if isinstance(payload, dict):
                entries.append(payload)
    write_json(
        debug_index_path(project_root),
        {
            "schema_version": "1.0",
            "generated_at": now_iso(),
            "runs": entries,
        },
    )


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
    _write_canonical_debug_event(project_root, run_id=target_run_id, payload=payload)
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
