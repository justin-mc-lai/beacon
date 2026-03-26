"""Helpers for Beacon prototype lifecycle artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PROTOTYPE_UI_KIT = "bootstrap-5.3.x"


def slugify_feature(feature: str) -> str:
    return (feature or "").strip().lower().replace(" ", "-")


def prototype_dir(project_root: Path, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "prototype" / slugify_feature(feature)


def prototype_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    root = prototype_dir(project_root, version, feature)
    return {
        "root": root,
        "index": root / "index.html",
        "manifest": root / "manifest.json",
        "source_map": root / "source-map.json",
        "freeze": root / "freeze.json",
        "theme": root / "theme.json",
        "navigation_map": root / "navigation-map.json",
        "interaction_map": root / "interaction-map.json",
        "review_json": root / "prototype-review.json",
        "review_md": root / "prototype-review.md",
    }


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_refs(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = slugify_feature(feature)
    return {
        "user_story": project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md",
        "prd": project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md",
    }


def source_fingerprints(project_root: Path, version: str, feature: str) -> dict[str, str]:
    refs = source_refs(project_root, version, feature)
    out: dict[str, str] = {}
    for key, path in refs.items():
        if path.exists():
            out[key] = _sha256_file(path)
    return out


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prototype_status(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    paths = prototype_paths(project_root, version, feature)
    freeze = _read_json(paths["freeze"])
    manifest = _read_json(paths["manifest"])
    current = source_fingerprints(project_root, version, feature)

    exists = all(paths[key].exists() for key in ("index", "manifest", "source_map", "freeze"))
    frozen = str(freeze.get("status", "")).strip().lower() == "frozen"
    stale = False
    recorded_source = freeze.get("source_fingerprints")
    if isinstance(recorded_source, dict):
        normalized_source = dict(recorded_source)
        if "user-story" in normalized_source and "user_story" not in normalized_source:
            normalized_source["user_story"] = normalized_source["user-story"]
        if "user_story" in normalized_source and "user-story" not in normalized_source:
            normalized_source["user-story"] = normalized_source["user_story"]
        recorded_source = normalized_source
    if isinstance(recorded_source, dict) and recorded_source and current:
        stale = any(str(recorded_source.get(key, "")) != value for key, value in current.items())
    if stale:
        status = "stale"
    elif frozen:
        status = "frozen"
    elif exists or manifest:
        status = "draft"
    else:
        status = "missing"

    return {
        "status": status,
        "exists": exists,
        "frozen": frozen,
        "stale": stale,
        "ui_kit": str((manifest or freeze).get("ui_kit", "") or PROTOTYPE_UI_KIT),
        "review_status": str((manifest or freeze).get("review_status", "") or _read_json(paths["review_json"]).get("overall_status", "missing")),
        "gate_ready": bool(
            exists
            and str((manifest or freeze).get("review_status", "") or _read_json(paths["review_json"]).get("overall_status", "missing")) == "pass"
            and status == "frozen"
        ),
        "files": {key: path for key, path in paths.items()},
        "paths": {key: str(path) for key, path in paths.items()},
        "source_fingerprints": current,
        "recorded_source_fingerprints": recorded_source if isinstance(recorded_source, dict) else {},
    }


_UI_REQUIRED_PATTERNS = (
    re.compile(r"ui_visualization_required\s*[:=]\s*true", re.IGNORECASE),
    re.compile(r"prototype_freeze_required\s*[:=]\s*true", re.IGNORECASE),
)


def version_requires_prototype(project_root: Path, version: str) -> bool:
    roots = [
        project_root / "docs" / "beacon" / version / "user-story",
        project_root / "docs" / "beacon" / version / "prd",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001
                continue
            if any(pattern.search(text) for pattern in _UI_REQUIRED_PATTERNS):
                return True
    return False
