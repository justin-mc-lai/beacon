"""Beacon built-in brainstorming sidecar helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.archive_governance import load_archive_read_model
from beacon.utils.diagram_truth import load_feature_diagram_truth
from beacon.utils.project_metadata import metadata_machine_path, resolve_project_metadata_view
from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


MODES = (
    "requirement-convergence",
    "project-evolution",
    "implementation-readiness",
    "scope-simplification",
)

_TRUTH_DIR_PARTS = (
    ("docs", "beacon", "{version}", "prd"),
    ("docs", "beacon", "{version}", "user-story"),
    ("docs", "beacon", "{version}", "qa", "test-cases"),
    ("docs", "beacon", "{version}", "prototype"),
    ("docs", "beacon", "{version}", ".machine"),
)


def _read_text(path: Path, *, max_chars: int = 6000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")[:max_chars]


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _material_entry(project_root: Path, path: Path, *, required: bool) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": _rel(project_root, path),
        "exists": exists,
        "required": required,
        "excerpt": _read_text(path) if exists else "",
    }


def collect_version_materials(project_root: Path, *, version: str, feature: str = "") -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    base = project_root / "docs" / "beacon" / resolved_version
    slug = feature_slug(feature) if feature else ""
    refs: list[dict[str, Any]] = [
        _material_entry(project_root, project_root / "docs" / "beacon" / "global-boundaries.md", required=True),
        _material_entry(project_root, base / "SUMMARY.md", required=False),
        _material_entry(project_root, base / "execution" / "index.md", required=False),
        _material_entry(project_root, base / "execution" / "architecture-blueprint.md", required=False),
    ]
    if slug:
        refs.extend(
            [
                _material_entry(project_root, base / "prd" / f"{slug}.md", required=True),
                _material_entry(project_root, base / "user-story" / f"{slug}.md", required=True),
                _material_entry(project_root, base / "qa" / "test-cases" / f"{slug}.md", required=True),
            ]
        )
    else:
        for folder in (base / "prd", base / "user-story", base / "qa" / "test-cases"):
            if folder.exists():
                refs.extend(_material_entry(project_root, path, required=False) for path in sorted(folder.glob("*.md")))
            else:
                refs.append(_material_entry(project_root, folder, required=False))
    missing_refs = [item["path"] for item in refs if item["required"] and not item["exists"]]
    return {
        "version": resolved_version,
        "feature": feature,
        "feature_slug": slug,
        "refs": refs,
        "missing_refs": missing_refs,
    }


def _joined_excerpts(materials: dict[str, Any]) -> str:
    chunks: list[str] = []
    for item in materials.get("refs", []):
        if not isinstance(item, dict) or not item.get("exists"):
            continue
        excerpt = str(item.get("excerpt") or "").strip()
        if excerpt:
            chunks.append(f"## {item.get('path')}\n{excerpt}")
    return "\n\n".join(chunks)


def _line_contains_any(text: str, words: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lowered = line.lower()
        if any(word in lowered for word in words):
            out.append(line[:220])
        if len(out) >= 8:
            break
    return out


def resolve_brainstorm_output_path(project_root: Path, *, prompt: str, output: str = "") -> Path:
    if output:
        path = Path(output)
        return path if path.is_absolute() else project_root / path
    date = now_iso()[:10]
    slug = feature_slug(prompt)[:80] or "beacon-brainstorm"
    return project_root / "docs" / "brainstorms" / f"{date}-{slug}.md"


def assert_not_requirement_truth_path(path: Path, *, project_root: Path, version: str) -> None:
    resolved = path.resolve()
    root = project_root.resolve()
    try:
        parts = resolved.relative_to(root).parts
    except ValueError:
        return
    for pattern in _TRUTH_DIR_PARTS:
        concrete = tuple(version if part == "{version}" else part for part in pattern)
        if len(parts) >= len(concrete) and parts[: len(concrete)] == concrete:
            raise ValueError("beacon-brainstorm refuses to write into frozen requirement truth paths")


def _mode_recommendation(mode: str) -> tuple[str, str]:
    if mode == "project-evolution":
        return (
            "Treat this as an evolution candidate. Capture options in brainstorm output first, then route accepted scope through beacon-prd or beacon-change.",
            "beacon-prd or beacon-change",
        )
    if mode == "implementation-readiness":
        return (
            "Use this only as a pre-implementation reasoning check. If frozen PRD/user-story/test-case drift is found, stop and route through beacon-change before implement.",
            "beacon-implement after drift is resolved",
        )
    if mode == "scope-simplification":
        return (
            "Cut any idea that does not preserve the frozen user outcome or acceptance evidence. Prefer the smallest requirement delta.",
            "beacon-change if scope changes are needed",
        )
    return (
        "Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.",
        "beacon-prd, beacon-user-story, beacon-test-case, or beacon-change",
    )


def run_beacon_brainstorm(
    project_root: Path,
    *,
    version: str,
    prompt: str,
    mode: str = "requirement-convergence",
    feature: str = "",
    output: str = "",
) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"unsupported brainstorm mode: {mode}")
    resolved_version = resolve_target_version(project_root, version)
    materials = collect_version_materials(project_root, version=resolved_version, feature=feature)
    source_text = _joined_excerpts(materials)
    archive_boundary = load_archive_read_model(project_root, version=resolved_version, feature=feature) if feature else {}
    diagram_truth = load_feature_diagram_truth(project_root, version=resolved_version, feature=feature) if feature else {}
    resolved_metadata_view = resolve_project_metadata_view(project_root, version=resolved_version)
    metadata_path = metadata_machine_path(project_root)
    recommendation, next_route = _mode_recommendation(mode)
    facts = [
        f"Beacon version material root is docs/beacon/{resolved_version}.",
        "This sidecar is read-only against Beacon requirement truth.",
        "Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.",
    ]
    if feature:
        facts.append(f"Feature focus: {feature}.")
    if feature and isinstance((archive_boundary or {}).get("feature"), dict):
        archive_status = str((archive_boundary.get("feature") or {}).get("status", "") or "active")
        facts.append(f"Archive boundary status: {archive_status}.")
    if feature and isinstance(diagram_truth, dict) and diagram_truth.get("required") and not diagram_truth.get("ready"):
        facts.append("Diagram truth layer is still incomplete for this complex feature.")
    topology_kind = str(resolved_metadata_view.get("topology_kind") or "").strip()
    if topology_kind:
        facts.append(f"Resolved project topology: {topology_kind}.")
    selected_service = str(resolved_metadata_view.get("selected_service") or "").strip()
    if selected_service:
        facts.append(f"Resolved execution service: {selected_service}.")
    selected_branch = str(resolved_metadata_view.get("selected_branch") or "").strip()
    if selected_branch:
        facts.append(f"Resolved canonical branch: {selected_branch}.")
    assumptions = [
        "The prompt may represent a requirement gap, an evolution idea, or implementation-risk question until mapped to frozen evidence.",
        "Any accepted requirement change must be routed through the Beacon requirement/change loop before implementation.",
    ]
    assumptions.extend(f"Missing required material: {path}" for path in materials["missing_refs"])
    first_principles = [
        "用户价值: identify the irreducible user outcome before proposing mechanism.",
        "证据约束: every implementation idea must trace back to frozen PRD/user-story/test-case evidence.",
        "闭环约束: if evidence is missing or changing, return to requirement/change routing instead of implementing.",
    ]
    socratic = [
        "What exact user outcome would fail if this idea is not implemented?",
        "Which frozen acceptance criterion proves this idea is required?",
        "What evidence would falsify this proposed direction?",
        "If this is an evolution, what is the smallest safe requirement delta?",
    ]
    cuts = [
        "Remove implementation mechanisms that cannot be tied to frozen acceptance evidence.",
        "Remove duplicate document-to-document reconciliation; use canonical Beacon truth or route a change.",
        "Remove broad roadmap speculation unless it produces a concrete next Beacon route.",
    ]
    evidence_lines = _line_contains_any(
        source_text,
        ("fr-", "ac-", "tc-", "non-goal", "boundary", "baseline", "brainstorm", "implement"),
    )
    output_path = resolve_brainstorm_output_path(project_root, prompt=prompt, output=output)
    assert_not_requirement_truth_path(output_path, project_root=project_root, version=resolved_version)
    payload = {
        "schema_version": "1.0",
        "artifact": "beacon_brainstorm",
        "version": resolved_version,
        "mode": mode,
        "prompt_summary": prompt.strip(),
        "feature": feature,
        "feature_slug": feature_slug(feature) if feature else "",
        "version_material_refs": [
            {key: item[key] for key in ("path", "exists", "required")}
            for item in materials["refs"]
            if isinstance(item, dict)
        ],
        "missing_refs": materials["missing_refs"],
        "confirmed_facts": facts,
        "assumptions_under_test": assumptions,
        "first_principles_breakdown": first_principles,
        "socratic_questions": socratic,
        "redundancy_cuts": cuts,
        "material_signals": evidence_lines,
        "archive_boundary": archive_boundary,
        "diagram_truth": diagram_truth,
        "resolved_metadata_view": resolved_metadata_view,
        "metadata_ref": _rel(project_root, metadata_path) if metadata_path.exists() else "",
        "converged_recommendation": recommendation,
        "next_route": next_route,
        "output_path": _rel(project_root, output_path),
        "generated_at": now_iso(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_brainstorm_markdown(payload), encoding="utf-8")
    return payload


def render_brainstorm_markdown(payload: dict[str, Any]) -> str:
    def list_block(title: str, values: list[Any]) -> list[str]:
        lines = [f"## {title}"]
        if not values:
            lines.append("- none")
        else:
            for value in values:
                if isinstance(value, dict):
                    status = "present" if value.get("exists") else "missing"
                    required = "required" if value.get("required") else "optional"
                    lines.append(f"- `{value.get('path', '')}` ({status}, {required})")
                else:
                    lines.append(f"- {value}")
        lines.append("")
        return lines

    lines = [
        "# Beacon Brainstorm",
        "",
        "## prompt_summary",
        str(payload.get("prompt_summary", "") or ""),
        "",
        f"- version: `{payload.get('version', '')}`",
        f"- mode: `{payload.get('mode', '')}`",
        f"- feature: `{payload.get('feature', '')}`",
        "",
    ]
    lines.extend(list_block("version_material_refs", payload.get("version_material_refs", [])))
    lines.extend(list_block("confirmed_facts", payload.get("confirmed_facts", [])))
    lines.extend(list_block("assumptions_under_test", payload.get("assumptions_under_test", [])))
    lines.extend(list_block("first_principles_breakdown", payload.get("first_principles_breakdown", [])))
    lines.extend(list_block("socratic_questions", payload.get("socratic_questions", [])))
    lines.extend(list_block("redundancy_cuts", payload.get("redundancy_cuts", [])))
    lines.extend(list_block("material_signals", payload.get("material_signals", [])))
    archive_boundary = payload.get("archive_boundary") if isinstance(payload.get("archive_boundary"), dict) else {}
    archive_feature = archive_boundary.get("feature") if isinstance(archive_boundary.get("feature"), dict) else {}
    if archive_feature:
        lines.extend(
            [
                "## archive_boundary",
                f"- status: `{archive_feature.get('status', 'active')}`",
                f"- reason: `{archive_feature.get('reason', '')}`",
                "",
            ]
        )
    diagram_truth = payload.get("diagram_truth") if isinstance(payload.get("diagram_truth"), dict) else {}
    if diagram_truth:
        lines.extend(
            [
                "## diagram_truth",
                f"- required: `{bool(diagram_truth.get('required', False))}`",
                f"- ready: `{bool(diagram_truth.get('ready', False))}`",
                f"- diagram_types: {', '.join(diagram_truth.get('diagram_types', [])) or 'none'}",
                f"- state_axes: {', '.join(diagram_truth.get('state_axes', [])) or 'none'}",
                "",
            ]
        )
    metadata_view = payload.get("resolved_metadata_view") if isinstance(payload.get("resolved_metadata_view"), dict) else {}
    metadata_ref = str(payload.get("metadata_ref", "") or "").strip()
    if metadata_ref or metadata_view:
        lines.extend(
            [
                "## project_metadata",
                f"- metadata_ref: `{metadata_ref or 'none'}`",
                f"- topology_kind: `{metadata_view.get('topology_kind', '')}`",
                f"- selected_service: `{metadata_view.get('selected_service', '')}`",
                f"- selected_branch: `{metadata_view.get('selected_branch', '')}`",
                "",
            ]
        )
    lines.extend(
        [
            "## converged_recommendation",
            str(payload.get("converged_recommendation", "") or ""),
            "",
            "## next_route",
            str(payload.get("next_route", "") or ""),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
