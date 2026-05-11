"""Support helpers for Beacon prototype gate and lifecycle checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.prototype_utils import (
    evaluate_prototype_status,
    prototype_files,
    slugify_feature,
    source_doc_paths,
)


PROTOTYPE_TRIGGER_PATTERNS = (
    re.compile(r"ui_visualization_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"prototype_freeze_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"interactive_prototype_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"prototype_ux_prd_required\s*[:=]\s*true", re.IGNORECASE),
)
ROUTE_CLOSURE_PATTERNS = (
    re.compile(r"route_closure_required\s*[:=]\s*true", re.IGNORECASE),
)


def prototype_dir(project_root: Path, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "prototype" / slugify_feature(feature)


def prototype_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    return prototype_files(project_root, version, feature)


def _sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_refs(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    resolved = source_doc_paths(project_root, version, feature)
    return {
        "user_story": resolved["user-story"],
        "prd": resolved["prd"],
        "test_case": resolved["test-case"],
    }


def source_fingerprints(project_root: Path, version: str, feature: str) -> dict[str, str]:
    refs = source_refs(project_root, version, feature)
    out: dict[str, str] = {}
    for key, path in refs.items():
        if path.exists():
            out[key] = _sha256_file(path)
    if "user_story" in out and "user-story" not in out:
        out["user-story"] = out["user_story"]
    return out


def prototype_status(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    payload = evaluate_prototype_status(project_root, version, feature)
    files = prototype_paths(project_root, version, feature)
    payload["files"] = files
    payload["paths"] = {key: str(path) for key, path in files.items()}
    return payload


def feature_requires_prototype(project_root: Path, version: str, feature: str) -> bool:
    refs = source_refs(project_root, version, feature)
    for path in refs.values():
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        if any(pattern.search(text) for pattern in PROTOTYPE_TRIGGER_PATTERNS):
            return True
    return False


def version_requires_prototype(project_root: Path, version: str) -> bool:
    roots = [
        project_root / "docs" / "beacon" / version / "user-story",
        project_root / "docs" / "beacon" / version / "prd",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001
                continue
            if any(pattern.search(text) for pattern in PROTOTYPE_TRIGGER_PATTERNS):
                return True
    return False


def feature_requires_route_closure(project_root: Path, version: str, feature: str) -> bool:
    refs = source_refs(project_root, version, feature)
    for path in refs.values():
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        if any(pattern.search(text) for pattern in ROUTE_CLOSURE_PATTERNS):
            return True
    return False
