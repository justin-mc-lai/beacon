"""Requirement clarity gates for v1.3.1+ freeze flows."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file
from beacon.utils.runtime import write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version

_SECTION_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_UNRESOLVED_SECTION_TITLES = {
    "open questions",
    "unresolved",
    "unresolved items",
    "pending clarifications",
    "clarifications needed",
    "未决项",
    "待澄清",
    "待确认",
    "疑问",
    "未澄清",
    "需求疑问",
}
_INLINE_MARKERS = (
    "TBD",
    "TODO",
    "???",
    "待补充",
    "待明确",
    "待确认",
    "未澄清",
    "待澄清",
    "需求不明",
    "需确认",
    "待定",
)


def requirement_clarity_gate_supported(version: str | None) -> bool:
    normalized_full = normalize_version(version) or "v0.0.0"
    normalized = release_line_key(version) or normalized_full
    if normalized_full != normalized:
        return False
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch)) >= (1, 3, 1)
    except Exception:  # noqa: BLE001
        return False


def _version_root(project_root: Path, version: str, feature: str) -> list[Path]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    base = project_root / "docs" / "beacon" / resolved_version
    return [
        base / "prd" / f"{slug}.md",
        base / "user-story" / f"{slug}.md",
    ]


def _scan_file(path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not path.exists():
        return findings
    lines = path.read_text(encoding="utf-8").splitlines()
    in_code_fence = False
    current_unresolved_section = ""

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        heading = _SECTION_HEADING_RE.match(stripped)
        if heading:
            title = str(heading.group(2) or "").strip().lower()
            current_unresolved_section = title if title in _UNRESOLVED_SECTION_TITLES else ""
            continue

        if current_unresolved_section and stripped:
            if stripped.startswith(("-", "*", "+")) or stripped[0].isdigit():
                findings.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "kind": "unresolved_section_item",
                        "section": current_unresolved_section,
                        "text": stripped,
                    }
                )
                continue

        upper = stripped.upper()
        if any(marker in upper for marker in _INLINE_MARKERS[:3]) or any(marker in stripped for marker in _INLINE_MARKERS[3:]):
            findings.append(
                {
                    "file": str(path),
                    "line": line_no,
                    "kind": "inline_marker",
                    "text": stripped,
                }
            )
            continue

        if stripped.startswith(("-", "*", "+")) and ("?" in stripped or "？" in stripped):
            findings.append(
                {
                    "file": str(path),
                    "line": line_no,
                    "kind": "question_bullet",
                    "text": stripped,
                }
            )
    return findings


def build_requirement_clarity_gate_payload(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "required": requirement_clarity_gate_supported(resolved_version),
        "reason_code": "",
        "blocked": False,
        "status": "pass",
        "findings": [],
    }
    if not payload["required"]:
        return payload

    findings: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    for path in _version_root(project_root, resolved_version, feature):
        scanned_files.append(str(path.relative_to(project_root)))
        findings.extend(_scan_file(path))

    payload["scanned_files"] = scanned_files
    payload["findings"] = findings
    if findings:
        payload["blocked"] = True
        payload["status"] = "blocked"
        payload["reason_code"] = "requirement_clarity_open"
        payload["recommended_action"] = "resolve_prd_and_user_story_open_questions_before_freeze"
    return payload


def requirement_clarity_json_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, f"requirement-clarity-{feature_slug(feature)}.json")


def requirement_clarity_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return human_execution_file(project_root, resolved_version, f"requirement-clarity-{feature_slug(feature)}.md")


def _render_requirement_clarity_markdown(payload: dict[str, Any]) -> str:
    findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
    lines = [
        "# Requirement Clarity Report",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- required: `{bool(payload.get('required', False))}`",
        f"- status: `{payload.get('status', '')}`",
        f"- reason_code: `{payload.get('reason_code', '')}`",
        "",
        "## Scanned Files",
    ]
    for item in payload.get("scanned_files", []) if isinstance(payload.get("scanned_files"), list) else []:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Findings")
    if findings:
        for item in findings:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- `{item.get('kind', '')}` {item.get('file', '')}:{item.get('line', '')} :: {item.get('text', '')}"
            )
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_requirement_clarity_report(
    project_root: Path,
    *,
    version: str,
    feature: str,
    payload: dict[str, Any],
) -> dict[str, str]:
    resolved_version = resolve_target_version(project_root, version)
    json_path = requirement_clarity_json_path(project_root, resolved_version, feature)
    markdown_path = requirement_clarity_markdown_path(project_root, resolved_version, feature)
    write_json(json_path, payload)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_requirement_clarity_markdown(payload), encoding="utf-8")
    return {
        "json": str(json_path.relative_to(project_root)),
        "markdown": str(markdown_path.relative_to(project_root)),
    }
