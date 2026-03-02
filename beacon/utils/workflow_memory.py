"""Workflow lifecycle memory helpers.

This module builds a PTK-style memory loop for the default workflow path:
think -> user-story -> prd -> test-case.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from beacon.utils.memory import append_memory_entry, load_memory_entries
from beacon.utils.runtime import now_iso

LIFECYCLE_FILE = "workflow-lifecycle.json"
LIFECYCLE_INDEX_FILE = "workflow-lifecycle.index.json"
LIFECYCLE_SCHEMA_FILE = "workflow-lifecycle.schema.json"
WORKFLOW_STAGES = ("think", "user-story", "prd", "test-case")

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
    key = _dedupe_key(run_id=run_id, stage=stage, event=event, evidence_ref=refs, source=source)
    if key in dedupe_keys:
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


def compute_memory_metrics(project_root: Path, run_id: str | None = None) -> dict[str, Any]:
    events = load_lifecycle_events(project_root)
    target_run_id = run_id or _latest_run_id_from_events(events)
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

    return {
        "run_id": target_run_id,
        "lifecycle_events_total": len(events),
        "run_lifecycle_events": len(run_events),
        "recall_injections": len(recalls),
        "writebacks": len(writebacks),
        "feedback_assimilations": len(feedback_items),
        "closure_complete": len(missing_stages) == 0 and bool(target_run_id),
        "missing_closure_stages": missing_stages,
    }

