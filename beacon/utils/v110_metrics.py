"""v1.1.0 report metrics helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.memory import load_memory_entries
from beacon.utils.v110_baseline import load_latest_baseline_snapshot


def _json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _count_jsonl_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])


def compute_memory_governance_metrics(project_root: Path) -> dict[str, Any]:
    debug_root = project_root / ".beacon" / "state" / "debug-feedback"
    candidate_root = project_root / ".beacon" / "state" / "feedback-candidates"
    apply_root = project_root / ".beacon" / "state" / "feedback-apply-report"
    lifecycle_index = _json(project_root / ".beacon" / "memory" / "workflow-lifecycle.index.json")

    debug_files = sorted([p for p in debug_root.glob("*.jsonl") if p.is_file()]) if debug_root.exists() else []
    candidate_files = sorted([p for p in candidate_root.glob("*.json") if p.is_file()]) if candidate_root.exists() else []
    apply_files = sorted([p for p in apply_root.glob("*.json") if p.is_file()]) if apply_root.exists() else []

    debug_events_total = sum(_count_jsonl_lines(path) for path in debug_files)
    candidate_run_ids = {path.stem for path in candidate_files}
    applied_run_ids = {path.stem for path in apply_files}
    unsynced = sorted(candidate_run_ids - applied_run_ids)

    dedupe_keys = lifecycle_index.get("dedupe_keys")
    dedupe_size = len(dedupe_keys) if isinstance(dedupe_keys, list) else 0
    memory_total = len(load_memory_entries(project_root))

    return {
        "raw_debug_files": len(debug_files),
        "raw_debug_events": debug_events_total,
        "candidate_files": len(candidate_files),
        "apply_reports": len(apply_files),
        "unsynced_candidates": len(unsynced),
        "unsynced_candidate_run_ids": unsynced[:20],
        "lifecycle_dedupe_keys": dedupe_size,
        "memory_items_total": memory_total,
    }


def compute_baseline_drift_metrics(project_root: Path, *, version: str) -> dict[str, Any]:
    latest = load_latest_baseline_snapshot(project_root, version=version)
    if not latest:
        return {
            "has_baseline": False,
            "baseline_id": "",
            "revision_of": "",
            "changed_layers": [],
            "doc_chain_update_required": False,
            "risk_flags": [],
        }
    delta = latest.get("delta_summary", {}) if isinstance(latest.get("delta_summary"), dict) else {}
    changed_layers = delta.get("changed_layers")
    if not isinstance(changed_layers, list):
        changed_layers = []
    return {
        "has_baseline": True,
        "baseline_id": str(latest.get("baseline_id", "") or ""),
        "revision_of": str(latest.get("revision_of", "") or ""),
        "changed_layers": [str(x) for x in changed_layers if str(x).strip()],
        "doc_chain_update_required": bool(delta.get("doc_chain_update_required", False)),
        "risk_flags": [str(x) for x in (latest.get("risk_flags") or []) if str(x).strip()],
    }
