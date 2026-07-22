"""Structured agent trace (agent_trace.v1) for governed harness runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso
from beacon.utils.workflow_memory import ensure_lifecycle_files, lifecycle_index_path
import os


def lifecycle_trace_fail_closed_enabled() -> bool:
    """Governed stages fail when agent_trace append fails (default on).

    Override with BEACON_AGENT_TRACE_FAIL_CLOSED=0|false|off for soft mode.
    """
    raw = str(os.environ.get("BEACON_AGENT_TRACE_FAIL_CLOSED", "1") or "1").strip().lower()
    return raw not in {"0", "false", "no", "off", "soft"}


SCHEMA_VERSION = "agent_trace.v1"

EVENT_TYPES = frozenset({"decision", "failure", "retry", "output", "tool_call", "gate_verdict"})
ITERATION_EVENT_TYPES = frozenset({"decision", "failure", "retry", "output"})
LOOP_LAYERS = frozenset({"coding", "developer", "realworld"})

REASON_INVALID_EVENT_TYPE = "agent_trace_invalid_event_type"
REASON_INVALID_LOOP_LAYER = "agent_trace_invalid_loop_layer"
REASON_MISSING_REQUIRED_FIELD = "agent_trace_missing_required_field"
REASON_MISSING = "agent_trace_missing"
REASON_APPEND_FAILED = "agent_trace_append_failed"


def traces_dir(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / ".beacon" / "traces"


def trace_path(project_root: Path, run_id: str) -> Path:
    safe_run_id = str(run_id or "").strip()
    if not safe_run_id:
        raise ValueError("run_id is required")
    return traces_dir(project_root) / f"{safe_run_id}.jsonl"


def _read_index(project_root: Path) -> dict[str, Any]:
    ensure_lifecycle_files(project_root)
    path = lifecycle_index_path(project_root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    run_traces = payload.get("run_traces")
    if not isinstance(run_traces, dict):
        payload["run_traces"] = {}
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("dedupe_keys", [])
    return payload


def _write_index(project_root: Path, payload: dict[str, Any]) -> None:
    path = lifecycle_index_path(project_root)
    payload["updated_at"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_run_trace_index(project_root: Path, run_id: str) -> dict[str, Any] | None:
    index = _read_index(project_root)
    entry = index.get("run_traces", {}).get(str(run_id))
    return entry if isinstance(entry, dict) else None


def update_run_trace_index(
    project_root: Path,
    *,
    run_id: str,
    trace_path_value: str,
    trace_event_count: int,
) -> dict[str, Any]:
    index = _read_index(project_root)
    run_traces = index.setdefault("run_traces", {})
    entry = {
        "trace_path": str(trace_path_value),
        "trace_event_count": int(trace_event_count),
        "updated_at": now_iso(),
    }
    run_traces[str(run_id)] = entry
    _write_index(project_root, index)
    return entry


def validate_event(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {
            "status": "fail",
            "reason_code": REASON_MISSING_REQUIRED_FIELD,
            "findings": [{"field": "<root>", "message": "event must be an object"}],
        }
    findings: list[dict[str, Any]] = []
    required = ("schema_version", "event_type", "run_id", "timestamp", "iteration", "reason_code", "summary", "payload")
    for field in required:
        if field not in event:
            findings.append({"field": field, "message": "missing required field"})
    event_type = str(event.get("event_type") or "")
    if event_type and event_type not in EVENT_TYPES:
        return {
            "status": "fail",
            "reason_code": REASON_INVALID_EVENT_TYPE,
            "findings": [{"field": "event_type", "value": event_type}],
        }
    loop_layer = event.get("loop_layer")
    if loop_layer is not None and str(loop_layer).strip():
        if str(loop_layer) not in LOOP_LAYERS:
            return {
                "status": "fail",
                "reason_code": REASON_INVALID_LOOP_LAYER,
                "findings": [{"field": "loop_layer", "value": loop_layer}],
            }
    if not isinstance(event.get("payload"), dict):
        findings.append({"field": "payload", "message": "payload must be an object"})
    if findings:
        return {"status": "fail", "reason_code": REASON_MISSING_REQUIRED_FIELD, "findings": findings}
    return {"status": "pass", "reason_code": "", "findings": []}


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "schema_version": str(event.get("schema_version") or ""),
        "event_type": str(event.get("event_type") or ""),
        "run_id": str(event.get("run_id") or ""),
        "timestamp": str(event.get("timestamp") or ""),
        "iteration": int(event.get("iteration") or 0),
        "reason_code": str(event.get("reason_code") or ""),
        "summary": str(event.get("summary") or ""),
        "payload": event.get("payload") if isinstance(event.get("payload"), dict) else {},
    }
    if event.get("loop_layer") is not None:
        normalized["loop_layer"] = str(event.get("loop_layer"))
    return normalized


def normalize_trace_lines(lines: list[str]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        payload = json.loads(text)
        if isinstance(payload, dict):
            events.append(normalize_event(payload))
    events.sort(key=lambda item: (item.get("timestamp", ""), item.get("event_type", ""), item.get("iteration", 0)))
    return events


def read_trace_events(project_root: Path, run_id: str) -> list[dict[str, Any]]:
    path = trace_path(project_root, run_id)
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    return events


def append_event(project_root: Path, event: dict[str, Any]) -> dict[str, Any]:
    validation = validate_event(event)
    if validation.get("status") != "pass":
        return {"status": "blocked", **validation}
    run_id = str(event.get("run_id") or "")
    path = trace_path(project_root, run_id)
    try:
        if path.parent.exists() and not path.parent.is_dir():
            return {
                "status": "blocked",
                "reason_code": REASON_MISSING,
                "findings": [{"message": "traces path is not a directory"}],
            }
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    except OSError as exc:
        return {
            "status": "blocked",
            "reason_code": REASON_MISSING,
            "findings": [{"message": str(exc)}],
        }
    events = read_trace_events(project_root, run_id)
    rel_path = str(path.relative_to(project_root.expanduser().resolve()))
    update_run_trace_index(
        project_root,
        run_id=run_id,
        trace_path_value=rel_path,
        trace_event_count=len(events),
    )
    return {"status": "pass", "trace_path": rel_path, "trace_event_count": len(events)}


def build_event(
    *,
    run_id: str,
    event_type: str,
    summary: str,
    iteration: int = 0,
    reason_code: str = "",
    payload: dict[str, Any] | None = None,
    loop_layer: str | None = None,
    feature_slug: str | None = None,
    harness: str | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "event_type": event_type,
        "run_id": run_id,
        "timestamp": now_iso(),
        "iteration": int(iteration),
        "reason_code": str(reason_code or ""),
        "summary": str(summary or ""),
        "payload": dict(payload or {}),
    }
    if loop_layer:
        event["loop_layer"] = loop_layer
    if feature_slug:
        event["feature_slug"] = feature_slug
    if harness:
        event["harness"] = harness
    return event


def preflight_governed_trace(project_root: Path, *, run_id: str) -> dict[str, Any]:
    if not str(run_id or "").strip():
        return {"status": "blocked", "reason_code": REASON_MISSING, "findings": [{"message": "run_id required"}]}
    root = project_root.expanduser().resolve()
    tdir = traces_dir(root)
    if tdir.exists() and not tdir.is_dir():
        return {
            "status": "blocked",
            "reason_code": REASON_MISSING,
            "findings": [{"message": "traces path is not a directory"}],
        }
    try:
        tdir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {
            "status": "blocked",
            "reason_code": REASON_MISSING,
            "findings": [{"message": str(exc)}],
        }
    path = trace_path(root, run_id)
    return {
        "status": "pass",
        "reason_code": "",
        "trace_path": str(path.relative_to(root)),
    }


def record_governed_iteration(
    project_root: Path,
    *,
    run_id: str,
    event_type: str = "decision",
    summary: str,
    iteration: int = 0,
    reason_code: str = "",
    payload: dict[str, Any] | None = None,
    loop_layer: str | None = "coding",
    feature_slug: str | None = None,
    harness: str | None = None,
) -> dict[str, Any]:
    preflight = preflight_governed_trace(project_root, run_id=run_id)
    if preflight.get("status") != "pass":
        return preflight
    event = build_event(
        run_id=run_id,
        event_type=event_type,
        summary=summary,
        iteration=iteration,
        reason_code=reason_code,
        payload=payload,
        loop_layer=loop_layer,
        feature_slug=feature_slug,
        harness=harness,
    )
    return append_event(project_root, event)


def agent_trace_coverage_signal(project_root: Path) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    tdir = traces_dir(root)
    if not tdir.is_dir() or not any(tdir.glob("*.jsonl")):
        return {
            "signal": "agent_trace_coverage",
            "status": "missing",
            "reason_code": REASON_MISSING,
            "findings": [{"message": "no agent trace files under .beacon/traces/"}],
        }
    findings: list[dict[str, Any]] = []
    valid_runs = 0
    for path in sorted(tdir.glob("*.jsonl")):
        run_id = path.stem
        events = read_trace_events(root, run_id)
        if not events:
            findings.append({"run_id": run_id, "message": "empty trace file"})
            continue
        invalid = False
        for event in events:
            result = validate_event(event)
            if result.get("status") != "pass":
                invalid = True
                findings.append({"run_id": run_id, "reason_code": result.get("reason_code"), "message": "invalid event"})
                break
        if not invalid:
            valid_runs += 1
    if valid_runs > 0 and not findings:
        return {"signal": "agent_trace_coverage", "status": "pass", "reason_code": "", "findings": [], "valid_run_count": valid_runs}
    if valid_runs > 0:
        return {
            "signal": "agent_trace_coverage",
            "status": "fail",
            "reason_code": REASON_INVALID_EVENT_TYPE,
            "findings": findings,
            "valid_run_count": valid_runs,
        }
    return {
        "signal": "agent_trace_coverage",
        "status": "fail",
        "reason_code": REASON_MISSING,
        "findings": findings or [{"message": "trace files present but none valid"}],
    }

def resolve_lifecycle_trace_run_id(
    *,
    feature_slug: str | None = None,
    run_id: str | None = None,
    harness: str = "",
) -> str:
    """Prefer explicit/goal run_id; else stable per-feature lifecycle stream."""
    explicit = str(run_id or "").strip()
    if explicit:
        return explicit
    feat = str(feature_slug or "").strip() or "project"
    # keep filename-safe
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in feat)
    return f"lifecycle-{safe}"


def record_lifecycle_stage_trace(
    project_root: Path,
    *,
    harness: str,
    stage: str = "",
    feature_slug: str | None = None,
    run_id: str | None = None,
    event_type: str = "gate_verdict",
    summary: str = "",
    reason_code: str = "",
    payload: dict[str, Any] | None = None,
    iteration: int = 0,
    loop_layer: str | None = "coding",
    fail_closed: bool = False,
) -> dict[str, Any]:
    """Append one agent_trace.v1 event for a 1+6 lifecycle stage exit.

    No full chat bodies. Binds harness (+ feature_slug when known).
    When fail_closed=True, append/schema failure returns blocked (caller should not silent-pass).
    """
    root = Path(project_root).expanduser().resolve()
    harness_name = str(harness or "").strip() or "unknown"
    feat = str(feature_slug or "").strip() or None
    resolved_run = resolve_lifecycle_trace_run_id(
        feature_slug=feat,
        run_id=run_id,
        harness=harness_name,
    )
    body: dict[str, Any] = dict(payload or {})
    # never allow full chat authority in lifecycle traces
    body.pop("full_chat", None)
    body.setdefault("stage", str(stage or harness_name))
    body.setdefault("chat_body", None)
    summary_text = str(summary or f"{harness_name} stage exit").strip()[:240]
    result = record_governed_iteration(
        root,
        run_id=resolved_run,
        event_type=event_type if event_type in EVENT_TYPES else "gate_verdict",
        summary=summary_text,
        iteration=int(iteration or 0),
        reason_code=str(reason_code or ""),
        payload=body,
        loop_layer=loop_layer,
        feature_slug=feat,
        harness=harness_name,
    )
    out = {
        **result,
        "run_id": resolved_run,
        "harness": harness_name,
        "feature_slug": feat or "",
        "fail_closed": bool(fail_closed),
    }
    if fail_closed and str(result.get("status") or "") != "pass":
        out["status"] = "blocked"
        out.setdefault("reason_code", result.get("reason_code") or REASON_MISSING)
    return out

