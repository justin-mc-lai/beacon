"""Workflow lifecycle memory helpers.

This module projects legacy workflow lifecycle events onto Beacon's canonical
human-facing lifecycle:
prd -> user-story -> test-case -> [prototype] -> implement -> qa -> release.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any

from beacon.utils.memory import append_memory_entry, load_memory_entries, memory_dir, memory_v1_path
from beacon.utils.runtime import load_run_state, now_iso, runs_dir, save_run_state
from beacon.utils.story_state import feature_slug

LIFECYCLE_FILE = "workflow-lifecycle.json"
LIFECYCLE_INDEX_FILE = "workflow-lifecycle.index.json"
LIFECYCLE_SCHEMA_FILE = "workflow-lifecycle.schema.json"
WORKFLOW_TRANSACTION_FILE = "transactions.json"
WORKFLOW_STAGES = ("prd", "user-story", "test-case", "implement", "qa", "release")
OPTIONAL_WORKFLOW_STAGES = ("prototype",)
_LEGACY_STAGE_ALIASES = {
    "think": "prd",
    "implementation": "implement",
    "verify": "qa",
    "review": "qa",
    "gate": "release",
    "delivery": "release",
}


def normalize_workflow_stage(stage: str | None) -> str:
    normalized = str(stage or "").strip().lower()
    return _LEGACY_STAGE_ALIASES.get(normalized, normalized)


def lifecycle_stage_aliases(stage: str | None) -> tuple[str, ...]:
    canonical = normalize_workflow_stage(stage)
    if canonical == "prd":
        return ("prd", "think")
    if canonical == "implement":
        return ("implement", "implementation")
    if canonical == "qa":
        return ("qa", "verify", "review")
    if canonical == "release":
        return ("release", "gate", "delivery")
    if canonical:
        return (canonical,)
    return ()

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


def workflow_stages_for_run(
    project_root: Path,
    *,
    run_id: str | None = None,
    run_state: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
) -> tuple[str, ...]:
    state = run_state if isinstance(run_state, dict) else (load_run_state(project_root, run_id) if run_id else None)
    seen_events = events if isinstance(events, list) else (load_lifecycle_events(project_root, run_id=run_id) if run_id else [])
    prototype_enabled = bool((state or {}).get("prototype_enabled"))
    prototype_seen = any(
        isinstance(item, dict) and normalize_workflow_stage(str(item.get("stage", ""))) == "prototype"
        for item in seen_events
    )
    if prototype_enabled or prototype_seen:
        return ("prd", "user-story", "test-case", "prototype", "implement", "qa", "release")
    return WORKFLOW_STAGES


def lifecycle_path(project_root: Path) -> Path:
    return _memory_root(project_root) / LIFECYCLE_FILE


def lifecycle_index_path(project_root: Path) -> Path:
    return _memory_root(project_root) / LIFECYCLE_INDEX_FILE


def lifecycle_schema_path(project_root: Path) -> Path:
    return _memory_root(project_root) / LIFECYCLE_SCHEMA_FILE


def stage_context_path(project_root: Path, run_id: str, stage: str) -> Path:
    canonical_stage = normalize_workflow_stage(stage)
    return project_root / ".beacon" / "state" / "workflow-memory" / run_id / f"{canonical_stage}-context.json"


def workflow_transaction_path(project_root: Path, run_id: str) -> Path:
    return project_root / ".beacon" / "state" / "workflow-memory" / run_id / WORKFLOW_TRANSACTION_FILE


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


def _stable_hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_hash_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").strip().lower()).strip("-")


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


def _load_transaction_journal(project_root: Path, run_id: str) -> dict[str, Any]:
    path = workflow_transaction_path(project_root, run_id)
    payload = _read_json(path, {"schema_version": "1.0", "items": [], "updated_at": now_iso()})
    if not isinstance(payload.get("items"), list):
        payload["items"] = []
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("updated_at", now_iso())
    return payload


def _save_transaction_journal(project_root: Path, run_id: str, payload: dict[str, Any]) -> None:
    path = workflow_transaction_path(project_root, run_id)
    payload["schema_version"] = "1.0"
    payload["updated_at"] = now_iso()
    _write_json(path, payload)


def list_workflow_transactions(
    project_root: Path,
    *,
    run_id: str,
    stage: str | None = None,
    action: str | None = None,
) -> list[dict[str, Any]]:
    payload = _load_transaction_journal(project_root, run_id)
    items = payload.get("items")
    if not isinstance(items, list):
        return []
    canonical_stage = normalize_workflow_stage(stage) if stage else ""
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if canonical_stage and normalize_workflow_stage(str(item.get("stage", ""))) != canonical_stage:
            continue
        if action and str(item.get("action", "")).strip() != str(action).strip():
            continue
        out.append(dict(item))
    out.sort(key=lambda row: str(row.get("committed_at") or row.get("occurred_at") or ""))
    return out


def _requirement_refs(project_root: Path, *, version: str, feature: str) -> list[str]:
    slug = _slug(feature)
    docs_root = project_root / "docs" / "beacon" / version
    candidates = [
        docs_root / "prd" / f"{slug}.md",
        docs_root / "user-story" / f"{slug}.md",
        docs_root / "qa" / "test-cases" / f"{slug}.md",
        docs_root / "prototype" / slug / "freeze.json",
        docs_root / "prototype" / slug / "prototype-review.json",
        docs_root / "release" / f"{version}.md",
    ]
    refs: list[str] = []
    for path in candidates:
        if path.exists():
            refs.append(str(path.relative_to(project_root)))
    return refs


def _decision_trace(project_root: Path, *, run_id: str, stage: str, feature: str, limit: int = 6) -> list[dict[str, Any]]:
    canonical_stage = normalize_workflow_stage(stage)
    feature_l = str(feature or "").strip().lower()
    items = load_memory_entries(project_root, mem_type="decision")
    trace: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        tags = [str(x).strip().lower() for x in item.get("tags", []) if str(x).strip()]
        content = str(item.get("content", "")).strip()
        source_session_id = str(item.get("source_session_id", "") or "")
        if source_session_id != run_id and feature_l and feature_l not in content.lower():
            continue
        if canonical_stage and canonical_stage not in tags and source_session_id != run_id:
            continue
        trace.append(
            {
                "memory_id": str(item.get("memory_id", "") or ""),
                "summary": content[:160],
                "source": str(item.get("source", "") or ""),
                "updated_at": str(item.get("updated_at", "") or ""),
            }
        )
        if len(trace) >= limit:
            break
    return trace


def _blockers(project_root: Path, *, run_id: str, stage: str, version: str) -> list[str]:
    blockers: list[str] = []
    state = load_run_state(project_root, run_id) or {}
    reason = str(state.get("reason", "") or "").strip()
    if reason:
        blockers.append(reason)
    think_state = _read_json(project_root / ".beacon" / "state" / "think-progress" / f"{version}.json", {})
    open_questions = think_state.get("open_questions") if isinstance(think_state.get("open_questions"), list) else []
    conflicts = think_state.get("conflicts") if isinstance(think_state.get("conflicts"), list) else []
    blockers.extend(str(item).strip() for item in open_questions if str(item).strip())
    blockers.extend(str(item).strip() for item in conflicts if str(item).strip())
    progress = compute_workflow_progress(project_root, run_id=run_id)
    stage_payload = progress.get("stages", {}).get(normalize_workflow_stage(stage), {}) if isinstance(progress.get("stages"), dict) else {}
    latest_failure = str(stage_payload.get("latest_failure_ts", "") or "").strip()
    if latest_failure:
        blockers.append(f"{normalize_workflow_stage(stage)}_failed@{latest_failure}")
    return blockers[:8]


def _prepare_workflow_transaction(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    action: str,
    feature: str,
    version: str,
    evidence_ref: list[str],
) -> dict[str, Any]:
    canonical_stage = normalize_workflow_stage(stage)
    journal_items = list_workflow_transactions(project_root, run_id=run_id)
    stage_items = [item for item in journal_items if normalize_workflow_stage(str(item.get("stage", ""))) == canonical_stage]
    previous_transaction_id = str(journal_items[-1].get("transaction_id", "") or "") if journal_items else ""
    lineage_ids = [str(item.get("transaction_id", "") or "") for item in journal_items[-6:] if str(item.get("transaction_id", "") or "").strip()]
    attempt_seq = 1
    for item in stage_items:
        try:
            value = int(item.get("attempt_seq", 0) or 0)
        except Exception:  # noqa: BLE001
            value = 0
        if value > attempt_seq:
            attempt_seq = value
    if action == "stage_context":
        attempt_seq = max(1, attempt_seq if stage_items else 1)
    payload = {
        "run_id": run_id,
        "stage": canonical_stage,
        "action": action,
        "feature": feature,
        "version": version,
        "evidence_ref": sorted(set(str(x) for x in evidence_ref if str(x).strip())),
        "requirement_refs": _requirement_refs(project_root, version=version, feature=feature),
        "decision_trace": _decision_trace(project_root, run_id=run_id, stage=canonical_stage, feature=feature),
        "blockers": _blockers(project_root, run_id=run_id, stage=canonical_stage, version=version),
        "attempt_seq": attempt_seq,
        "previous_transaction_id": previous_transaction_id,
        "lineage_ids": lineage_ids,
    }
    source_hash = _stable_hash_payload(payload)
    projection_seq = f"wf-{source_hash[:16]}"
    transaction_id = f"tx-wf-{run_id}-{canonical_stage}-{action}-{source_hash[:12]}"
    return {
        **payload,
        "transaction_id": transaction_id,
        "source_hash": source_hash,
        "projection_seq": projection_seq,
        "occurred_at": now_iso(),
    }


def _record_workflow_transaction(
    project_root: Path,
    *,
    run_id: str,
    record: dict[str, Any],
) -> dict[str, Any]:
    payload = _load_transaction_journal(project_root, run_id)
    items = payload.get("items")
    if not isinstance(items, list):
        items = []
        payload["items"] = items
    items.append(record)
    payload["items"] = items[-200:]
    _save_transaction_journal(project_root, run_id, payload)
    return record


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
    raw_stage = str(stage or "").strip()
    canonical_stage = normalize_workflow_stage(raw_stage)

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
        if (
            isinstance(item, dict)
            and item.get("run_id") == run_id
            and normalize_workflow_stage(str(item.get("stage", ""))) == canonical_stage
        )
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
    if canonical_stage in WORKFLOW_STAGES or canonical_stage in OPTIONAL_WORKFLOW_STAGES:
        if explicit_attempt_seq is not None and explicit_attempt_seq > 0:
            attempt_seq = explicit_attempt_seq
        elif event == "stage_started":
            attempt_seq = latest_attempt_seq + 1 if latest_attempt_seq > 0 else 1
        else:
            attempt_seq = latest_attempt_seq if latest_attempt_seq > 0 else 1
    attempt_id = f"{raw_stage}@attempt-{attempt_seq}" if attempt_seq > 0 and (canonical_stage in WORKFLOW_STAGES or canonical_stage in OPTIONAL_WORKFLOW_STAGES) else None

    supersedes_event_id = None
    if (canonical_stage in WORKFLOW_STAGES or canonical_stage in OPTIONAL_WORKFLOW_STAGES) and event == "stage_started":
        if stage_events:
            supersedes_event_id = str(stage_events[-1].get("event_id", "") or "") or None
    if details and isinstance(details, dict) and details.get("supersedes_event_id"):
        supersedes_event_id = str(details.get("supersedes_event_id"))
    key = _dedupe_key(run_id=run_id, stage=canonical_stage or raw_stage, event=event, evidence_ref=refs, source=source)
    if event not in _ALLOW_REPEAT_EVENTS and key in dedupe_keys:
        # Return existing latest event with same dedupe key.
        for item in reversed(items):
            if (
                item.get("run_id") == run_id
                and normalize_workflow_stage(str(item.get("stage", ""))) == canonical_stage
                and item.get("event") == event
                and item.get("source") == source
            ):
                return item

    payload = {
        "event_id": str(uuid.uuid4()),
        "run_id": run_id,
        "stage": raw_stage,
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
    target_stage = normalize_workflow_stage(stage) if stage else ""
    for item in items:
        if not isinstance(item, dict):
            continue
        if run_id and item.get("run_id") != run_id:
            continue
        if target_stage and normalize_workflow_stage(str(item.get("stage", ""))) != target_stage:
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
    version: str | None = None,
    transaction: dict[str, Any] | None = None,
    limit: int = 8,
) -> dict[str, Any]:
    memories = load_memory_entries(project_root)
    lifecycle = load_lifecycle_events(project_root, run_id=run_id, limit=20)
    feature_l = (feature or "").lower()
    state = load_run_state(project_root, run_id) or {}
    resolved_version = str(version or state.get("version", "") or "").strip()
    tx = transaction if isinstance(transaction, dict) else {}
    evidence_refs = sorted(
        {
            str(ref).strip()
            for item in lifecycle[-limit:]
            if isinstance(item, dict)
            for ref in (item.get("evidence_ref") or [])
            if str(ref).strip()
        }
    )

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
        "version": resolved_version,
        "generated_at": now_iso(),
        "memory_recall": selected_memories[:limit],
        "lifecycle_events": lifecycle[-limit:],
        "requirement_refs": _requirement_refs(project_root, version=resolved_version, feature=feature) if resolved_version else [],
        "evidence_refs": evidence_refs,
        "decision_trace": _decision_trace(project_root, run_id=run_id, stage=stage, feature=feature),
        "blockers": _blockers(project_root, run_id=run_id, stage=stage, version=resolved_version) if resolved_version else [],
        "transaction_lineage": {
            "current_transaction_id": str(tx.get("transaction_id", "") or ""),
            "projection_seq": str(tx.get("projection_seq", "") or ""),
            "source_hash": str(tx.get("source_hash", "") or ""),
            "previous_transaction_id": str(tx.get("previous_transaction_id", "") or ""),
            "recent_transaction_ids": list(tx.get("lineage_ids", []) or []),
            "attempt_seq": tx.get("attempt_seq"),
            "action": str(tx.get("action", "") or ""),
        },
    }


def write_stage_context(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    feature: str,
) -> Path:
    canonical_stage = normalize_workflow_stage(stage)
    state = load_run_state(project_root, run_id) or {}
    version = str(state.get("version", "") or "")
    transaction = _prepare_workflow_transaction(
        project_root,
        run_id=run_id,
        stage=canonical_stage,
        action="stage_context",
        feature=feature,
        version=version,
        evidence_ref=[],
    )
    payload = build_stage_context(
        project_root,
        run_id=run_id,
        stage=canonical_stage,
        feature=feature,
        version=version,
        transaction=transaction,
    )
    path = stage_context_path(project_root, run_id, canonical_stage)
    _write_json(path, payload)
    lifecycle_event = append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=canonical_stage,
        event="stage_context_injected",
        source="workflow.memory.recall",
        evidence_ref=[str(path.relative_to(project_root))],
        details={
            "recall_count": len(payload.get("memory_recall", [])),
            "transaction_id": transaction["transaction_id"],
            "source_hash": transaction["source_hash"],
            "projection_seq": transaction["projection_seq"],
        },
    )
    record = {
        **transaction,
        "status": "applied",
        "committed_at": now_iso(),
        "sink_paths": {
            "context_pack": str(path.relative_to(project_root)),
            "workflow_lifecycle": str(lifecycle_path(project_root).relative_to(project_root)),
        },
        "sink_checksums": {
            "context_pack": _stable_hash_file(path),
            "workflow_lifecycle": _stable_hash_file(lifecycle_path(project_root)),
        },
        "event_id": str(lifecycle_event.get("event_id", "") or ""),
    }
    _record_workflow_transaction(project_root, run_id=run_id, record=record)
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
    canonical_stage = normalize_workflow_stage(stage)
    state = load_run_state(project_root, run_id) or {}
    version = str(state.get("version", "") or "")
    tx = _prepare_workflow_transaction(
        project_root,
        run_id=run_id,
        stage=canonical_stage,
        action="memory_writeback",
        feature=feature,
        version=version,
        evidence_ref=evidence_ref,
    )
    mem_type = "decision"
    summary = f"[{canonical_stage}] {feature} => {status}"
    entry = append_memory_entry(
        project_root=project_root,
        mem_type=mem_type,
        text=summary,
        source_session_id=run_id,
        source=f"workflow.{canonical_stage}.writeback",
        evidence_ref=evidence_ref,
        confidence=0.8,
        tags=["workflow-lifecycle", canonical_stage, status.lower()],
        metadata={
            "run_id": run_id,
            "stage": canonical_stage,
            "feature": feature,
            "version": version,
            "transaction_id": tx["transaction_id"],
            "source_hash": tx["source_hash"],
            "projection_seq": tx["projection_seq"],
            "attempt_seq": tx["attempt_seq"],
        },
    )
    lifecycle_event = append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=canonical_stage,
        event="memory_writeback",
        source="workflow.memory.writeback",
        evidence_ref=evidence_ref,
        details={
            "memory_id": entry.get("memory_id"),
            "memory_type": mem_type,
            "transaction_id": tx["transaction_id"],
            "source_hash": tx["source_hash"],
            "projection_seq": tx["projection_seq"],
        },
    )
    legacy_projection_path = memory_dir(project_root) / "decisions.json"
    record = {
        **tx,
        "status": "applied",
        "committed_at": now_iso(),
        "memory_id": str(entry.get("memory_id", "") or ""),
        "event_id": str(lifecycle_event.get("event_id", "") or ""),
        "sink_paths": {
            "memory_v1": str(memory_v1_path(project_root).relative_to(project_root)),
            "legacy_projection": str(legacy_projection_path.relative_to(project_root)),
            "workflow_lifecycle": str(lifecycle_path(project_root).relative_to(project_root)),
        },
        "sink_checksums": {
            "memory_v1": _stable_hash_file(memory_v1_path(project_root)),
            "legacy_projection": _stable_hash_file(legacy_projection_path),
            "workflow_lifecycle": _stable_hash_file(lifecycle_path(project_root)),
        },
    }
    _record_workflow_transaction(project_root, run_id=run_id, record=record)
    return entry


def _existing_rel_refs(project_root: Path, candidates: list[Path]) -> list[str]:
    refs: list[str] = []
    for path in candidates:
        if path.exists():
            try:
                refs.append(str(path.relative_to(project_root)))
            except ValueError:
                refs.append(str(path))
    return sorted(set(refs))


def _workflow_memory_evidence_refs(project_root: Path, *, version: str, feature: str, run_id: str) -> dict[str, list[str]]:
    slug = feature_slug(feature)
    docs_root = project_root / "docs" / "beacon" / version
    feature_root = project_root / ".beacon" / "qa" / "features" / slug
    run_state_path = runs_dir(project_root) / run_id / "state.json"
    stage_refs = {
        "prd": _existing_rel_refs(project_root, [
            docs_root / "prd" / f"{slug}.md",
            docs_root / "user-story" / f"{slug}.md",
        ]),
        "user-story": _existing_rel_refs(project_root, [
            docs_root / "user-story" / f"{slug}.md",
            docs_root / "prd" / f"{slug}.md",
        ]),
        "test-case": _existing_rel_refs(project_root, [
            docs_root / "qa" / "test-cases" / f"{slug}.md",
            docs_root / ".machine" / "qa" / f"{slug}.qa9-matrix.json",
            docs_root / ".machine" / "qa" / f"{slug}.ac-test-matrix.json",
        ]),
        "implement": _existing_rel_refs(project_root, [
            project_root / ".beacon" / "state" / f"implementation-{slug}.json",
            docs_root / ".machine" / "execution" / f"implementation-plan-{slug}.json",
            docs_root / "user-story" / f"{slug}.md",
        ]),
        "qa": _existing_rel_refs(project_root, [
            project_root / ".beacon" / "auto-test-status.json",
            project_root / ".beacon" / "qa" / "status.json",
            project_root / ".beacon" / "coverage-summary.json",
            feature_root / "scorecard.json",
            feature_root / "ac-closure.json",
        ]),
        "release": _existing_rel_refs(project_root, [
            run_state_path,
            project_root / ".beacon" / "gate-report.json",
            project_root / ".beacon" / "coverage-summary.json",
            project_root / ".beacon" / "evidence-manifest.json",
            docs_root / "change" / f"{version}.md",
            docs_root / ".machine" / "change" / f"{version}.json",
            docs_root / "execution" / "boundaries.md",
        ]),
    }
    return stage_refs


def backfill_workflow_memory(
    project_root: Path,
    *,
    version: str,
    feature: str,
    run_id: str,
) -> dict[str, Any]:
    """Backfill workflow-memory surfaces for an already-completed feature run."""
    state = load_run_state(project_root, run_id) or {}
    started_at = str(
        state.get("started_at")
        or _read_json(project_root / ".beacon" / "auto-test-status.json", {}).get("timestamp")
        or _read_json(project_root / ".beacon" / "qa" / "status.json", {}).get("timestamp")
        or now_iso()
    )
    ended_at = str(
        state.get("ended_at")
        or _read_json(project_root / ".beacon" / "coverage-summary.json", {}).get("updated_at")
        or now_iso()
    )
    run_state_payload = {
        **state,
        "run_id": run_id,
        "workflow": str(state.get("workflow") or "workflow.start"),
        "mode": str(state.get("mode") or "recovered_release_backfill"),
        "feature": feature,
        "version": version,
        "status": str(state.get("status") or "completed"),
        "started_at": started_at,
        "ended_at": ended_at,
    }
    save_run_state(project_root, run_id, run_state_payload)

    stage_refs = _workflow_memory_evidence_refs(project_root, version=version, feature=feature, run_id=run_id)
    created: list[dict[str, str]] = []
    workflow_stages = ("prd", "user-story", "test-case", "implement", "qa", "release")
    for stage in workflow_stages:
        refs = stage_refs.get(stage, [])
        if not refs:
            continue
        stage_events = load_lifecycle_events(project_root, run_id=run_id, stage=stage)
        event_names = {str(item.get("event", "") or "") for item in stage_events if isinstance(item, dict)}
        details = {"feature": feature, "version": version, "sync_source": "doctor.workflow-memory.sync"}
        if "stage_started" not in event_names:
            append_lifecycle_event(
                project_root,
                run_id=run_id,
                stage=stage,
                event="stage_started",
                source="doctor.workflow-memory.sync",
                evidence_ref=refs,
                details=details,
            )
            created.append({"stage": stage, "event": "stage_started"})
        if "stage_context_injected" not in event_names:
            write_stage_context(
                project_root,
                run_id=run_id,
                stage=stage,
                feature=feature,
            )
            created.append({"stage": stage, "event": "stage_context_injected"})
        if "stage_finished" not in event_names:
            append_lifecycle_event(
                project_root,
                run_id=run_id,
                stage=stage,
                event="stage_finished",
                source="doctor.workflow-memory.sync",
                evidence_ref=refs,
                details={**details, "status": "completed"},
            )
            created.append({"stage": stage, "event": "stage_finished"})
        if "memory_writeback" not in event_names:
            record_stage_writeback(
                project_root,
                run_id=run_id,
                stage=stage,
                feature=feature,
                evidence_ref=refs,
                status="completed",
            )
            created.append({"stage": stage, "event": "memory_writeback"})

    release_event_exists = bool(load_lifecycle_events(project_root, run_id=run_id, stage="release", event="release_decision_recorded"))
    release_refs = stage_refs.get("release", [])
    if release_refs and not release_event_exists:
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage="release",
            event="release_decision_recorded",
            source="doctor.workflow-memory.sync",
            evidence_ref=release_refs,
            details={"action": "backfill", "version": version, "feature": feature},
        )
        created.append({"stage": "release", "event": "release_decision_recorded"})

    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "version": version,
        "feature": feature,
        "state_path": str((runs_dir(project_root) / run_id / "state.json").relative_to(project_root)),
        "created": created,
        "stage_evidence_refs": stage_refs,
    }


def _latest_run_id_from_events(events: list[dict[str, Any]]) -> str | None:
    if not events:
        return None
    ordered = sorted(events, key=lambda x: str(x.get("ts", "")))
    return str(ordered[-1].get("run_id", "") or "") or None


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _match_slug(text: str) -> str:
    raw = str(text or "").strip().lower()
    if not raw:
        return ""
    return "-".join(token for token in re.findall(r"[a-z0-9]+", raw) if token)


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
    3. latest lifecycle-backed workflow run matching version/feature
    """
    if run_id:
        if load_run_state(project_root, run_id):
            return run_id
        if load_lifecycle_events(project_root, run_id=run_id):
            return run_id
        return None

    versions_filter = (version or "").strip()
    feature_filter = _slug(feature or "")
    loose_feature_filter = _match_slug(feature or "")
    candidates: list[tuple[str, str]] = []
    exact_feature_candidates: list[tuple[str, str]] = []
    loose_feature_candidates: list[tuple[str, str]] = []

    for run_dir in runs_dir(project_root).iterdir():
        if not run_dir.is_dir():
            continue
        rid = run_dir.name
        if not rid.startswith(("run-", "repair-")):
            continue
        state = load_run_state(project_root, rid)
        if not isinstance(state, dict):
            continue
        workflow_name = str(state.get("workflow", ""))
        if workflow_name not in {"workflow.start", "workflow"}:
            continue
        if versions_filter and str(state.get("version", "")) != versions_filter:
            continue
        state_feature = str(state.get("feature", ""))
        candidate_slug = _slug(state_feature)
        candidate_match_slug = _match_slug(state_feature)
        ts = str(state.get("ended_at") or state.get("started_at") or rid)
        candidates.append((rid, ts))
        if feature_filter and candidate_slug == feature_filter:
            exact_feature_candidates.append((rid, ts))
        if feature_filter and loose_feature_filter and candidate_match_slug:
            if (
                candidate_match_slug == loose_feature_filter
                or loose_feature_filter in candidate_match_slug
                or candidate_match_slug in loose_feature_filter
            ):
                loose_feature_candidates.append((rid, ts))

    filtered = candidates
    if feature_filter:
        if exact_feature_candidates:
            filtered = exact_feature_candidates
        elif loose_feature_candidates:
            filtered = loose_feature_candidates
        elif versions_filter and len(candidates) == 1:
            filtered = candidates
        else:
            filtered = []

    if not filtered and feature_filter:
        event_exact_candidates: dict[str, str] = {}
        event_loose_candidates: dict[str, str] = {}
        for item in load_lifecycle_events(project_root):
            if not isinstance(item, dict):
                continue
            rid = str(item.get("run_id", "") or "")
            if not rid.startswith(("run-", "repair-")):
                continue
            state = load_run_state(project_root, rid)
            if not isinstance(state, dict):
                continue
            workflow_name = str(state.get("workflow", ""))
            if workflow_name not in {"workflow.start", "workflow"}:
                continue
            details = item.get("details") if isinstance(item.get("details"), dict) else {}
            event_version = str(details.get("version") or state.get("version", "") or "")
            if versions_filter and event_version != versions_filter:
                continue
            detail_feature = str(details.get("feature") or item.get("feature", "") or "")
            if not detail_feature.strip():
                continue
            candidate_slug = _slug(detail_feature)
            candidate_match_slug = _match_slug(detail_feature)
            ts = str(item.get("ts", "") or state.get("ended_at") or state.get("started_at") or rid)
            if candidate_slug == feature_filter:
                previous = event_exact_candidates.get(rid, "")
                if ts >= previous:
                    event_exact_candidates[rid] = ts
            elif loose_feature_filter and candidate_match_slug and (
                candidate_match_slug == loose_feature_filter
                or loose_feature_filter in candidate_match_slug
                or candidate_match_slug in loose_feature_filter
            ):
                previous = event_loose_candidates.get(rid, "")
                if ts >= previous:
                    event_loose_candidates[rid] = ts

        if event_exact_candidates:
            filtered = list(event_exact_candidates.items())
        elif event_loose_candidates:
            filtered = list(event_loose_candidates.items())

    if not filtered:
        return None
    # ISO timestamps and run-id lexical order are both monotonic enough for our scope.
    filtered.sort(key=lambda x: x[1])
    return filtered[-1][0]


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
        stage = normalize_workflow_stage(str(item.get("stage", "") or ""))
        event = str(item.get("event", "") or "")
        ts = str(item.get("ts", "") or "")
        if not run_id.startswith(("run-", "repair-")):
            continue
        if stage not in WORKFLOW_STAGES + OPTIONAL_WORKFLOW_STAGES or event not in workflow_event_names:
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
    run_state = load_run_state(project_root, target_run_id) if target_run_id else None
    workflow_stages = workflow_stages_for_run(project_root, run_id=target_run_id, run_state=run_state, events=events)

    def _seq(item: dict[str, Any]) -> int:
        try:
            return int(item.get("attempt_seq"))
        except Exception:  # noqa: BLE001
            return 0

    for stage in workflow_stages:
        stage_events = [e for e in events if normalize_workflow_stage(str(e.get("stage", ""))) == stage]
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
            "canonical_stage": stage,
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
            "source_stages": sorted(
                {
                    str(item.get("stage", "")).strip()
                    for item in stage_events
                    if str(item.get("stage", "")).strip()
                }
            ),
        }

    ordered = [stage for stage in workflow_stages if stage_status[stage]["status"] != "completed"]
    next_stage = ordered[0] if ordered else None
    missing_stages = [stage for stage in workflow_stages if stage_status[stage]["status"] != "completed"]
    closure_complete = len(missing_stages) == 0 and bool(target_run_id)

    run_feature = str(run_state.get("feature", "")) if isinstance(run_state, dict) else ""
    run_version = str(run_state.get("version", "")) if isinstance(run_state, dict) else ""
    release_stage_status = str(stage_status.get("release", {}).get("status", "not_started"))
    gate_status = "unknown"
    gate_pass = False
    if release_stage_status == "completed":
        gate_status = "Pass"
        gate_pass = True
    elif release_stage_status == "failed":
        gate_status = "Blocked"
    elif release_stage_status == "skipped":
        gate_status = "Skipped"
    elif release_stage_status in {"in_progress", "not_started"}:
        gate_status = "unknown"

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
        "workflow_stages": list(workflow_stages),
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
    starts = {
        (normalize_workflow_stage(str(e.get("stage", ""))), e.get("event"))
        for e in run_events
        if e.get("event") == "stage_started"
    }
    finishes = {
        (normalize_workflow_stage(str(e.get("stage", ""))), e.get("event"))
        for e in run_events
        if e.get("event") == "stage_finished"
    }
    writeback_stages = {normalize_workflow_stage(str(e.get("stage", ""))) for e in writebacks}
    recall_stages = {normalize_workflow_stage(str(e.get("stage", ""))) for e in recalls}
    progress = compute_workflow_progress(project_root, run_id=target_run_id)

    missing_stages: list[str] = []
    workflow_stages = tuple(progress.get("workflow_stages", []) or WORKFLOW_STAGES)
    for stage in workflow_stages:
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
        "next_stage": progress.get("next_stage"),
    }


def workflow_memory_transaction_contract(
    project_root: Path,
    *,
    run_id: str | None = None,
    version: str | None = None,
    feature: str | None = None,
) -> dict[str, Any]:
    target_run_id = resolve_workflow_run_id(project_root, run_id=run_id, version=version, feature=feature)
    if not target_run_id:
        # No run resolved (fresh project / not started). Informational warn,
        # not blocked — distinguishes "no run" from "run without completion truth".
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "workflow_memory_no_run_resolved",
            "message": "no workflow run resolved; completion truth not applicable",
            "run_id": "",
            "details": {},
        }
    items = list_workflow_transactions(project_root, run_id=target_run_id)
    if not items:
        # Run exists but has no completion transaction record — completion truth
        # is missing, so fail closed (gate.py blocks on status=="fail").
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "workflow_memory_transaction_missing",
            "message": "workflow memory transaction record missing for resolved run; completion truth absent",
            "run_id": target_run_id,
            "details": {},
        }
    latest = items[-1]
    status = str(latest.get("status", "") or "").strip().lower()
    sink_checksums = latest.get("sink_checksums") if isinstance(latest.get("sink_checksums"), dict) else {}
    metadata_ok = bool(latest.get("transaction_id")) and bool(latest.get("source_hash")) and bool(latest.get("projection_seq"))
    checksum_ok = bool(sink_checksums) and all(str(value or "").strip() not in {"", "missing"} for value in sink_checksums.values())
    if status == "failed_transaction":
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "workflow_memory_failed_transaction",
            "message": "workflow memory transaction failed; stage closure is not fully committed",
            "run_id": target_run_id,
            "details": latest,
        }
    if not metadata_ok or not checksum_ok:
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "workflow_memory_transaction_drift",
            "message": "workflow memory transaction metadata/checksum drift detected",
            "run_id": target_run_id,
            "details": latest,
        }
    return {
        "status": "pass",
        "blocked": False,
        "reason_code": "workflow_memory_transaction_ok",
        "message": "workflow memory transaction metadata is consistent",
        "run_id": target_run_id,
        "details": latest,
    }
