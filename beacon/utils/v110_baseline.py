"""v1.1.0 baseline and spec-fingerprint helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import resolve_target_version


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _find_layer_files(project_root: Path, *, version: str, layer: str) -> list[Path]:
    rel_map = {
        "user_story": "user-story",
        "prd": "prd",
        "test_case": "qa/test-cases",
    }
    rel = rel_map[layer]
    out: list[Path] = []
    for root_name in ("beacon", "product"):
        base = project_root / "docs" / root_name / version / rel
        if not base.exists():
            continue
        if layer == "test_case":
            files = sorted(base.glob("*.ac-test-matrix.json"))
        else:
            files = sorted(base.glob("*.md"))
        out.extend([f for f in files if f.is_file()])
    dedup: dict[str, Path] = {}
    for path in out:
        dedup[str(path.resolve())] = path
    return list(dedup.values())


def _layer_signature(paths: list[Path]) -> tuple[str, list[dict[str, str]]]:
    parts: list[str] = []
    files: list[dict[str, str]] = []
    for path in sorted(paths):
        digest = _sha256(path)
        files.append({"path": str(path), "sha256": digest})
        parts.append(f"{path}:{digest}")
    merged = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest() if parts else ""
    return merged, files


def _baseline_root(project_root: Path, version: str) -> Path:
    return project_root / ".beacon" / "state" / "baselines" / version


def _fingerprint_root(project_root: Path, version: str) -> Path:
    return project_root / ".beacon" / "state" / "spec-fingerprints" / version


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _latest_baseline(project_root: Path, version: str) -> dict[str, Any]:
    root = _baseline_root(project_root, version)
    if not root.exists():
        return {}
    snapshots = sorted([p for p in root.glob("*.json") if p.is_file()])
    if not snapshots:
        return {}
    return _load_json(snapshots[-1])


def generate_spec_fingerprint(
    project_root: Path,
    *,
    run_id: str,
    version: str,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    layers: dict[str, Any] = {}
    merged_parts: list[str] = []
    for layer_key in ("user_story", "prd", "test_case"):
        files = _find_layer_files(project_root, version=resolved_version, layer=layer_key)
        layer_hash, refs = _layer_signature(files)
        layers[layer_key] = {
            "hash": layer_hash,
            "count": len(refs),
            "files": refs,
        }
        merged_parts.append(f"{layer_key}:{layer_hash}")
    fingerprint_hash = hashlib.sha256("\n".join(merged_parts).encode("utf-8")).hexdigest()
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "version": resolved_version,
        "generated_at": now_iso(),
        "layers": layers,
        "fingerprint_hash": fingerprint_hash,
    }

    root = _fingerprint_root(project_root, resolved_version)
    write_json(root / f"{run_id}.json", payload)
    write_json(root / "latest.json", payload)
    return payload


def record_baseline_snapshot(
    project_root: Path,
    *,
    run_id: str,
    version: str,
    feature: str,
    workflow_status: str,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    fingerprint = generate_spec_fingerprint(
        project_root,
        run_id=run_id,
        version=resolved_version,
    )
    previous = _latest_baseline(project_root, resolved_version)
    previous_id = str(previous.get("baseline_id", "") or "").strip()
    previous_fp = (previous.get("spec_fingerprint") or {}) if isinstance(previous, dict) else {}

    current_fp = {
        "user_story": str((fingerprint.get("layers", {}).get("user_story", {}) or {}).get("hash", "")),
        "prd": str((fingerprint.get("layers", {}).get("prd", {}) or {}).get("hash", "")),
        "test_case": str((fingerprint.get("layers", {}).get("test_case", {}) or {}).get("hash", "")),
        "fingerprint_hash": str(fingerprint.get("fingerprint_hash", "")),
    }

    changed_layers: list[str] = []
    if previous_fp:
        for key in ("user_story", "prd", "test_case"):
            if str(previous_fp.get(key, "")) != str(current_fp.get(key, "")):
                changed_layers.append(key)

    baseline_id = f"bl-{run_id}"
    payload = {
        "schema_version": "1.0",
        "baseline_id": baseline_id,
        "run_id": run_id,
        "version": resolved_version,
        "feature": feature,
        "workflow_status": workflow_status,
        "generated_at": now_iso(),
        "spec_fingerprint": current_fp,
        "open_questions": [],
        "delta_summary": {
            "changed_layers": changed_layers,
            "doc_chain_update_required": bool(changed_layers),
        },
        "risk_flags": ["spec_impl_drift_detected"] if changed_layers and workflow_status != "completed" else [],
        "revision_of": previous_id or None,
    }
    if not payload["revision_of"]:
        payload.pop("revision_of", None)

    root = _baseline_root(project_root, resolved_version)
    write_json(root / f"{baseline_id}.json", payload)
    write_json(root / "latest.json", payload)

    change_impact = {
        "schema_version": "1.0",
        "run_id": run_id,
        "version": resolved_version,
        "baseline_id": baseline_id,
        "updated_at": now_iso(),
        "doc_chain_update_required": bool(changed_layers),
        "changed_layers": changed_layers,
        "tasks": [
            {
                "task": f"regenerate-{layer}",
                "status": "pending",
            }
            for layer in changed_layers
        ],
    }
    write_json(project_root / ".beacon" / "state" / "change-impact" / f"{run_id}.json", change_impact)
    return {
        "fingerprint": fingerprint,
        "baseline": payload,
        "change_impact": change_impact,
        "fingerprint_path": str((_fingerprint_root(project_root, resolved_version) / f"{run_id}.json").relative_to(project_root)),
        "baseline_path": str((root / f"{baseline_id}.json").relative_to(project_root)),
        "change_impact_path": str((project_root / ".beacon" / "state" / "change-impact" / f"{run_id}.json").relative_to(project_root)),
    }


def load_latest_spec_fingerprint(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    return _load_json(_fingerprint_root(project_root, resolved_version) / "latest.json")


def load_latest_baseline_snapshot(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    return _load_json(_baseline_root(project_root, resolved_version) / "latest.json")
