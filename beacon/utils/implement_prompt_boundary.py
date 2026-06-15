"""Frozen-truth prompt boundary checks for Beacon implement flows."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.change_surface import build_change_command
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_map import feature_package_authoritative
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version

_TRUTH_CONFLICT_PATTERNS = (
    r"忽略(?:已)?冻结(?:的)?\s*(?:需求|truth|真相|prd|user[- ]?story|test[- ]?case)",
    r"跳过(?:已)?冻结(?:的)?\s*(?:需求|test[- ]?case|qa|验收|ac)",
    r"不(?:按|按照|依据)(?:已)?冻结(?:的)?\s*(?:需求|prd|user[- ]?story|test[- ]?case|验收|ac)",
    r"以(?:这个|当前)?(?:提示|prompt)为准",
    r"override\s+(?:the\s+)?(?:frozen|prd|user\s*story|test\s*case)",
    r"ignore\s+(?:the\s+)?(?:frozen|prd|user\s*story|test\s*case)",
    r"skip\s+(?:qa|acceptance|test\s*case)",
    r"绕过(?:已)?冻结(?:的)?(?:需求|真相|prd|user[- ]?story|test[- ]?case|验收)",
)

_REQUIREMENT_CHANGE_PATTERNS = (
    r"(?:新增|增加|扩展|扩充|补充|调整|修改|改变).{0,12}(?:用户故事|user[- ]?story|需求|验收|ac|测试范围|test(?:-|\s)?scope|边界|scope|场景)",
    r"(?:new|add|expand|extend|adjust|change|modify).{0,20}(?:user\s*story|requirement|acceptance|ac|test\s*scope|scope|boundary|scenario)",
    r"需求变更",
    r"requirement\s+change",
    r"change\s+request",
)

_CLARIFICATION_PATTERNS = (
    r"澄清",
    r"核实",
    r"确认",
    r"clarif",
    r"confirm",
    r"verify",
    r"对齐",
    r"是否",
)


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def implement_prompt_boundary_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 3, 7)


def _frozen_refs(project_root: Path, *, version: str, feature: str) -> list[str]:
    slug = feature_slug(feature)
    base = project_root / "docs" / "beacon" / version
    if feature_package_authoritative(version):
        package_root = base / "features" / slug
        refs = [
            package_root / "truth.md",
            package_root / "tests.md",
            package_root / "tasks.md",
            package_root / "evidence.md",
        ]
    else:
        refs = [
            base / "prd" / f"{slug}.md",
            base / "user-story" / f"{slug}.md",
            base / "qa" / "test-cases" / f"{slug}.md",
        ]
    return [str(path.relative_to(project_root)) for path in refs]


def _match_patterns(prompt: str, patterns: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for pattern in patterns:
        if re.search(pattern, prompt, flags=re.IGNORECASE):
            out.append(pattern)
    return out


def _has_expected_beacon_scaffold(prompt: str) -> bool:
    normalized = str(prompt or "").lower()
    legacy_truth_scaffold = (
        "implement the scoped beacon feature" in normalized
        and "read beacon source of truth" in normalized
        and "implement only against the frozen prd, user-story, and test-case truth above" in normalized
    )
    package_truth_scaffold = (
        "import externally produced implementation evidence for the scoped beacon feature" in normalized
        and "read beacon source of truth" in normalized
        and "bind the imported evidence to the frozen feature package truth" in normalized
        and "implement only against the frozen feature package truth above" in normalized
    )
    return legacy_truth_scaffold or package_truth_scaffold


def evaluate_implement_prompt_boundary(
    project_root: Path,
    *,
    version: str,
    feature: str,
    host_prompt: str,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    prompt = str(host_prompt or "").strip()
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "required": implement_prompt_boundary_supported(resolved_version),
        "prompt": prompt,
        "classification": "",
        "blocked": False,
        "status": "not_required",
        "reason_code": "",
        "next_action": "",
        "recommended_command": "",
        "matched_signals": [],
        "frozen_refs": _frozen_refs(project_root, version=resolved_version, feature=feature),
    }
    if not payload["required"]:
        return payload
    if not prompt:
        payload["status"] = "not_provided"
        return payload

    normalized = prompt.lower()
    truth_conflict_hits = _match_patterns(normalized, _TRUTH_CONFLICT_PATTERNS)
    requirement_change_hits = _match_patterns(normalized, _REQUIREMENT_CHANGE_PATTERNS)

    if truth_conflict_hits:
        payload["classification"] = "truth_conflict"
        payload["blocked"] = True
        payload["status"] = "blocked"
        payload["reason_code"] = "implement_prompt_truth_conflict"
        payload["next_action"] = "beacon-change"
        payload["recommended_command"] = build_change_command(
            feature=feature,
            project_root=project_root,
            version=resolved_version,
            reason="implement-prompt-truth-conflict",
        )
        payload["matched_signals"] = truth_conflict_hits
        return payload

    if requirement_change_hits and not _has_expected_beacon_scaffold(prompt):
        payload["classification"] = "requirement_change"
        payload["blocked"] = True
        payload["status"] = "blocked"
        payload["reason_code"] = "implement_prompt_requirement_change"
        payload["next_action"] = "beacon-change"
        payload["recommended_command"] = build_change_command(
            feature=feature,
            project_root=project_root,
            version=resolved_version,
            reason="implement-prompt-requirement-change",
        )
        payload["matched_signals"] = requirement_change_hits
        return payload

    payload["classification"] = (
        "clarification_within_scope"
        if "?" in prompt or "？" in prompt or _match_patterns(normalized, _CLARIFICATION_PATTERNS)
        else "in_scope_implementation"
    )
    payload["status"] = "pass"
    return payload
