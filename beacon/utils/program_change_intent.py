"""Program change intent log — append-only audit chain under programs/<slug>/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.program_freeze_gate import build_program_freeze_gate, write_program_freeze_gate
from beacon.utils.program_graph import (
    capture_feature_graph_structure_baseline,
    feature_graph_path,
    feature_graph_structure_changed,
    load_feature_graph,
)
from beacon.utils.runtime import now_iso, write_json


def change_intent_log_path(project_root: Path, version: str, program_slug: str) -> Path:
    return (
        project_root
        / "docs"
        / "beacon"
        / version
        / "programs"
        / program_slug
        / "change-intent-log.jsonl"
    )


def append_change_intent_log(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
    utterance: str,
    affected_slugs: list[str] | None = None,
    scope_mode: str = "",
) -> Path:
    log_path = change_intent_log_path(project_root, version, program_slug)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry: dict[str, Any] = {
        "recorded_at": now_iso(),
        "utterance": utterance,
        "affected_slugs": [str(item) for item in (affected_slugs or []) if str(item).strip()],
        "scope_mode": scope_mode or "",
        "program_slug": program_slug,
        "version": version,
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log_path


def promotion_diff_review_marker_path(project_root: Path, version: str, program_slug: str) -> Path:
    return (
        project_root
        / ".beacon"
        / "state"
        / "program-change-review"
        / version
        / f"{program_slug}.json"
    )


def require_promotion_diff_before_refreeze(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
) -> dict[str, Any]:
    """Fail closed when program change intent exists but promotion_diff review is missing."""
    log_path = change_intent_log_path(project_root, version, program_slug)
    marker_path = promotion_diff_review_marker_path(project_root, version, program_slug)
    if not log_path.exists():
        return {"blocked": False, "reason_code": ""}
    if marker_path.exists():
        try:
            payload = json.loads(marker_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if payload.get("promotion_diff"):
            return {"blocked": False, "reason_code": ""}
    return {
        "blocked": True,
        "reason_code": "promotion_diff_review_required",
        "recommended_command": (
            f'beacon-pln-review --program {program_slug} --version {version} '
            f"(promotion_diff vs frozen truth + change intent)"
        ),
        "change_intent_log": str(log_path.relative_to(project_root)),
    }


def record_promotion_diff_review(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
    promotion_diff: Any,
    reviewed_by: str = "",
) -> Path:
    marker_path = promotion_diff_review_marker_path(project_root, version, program_slug)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "program_slug": program_slug,
        "version": version,
        "promotion_diff": promotion_diff,
        "reviewed_by": reviewed_by,
        "reviewed_at": now_iso(),
    }
    write_json(marker_path, payload)
    return marker_path


def rerun_program_freeze_after_structural_refreeze(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
    lake_or_ocean: str = "海",
    feature_graph_ack: bool = True,
) -> dict[str, Any]:
    """Re-run program freeze gate (P6) when graph structure changed after refreeze."""
    structure = feature_graph_structure_changed(
        project_root,
        version=version,
        program_slug=program_slug,
    )
    if not structure.get("changed"):
        return {
            "schema_version": "1.0",
            "status": "skipped",
            "reason_code": str(structure.get("reason_code") or "no_structural_change"),
            "structure_check": structure,
        }
    gate = build_program_freeze_gate(
        project_root,
        version=version,
        program_slug=program_slug,
        lake_or_ocean=lake_or_ocean,
        feature_graph_ack=feature_graph_ack,
    )
    gate["rerun_reason"] = "structural_graph_change_after_refreeze"
    gate["structure_check"] = structure
    out_path = write_program_freeze_gate(project_root, gate)
    gate["path"] = str(out_path.relative_to(project_root))
    if gate.get("status") == "frozen":
        graph_payload, _errors = load_feature_graph(
            feature_graph_path(project_root, version, program_slug)
        )
        capture_feature_graph_structure_baseline(
            project_root,
            version=version,
            program_slug=program_slug,
            graph_payload=graph_payload,
        )
    return {
        "schema_version": "1.0",
        "status": "rerun",
        "program_freeze_gate": gate,
        "structure_check": structure,
    }
