"""Feature graph validation for program plan harness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_GRAPH_KEYS = ("program_slug", "version", "scope_mode", "lakes")
REQUIRED_LAKE_KEYS = ("slug", "depends_on", "parity_subset", "status")


def validate_feature_graph_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_GRAPH_KEYS:
        if key not in payload:
            errors.append(f"missing:{key}")
    lakes = payload.get("lakes")
    if not isinstance(lakes, list) or not lakes:
        errors.append("lakes_must_be_non_empty_list")
        return errors
    for index, lake in enumerate(lakes):
        if not isinstance(lake, dict):
            errors.append(f"lakes[{index}]:not_object")
            continue
        for key in REQUIRED_LAKE_KEYS:
            if key not in lake:
                errors.append(f"lakes[{index}]:missing:{key}")
        if "depends_on" in lake and not isinstance(lake.get("depends_on"), list):
            errors.append(f"lakes[{index}]:depends_on_must_be_list")
    return errors


def load_feature_graph(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, ["file_missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, ["invalid_json"]
    if not isinstance(payload, dict):
        return None, ["root_must_be_object"]
    return payload, validate_feature_graph_payload(payload)


def program_dir(project_root: Path, version: str, program_slug: str) -> Path:
    return project_root / "docs" / "beacon" / version / "programs" / program_slug


def feature_graph_path(project_root: Path, version: str, program_slug: str) -> Path:
    return program_dir(project_root, version, program_slug) / "feature-graph.json"


def feature_graph_structure_snapshot(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize graph fields that constitute a structural program change."""
    if not isinstance(payload, dict):
        return {"lakes": []}
    lakes: list[dict[str, Any]] = []
    for lake in payload.get("lakes") or []:
        if not isinstance(lake, dict):
            continue
        slug = str(lake.get("slug") or "").strip()
        if not slug:
            continue
        depends_on = sorted(str(item).strip() for item in (lake.get("depends_on") or []) if str(item).strip())
        parity_subset = sorted(str(item).strip() for item in (lake.get("parity_subset") or []) if str(item).strip())
        lakes.append(
            {
                "slug": slug,
                "depends_on": depends_on,
                "parity_subset": parity_subset,
            }
        )
    lakes.sort(key=lambda item: item["slug"])
    return {
        "program_slug": str(payload.get("program_slug") or "").strip(),
        "version": str(payload.get("version") or "").strip(),
        "scope_mode": str(payload.get("scope_mode") or "").strip(),
        "lakes": lakes,
    }


def feature_graph_structure_fingerprint(payload: dict[str, Any] | None) -> str:
    snapshot = feature_graph_structure_snapshot(payload)
    canonical = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def graph_structure_baseline_path(project_root: Path, version: str, program_slug: str) -> Path:
    return (
        project_root
        / ".beacon"
        / "state"
        / "program-graph-structure"
        / version
        / f"{program_slug}.json"
    )


def capture_feature_graph_structure_baseline(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
    graph_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from beacon.utils.runtime import now_iso, write_json

    if graph_payload is None:
        graph_path = feature_graph_path(project_root, version, program_slug)
        graph_payload, _errors = load_feature_graph(graph_path)
    snapshot = feature_graph_structure_snapshot(graph_payload)
    fingerprint = feature_graph_structure_fingerprint(graph_payload)
    payload = {
        "schema_version": "1.0",
        "program_slug": program_slug,
        "version": version,
        "structure": snapshot,
        "fingerprint": fingerprint,
        "captured_at": now_iso(),
        "source": "program_freeze_gate",
    }
    path = graph_structure_baseline_path(project_root, version, program_slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, payload)
    return payload


def feature_graph_structure_changed(
    project_root: Path,
    *,
    version: str,
    program_slug: str,
) -> dict[str, Any]:
    baseline_path = graph_structure_baseline_path(project_root, version, program_slug)
    if not baseline_path.exists():
        return {
            "changed": False,
            "reason_code": "graph_structure_baseline_missing",
            "baseline_path": str(baseline_path.relative_to(project_root)),
        }
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        baseline = {}
    graph_path = feature_graph_path(project_root, version, program_slug)
    graph_payload, errors = load_feature_graph(graph_path)
    if errors:
        return {
            "changed": False,
            "blocked": True,
            "reason_code": "feature_graph_invalid",
            "errors": errors,
            "graph_path": str(graph_path.relative_to(project_root)),
        }
    current_fingerprint = feature_graph_structure_fingerprint(graph_payload)
    previous_fingerprint = str(baseline.get("fingerprint") or "")
    changed = bool(previous_fingerprint) and current_fingerprint != previous_fingerprint
    return {
        "changed": changed,
        "reason_code": "feature_graph_structure_changed" if changed else "",
        "baseline_path": str(baseline_path.relative_to(project_root)),
        "graph_path": str(graph_path.relative_to(project_root)),
        "previous_fingerprint": previous_fingerprint,
        "current_fingerprint": current_fingerprint,
    }
