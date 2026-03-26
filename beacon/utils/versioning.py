"""Version resolution helpers.

Beacon project docs version and Beacon runtime/toolkit version are distinct:

- docs version controls which `docs/beacon/<version>/` line is treated as source of truth
- runtime version controls managed context markers and runtime compatibility checks
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

from beacon import __toolkit_version__

_SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
_RELEASE_LINE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[.-].+)?$")
_TOOLKIT_VERSION = re.compile(r'__toolkit_version__\s*=\s*"(?P<version>v\d+\.\d+\.\d+)"')
_CONTEXT_MARKER = re.compile(r"<!--\s*BEACON:VERSION:([^>\s]+)\s*-->")


def normalize_version(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    match = _SEMVER.match(raw)
    if not match:
        return raw
    major, minor, patch = match.groups()
    return f"v{int(major)}.{int(minor)}.{int(patch)}"


def release_line_key(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    match = _RELEASE_LINE.match(raw)
    if not match:
        return None
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


def load_project_onboarding_state(project_root: Path) -> dict[str, Any]:
    state_file = project_root / ".beacon" / "state" / "project-onboarding.json"
    if not state_file.exists():
        return {}
    try:
        payload = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def onboarding_docs_version(project_root: Path) -> str | None:
    payload = load_project_onboarding_state(project_root)
    return normalize_version(str(payload.get("docs_version", "") or "").strip())


def onboarding_runtime_version(project_root: Path) -> str | None:
    payload = load_project_onboarding_state(project_root)
    return normalize_version(str(payload.get("runtime_version", "") or "").strip())


def context_managed_versions(project_root: Path) -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = project_root / name
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        match = _CONTEXT_MARKER.search(text)
        if not match:
            continue
        normalized = normalize_version(match.group(1))
        if normalized:
            versions[name] = normalized
    return versions


def context_managed_version(project_root: Path) -> str | None:
    versions = {value for value in context_managed_versions(project_root).values() if value}
    if len(versions) != 1:
        return None
    return next(iter(versions))


def current_runtime_release_version(project_root: Path) -> str | None:
    init_file = project_root / "beacon" / "__init__.py"
    if not init_file.exists():
        return None
    try:
        text = init_file.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return None
    match = _TOOLKIT_VERSION.search(text)
    if not match:
        return None
    version = normalize_version(match.group("version"))
    if not version:
        return None
    versions = set(discover_versions(project_root))
    return version if version in versions else None


def resolve_docs_version(
    project_root: Path,
    requested: str | None,
    *,
    fallback: str = "v1.0.0",
    return_source: bool = False,
) -> str | tuple[str, str]:
    raw = str(requested or "").strip().lower()
    source = "explicit"
    if raw in {"latest-docs", "planned"}:
        resolved = largest_version(project_root, fallback=fallback)
        source = "docs_scan"
    elif raw in {"", "auto", "latest"}:
        onboarding = onboarding_docs_version(project_root)
        if onboarding:
            resolved = onboarding
            source = "onboarding_state"
        else:
            runtime_release = current_runtime_release_version(project_root)
            if runtime_release:
                resolved = runtime_release
                source = "runtime_release"
            else:
                resolved = largest_version(project_root, fallback=fallback)
                source = "docs_scan"
    else:
        normalized = normalize_version(requested)
        if not normalized:
            raise ValueError(
                f"Invalid version '{requested}'. Use semver like v1.2.3, or one of: auto/latest, latest-docs/planned."
            )
        resolved = normalized
        source = "explicit"
    return (resolved, source) if return_source else resolved


def resolve_runtime_version(
    project_root: Path,
    requested: str | None,
    *,
    fallback: str | None = None,
    return_source: bool = False,
) -> str | tuple[str, str]:
    raw = str(requested or "").strip().lower()
    source = "explicit"
    if raw not in {"", "auto", "latest"}:
        normalized = normalize_version(requested)
        if not normalized:
            raise ValueError(
                f"Invalid runtime version '{requested}'. Use semver like v1.2.3 or auto/latest."
            )
        resolved = normalized
        source = "explicit"
    else:
        toolkit = normalize_version(__toolkit_version__)
        if toolkit:
            resolved = toolkit
            source = "toolkit_version"
        else:
            onboarding = onboarding_runtime_version(project_root)
            if onboarding:
                resolved = onboarding
                source = "onboarding_state"
            else:
                context_version = context_managed_version(project_root)
                if context_version:
                    resolved = context_version
                    source = "context_marker"
                else:
                    resolved = normalize_version(fallback) or "v1.0.0"
                    source = "fallback"
    return (resolved, source) if return_source else resolved


def describe_project_version_context(
    project_root: Path,
    *,
    docs_version: str | None = None,
    runtime_version: str | None = None,
) -> dict[str, Any]:
    resolved_docs, docs_source = resolve_docs_version(project_root, docs_version, return_source=True)
    resolved_runtime, runtime_source = resolve_runtime_version(project_root, runtime_version, return_source=True)
    context_versions = context_managed_versions(project_root)
    unique_context = sorted({value for value in context_versions.values() if value})
    return {
        "docs_version": resolved_docs,
        "docs_version_source": docs_source,
        "runtime_version": resolved_runtime,
        "runtime_version_source": runtime_source,
        "onboarding_docs_version": onboarding_docs_version(project_root) or "",
        "onboarding_runtime_version": onboarding_runtime_version(project_root) or "",
        "context_versions": context_versions,
        "context_managed_version": unique_context[0] if len(unique_context) == 1 else "",
        "context_version_consistent": len(unique_context) <= 1,
        "available_docs_versions": discover_versions(project_root),
        "latest_scanned_docs_version": largest_version(project_root, fallback=resolved_docs),
    }


def resolve_target_version(
    project_root: Path,
    requested: str | None,
    *,
    fallback: str = "v1.0.0",
) -> str:
    resolved = resolve_docs_version(project_root, requested, fallback=fallback)
    return resolved if isinstance(resolved, str) else resolved[0]
