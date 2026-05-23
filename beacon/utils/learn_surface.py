"""Governed learning support-surface helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.memory import load_memory_entries, normalize_memory_type, search_memory_entries
from beacon.utils.support_surface_transactions import build_support_surface_transaction, write_support_surface_transaction
from beacon.utils.support_research_topology import upsert_learning_influence_summary
from beacon.utils.versioning import resolve_target_version


def run_governed_recall(
    project_root: Path,
    *,
    version: str,
    feature: str,
    mode: str,
    query: str = "",
    memory_type: str = "",
    limit: int = 10,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    normalized_type = normalize_memory_type(memory_type) if memory_type else None
    if query:
        entries = search_memory_entries(
            project_root,
            query,
            mem_type=normalized_type,
            limit=limit,
            mode="hybrid",
            layer="detail",
            ids=[],
        )
    else:
        entries = load_memory_entries(project_root, mem_type=normalized_type)[: max(limit, 0)]
    conflicts = [item for item in entries if "conflict" in str(item.get("content", "")).lower()]
    conflict_ids = {str(item.get("memory_id", "") or "").strip() for item in conflicts if str(item.get("memory_id", "")).strip()}
    stale = [
        item
        for item in entries
        if "stale" in str(item.get("content", "")).lower()
        and str(item.get("memory_id", "") or "").strip() not in conflict_ids
    ]
    applied = entries[: min(3, len(entries))]
    suppressed = entries[min(3, len(entries)) : min(5, len(entries))]
    reason_codes: list[str] = []
    if conflicts:
        reason_codes.append("learning_conflict_requires_operator_resolution")
    if not entries:
        reason_codes.append("learning_index_missing")
    blocked = False
    next_route = {
        "command": "beacon help",
        "why": "Learning influence should be rendered through operator guidance surfaces.",
        "target_surface": "beacon-help",
        "priority": "medium",
        "prerequisites": ["learning audit available"],
    }
    payload = build_support_surface_transaction(
        surface="beacon-learn",
        mode=mode or "recall",
        version=resolved_version,
        feature=feature,
        status="blocked" if blocked else "advisory",
        decision=mode or "recall",
        reason_codes=reason_codes,
        truth_refs=[],
        evidence_refs=[str(item.get("evidence_ref", "")) for item in applied if str(item.get("evidence_ref", "")).strip()],
        route_decision={"route": "operator-guidance", "target_surface": "beacon-help"},
        next_route=next_route,
        writeback_targets=["learning audit log", "route explanation output"],
        blocked=blocked,
        blocked_reason="",
        operator_visible_summary=(
            f"Applied {len(applied)} learning entries; stale={len(stale)} conflicting={len(conflicts)} suppressed={len(suppressed)}."
        ),
    )
    payload["learning_candidates"] = entries
    payload["applied_learning"] = applied
    payload["suppressed_learning"] = suppressed
    payload["stale_learning"] = stale
    payload["conflicting_learning"] = conflicts
    payload["route_influence_summary"] = payload["operator_visible_summary"]
    payload["support_research_writeback"] = upsert_learning_influence_summary(
        project_root,
        version=resolved_version,
        feature=feature,
        payload=payload,
    )
    receipts = write_support_surface_transaction(project_root, version=resolved_version, payload=payload)
    payload["artifacts"] = receipts
    return payload
