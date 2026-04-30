"""Requirement clarity gates for v1.3.3+ freeze flows."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file
from beacon.utils.diagram_truth import diagram_truth_findings, load_feature_diagram_truth
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import (
    normalize_version,
    project_runtime_feature_enabled,
    release_line_key,
    resolve_runtime_version,
    resolve_target_version,
)
from beacon.utils.workflow_memory import append_lifecycle_event, record_stage_writeback, resolve_workflow_run_id

_SECTION_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_BACKTICK_PATH_RE = re.compile(r"`([^`\n]+)`")
_HEADING_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*[.)]?\s*")
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
_FREEZE_DELIVERABLE_SECTION_TITLES = {
    "冻结交付物",
    "freeze deliverables",
    "frozen deliverables",
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
            title = _normalize_heading_title(str(heading.group(2) or ""))
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


def _normalize_heading_title(title: str) -> str:
    text = str(title or "").strip().lower()
    return _HEADING_PREFIX_RE.sub("", text).strip()


def _extract_required_artifacts(path: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    if not path.exists():
        return artifacts

    lines = path.read_text(encoding="utf-8").splitlines()
    current_section = ""
    in_code_fence = False

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        heading = _SECTION_HEADING_RE.match(stripped)
        if heading:
            current_section = _normalize_heading_title(str(heading.group(2) or ""))
            continue

        if current_section not in _FREEZE_DELIVERABLE_SECTION_TITLES:
            continue
        if not stripped:
            continue
        if not (
            stripped.startswith(("-", "*", "+"))
            or stripped[0].isdigit()
            or "`" in stripped
        ):
            continue

        for match in _BACKTICK_PATH_RE.findall(stripped):
            relative = str(match or "").strip()
            if not relative or "/" not in relative:
                continue
            if not (
                relative.startswith("docs/")
                or relative.startswith("skills/")
                or relative.startswith(".beacon/")
            ):
                continue
            artifacts.append({"path": relative, "line": line_no})

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in artifacts:
        rel = str(item.get("path") or "").strip()
        if not rel or rel in seen:
            continue
        seen.add(rel)
        deduped.append(item)
    return deduped


def build_requirement_clarity_gate_payload(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    prd_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{feature_slug(feature)}.md"
    resolved_runtime = resolve_runtime_version(project_root, "auto")
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "runtime_version": resolved_runtime,
        "runtime_capability_line": "v1.3.3",
        "required": project_runtime_feature_enabled(
            project_root,
            "v1.3.3",
            docs_version=resolved_version,
            runtime_version=resolved_runtime,
        ),
        "reason_code": "",
        "blocked": False,
        "status": "pass",
        "findings": [],
        "report_json_path": str(requirement_clarity_json_path(project_root, resolved_version, feature).relative_to(project_root)),
        "report_markdown_path": str(requirement_clarity_markdown_path(project_root, resolved_version, feature).relative_to(project_root)),
        "state_path": str(requirement_clarity_state_path(project_root, feature).relative_to(project_root)),
    }
    if not payload["required"]:
        return payload

    findings: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    for path in _version_root(project_root, resolved_version, feature):
        scanned_files.append(str(path.relative_to(project_root)))
        findings.extend(_scan_file(path))

    diagram_truth = load_feature_diagram_truth(project_root, version=resolved_version, feature=feature)
    payload["diagram_truth"] = diagram_truth
    findings.extend(diagram_truth_findings(project_root, version=resolved_version, feature=feature))

    required_artifacts = _extract_required_artifacts(prd_path)
    payload["required_artifacts"] = [str(item.get("path") or "") for item in required_artifacts]
    for artifact in required_artifacts:
        relative = str(artifact.get("path") or "").strip()
        if not relative:
            continue
        if not (project_root / relative).exists():
            findings.append(
                {
                    "file": str(prd_path),
                    "line": int(artifact.get("line") or 0),
                    "kind": "missing_required_artifact",
                    "text": f"missing required artifact: {relative}",
                    "path": relative,
                }
            )

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


def requirement_clarity_state_path(project_root: Path, feature: str) -> Path:
    return project_root / ".beacon" / "state" / f"requirement-clarity-{feature_slug(feature)}.json"


def load_requirement_clarity_state(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(requirement_clarity_state_path(project_root, feature), {})
    return payload if isinstance(payload, dict) else {}


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


def write_requirement_clarity_writeback(
    project_root: Path,
    *,
    version: str,
    feature: str,
    gate_payload: dict[str, Any],
    report: dict[str, str],
    source: str = "freeze",
    run_id: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    state_path = requirement_clarity_state_path(project_root, feature)
    resolved_run_id = run_id or resolve_workflow_run_id(project_root, version=resolved_version, feature=feature) or ""
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "status": str(gate_payload.get("status", "") or ""),
        "blocked": bool(gate_payload.get("blocked", False)),
        "reason_code": str(gate_payload.get("reason_code", "") or ""),
        "report_json_path": str(report.get("json", "") or ""),
        "report_markdown_path": str(report.get("markdown", "") or ""),
        "finding_count": len(gate_payload.get("findings", []) if isinstance(gate_payload.get("findings"), list) else []),
        "run_id": resolved_run_id,
        "source": source,
        "written_at": now_iso(),
    }
    write_json(state_path, payload)

    if resolved_run_id:
        evidence_ref = [
            str(report.get("json", "") or ""),
            str(report.get("markdown", "") or ""),
            str(state_path.relative_to(project_root)),
        ]
        append_lifecycle_event(
            project_root,
            run_id=resolved_run_id,
            stage="requirement-review",
            event="clarity_synced",
            source=source,
            evidence_ref=evidence_ref,
            details={"status": payload["status"], "finding_count": payload["finding_count"]},
        )
        if not payload["blocked"]:
            record_stage_writeback(
                project_root,
                run_id=resolved_run_id,
                stage="requirement-review",
                feature=feature,
                evidence_ref=evidence_ref,
                status="cleared",
            )
    return {
        **payload,
        "state_path": str(state_path.relative_to(project_root)),
    }


def materialize_requirement_clarity(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    source: str = "doctor.sync-requirement-clarity",
    run_id: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    gate_payload = build_requirement_clarity_gate_payload(project_root, version=resolved_version, feature=feature)
    report = write_requirement_clarity_report(
        project_root,
        version=resolved_version,
        feature=feature,
        payload=gate_payload,
    )
    writeback = write_requirement_clarity_writeback(
        project_root,
        version=resolved_version,
        feature=feature,
        gate_payload=gate_payload,
        report=report,
        source=source,
        run_id=run_id,
    )
    return {
        "gate": gate_payload,
        "report": report,
        "writeback": writeback,
    }
