"""Version resolution helpers.

Beacon defaults to the largest semantic version found under docs/
instead of using the legacy `latest` virtual version.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

_SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def normalize_version(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    match = _SEMVER.match(raw)
    if not match:
        return raw
    major, minor, patch = match.groups()
    return f"v{int(major)}.{int(minor)}.{int(patch)}"


def _iter_version_names(root: Path) -> Iterable[str]:
    if not root.exists():
        return []
    names: list[str] = []
    for child in root.iterdir():
        if child.is_dir() and _SEMVER.match(child.name):
            names.append(child.name)
    return names


def discover_versions(project_root: Path) -> list[str]:
    candidates: set[str] = set()
    for base in (project_root / "docs" / "beacon",):
        for name in _iter_version_names(base):
            normalized = normalize_version(name)
            if normalized:
                candidates.add(normalized)
    def _key(ver: str) -> tuple[int, int, int]:
        match = _SEMVER.match(ver)
        if not match:
            return (0, 0, 0)
        a, b, c = match.groups()
        return (int(a), int(b), int(c))
    return sorted(candidates, key=_key)


def largest_version(project_root: Path, *, fallback: str = "v1.0.0") -> str:
    versions = discover_versions(project_root)
    if not versions:
        return normalize_version(fallback) or "v1.0.0"
    return versions[-1]


def resolve_target_version(
    project_root: Path,
    requested: str | None,
    *,
    fallback: str = "v1.0.0",
) -> str:
    raw = str(requested or "").strip().lower()
    if raw in {"", "auto", "latest"}:
        return largest_version(project_root, fallback=fallback)
    normalized = normalize_version(requested)
    if normalized:
        return normalized
    return largest_version(project_root, fallback=fallback)
