"""Protected path denylist helpers for automatic Beacon write surfaces."""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
from typing import Any

REASON_CODE = "protected_path_denylist"

EXACT_PATTERNS = {".env"}
GLOB_PATTERNS = {".env.*", "secrets/**", "credentials/**", "*_key*"}
EXTENSIONS = {".pem", ".key"}
SEGMENTS = {
    "auth",
    "oauth",
    "sso",
    "payments",
    "billing",
    "stripe",
    "migrations",
    "schema_migrations",
}


def normalize_relative_path(path: Path | str, *, project_root: Path | None = None) -> str:
    target = Path(path).expanduser()
    if project_root is not None:
        root = project_root.expanduser().resolve()
        if not target.is_absolute():
            target = (root / target).resolve()
        try:
            return target.relative_to(root).as_posix()
        except ValueError:
            return target.as_posix()
    text = target.as_posix()
    while text.startswith("./"):
        text = text[2:]
    return text


def protected_path_match(path: Path | str, *, project_root: Path | None = None) -> dict[str, Any]:
    rel = normalize_relative_path(path, project_root=project_root)
    name = Path(rel).name
    parts = [part for part in Path(rel).parts if part not in {"", "."}]
    lower_parts = {part.lower() for part in parts}

    if rel in EXACT_PATTERNS or name in EXACT_PATTERNS:
        return {"matched": True, "reason_code": REASON_CODE, "match_type": "exact", "pattern": name}
    for pattern in sorted(GLOB_PATTERNS):
        if fnmatch(rel, pattern) or fnmatch(name, pattern):
            return {"matched": True, "reason_code": REASON_CODE, "match_type": "glob", "pattern": pattern}
    suffix = Path(rel).suffix.lower()
    if suffix in EXTENSIONS:
        return {"matched": True, "reason_code": REASON_CODE, "match_type": "extension", "pattern": suffix}
    for segment in sorted(SEGMENTS):
        if segment in lower_parts:
            return {"matched": True, "reason_code": REASON_CODE, "match_type": "segment", "pattern": segment}
    return {"matched": False, "reason_code": "", "match_type": "", "pattern": ""}


def build_protected_path_block(path: Path | str, *, project_root: Path | None = None) -> dict[str, Any]:
    match = protected_path_match(path, project_root=project_root)
    rel = normalize_relative_path(path, project_root=project_root)
    return {
        "schema_version": "1.0",
        "status": "blocked" if match.get("matched") else "pass",
        "blocked": bool(match.get("matched")),
        "reason_code": REASON_CODE if match.get("matched") else "",
        "reason_codes": [REASON_CODE] if match.get("matched") else [],
        "path": rel,
        "match": match,
        "route_recommendation": (
            "Stop automatic write; ask the human operator for explicit handling or a scoped exception."
            if match.get("matched")
            else ""
        ),
    }


def planner_protected_path_advisory(path: Path | str, *, project_root: Path | None = None) -> dict[str, Any]:
    match = protected_path_match(path, project_root=project_root)
    return {
        "schema_version": "1.0",
        "status": "advisory" if match.get("matched") else "pass",
        "blocked": False,
        "reason_code": REASON_CODE if match.get("matched") else "",
        "path": normalize_relative_path(path, project_root=project_root),
        "risk": "protected_path" if match.get("matched") else "",
        "match": match,
    }
