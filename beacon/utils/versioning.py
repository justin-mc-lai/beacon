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
_VERSION_SEMANTICS_CANONICAL = Path("beacon/version-semantics.json")
_ALLOW_CONTEXT_VERSION_DRIFT_ENV = "BEACON_ALLOW_CONTEXT_VERSION_DRIFT"
_RUNTIME_PROJECT_ROOT = Path(__file__).resolve().parents[2]


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


def runtime_feature_supported(version: str | None, *, runtime_version: str | None = None) -> bool:
    normalized = release_line_key(version) or normalize_version(version)
    if not normalized:
        return False
    resolved_runtime = normalize_version(runtime_version or __toolkit_version__) or "v0.0.0"
    if _version_key(resolved_runtime) >= _version_key(normalized):
        return True
    runtime_truth = load_version_truth(_RUNTIME_PROJECT_ROOT)
    status = release_truth_status(runtime_truth, normalized)
    return status in {"current_runtime_release", "planning_with_partial_runtime_supplement"}


def runtime_capability_lines() -> list[str]:
    runtime_truth = load_version_truth(_RUNTIME_PROJECT_ROOT)
    current_release = normalize_version(str(runtime_truth.get("current_runtime_release_line", "") or ""))
    current_match = _SEMVER.match(current_release or "")
    compatible_historical_lines: set[str] = set()
    if current_match:
        current_major, current_minor, _ = current_match.groups()
        lines_payload = runtime_truth.get("lines") if isinstance(runtime_truth.get("lines"), dict) else {}
        for version, row in lines_payload.items():
            normalized = normalize_version(str(version or "").strip())
            if not normalized or normalized == current_release:
                continue
            match = _SEMVER.match(normalized)
            if not match:
                continue
            major, minor, _patch = match.groups()
            status = str(row.get("status", "") or "").strip() if isinstance(row, dict) else ""
            # Keep same-minor historical release lines visible as runtime-compatible docs lanes.
            if status == "historical_release" and major == current_major and minor == current_minor:
                compatible_historical_lines.add(normalized)
    lines = {
        normalize_version(__toolkit_version__),
        normalize_version(str(runtime_truth.get("runtime_version", "") or "")),
        current_release,
        *(_normalize_version_list(runtime_truth.get("partial_runtime_supplement_lines"))),
        *compatible_historical_lines,
    }
    return [item for item in sorted({line for line in lines if line}, key=_version_key) if item]


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _default_version_semantics() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact": "beacon-version-semantics",
        "description": (
            "Canonical version semantics contract for Beacon. Consumers must resolve version meaning "
            "through beacon.utils.versioning rather than command-local interpretation."
        ),
        "fields": {
            "package_version": {
                "kind": "package",
                "meaning": "Installed Beacon package version.",
                "example": "1.2.0",
            },
            "runtime_version": {
                "kind": "runtime",
                "meaning": "Active Beacon runtime/toolkit line used by the CLI and managed context.",
                "example": "v1.2.0",
            },
            "docs_default_line": {
                "kind": "docs",
                "meaning": "Default docs line for docs-oriented commands when the caller uses auto/latest.",
                "example": "v1.2.0",
            },
            "current_runtime_release_line": {
                "kind": "release_truth",
                "meaning": "Beacon runtime line currently considered the formal runtime release truth.",
                "example": "v1.2.0",
            },
            "planning_lines": {
                "kind": "planning",
                "meaning": "Future docs lines opened for planning and not yet promoted to the current runtime release.",
                "example": ["v1.3.0"],
            },
            "partial_runtime_supplement_lines": {
                "kind": "supplement",
                "meaning": (
                    "Planning lines with bounded runtime supplements that still do not replace the current runtime release."
                ),
                "example": ["v1.2.1"],
            },
        },
        "status_values": {
            "historical_release": "A historical released line that is not the current runtime release.",
            "planning_only": "A planning line with docs/package planning but no accepted runtime promotion.",
            "planning_with_partial_runtime_supplement": (
                "A planning line with bounded runtime supplements that still does not replace the current runtime release."
            ),
            "current_runtime_release": "The current Beacon runtime release line.",
        },
        "resolver_contract": {
            "docs_target": "resolve_docs_version()",
            "runtime_target": "resolve_runtime_version()",
            "version_context": "describe_project_version_context()",
            "release_truth_status": "release_truth_status()",
        },
        "consumer_surfaces": ["ask", "help", "status", "doctor", "init", "version"],
        "rules": [
            "Do not conflate docs-target resolution with runtime-target resolution.",
            "Do not add overlapping aliases for existing version fields without updating this contract.",
            "Commands should expose version_context and version_semantics rather than reinterpreting raw fields.",
        ],
    }


def load_version_semantics(project_root: Path) -> dict[str, Any]:
    payload = _read_json_file(project_root / _VERSION_SEMANTICS_CANONICAL)
    merged = _default_version_semantics()

    for key in ("schema_version", "artifact", "description"):
        value = str(payload.get(key, "")).strip() if payload else ""
        if value:
            merged[key] = value

    for key in ("fields", "status_values", "resolver_contract"):
        if isinstance(payload.get(key), dict):
            base = merged.get(key, {})
            if isinstance(base, dict):
                merged[key] = {**base, **payload[key]}
            else:
                merged[key] = dict(payload[key])

    for key in ("consumer_surfaces", "rules"):
        values = payload.get(key)
        if isinstance(values, list) and values:
            merged[key] = [str(item) for item in values if str(item).strip()]

    artifact_path = project_root / _VERSION_SEMANTICS_CANONICAL
    merged["source_path"] = str(_VERSION_SEMANTICS_CANONICAL) if artifact_path.exists() else ""
    merged["source_kind"] = "canonical_file" if artifact_path.exists() else "default"
    return merged


def _render_semantics_example(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


_FIELD_KIND_LABELS = {
    "package": "包版本",
    "runtime": "运行版本",
    "docs": "文档版本",
    "release_truth": "发布真相",
    "planning": "规划版本",
    "supplement": "补充增强",
}

_FIELD_MEANING_ZH = {
    "package_version": "已安装 Beacon 包版本。",
    "runtime_version": "CLI 与受管上下文当前使用的 Beacon runtime/toolkit 版本线。",
    "docs_default_line": "当命令使用 auto/latest 解析文档目标时默认命中的文档线。",
    "current_runtime_release_line": "当前被视为正式 runtime 发布真相的 Beacon 版本线。",
    "planning_lines": "已开启规划但尚未提升为当前 runtime release 的未来文档线。",
    "partial_runtime_supplement_lines": "已有局部 runtime 增强、但仍未替代当前 runtime release 的规划版本线。",
}

_STATUS_VALUE_ZH = {
    "historical_release": "历史正式版本线，已不是当前 runtime release。",
    "planning_only": "仅规划中的版本线，已有 docs/package 规划但尚未成为 runtime release。",
    "planning_with_partial_runtime_supplement": "带局部 runtime 增强的规划版本线，但仍不是当前 runtime release。",
    "current_runtime_release": "当前 Beacon runtime 正式发布线。",
}

_RESOLVER_LABEL_ZH = {
    "docs_target": "文档目标解析",
    "runtime_target": "运行目标解析",
    "version_context": "统一版本上下文",
    "release_truth_status": "发布真相状态判断",
}

_CONSUMER_SURFACE_ZH = {
    "ask": "自然语言入口",
    "help": "阶段导航",
    "status": "状态面板",
    "doctor": "诊断与修复建议",
    "init": "项目初始化",
    "version": "版本规划",
}

_RULE_ZH = {
    "Do not conflate docs-target resolution with runtime-target resolution.": "不得把文档目标解析与运行目标解析混为一谈。",
    "Do not add overlapping aliases for existing version fields without updating this contract.": "未经更新本 contract，不得为现有版本字段新增语义重叠的别名。",
    "Commands should expose version_context and version_semantics rather than reinterpreting raw fields.": "命令应暴露统一的 version_context 与 version_semantics，而不是各自重解释原始字段。",
}


def render_version_semantics_markdown(semantics: dict[str, Any], *, version: str) -> str:
    version_text = normalize_version(version) or str(version or "").strip() or "<version>"
    lines = [
        "# Beacon 版本语义契约",
        "",
        f"- 文档线: `{version_text}`",
        "- 镜像源: `beacon/version-semantics.json`",
        "- 镜像规则: 本文档是机器可读版本语义 artifact 的人类可读中文镜像；两侧必须同步更新。",
        "",
        "## 目的",
        "",
        "Beacon 版本语义的统一中文说明入口。"
        " 机器侧以 `beacon/version-semantics.json` 为准，"
        "人类侧通过本镜像理解字段语义、状态含义、解析入口与使用规则。",
        "",
        "## 规范字段",
        "",
        "| 字段 | 类型 | 中文说明 | 示例 |",
        "| --- | --- | --- | --- |",
    ]
    fields = semantics.get("fields", {}) if isinstance(semantics.get("fields"), dict) else {}
    for field_name, payload in fields.items():
        if not isinstance(payload, dict):
            continue
        kind = str(payload.get("kind", "")).strip()
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{field_name}`",
                    _FIELD_KIND_LABELS.get(kind, kind),
                    _FIELD_MEANING_ZH.get(field_name, str(payload.get("meaning", "")).strip()),
                    f"`{_render_semantics_example(payload.get('example', ''))}`",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 状态值",
            "",
            "| 状态值 | 中文说明 |",
            "| --- | --- |",
        ]
    )
    status_values = semantics.get("status_values", {}) if isinstance(semantics.get("status_values"), dict) else {}
    for status_name, meaning in status_values.items():
        lines.append(f"| `{status_name}` | {_STATUS_VALUE_ZH.get(status_name, str(meaning).strip())} |")

    lines.extend(
        [
            "",
            "## 解析入口契约",
            "",
            "| 语义面 | 统一入口 |",
            "| --- | --- |",
        ]
    )
    resolver_contract = semantics.get("resolver_contract", {}) if isinstance(semantics.get("resolver_contract"), dict) else {}
    for key, value in resolver_contract.items():
        lines.append(f"| {_RESOLVER_LABEL_ZH.get(key, key)} | `{str(value).strip()}` |")

    lines.extend(["", "## 消费面", ""])
    consumer_surfaces = semantics.get("consumer_surfaces", []) if isinstance(semantics.get("consumer_surfaces"), list) else []
    if consumer_surfaces:
        lines.extend(
            f"- `{str(item).strip()}`：{_CONSUMER_SURFACE_ZH.get(str(item).strip(), str(item).strip())}"
            for item in consumer_surfaces
            if str(item).strip()
        )
    else:
        lines.append("- 无")

    lines.extend(["", "## 规则", ""])
    rules = semantics.get("rules", []) if isinstance(semantics.get("rules"), list) else []
    if rules:
        lines.extend(f"- {_RULE_ZH.get(str(item).strip(), str(item).strip())}" for item in rules if str(item).strip())
    else:
        lines.append("- 无")

    lines.extend(
        [
            "",
            "## 镜像同步契约",
            "",
            "1. `beacon/version-semantics.json` 是机器可读单一事实源。",
            "2. `docs/beacon/<version>/execution/version-semantics-contract.md` 是人类可读中文镜像。",
            "3. 后续变更必须同时更新两侧。",
            "4. 若 Markdown 镜像与 JSON artifact 漂移，测试必须失败。",
            "",
        ]
    )
    return "\n".join(lines)


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


def onboarding_runtime_capability_lines(project_root: Path) -> list[str]:
    payload = load_project_onboarding_state(project_root)
    return _normalize_version_list(payload.get("runtime_capability_lines"))


def project_runtime_feature_enabled(
    project_root: Path,
    capability_version: str | None,
    *,
    docs_version: str | None = None,
    runtime_version: str | None = None,
) -> bool:
    normalized_capability = release_line_key(capability_version) or normalize_version(capability_version)
    if not normalized_capability:
        return False
    normalized_docs_full = normalize_version(docs_version)
    normalized_docs = release_line_key(docs_version) or normalized_docs_full
    if (
        normalized_docs
        and normalized_docs_full == normalized_docs
        and _version_key(normalized_docs) >= _version_key(normalized_capability)
    ):
        return True
    if not runtime_feature_supported(normalized_capability, runtime_version=runtime_version):
        return False
    capability_lines = onboarding_runtime_capability_lines(project_root)
    if normalized_capability in capability_lines:
        return True
    onboarding_runtime = onboarding_runtime_version(project_root)
    if onboarding_runtime and _version_key(onboarding_runtime) >= _version_key(normalized_capability):
        return True
    return False


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
    runtime_truth = load_version_truth(_RUNTIME_PROJECT_ROOT)
    version_semantics = load_version_semantics(project_root)
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
        "runtime_capability_lines": runtime_capability_lines(),
        "runtime_truth_runtime_version": str(runtime_truth.get("runtime_version", "") or ""),
        "runtime_truth_current_release_line": str(runtime_truth.get("current_runtime_release_line", "") or ""),
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
        "version_semantics_source": str(version_semantics.get("source_path", "") or ""),
        "version_semantics_source_kind": str(version_semantics.get("source_kind", "") or ""),
        "version_semantics": version_semantics,
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
