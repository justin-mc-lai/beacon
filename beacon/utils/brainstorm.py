"""Beacon built-in brainstorming sidecar helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.archive_governance import load_archive_read_model
from beacon.utils.diagram_truth import load_feature_diagram_truth
from beacon.utils.guidance_family import build_guidance_surface_projection
from beacon.utils.help_support import build_help_payload
from beacon.utils.project_metadata import metadata_machine_path, resolve_project_metadata_view
from beacon.utils.requirement_refs import requirement_truth_paths
from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_map import feature_package_authoritative
from beacon.utils.support_research_topology import (
    assert_support_write_topology,
    support_research_topology_supported,
    upsert_support_finding_section,
)
from beacon.utils.versioning import resolve_target_version


MODES = (
    "requirement-convergence",
    "project-evolution",
    "implementation-readiness",
    "scope-simplification",
)

_MODE_ALIASES = {
    "frozen-truth-delta": "implementation-readiness",
    "evolution-exploration": "project-evolution",
    "redundancy-pruning": "scope-simplification",
}

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
        requirement_refs = requirement_truth_paths(
            project_root,
            version=resolved_version,
            feature=feature,
            consumer="brainstorm",
        )
        refs.extend(
            [
                _material_entry(project_root, requirement_refs["prd"], required=True),
                _material_entry(project_root, requirement_refs["user_story"], required=True),
                _material_entry(project_root, requirement_refs["test_case"], required=True),
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


def _prompt_targets_external_context(prompt: str) -> bool:
    lowered = prompt.lower()
    external_markers = (
        "/users/",
        "shopxo",
        "rolo",
        "symphony",
        "oss-sync",
        "vibe-kanban",
        "third-party",
        "第三方",
        "供应商",
        "provider",
    )
    return any(marker in lowered for marker in external_markers)


def _path_safe_slug(text: str, *, fallback: str) -> str:
    slug = feature_slug(text)
    slug = re.sub(r"[\\\\/:]+", "-", slug)
    slug = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff._-]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-._")
    return slug or fallback


_FEATURE_CONTRACT_RE = re.compile(r"(?P<feature>[0-9a-zA-Z][0-9a-zA-Z._-]{6,}-(?:contract|feature|gate|closure|rebuild|retirement|boundary|guard))")


def infer_brainstorm_feature(prompt: str) -> str:
    text = str(prompt or "")
    quoted = re.findall(r"`([^`]+)`", text)
    for candidate in quoted + [text]:
        match = _FEATURE_CONTRACT_RE.search(candidate)
        if match:
            return match.group("feature").strip("-._")
    return ""


def compact_brainstorm_slug(prompt: str, *, fallback: str = "beacon-brainstorm") -> str:
    inferred = infer_brainstorm_feature(prompt)
    if inferred:
        return _path_safe_slug(inferred, fallback=fallback)[:72]
    text = str(prompt or "")
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"[/\\][^\s，。；;：:、]+", " ", text)
    text = re.sub(r"\b[a-zA-Z0-9_.-]+\.(?:md|json|py|sql|ts|tsx|js|jsx|yaml|yml)\b", " ", text)
    text = re.sub(r"\b(v\d+\.\d+\.\d+)\b", r"\1", text)
    chunks = re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z0-9][a-zA-Z0-9._-]*", text)
    stopwords = {
        "beacon",
        "brainstorm",
        "analysis",
        "analyze",
        "docs",
        "target",
        "goal",
        "input",
        "material",
        "materials",
    }
    selected: list[str] = []
    for chunk in chunks:
        lowered = chunk.lower()
        if lowered in stopwords:
            continue
        selected.append(chunk)
        if len(selected) >= 8:
            break
    return _path_safe_slug("-".join(selected), fallback=fallback)[:72]


def resolve_brainstorm_output_path(
    project_root: Path,
    *,
    version: str = "",
    prompt: str,
    feature: str = "",
    output: str = "",
) -> Path:
    if output:
        path = Path(output)
        return path if path.is_absolute() else project_root / path
    resolved_feature = feature.strip() or infer_brainstorm_feature(prompt)
    if resolved_feature and support_research_topology_supported(version):
        return project_root / "docs" / "beacon" / version / "research" / f"{feature_slug(resolved_feature)}.md"
    date = now_iso()[:10]
    if resolved_feature:
        slug = _path_safe_slug(resolved_feature, fallback="beacon-brainstorm")[:72]
        return project_root / "docs" / "brainstorms" / f"{date}-{slug}-brainstorm.md"
    slug = compact_brainstorm_slug(prompt, fallback="beacon-brainstorm")
    if _prompt_targets_external_context(prompt):
        return project_root / "docs" / "brainstorms" / "external" / f"{date}-{slug}.md"
    return project_root / "docs" / "brainstorms" / f"{date}-beacon-brainstorm-{slug}.md"


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
    canonical_mode = _MODE_ALIASES.get(mode, mode)
    if canonical_mode == "project-evolution":
        return (
            "Treat this as an evolution candidate. Capture options in brainstorm output first, then route accepted scope through beacon-prd or beacon-change.",
            "beacon-prd or beacon-change",
        )
    if canonical_mode == "implementation-readiness":
        return (
            "Use this only as a pre-implementation reasoning check. If frozen PRD/user-story/test-case drift is found, stop and route through beacon-change before implement.",
            "beacon-implement after drift is resolved",
        )
    if canonical_mode == "scope-simplification":
        return (
            "Cut any idea that does not preserve the frozen user outcome or acceptance evidence. Prefer the smallest requirement delta.",
            "beacon-change if scope changes are needed",
        )
    return (
        "Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.",
        "beacon-prd, beacon-user-story, beacon-test-case, or beacon-change",
    )


def _string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _load_convergence_contract(
    project_root: Path,
    *,
    version: str,
    feature: str,
    prompt: str,
    requirement_gap_digest: dict[str, Any] | None = None,
    brainstorm_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not feature.strip():
        return {}
    payload = build_help_payload(project_root, version=version, feature=feature)
    digest = requirement_gap_digest if isinstance(requirement_gap_digest, dict) else payload.get("requirement_gap_digest", {})
    hint = brainstorm_hint if isinstance(brainstorm_hint, dict) else payload.get("brainstorm_hint", {})
    change_loop = payload.get("change_loop", {}) if isinstance(payload.get("change_loop"), dict) else {}
    completeness = payload.get("requirement_completeness", {}) if isinstance(payload.get("requirement_completeness"), dict) else {}
    digest = digest if isinstance(digest, dict) else {}
    hint = hint if isinstance(hint, dict) else {}
    gap_dimensions = _string_list(digest.get("gap_dimensions"))
    focus_areas = _string_list(hint.get("focus_areas")) or _string_list(completeness.get("focus_areas"))
    open_questions = _string_list(hint.get("open_questions"))
    if not open_questions and focus_areas:
        open_questions = [f"补齐 `{item}` 是否会影响冻结后的验收闭环？" for item in focus_areas[:4]]
    has_followup = bool(digest.get("human_followup_needed")) or bool(change_loop.get("recommended", False))
    if not has_followup:
        recommended_route = str(digest.get("recommended_route") or "beacon-brainstorm")
        route_reason = str(digest.get("gap_summary") or "no requirement gap requires follow-up")
        target_artifact = ""
    elif bool(change_loop.get("recommended", False)) or str(digest.get("recommended_route") or "") == "beacon-change":
        recommended_route = "beacon-change"
        route_reason = str(change_loop.get("reason") or digest.get("gap_summary") or "change loop is required")
        target_artifact = ""
    else:
        prompt_text = f"{prompt} {' '.join(gap_dimensions)} {' '.join(focus_areas)}".lower()
        test_markers = ("test", "case", "coverage", "scenario", "ac", "验证", "测试", "覆盖", "场景")
        story_markers = ("story", "user", "role", "persona", "boundary", "exception", "用户", "角色", "边界", "异常", "状态机", "风险")
        if any(marker in prompt_text for marker in test_markers):
            target_artifact = "test-case"
            recommended_route = "beacon-test-case"
            route_reason = "gap is coverage-heavy and should be deepened in test-case"
        elif any(marker in prompt_text for marker in story_markers):
            target_artifact = "user-story"
            recommended_route = "beacon-user-story"
            route_reason = "gap is outcome/role-heavy and should be deepened in user-story"
        elif "coverage" in " ".join(gap_dimensions).lower() or "test" in " ".join(gap_dimensions).lower():
            target_artifact = "test-case"
            recommended_route = "beacon-test-case"
            route_reason = "gap dimensions indicate missing verification coverage"
        else:
            target_artifact = "user-story"
            recommended_route = "beacon-user-story"
            route_reason = "gap dimensions indicate missing product behavior or role detail"

    slug = feature_slug(feature)
    package_authority = feature_package_authoritative(version)
    default_truth_ref = f"docs/beacon/{version}/features/{slug}/truth.md" if package_authority else f"docs/beacon/{version}/prd/{slug}.md"
    source_truth_ref = str(digest.get("source_truth_ref") or default_truth_ref)
    if not target_artifact:
        writeback_target = ""
    elif package_authority and target_artifact == "test-case":
        writeback_target = f"docs/beacon/{version}/features/{slug}/tests.md"
    elif package_authority:
        writeback_target = f"docs/beacon/{version}/features/{slug}/truth.md"
    else:
        writeback_target = f"docs/beacon/{version}/{target_artifact}/{slug}.md"
    supplement_task = {
        "feature": feature,
        "version": version,
        "target_artifact": target_artifact,
        "writeback_target": writeback_target,
        "candidate_kind": "supplement_task" if target_artifact else "",
        "candidate_payload": {
            "gap_dimensions": gap_dimensions,
            "focus_areas": focus_areas,
            "open_questions": open_questions,
        }
        if target_artifact
        else {},
        "source_truth_ref": source_truth_ref,
        "rationale": route_reason,
        "confidence": "medium" if target_artifact else "low",
        "human_decision": "pending",
        "audit_trail_required": bool(target_artifact),
        "recommended_route": recommended_route,
    }
    return {
        "feature": feature,
        "version": version,
        "gap_digest": digest,
        "brainstorm_hint": hint,
        "change_loop": change_loop,
        "supplement_task": supplement_task,
        "route_reason": route_reason,
        "recommended_route": recommended_route,
    }


def run_beacon_brainstorm(
    project_root: Path,
    *,
    version: str,
    prompt: str,
    mode: str = "requirement-convergence",
    feature: str = "",
    output: str = "",
    requirement_gap_digest: dict[str, Any] | None = None,
    brainstorm_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    canonical_mode = _MODE_ALIASES.get(mode, mode)
    if canonical_mode not in MODES:
        raise ValueError(f"unsupported brainstorm mode: {mode}")
    effective_feature = feature.strip() or infer_brainstorm_feature(prompt)
    resolved_version = _resolve_brainstorm_version(project_root, version=version, feature=effective_feature, prompt=prompt)
    materials = collect_version_materials(project_root, version=resolved_version, feature=effective_feature)
    source_text = _joined_excerpts(materials)
    archive_boundary = load_archive_read_model(project_root, version=resolved_version, feature=effective_feature) if effective_feature else {}
    diagram_truth = load_feature_diagram_truth(project_root, version=resolved_version, feature=effective_feature) if effective_feature else {}
    resolved_metadata_view = resolve_project_metadata_view(project_root, version=resolved_version)
    metadata_path = metadata_machine_path(project_root)
    recommendation, next_route = _mode_recommendation(canonical_mode)
    convergence_contract = _load_convergence_contract(
        project_root,
        version=resolved_version,
        feature=effective_feature,
        prompt=prompt,
        requirement_gap_digest=requirement_gap_digest,
        brainstorm_hint=brainstorm_hint,
    )
    contract_gap_digest = convergence_contract.get("gap_digest", {}) if isinstance(convergence_contract.get("gap_digest"), dict) else {}
    contract_brainstorm_hint = convergence_contract.get("brainstorm_hint", {}) if isinstance(convergence_contract.get("brainstorm_hint"), dict) else {}
    contract_supplement_task = convergence_contract.get("supplement_task", {}) if isinstance(convergence_contract.get("supplement_task"), dict) else {}
    facts = [
        f"Beacon version material root is docs/beacon/{resolved_version}.",
        "This sidecar is read-only against Beacon requirement truth.",
        "Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.",
    ]
    if effective_feature:
        facts.append(f"Feature focus: {effective_feature}.")
    if effective_feature and isinstance((archive_boundary or {}).get("feature"), dict):
        archive_status = str((archive_boundary.get("feature") or {}).get("status", "") or "active")
        facts.append(f"Archive boundary status: {archive_status}.")
    if effective_feature and isinstance(diagram_truth, dict) and diagram_truth.get("required") and not diagram_truth.get("ready"):
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
    if contract_gap_digest.get("human_followup_needed"):
        facts.append(
            f"Convergence route resolved: {contract_supplement_task.get('recommended_route') or contract_gap_digest.get('recommended_route') or 'beacon-brainstorm'}."
        )
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
    output_path = resolve_brainstorm_output_path(project_root, version=resolved_version, prompt=prompt, feature=effective_feature, output=output)
    topology_gate = {}
    if effective_feature and support_research_topology_supported(resolved_version):
        topology_gate = assert_support_write_topology(
            project_root,
            version=resolved_version,
            feature=effective_feature,
            surface="beacon-brainstorm",
            actual_path=output_path,
        )
    assert_not_requirement_truth_path(output_path, project_root=project_root, version=resolved_version)
    human_closure_scaffold = _materialize_human_closure_scaffold(
        project_root,
        version=resolved_version,
        feature=effective_feature,
        canonical_mode=canonical_mode,
        diagram_truth=diagram_truth,
    )
    payload = {
        "schema_version": "1.0",
        "artifact": "beacon_brainstorm",
        "version": resolved_version,
        "mode": mode,
        "canonical_mode": canonical_mode,
        "prompt_summary": prompt.strip(),
        "feature": effective_feature,
        "feature_slug": feature_slug(effective_feature) if effective_feature else "",
        "feature_inferred": bool(effective_feature and not feature.strip()),
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
        "requirement_gap_digest": contract_gap_digest,
        "brainstorm_hint": contract_brainstorm_hint,
        "supplement_task": contract_supplement_task,
        "convergence_contract": convergence_contract,
        "human_closure_scaffold": human_closure_scaffold,
        "guidance_family": build_guidance_surface_projection(
            "brainstorm",
            current_loop_layer="challenge",
            missing_evidence=materials["missing_refs"],
            target_surface=str(
                contract_supplement_task.get("target_artifact")
                or contract_gap_digest.get("recommended_route")
                or ""
            ),
            recommended_route=str(
                contract_supplement_task.get("recommended_route")
                or contract_gap_digest.get("recommended_route")
                or next_route
            ),
        ),
        "converged_recommendation": recommendation,
        "next_route": "brainstorm closed" if not contract_supplement_task.get("target_artifact") and not contract_gap_digest.get("human_followup_needed") else next_route,
        "recommended_route": str(
            contract_supplement_task.get("recommended_route")
            or contract_gap_digest.get("recommended_route")
            or next_route
        ),
        "output_path": _rel(project_root, output_path),
        "support_write_topology": topology_gate,
        "generated_at": now_iso(),
    }
    if effective_feature and support_research_topology_supported(resolved_version):
        writeback = upsert_support_finding_section(
            project_root,
            version=resolved_version,
            feature=effective_feature,
            surface="beacon-brainstorm",
            finding_summary=str(payload.get("converged_recommendation") or prompt).strip(),
            source_refs=[
                str(item.get("path") or "")
                for item in payload.get("version_material_refs", [])
                if isinstance(item, dict) and str(item.get("path") or "").strip()
            ],
            route_decision=str(payload.get("recommended_route") or payload.get("next_route") or "beacon-brainstorm"),
        )
        payload["output_path"] = str(writeback.get("path") or payload["output_path"])
        payload["support_research_writeback"] = writeback
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_brainstorm_markdown(payload), encoding="utf-8")
    return payload


def _resolve_brainstorm_version(project_root: Path, *, version: str, feature: str, prompt: str) -> str:
    resolved = resolve_target_version(project_root, version)
    if str(version or "").strip() != "auto":
        return resolved
    feature_version = _extract_version_from_feature(feature) or _extract_version_from_prompt(prompt)
    if feature_version:
        return resolve_target_version(project_root, feature_version)
    return resolved


def _extract_version_from_feature(feature: str) -> str:
    match = re.search(r"v\d+\.\d+\.\d+", feature or "")
    return match.group(0) if match else ""


def _extract_version_from_prompt(prompt: str) -> str:
    match = re.search(r"v\d+\.\d+\.\d+", prompt or "")
    return match.group(0) if match else ""


def _feature_research_path(project_root: Path, *, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "research" / f"{feature_slug(feature)}.md"


def _feature_source_architecture_path(project_root: Path, *, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "source-architecture" / f"{feature_slug(feature)}.md"


def _render_research_closure_scaffold(*, version: str, feature: str, diagram_truth: dict[str, Any]) -> str:
    diagram_types = [str(item).strip() for item in (diagram_truth.get("diagram_types") or []) if str(item).strip()]
    state_axes = [str(item).strip() for item in (diagram_truth.get("state_axes") or []) if str(item).strip()]
    lines = [
        f"# Research Closure: {feature}",
        "",
        f"- version: `{version}`",
        f"- feature: `{feature}`",
        f"- diagram_types: {', '.join(diagram_types) or 'none'}",
        f"- state_axes: {', '.join(state_axes) or 'none'}",
        "",
        "## Architecture",
        "- Describe the participating modules, services, or bounded contexts for this feature.",
        "- State which layer owns the canonical write path and which surfaces are read-only projections.",
        "",
        "## Business Flow",
        "- Describe the trigger, major steps, branch points, and terminal outcomes for the business workflow.",
        "- Include the actor handoff or system handoff when responsibility changes.",
        "",
        "## State Machine",
        "- List the stable states, legal transitions, blocked transitions, and recovery transitions for this feature.",
        "- Explain how each declared state axis affects the permitted transitions.",
        "",
        "## Decision Priority",
        "- Explain which rule wins when eligibility, ownership, stale data, or guardrail conditions conflict.",
        "- Note the order in which the implementation and QA layers must evaluate the rules.",
        "",
        "## Open Questions",
        "- Confirm the exact branch conditions that separate the main business path from blocked paths.",
        "- Confirm the states and transitions that QA must treat as non-negotiable coverage targets.",
        "",
        "## Promotion Notes",
        "- Promote accepted decisions into PRD, user-story, test-case, and requirement_clarity inputs before freeze.",
        "",
    ]
    return "\n".join(lines)


def _render_source_architecture_scaffold(*, version: str, feature: str) -> str:
    return "\n".join(
        [
            f"# Source Architecture: {feature}",
            "",
            f"- version: `{version}`",
            f"- feature: `{feature}`",
            "",
            "## Runtime Placement",
            "- Describe where this feature enters the command/runtime surface and which modules own the long-lived behavior.",
            "",
            "## Write Path",
            "- Describe the canonical write path and the persistence or state updates that define the feature result.",
            "",
            "## Read Models And Projections",
            "- Describe the read-side surfaces, derived projections, or evidence artifacts that the feature updates.",
            "",
            "## Contract Boundaries",
            "- Describe the modules, services, or external systems that are in scope and the boundaries that remain out of scope.",
            "",
        ]
    ) + "\n"


def _materialize_human_closure_scaffold(
    project_root: Path,
    *,
    version: str,
    feature: str,
    canonical_mode: str,
    diagram_truth: dict[str, Any],
) -> dict[str, Any]:
    if not feature or canonical_mode != "requirement-convergence":
        return {"enabled": False, "created": [], "existing": []}

    created: list[str] = []
    existing: list[str] = []
    research_path = _feature_research_path(project_root, version=version, feature=feature)
    source_arch_path = _feature_source_architecture_path(project_root, version=version, feature=feature)

    if research_path.exists():
        existing.append(_rel(project_root, research_path))
    else:
        research_path.parent.mkdir(parents=True, exist_ok=True)
        research_path.write_text(
            _render_research_closure_scaffold(version=version, feature=feature, diagram_truth=diagram_truth),
            encoding="utf-8",
        )
        created.append(_rel(project_root, research_path))

    if source_arch_path.exists():
        existing.append(_rel(project_root, source_arch_path))
    else:
        source_arch_path.parent.mkdir(parents=True, exist_ok=True)
        source_arch_path.write_text(_render_source_architecture_scaffold(version=version, feature=feature), encoding="utf-8")
        created.append(_rel(project_root, source_arch_path))

    return {
        "enabled": True,
        "created": created,
        "existing": existing,
        "research_path": _rel(project_root, research_path),
        "source_architecture_path": _rel(project_root, source_arch_path),
    }


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
        f"- canonical_mode: `{payload.get('canonical_mode', '')}`",
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
    gap_digest = payload.get("requirement_gap_digest") if isinstance(payload.get("requirement_gap_digest"), dict) else {}
    brainstorm_hint = payload.get("brainstorm_hint") if isinstance(payload.get("brainstorm_hint"), dict) else {}
    supplement_task = payload.get("supplement_task") if isinstance(payload.get("supplement_task"), dict) else {}
    if gap_digest or brainstorm_hint or supplement_task:
        lines.extend(
            [
                "## convergence_contract",
                f"- recommended_route: `{payload.get('recommended_route', '')}`",
                f"- route_reason: `{(payload.get('convergence_contract', {}) or {}).get('route_reason', '') if isinstance(payload.get('convergence_contract'), dict) else ''}`",
                "",
            ]
        )
        if gap_digest:
            lines.extend(list_block("requirement_gap_digest", [f"{k}: {v}" for k, v in gap_digest.items()]))
        if brainstorm_hint:
            lines.extend(list_block("brainstorm_hint", [f"{k}: {v}" for k, v in brainstorm_hint.items()]))
        if supplement_task:
            lines.extend(list_block("supplement_task", [f"{k}: {v}" for k, v in supplement_task.items()]))
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
    human_closure_scaffold = payload.get("human_closure_scaffold") if isinstance(payload.get("human_closure_scaffold"), dict) else {}
    if human_closure_scaffold:
        lines.extend(
            [
                "## human_closure_scaffold",
                f"- enabled: `{bool(human_closure_scaffold.get('enabled', False))}`",
                f"- research_path: `{human_closure_scaffold.get('research_path', '')}`",
                f"- source_architecture_path: `{human_closure_scaffold.get('source_architecture_path', '')}`",
                "",
            ]
        )
        if isinstance(human_closure_scaffold.get("created"), list):
            lines.extend(list_block("human_closure_created", human_closure_scaffold.get("created", [])))
        if isinstance(human_closure_scaffold.get("existing"), list):
            lines.extend(list_block("human_closure_existing", human_closure_scaffold.get("existing", [])))
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
