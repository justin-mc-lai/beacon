"""Workflow lifecycle memory helpers.

This module builds a PTK-style memory loop for the default workflow path:
think -> user-story -> prd -> test-case -> implementation -> verify -> gate.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from beacon.utils.memory import append_memory_entry, load_memory_entries
from beacon.utils.runtime import load_run_state, now_iso, runs_dir

LIFECYCLE_FILE = "workflow-lifecycle.json"
LIFECYCLE_INDEX_FILE = "workflow-lifecycle.index.json"
LIFECYCLE_SCHEMA_FILE = "workflow-lifecycle.schema.json"
WORKFLOW_STAGES = ("think", "user-story", "prd", "test-case", "implementation", "verify", "gate")

_ALLOW_REPEAT_EVENTS = {
    # stage retry trace
    "stage_started",
    "stage_skipped",
    "stage_context_injected",
    "stage_finished",
    "stage_failed",
    "memory_writeback",
    # interactive HUD lifecycle
    "hud_rendered",
    "next_step_prompted",
    "human_checkpoint_confirmed",
    "human_checkpoint_rejected",
    "workflow_paused",
    "feedback_apply_triggered",
}

_LIFECYCLE_SCHEMA = {
    "schema_version": "1.0",
    "title": "Beacon Workflow Lifecycle Memory",
    "type": "object",
    "required": ["schema_version", "items", "updated_at"],
    "properties": {
        "schema_version": {"type": "string"},
        "updated_at": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "event_id",
                    "run_id",
                    "stage",
                    "event",
                    "source",
                    "source_session_id",
                    "evidence_ref",
                    "ts",
                ],
                "properties": {
                    "event_id": {"type": "string"},
                    "run_id": {"type": "string"},
                    "stage": {"type": "string"},
                    "event": {"type": "string"},
                    "source": {"type": "string"},
                    "source_session_id": {"type": "string"},
                    "evidence_ref": {"type": "array", "items": {"type": "string"}},
                    "ts": {"type": "string"},
                    "attempt_id": {"type": "string"},
                    "attempt_seq": {"type": "integer"},
                    "supersedes_event_id": {"type": "string"},
                    "details": {"type": "object"},
                },
            },
        },
    },
}


def _memory_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "memory"


def lifecycle_path(project_root: Path) -> Path:
    return _memory_root(project_root) / LIFECYCLE_FILE


def lifecycle_index_path(project_root: Path) -> Path:
    return _memory_root(project_root) / LIFECYCLE_INDEX_FILE


def lifecycle_schema_path(project_root: Path) -> Path:
    return _memory_root(project_root) / LIFECYCLE_SCHEMA_FILE


def stage_context_path(project_root: Path, run_id: str, stage: str) -> Path:
    return project_root / ".beacon" / "state" / "workflow-memory" / run_id / f"{stage}-context.json"


def _read_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:  # noqa: BLE001
        return fallback
    return fallback


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_lifecycle_files(project_root: Path) -> None:
    root = _memory_root(project_root)
    root.mkdir(parents=True, exist_ok=True)

    lifecycle = lifecycle_path(project_root)
    if not lifecycle.exists():
        _write_json(lifecycle, {"schema_version": "1.0", "items": [], "updated_at": now_iso()})

    index = lifecycle_index_path(project_root)
    if not index.exists():
        _write_json(index, {"schema_version": "1.0", "dedupe_keys": [], "updated_at": now_iso()})

    schema = lifecycle_schema_path(project_root)
    if not schema.exists():
        _write_json(schema, _LIFECYCLE_SCHEMA)


def _dedupe_key(
    *,
    run_id: str,
    stage: str,
    event: str,
    evidence_ref: list[str] | None,
    source: str,
) -> str:
    refs = sorted([str(x) for x in (evidence_ref or []) if str(x).strip()])
    return "|".join([run_id, stage, event, source, ",".join(refs)])


def append_lifecycle_event(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    event: str,
    source: str = "workflow",
    source_session_id: str | None = None,
    evidence_ref: list[str] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ensure_lifecycle_files(project_root)
    lifecycle_file = lifecycle_path(project_root)
    index_file = lifecycle_index_path(project_root)

    lifecycle = _read_json(lifecycle_file, {"schema_version": "1.0", "items": [], "updated_at": now_iso()})
    index = _read_json(index_file, {"schema_version": "1.0", "dedupe_keys": [], "updated_at": now_iso()})

    items = lifecycle.get("items")
    if not isinstance(items, list):
        items = []
    dedupe_keys = index.get("dedupe_keys")
    if not isinstance(dedupe_keys, list):
        dedupe_keys = []

    refs = [str(x) for x in (evidence_ref or []) if str(x).strip()]

    stage_events = [
        item
        for item in items
        if isinstance(item, dict) and item.get("run_id") == run_id and item.get("stage") == stage
    ]
    latest_attempt_seq = 0
    for item in stage_events:
        value = item.get("attempt_seq")
        try:
            seq = int(value)
        except Exception:  # noqa: BLE001
            seq = 0
        if seq > latest_attempt_seq:
            latest_attempt_seq = seq
    explicit_attempt_seq = None
    if details and isinstance(details, dict) and "attempt_seq" in details:
        try:
            explicit_attempt_seq = int(details.get("attempt_seq"))
        except Exception:  # noqa: BLE001
            explicit_attempt_seq = None

    attempt_seq = 0
    if stage in WORKFLOW_STAGES:
        if explicit_attempt_seq is not None and explicit_attempt_seq > 0:
            attempt_seq = explicit_attempt_seq
        elif event == "stage_started":
            attempt_seq = latest_attempt_seq + 1 if latest_attempt_seq > 0 else 1
        else:
            attempt_seq = latest_attempt_seq if latest_attempt_seq > 0 else 1
    attempt_id = f"{stage}@attempt-{attempt_seq}" if attempt_seq > 0 and stage in WORKFLOW_STAGES else None

    supersedes_event_id = None
    if stage in WORKFLOW_STAGES and event == "stage_started":
        if stage_events:
            supersedes_event_id = str(stage_events[-1].get("event_id", "") or "") or None
    if details and isinstance(details, dict) and details.get("supersedes_event_id"):
        supersedes_event_id = str(details.get("supersedes_event_id"))
    key = _dedupe_key(run_id=run_id, stage=stage, event=event, evidence_ref=refs, source=source)
    if event not in _ALLOW_REPEAT_EVENTS and key in dedupe_keys:
        # Return existing latest event with same dedupe key.
        for item in reversed(items):
            if (
                item.get("run_id") == run_id
                and item.get("stage") == stage
                and item.get("event") == event
                and item.get("source") == source
            ):
                return item

    payload = {
        "event_id": str(uuid.uuid4()),
        "run_id": run_id,
        "stage": stage,
        "event": event,
        "source": source,
        "source_session_id": source_session_id or run_id,
        "evidence_ref": refs,
        "ts": now_iso(),
        "details": details or {},
    }
    if attempt_id:
        payload["attempt_id"] = attempt_id
        payload["attempt_seq"] = attempt_seq
    if supersedes_event_id:
        payload["supersedes_event_id"] = supersedes_event_id
    items.append(payload)
    dedupe_keys.append(key)

    lifecycle["schema_version"] = "1.0"
    lifecycle["items"] = items[-5000:]
    lifecycle["updated_at"] = now_iso()
    index["schema_version"] = "1.0"
    index["dedupe_keys"] = dedupe_keys[-8000:]
    index["updated_at"] = now_iso()

    _write_json(lifecycle_file, lifecycle)
    _write_json(index_file, index)
    return payload


def load_lifecycle_events(
    project_root: Path,
    *,
    run_id: str | None = None,
    stage: str | None = None,
    event: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    ensure_lifecycle_files(project_root)
    lifecycle = _read_json(lifecycle_path(project_root), {"schema_version": "1.0", "items": []})
    items = lifecycle.get("items")
    if not isinstance(items, list):
        items = []
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if run_id and item.get("run_id") != run_id:
            continue
        if stage and item.get("stage") != stage:
            continue
        if event and item.get("event") != event:
            continue
        out.append(item)
    out.sort(key=lambda x: str(x.get("ts", "")))
    if isinstance(limit, int) and limit >= 0:
        return out[-limit:]
    return out


def build_stage_context(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    feature: str,
    limit: int = 8,
) -> dict[str, Any]:
    memories = load_memory_entries(project_root)
    lifecycle = load_lifecycle_events(project_root, run_id=run_id, limit=20)
    feature_l = (feature or "").lower()

    selected_memories: list[dict[str, Any]] = []
    for item in memories:
        content = str(item.get("content", "")).lower()
        tags = [str(x).lower() for x in item.get("tags", []) if str(x).strip()]
        if feature_l and feature_l in content:
            selected_memories.append(item)
            continue
        if stage.replace("-", "") in "".join(tags):
            selected_memories.append(item)
            continue
        if len(selected_memories) < limit:
            selected_memories.append(item)
        if len(selected_memories) >= limit:
            break

    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "stage": stage,
        "feature": feature,
        "generated_at": now_iso(),
        "memory_recall": selected_memories[:limit],
        "lifecycle_events": lifecycle[-limit:],
    }


def write_stage_context(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    feature: str,
) -> Path:
    payload = build_stage_context(project_root, run_id=run_id, stage=stage, feature=feature)
    path = stage_context_path(project_root, run_id, stage)
    _write_json(path, payload)
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=stage,
        event="stage_context_injected",
        source="workflow.memory.recall",
        evidence_ref=[str(path.relative_to(project_root))],
        details={"recall_count": len(payload.get("memory_recall", []))},
    )
    return path


def record_stage_writeback(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    feature: str,
    evidence_ref: list[str],
    status: str,
) -> dict[str, Any]:
    mem_type = "insight" if stage == "think" else "decision"
    summary = f"[{stage}] {feature} => {status}"
    entry = append_memory_entry(
        project_root=project_root,
        mem_type=mem_type,
        text=summary,
        source_session_id=run_id,
        source=f"workflow.{stage}.writeback",
        evidence_ref=evidence_ref,
        confidence=0.8,
        tags=["workflow-lifecycle", stage, status.lower()],
    )
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=stage,
        event="memory_writeback",
        source="workflow.memory.writeback",
        evidence_ref=evidence_ref,
        details={"memory_id": entry.get("memory_id"), "memory_type": mem_type},
    )
    return entry


def _latest_run_id_from_events(events: list[dict[str, Any]]) -> str | None:
    if not events:
        return None
    ordered = sorted(events, key=lambda x: str(x.get("ts", "")))
    return str(ordered[-1].get("run_id", "") or "") or None


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def resolve_workflow_run_id(
    project_root: Path,
    *,
    run_id: str | None = None,
    version: str | None = None,
    feature: str | None = None,
) -> str | None:
    """Resolve workflow run-id by explicit id or version/feature filters.

    Priority:
    1. explicit run_id (if exists)
    2. latest workflow.start run matching version/feature
    """
    if run_id:
        if load_run_state(project_root, run_id):
            return run_id
        if load_lifecycle_events(project_root, run_id=run_id):
            return run_id
        return None

    versions_filter = (version or "").strip()
    feature_filter = _slug(feature or "")
    candidates: list[tuple[str, str]] = []

    for run_dir in runs_dir(project_root).iterdir():
        if not run_dir.is_dir():
            continue
        rid = run_dir.name
        if not rid.startswith("run-"):
            continue
        state = load_run_state(project_root, rid)
        if not isinstance(state, dict):
            continue
        if str(state.get("workflow", "")) != "workflow.start":
            continue
        if versions_filter and str(state.get("version", "")) != versions_filter:
            continue
        if feature_filter and _slug(str(state.get("feature", ""))) != feature_filter:
            continue
        ts = str(state.get("ended_at") or state.get("started_at") or rid)
        candidates.append((rid, ts))

    if not candidates:
        return None
    # ISO timestamps and run-id lexical order are both monotonic enough for our scope.
    candidates.sort(key=lambda x: x[1])
    return candidates[-1][0]


def _select_default_run_id(events: list[dict[str, Any]]) -> str | None:
    """Prefer recent workflow run-id over generic latest event run-id.

    Rationale:
    - release/team/bridge events can be written after workflow completion
    - those run_ids (e.g. release:v1.2.3) should not become default target for
      workflow closure metrics
    """
    if not events:
        return None

    workflow_event_names = {"stage_started", "stage_context_injected", "stage_finished", "memory_writeback"}
    latest_workflow_ts_by_run: dict[str, str] = {}
    for item in events:
        if not isinstance(item, dict):
            continue
        run_id = str(item.get("run_id", "") or "")
        stage = str(item.get("stage", "") or "")
        event = str(item.get("event", "") or "")
        ts = str(item.get("ts", "") or "")
        if not run_id.startswith("run-"):
            continue
        if stage not in WORKFLOW_STAGES or event not in workflow_event_names:
            continue
        prev = latest_workflow_ts_by_run.get(run_id, "")
        if ts >= prev:
            latest_workflow_ts_by_run[run_id] = ts

    if latest_workflow_ts_by_run:
        return sorted(latest_workflow_ts_by_run.items(), key=lambda x: x[1])[-1][0]

    return _latest_run_id_from_events(events)


def compute_workflow_progress(
    project_root: Path,
    *,
    run_id: str | None = None,
    version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    """Compute workflow stage-level progress from lifecycle events."""
    target_run_id = resolve_workflow_run_id(
        project_root,
        run_id=run_id,
        version=version,
        feature=feature,
    )
    events = load_lifecycle_events(project_root, run_id=target_run_id) if target_run_id else []
    stage_status: dict[str, dict[str, Any]] = {}

    def _seq(item: dict[str, Any]) -> int:
        try:
            return int(item.get("attempt_seq"))
        except Exception:  # noqa: BLE001
            return 0

    for stage in WORKFLOW_STAGES:
        stage_events = [e for e in events if str(e.get("stage", "")) == stage]
        stage_events.sort(key=lambda x: str(x.get("ts", "")))
        has_skipped_any = any(str(e.get("event", "")) == "stage_skipped" for e in stage_events)
        latest_attempt_seq = 0
        for item in stage_events:
            seq = _seq(item)
            if seq > latest_attempt_seq:
                latest_attempt_seq = seq
        if latest_attempt_seq > 0:
            latest_attempt_events = [item for item in stage_events if _seq(item) == latest_attempt_seq]
        else:
            latest_attempt_events = stage_events

        names = {str(e.get("event", "")) for e in latest_attempt_events}
        has_started = "stage_started" in names
        has_context = "stage_context_injected" in names
        has_finished = "stage_finished" in names
        has_writeback = "memory_writeback" in names
        has_failed = "stage_failed" in names
        has_skipped = "stage_skipped" in names or (has_skipped_any and not latest_attempt_events)
        failure_events = [e for e in stage_events if str(e.get("event", "")) == "stage_failed"]
        latest_failure_ts = str(failure_events[-1].get("ts", "")) if failure_events else ""
        completion_events = [
            e for e in latest_attempt_events if str(e.get("event", "")) in {"stage_finished", "memory_writeback"}
        ]
        latest_completion_ts = str(completion_events[-1].get("ts", "")) if completion_events else ""

        completed_by_contract = has_started and has_context and has_finished and has_writeback
        if completed_by_contract:
            status = "completed"
        elif has_failed:
            status = "failed"
        elif has_skipped and not has_started and not has_finished and not has_writeback:
            status = "skipped"
        elif latest_attempt_events:
            status = "in_progress"
        else:
            status = "not_started"

        stage_status[stage] = {
            "status": status,
            "has_started": has_started,
            "has_context": has_context,
            "has_finished": has_finished,
            "has_writeback": has_writeback,
            "has_failed": has_failed,
            "has_skipped": has_skipped,
            "attempt_seq": latest_attempt_seq or None,
            "attempt_id": f"{stage}@attempt-{latest_attempt_seq}" if latest_attempt_seq > 0 else None,
            "retry_count": max(0, (latest_attempt_seq - 1)) if latest_attempt_seq > 0 else len(failure_events),
            "latest_failure_ts": latest_failure_ts or None,
            "latest_completion_ts": latest_completion_ts or None,
            "event_count": len(stage_events),
        }

    ordered = [stage for stage in WORKFLOW_STAGES if stage_status[stage]["status"] != "completed"]
    next_stage = ordered[0] if ordered else None
    missing_stages = [stage for stage in WORKFLOW_STAGES if stage_status[stage]["status"] != "completed"]
    closure_complete = len(missing_stages) == 0 and bool(target_run_id)

    gate_report = project_root / ".beacon" / "gate-report.json"
    gate_status = "unknown"
    gate_pass = False
    if gate_report.exists():
        try:
            gate_payload = json.loads(gate_report.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            gate_payload = {}
        gate_status = str(gate_payload.get("status", "")).strip() or "unknown"
        gate_pass = gate_status.lower() == "pass"

    run_state = load_run_state(project_root, target_run_id) if target_run_id else None
    run_feature = str(run_state.get("feature", "")) if isinstance(run_state, dict) else ""
    run_version = str(run_state.get("version", "")) if isinstance(run_state, dict) else ""

    return {
        "run_id": target_run_id,
        "version": run_version,
        "feature": run_feature,
        "closure_complete": closure_complete,
        "next_stage": next_stage,
        "missing_closure_stages": missing_stages,
        "gate_status": gate_status,
        "gate_pass": gate_pass,
        "stages": stage_status,
    }


def compute_memory_metrics(
    project_root: Path,
    run_id: str | None = None,
    *,
    version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    events = load_lifecycle_events(project_root)
    filtered_run_id = resolve_workflow_run_id(
        project_root,
        run_id=run_id,
        version=version,
        feature=feature,
    )
    target_run_id = filtered_run_id or _select_default_run_id(events)
    run_events = [e for e in events if not target_run_id or e.get("run_id") == target_run_id]

    writebacks = [e for e in run_events if e.get("event") == "memory_writeback"]
    recalls = [e for e in run_events if e.get("event") == "stage_context_injected"]
    feedback_items = [e for e in run_events if e.get("event") == "feedback_memory_assimilated"]
    starts = {(e.get("stage"), e.get("event")) for e in run_events if e.get("event") == "stage_started"}
    finishes = {(e.get("stage"), e.get("event")) for e in run_events if e.get("event") == "stage_finished"}
    writeback_stages = {e.get("stage") for e in writebacks}
    recall_stages = {e.get("stage") for e in recalls}

    missing_stages: list[str] = []
    for stage in WORKFLOW_STAGES:
        has_start = (stage, "stage_started") in starts
        has_finish = (stage, "stage_finished") in finishes
        has_recall = stage in recall_stages
        has_writeback = stage in writeback_stages
        if not (has_start and has_finish and has_recall and has_writeback):
            missing_stages.append(stage)

    progress = compute_workflow_progress(project_root, run_id=target_run_id)
    return {
        "run_id": target_run_id,
        "lifecycle_events_total": len(events),
        "run_lifecycle_events": len(run_events),
        "recall_injections": len(recalls),
        "writebacks": len(writebacks),
        "feedback_assimilations": len(feedback_items),
        "closure_complete": len(missing_stages) == 0 and bool(target_run_id),
        "missing_closure_stages": missing_stages,
        "next_stage": progress.get("next_stage"),
    }
