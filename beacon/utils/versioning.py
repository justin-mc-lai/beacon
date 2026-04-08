"""Version resolution helpers with Beacon release-truth support."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

from beacon import __toolkit_version__

_SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
_RELEASE_LINE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[.-].+)?$")
_TOOLKIT_VERSION = re.compile(r'__toolkit_version__\s*=\s*"(?P<version>v\d+\.\d+\.\d+)"')
_PACKAGE_VERSION = re.compile(r'__version__\s*=\s*"(?P<version>\d+\.\d+\.\d+)"')
_CONTEXT_MARKER = re.compile(r"<!--\s*BEACON:VERSION:([^>\s]+)\s*-->")
_SEMVER_SEARCH = re.compile(r"v?\d+\.\d+\.\d+")
_VERSION_TRUTH_STATE = Path(".beacon/state/version-truth/current.json")
_VERSION_TRUTH_CANONICAL = Path("beacon/version-truth.json")
_ALLOW_CONTEXT_VERSION_DRIFT_ENV = "BEACON_ALLOW_CONTEXT_VERSION_DRIFT"


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


def _version_key(value: str) -> tuple[int, int, int]:
    match = _SEMVER.match(value)
    if not match:
        return (0, 0, 0)
    major, minor, patch = match.groups()
    return (int(major), int(minor), int(patch))


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _normalize_version_list(values: Any) -> list[str]:
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for value in values:
        normalized = normalize_version(str(value or "").strip())
        if normalized and normalized not in out:
            out.append(normalized)
    return out


def discover_versions(project_root: Path) -> list[str]:
    candidates: set[str] = set()
    for base in (project_root / "docs" / "beacon",):
        for name in _iter_version_names(base):
            normalized = normalize_version(name)
            if normalized:
                candidates.add(normalized)
    return sorted(candidates, key=_version_key)


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


def current_git_branch(project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return ""
    if result.returncode != 0:
        return ""
    return str(result.stdout or "").strip()


def branch_context_version(project_root: Path) -> str | None:
    branch = current_git_branch(project_root)
    if not branch:
        return None
    versions = {
        normalize_version(token)
        for token in _SEMVER_SEARCH.findall(branch)
    }
    normalized = sorted({item for item in versions if item}, key=_version_key)
    if len(normalized) != 1:
        return None
    return normalized[0]


def _preferred_context_version(signals: dict[str, str]) -> str:
    non_empty = {key: value for key, value in signals.items() if value}
    if not non_empty:
        return ""
    counts: dict[str, int] = {}
    for value in non_empty.values():
        counts[value] = counts.get(value, 0) + 1
    ranked = sorted(
        counts.items(),
        key=lambda item: (-item[1], _version_key(item[0])),
    )
    if ranked and ranked[0][1] >= 2:
        return ranked[0][0]
    for key in ("context_marker", "onboarding_docs", "git_branch"):
        value = non_empty.get(key, "")
        if value:
            return value
    return ranked[0][0] if ranked else ""


def build_context_version_guard(
    project_root: Path,
    requested_version: str | None,
    *,
    resolved_version: str | None = None,
    docs_source: str = "",
) -> dict[str, Any]:
    raw_requested = str(requested_version or "").strip()
    raw_lower = raw_requested.lower()
    explicit_requested = bool(raw_requested and raw_lower not in {"auto", "latest", "latest-docs", "planned"})
    requested_normalized = normalize_version(raw_requested) if explicit_requested else ""
    resolved_normalized = normalize_version(resolved_version or requested_normalized or "")
    context_marker_version = context_managed_version(project_root) or ""
    if context_marker_version and not (project_root / "docs" / "beacon" / context_marker_version).exists():
        version_truth = load_version_truth(project_root)
        truth_versions = set()
        lines = version_truth.get("lines") if isinstance(version_truth.get("lines"), dict) else {}
        truth_versions.update(normalize_version(str(item)) for item in lines.keys())
        truth_versions.update(_normalize_version_list(version_truth.get("planning_lines")))
        truth_versions.update(_normalize_version_list(version_truth.get("partial_runtime_supplement_lines")))
        truth_versions.add(normalize_version(str(version_truth.get("docs_default_line", "") or "")))
        truth_versions.add(normalize_version(str(version_truth.get("current_runtime_release_line", "") or "")))
        truth_versions = {item for item in truth_versions if item}
        if context_marker_version not in truth_versions:
            context_marker_version = ""
    signals = {
        "context_marker": context_marker_version,
        "onboarding_docs": onboarding_docs_version(project_root) or "",
        "git_branch": branch_context_version(project_root) or "",
    }
    recommended_version = _preferred_context_version(signals)
    override_enabled = str(os.getenv(_ALLOW_CONTEXT_VERSION_DRIFT_ENV, "")).strip().lower() in {"1", "true", "yes", "on"}

    status = "not_applicable"
    reason_code = ""
    message = ""
    if explicit_requested:
        status = "pass"
        if recommended_version and requested_normalized and requested_normalized != recommended_version:
            if override_enabled:
                status = "warn"
                reason_code = "context_version_override"
                message = (
                    f"requested version {requested_normalized} differs from context-managed version "
                    f"{recommended_version}, but override is enabled via {_ALLOW_CONTEXT_VERSION_DRIFT_ENV}=1."
                )
            else:
                status = "blocked"
                reason_code = "context_version_mismatch"
                message = (
                    f"requested version {requested_normalized} conflicts with context-managed version "
                    f"{recommended_version}. Use --version {recommended_version} or set "
                    f"{_ALLOW_CONTEXT_VERSION_DRIFT_ENV}=1 if the drift is intentional."
                )

    return {
        "schema_version": "1.0",
        "requested_version": requested_normalized or raw_requested,
        "resolved_version": resolved_normalized or "",
        "docs_source": docs_source,
        "status": status,
        "reason_code": reason_code,
        "message": message,
        "recommended_version": recommended_version,
        "signals": signals,
        "git_branch": current_git_branch(project_root),
        "override_enabled": override_enabled,
        "override_env": _ALLOW_CONTEXT_VERSION_DRIFT_ENV,
    }


def resolve_operational_docs_version(
    project_root: Path,
    requested: str | None,
    *,
    fallback: str = "v1.0.0",
    command_name: str = "",
) -> str:
    resolved, source = resolve_docs_version(project_root, requested, fallback=fallback, return_source=True)
    guard = build_context_version_guard(
        project_root,
        requested,
        resolved_version=resolved,
        docs_source=source,
    )
    if str(guard.get("status", "") or "") == "blocked":
        prefix = f"{command_name}: " if command_name else ""
        raise ValueError(prefix + str(guard.get("message", "context version mismatch")))
    return str(resolved)


def _truth_source_candidates(project_root: Path) -> list[tuple[str, Path]]:
    return [
        ("runtime_state", project_root / _VERSION_TRUTH_STATE),
        ("canonical_file", project_root / _VERSION_TRUTH_CANONICAL),
    ]


def version_truth_source_path(project_root: Path) -> Path | None:
    for _, candidate in _truth_source_candidates(project_root):
        if candidate.exists():
            return candidate
    return None


def _read_init_versions(project_root: Path) -> tuple[str | None, str | None]:
    init_file = project_root / "beacon" / "__init__.py"
    if not init_file.exists():
        return (None, None)
    try:
        text = init_file.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return (None, None)
    package_match = _PACKAGE_VERSION.search(text)
    toolkit_match = _TOOLKIT_VERSION.search(text)
    package_version = str(package_match.group("version")) if package_match else None
    toolkit_version = normalize_version(toolkit_match.group("version")) if toolkit_match else None
    return (package_version, toolkit_version)


def _infer_version_truth(project_root: Path) -> dict[str, Any]:
    package_version, runtime_version = _read_init_versions(project_root)
    docs_versions = discover_versions(project_root)
    current_release = runtime_version or (docs_versions[-1] if docs_versions else None) or "v1.0.0"
    planning_lines = [item for item in docs_versions if _version_key(item) > _version_key(current_release)]
    lines: dict[str, dict[str, str]] = {}
    for version in docs_versions:
        status = "historical_release"
        if version == current_release:
            status = "current_runtime_release"
        elif version in planning_lines:
            status = "planning_only"
        lines[version] = {"status": status}
    if current_release not in lines:
        lines[current_release] = {"status": "current_runtime_release"}
    return {
        "schema_version": "1.0",
        "package_version": package_version or "",
        "runtime_version": current_release,
        "docs_default_line": current_release,
        "current_runtime_release_line": current_release,
        "planning_lines": planning_lines,
        "partial_runtime_supplement_lines": [],
        "lines": lines,
    }


def _normalize_version_truth(
    project_root: Path,
    payload: dict[str, Any],
    *,
    source_kind: str,
    source_path: Path | None,
) -> dict[str, Any]:
    inferred = _infer_version_truth(project_root)
    package_version = str(payload.get("package_version", "") or inferred.get("package_version", "")).strip()
    runtime_version = normalize_version(
        str(payload.get("runtime_version", "") or inferred.get("runtime_version", ""))
    )
    current_release = normalize_version(
        str(
            payload.get("current_runtime_release_line", "")
            or inferred.get("current_runtime_release_line", "")
            or runtime_version
            or ""
        )
    ) or inferred["current_runtime_release_line"]
    docs_default_line = normalize_version(
        str(payload.get("docs_default_line", "") or inferred.get("docs_default_line", "") or current_release)
    ) or current_release
    planning_lines = _normalize_version_list(payload.get("planning_lines"))
    if not planning_lines:
        planning_lines = _normalize_version_list(inferred.get("planning_lines"))
    partial_lines = _normalize_version_list(payload.get("partial_runtime_supplement_lines"))
    lines_payload = payload.get("lines") if isinstance(payload.get("lines"), dict) else {}
    lines: dict[str, dict[str, Any]] = {}
    for version, item in inferred.get("lines", {}).items():
        if isinstance(item, dict):
            lines[str(version)] = dict(item)
    for version, item in lines_payload.items():
        normalized = normalize_version(str(version or "").strip())
        if not normalized:
            continue
        row = dict(item) if isinstance(item, dict) else {}
        lines[normalized] = {
            "status": str(row.get("status", "") or lines.get(normalized, {}).get("status", "")).strip(),
        }
    all_versions = set(discover_versions(project_root))
    all_versions.update(lines.keys())
    all_versions.update(planning_lines)
    all_versions.update(partial_lines)
    all_versions.add(current_release)
    for version in sorted(all_versions, key=_version_key):
        status = str(lines.get(version, {}).get("status", "") or "").strip()
        if not status:
            if version == current_release:
                status = "current_runtime_release"
            elif version in partial_lines:
                status = "planning_with_partial_runtime_supplement"
            elif version in planning_lines:
                status = "planning_only"
            else:
                status = "historical_release"
        elif version in partial_lines and status == "planning_only":
            status = "planning_with_partial_runtime_supplement"
        lines[version] = {"status": status}
    return {
        "schema_version": str(payload.get("schema_version", "") or inferred.get("schema_version", "1.0")),
        "package_version": package_version,
        "runtime_version": runtime_version or current_release,
        "docs_default_line": docs_default_line,
        "current_runtime_release_line": current_release,
        "planning_lines": [item for item in planning_lines if item != current_release],
        "partial_runtime_supplement_lines": [item for item in partial_lines if item != current_release],
        "lines": lines,
        "source_kind": source_kind,
        "source_path": str(source_path.relative_to(project_root)) if source_path and source_path.exists() else "",
    }


def load_version_truth(project_root: Path) -> dict[str, Any]:
    for source_kind, candidate in _truth_source_candidates(project_root):
        payload = _read_json_file(candidate)
        if payload:
            return _normalize_version_truth(project_root, payload, source_kind=source_kind, source_path=candidate)
    return _normalize_version_truth(
        project_root,
        _infer_version_truth(project_root),
        source_kind="inferred",
        source_path=None,
    )


def release_truth_status(version_truth: dict[str, Any], version: str | None) -> str:
    normalized = normalize_version(version)
    if not normalized:
        return "unknown"
    lines = version_truth.get("lines") if isinstance(version_truth.get("lines"), dict) else {}
    row = lines.get(normalized) if isinstance(lines, dict) else None
    if isinstance(row, dict):
        status = str(row.get("status", "") or "").strip()
        if status:
            return status
    if normalized == str(version_truth.get("current_runtime_release_line", "") or ""):
        return "current_runtime_release"
    if normalized in _normalize_version_list(version_truth.get("partial_runtime_supplement_lines")):
        return "planning_with_partial_runtime_supplement"
    if normalized in _normalize_version_list(version_truth.get("planning_lines")):
        return "planning_only"
    return "historical_release"


def current_runtime_release_version(project_root: Path) -> str | None:
    version = normalize_version(
        str(load_version_truth(project_root).get("current_runtime_release_line", "") or "")
    )
    if not version:
        return None
    versions = set(discover_versions(project_root))
    return version if not versions or version in versions else None


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
            version_truth = load_version_truth(project_root)
            docs_default = normalize_version(
                str(
                    version_truth.get("docs_default_line", "")
                    or version_truth.get("current_runtime_release_line", "")
                    or ""
                )
            )
            if docs_default:
                resolved = docs_default
                source = "version_truth"
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
            version_truth = load_version_truth(project_root)
            truth_runtime = normalize_version(str(version_truth.get("runtime_version", "") or ""))
            if truth_runtime:
                resolved = truth_runtime
                source = "version_truth"
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
    version_truth = load_version_truth(project_root)
    context_version_guard = build_context_version_guard(
        project_root,
        docs_version,
        resolved_version=resolved_docs,
        docs_source=docs_source,
    )
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
        "package_version": str(version_truth.get("package_version", "") or ""),
        "docs_default_line": str(version_truth.get("docs_default_line", "") or ""),
        "current_runtime_release_line": str(version_truth.get("current_runtime_release_line", "") or ""),
        "planning_lines": _normalize_version_list(version_truth.get("planning_lines")),
        "partial_runtime_supplement_lines": _normalize_version_list(
            version_truth.get("partial_runtime_supplement_lines")
        ),
        "release_truth_status": release_truth_status(version_truth, resolved_docs),
        "version_truth_source": str(version_truth.get("source_path", "") or ""),
        "version_truth_source_kind": str(version_truth.get("source_kind", "") or ""),
        "version_truth": version_truth,
        "context_version_guard": context_version_guard,
    }


def resolve_target_version(
    project_root: Path,
    requested: str | None,
    *,
    fallback: str = "v1.0.0",
) -> str:
    resolved = resolve_docs_version(project_root, requested, fallback=fallback)
    return resolved if isinstance(resolved, str) else resolved[0]
