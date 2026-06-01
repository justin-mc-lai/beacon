"""Diagram truth admission and propagation helpers for v1.3.8."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version


DIAGRAM_TYPES: tuple[str, ...] = ("branch-flow", "state-machine", "decision-priority")
DEFAULT_STATE_AXES: tuple[str, ...] = ("relation", "sale", "ownership", "eligibility")
_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_BACKTICK_RE = re.compile(r"`([^`]+)`")
_COMPLEXITY_HINTS: tuple[str, ...] = (
    "复杂业务",
    "多状态轴",
    "多服务",
    "资格",
    "归属",
    "结算",
    "branch-flow",
    "state-machine",
    "decision-priority",
    "state axis",
    "state axes",
    "multi-state",
    "multi service",
    "eligibility",
    "ownership",
    "branch flow",
    "state machine",
    "decision priority",
)
_STATE_AXIS_TITLES: tuple[str, ...] = ("state axis", "state axes", "状态轴")
_BRANCH_FLOW_TITLES: tuple[str, ...] = ("branch-flow", "branch flow", "分支流")
_STATE_MACHINE_TITLES: tuple[str, ...] = ("state-machine", "state machine", "状态机")
_DECISION_PRIORITY_TITLES: tuple[str, ...] = ("decision-priority", "decision priority", "决策优先级")


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def diagram_truth_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 3, 8)


def normalize_diagram_types(values: list[str] | tuple[str, ...] | None) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    for value in values:
        text = str(value or "").strip().lower()
        if text in {"branch flow", "branch_flow"}:
            text = "branch-flow"
        elif text in {"state machine", "state_machine"}:
            text = "state-machine"
        elif text in {"decision priority", "decision_priority"}:
            text = "decision-priority"
        if text in DIAGRAM_TYPES and text not in out:
            out.append(text)
    return out


def normalize_state_axes(values: list[str] | tuple[str, ...] | None) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    for value in values:
        text = str(value or "").strip().lower()
        if not text:
            continue
        if text not in out:
            out.append(text)
    return out


def render_diagram_truth_section(*, include_diagrams: list[str], state_axes: list[str]) -> str:
    diagram_types = normalize_diagram_types(include_diagrams)
    axes = normalize_state_axes(state_axes)
    if not diagram_types and not axes:
        return ""
    lines = [
        "",
        "## Diagram Truth Layer",
        "",
        "### Diagram Types",
    ]
    if diagram_types:
        lines.extend(f"- `{item}`" for item in diagram_types)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "### State Axes",
        ]
    )
    if axes:
        lines.extend(f"- `{item}`" for item in axes)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "### Propagation Contract",
            "- Diagram truth must stay explicit through freeze readiness, implementation planning, and QA coverage.",
            "- State axes must not be silently compressed into one implicit status field.",
            "- User-story AC must declare which state axis transitions they cover.",
            "- Test-case coverage must declare which diagram branches they cover.",
            "",
        ]
    )
    return "\n".join(lines)


def _read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _extract_axes_from_line(line: str) -> list[str]:
    lowered = str(line or "").strip().lower()
    values: list[str] = []
    for token in _BACKTICK_RE.findall(line):
        normalized = str(token or "").strip().lower()
        if normalized:
            values.append(normalized)
    for axis in DEFAULT_STATE_AXES:
        if axis in lowered:
            values.append(axis)
    if ":" in line:
        tail = line.split(":", 1)[1]
        for chunk in re.split(r"[,/|]", tail):
            token = str(chunk or "").strip().lower().strip("`")
            if token and re.fullmatch(r"[a-z][a-z0-9_-]{1,40}", token):
                values.append(token)
    return normalize_state_axes(values)


def _extract_markdown_lines(text: str) -> dict[str, list[str]]:
    lines = text.splitlines()
    current_heading = ""
    buckets: dict[str, list[str]] = {
        "branch-flow": [],
        "state-machine": [],
        "decision-priority": [],
        "state-axes": [],
    }
    for raw in lines:
        line = str(raw or "").rstrip()
        stripped = line.strip()
        heading = _HEADING_RE.match(stripped)
        if heading:
            current_heading = str(heading.group(2) or "").strip().lower()
            continue
        if not stripped:
            continue
        lowered = stripped.lower()
        if any(token in lowered for token in _BRANCH_FLOW_TITLES) or any(token in current_heading for token in _BRANCH_FLOW_TITLES):
            buckets["branch-flow"].append(stripped)
        if any(token in lowered for token in _STATE_MACHINE_TITLES) or any(token in current_heading for token in _STATE_MACHINE_TITLES):
            buckets["state-machine"].append(stripped)
        if any(token in lowered for token in _DECISION_PRIORITY_TITLES) or any(token in current_heading for token in _DECISION_PRIORITY_TITLES):
            buckets["decision-priority"].append(stripped)
        if any(token in lowered for token in _STATE_AXIS_TITLES) or any(token in current_heading for token in _STATE_AXIS_TITLES):
            buckets["state-axes"].append(stripped)
    return buckets


def parse_diagram_truth(
    *,
    version: str,
    prd_text: str,
    user_story_text: str = "",
) -> dict[str, Any]:
    supported = diagram_truth_supported(version)
    combined = "\n".join([prd_text, user_story_text]).strip()
    lowered = combined.lower()
    buckets = _extract_markdown_lines(combined)

    diagram_types = normalize_diagram_types(
        [
            *(["branch-flow"] if buckets["branch-flow"] or "branch-flow" in lowered or "branch flow" in lowered else []),
            *(["state-machine"] if buckets["state-machine"] or "state-machine" in lowered or "state machine" in lowered else []),
            *(
                ["decision-priority"]
                if buckets["decision-priority"] or "decision-priority" in lowered or "decision priority" in lowered
                else []
            ),
        ]
    )

    if buckets["state-axes"]:
        state_axes = normalize_state_axes(
            [
                axis
                for line in buckets["state-axes"]
                for axis in _extract_axes_from_line(line)
            ]
        )
    else:
        state_axes = normalize_state_axes(
            [
                axis
                for axis in DEFAULT_STATE_AXES
                if axis in lowered and any(marker in lowered for marker in _STATE_AXIS_TITLES + ("多状态轴",))
            ]
        )

    complexity_signals = [
        hint
        for hint in _COMPLEXITY_HINTS
        if hint in lowered
    ]
    requires_diagram_truth = supported and bool(
        complexity_signals
        or len(state_axes) >= 2
        or "complex" in lowered
        or "复杂" in lowered
    )
    missing_diagram_types = [item for item in DIAGRAM_TYPES if requires_diagram_truth and item not in diagram_types]
    missing_state_axes = requires_diagram_truth and not state_axes
    ready = supported and (not requires_diagram_truth or (not missing_diagram_types and not missing_state_axes))

    review_gates: list[str] = []
    qa_hints: list[str] = []
    if "branch-flow" in diagram_types:
        review_gates.append("implementation must cover the declared branch-flow split points")
        qa_hints.append("cover primary and alternate branch-flow paths")
    if "state-machine" in diagram_types:
        review_gates.append("implementation must preserve the declared state-machine transitions")
        qa_hints.append("cover state transitions, illegal transitions, and recovery paths")
    if "decision-priority" in diagram_types:
        review_gates.append("implementation must preserve decision-priority ordering")
        qa_hints.append("cover conflicting conditions using declared decision priority")
    if state_axes:
        axis_labels = ", ".join(state_axes)
        review_gates.append(f"implementation must keep state axes explicit: {axis_labels}")
        qa_hints.append(f"cover axis combinations across: {axis_labels}")

    return {
        "schema_version": "1.0",
        "version": version,
        "supported": supported,
        "required": requires_diagram_truth,
        "ready": ready,
        "diagram_types": diagram_types,
        "state_axes": state_axes,
        "missing_diagram_types": missing_diagram_types,
        "missing_state_axes": missing_state_axes,
        "complexity_signals": complexity_signals,
        "review_gates": review_gates,
        "qa_coverage_hints": qa_hints,
        "evidence_lines": {
            key: values[:8]
            for key, values in buckets.items()
            if values
        },
        "generated_at": now_iso(),
    }


def load_feature_diagram_truth(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    prd_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{slug}.md"
    user_story_path = project_root / "docs" / "beacon" / resolved_version / "user-story" / f"{slug}.md"
    payload = parse_diagram_truth(
        version=resolved_version,
        prd_text=_read_text(prd_path),
        user_story_text=_read_text(user_story_path),
    )
    payload.update(
        {
            "feature": feature,
            "feature_slug": slug,
            "prd_ref": str(prd_path.relative_to(project_root)),
            "user_story_ref": str(user_story_path.relative_to(project_root)),
        }
    )
    return payload


def diagram_truth_findings(project_root: Path, *, version: str, feature: str) -> list[dict[str, Any]]:
    payload = load_feature_diagram_truth(project_root, version=version, feature=feature)
    findings: list[dict[str, Any]] = []
    if not payload.get("supported"):
        return findings
    if not payload.get("required"):
        return findings
    prd_ref = str(payload.get("prd_ref", "") or "")
    if payload.get("missing_diagram_types"):
        findings.append(
            {
                "file": prd_ref,
                "line": 1,
                "kind": "diagram_truth_missing",
                "text": "missing diagram truth types: " + ", ".join(payload.get("missing_diagram_types", [])),
            }
        )
    if payload.get("missing_state_axes"):
        findings.append(
            {
                "file": prd_ref,
                "line": 1,
                "kind": "state_axis_missing",
                "text": "complex feature requires explicit state axes before freeze",
            }
        )
    return findings
