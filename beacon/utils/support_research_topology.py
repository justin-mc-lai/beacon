"""Read-only support research write topology for v1.4.9+."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import release_line_key, resolve_target_version, runtime_feature_supported


ORDINARY_SUPPORT_SURFACES = {
    "beacon-brainstorm": "Brainstorm",
    "beacon-context-engineering": "Context Engineering",
    "beacon-source-driven": "Source Driven",
    "beacon-doubt-review": "Doubt Review",
    "beacon-security-review": "Security Review",
    "beacon-performance-review": "Performance Review",
    "beacon-documentation-adr": "Documentation / ADR",
    "beacon-debug-recovery": "Debug Recovery",
    "beacon-ceo-review": "CEO Review",
    "beacon-design-review": "Design Review",
}

SURFACE_ALIASES = {
    "brainstorm": "beacon-brainstorm",
    "ceo-review": "beacon-ceo-review",
    "design-review": "beacon-design-review",
    "deep": "beacon-deep",
    "learn": "beacon-learn",
}


def support_research_topology_supported(version: str | None) -> bool:
    normalized = release_line_key(version) or ""
    if normalized:
        try:
            major, minor, patch = normalized.lstrip("v").split(".")
            if (int(major), int(minor), int(patch)) >= (1, 4, 9):
                return True
        except Exception:  # noqa: BLE001
            pass
    return runtime_feature_supported("v1.4.9")


def normalize_support_surface(surface: str) -> str:
    text = str(surface or "").strip()
    return SURFACE_ALIASES.get(text, text)


def support_surface_class(surface: str) -> str:
    normalized = normalize_support_surface(surface)
    if normalized in ORDINARY_SUPPORT_SURFACES:
        return "ordinary_support_review"
    if normalized == "beacon-deep":
        return "deep"
    if normalized == "beacon-learn":
        return "learning"
    return "unknown"


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def feature_research_path(project_root: Path, *, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / "research" / f"{feature_slug(feature)}.md"


def deep_artifact_root(project_root: Path, *, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / "deep" / feature_slug(feature)


def machine_deep_artifact_root(project_root: Path, *, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / ".machine" / "deep" / feature_slug(feature)


def learning_audit_path(project_root: Path, *, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / "learning" / f"{feature_slug(feature)}.md"


def _same_or_inside(path: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(path.resolve())
        return True
    except ValueError:
        return candidate.resolve() == path.resolve()


def resolve_support_write_topology(
    project_root: Path,
    *,
    version: str,
    feature: str,
    surface: str,
    actual_path: str | Path = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    normalized_surface = normalize_support_surface(surface)
    policy_class = support_surface_class(normalized_surface)
    supported = support_research_topology_supported(resolved_version)
    actual = Path(actual_path) if actual_path else None
    actual_abs = actual if actual is None or actual.is_absolute() else project_root / actual
    diagnostics: list[dict[str, Any]] = []

    expected_paths: list[Path] = []
    if policy_class == "ordinary_support_review":
        expected_paths = [feature_research_path(project_root, version=resolved_version, feature=feature)]
    elif policy_class == "deep":
        expected_paths = [
            deep_artifact_root(project_root, version=resolved_version, feature=feature),
            machine_deep_artifact_root(project_root, version=resolved_version, feature=feature),
        ]
    elif policy_class == "learning":
        expected_paths = [
            learning_audit_path(project_root, version=resolved_version, feature=feature),
            project_root / "docs" / "beacon" / resolved_version / "execution" / "beacon-learn-transaction.md",
            project_root / "docs" / "beacon" / resolved_version / ".machine" / "execution" / "beacon-learn-transaction.json",
        ]

    if supported:
        if not str(feature or "").strip():
            diagnostics.append({"reason_code": "support_topology_feature_missing"})
        if not normalized_surface or policy_class == "unknown":
            diagnostics.append({"reason_code": "support_topology_surface_unresolved", "source_skill": normalized_surface})
        if actual_abs is not None and expected_paths:
            matches = any(_same_or_inside(expected, actual_abs) for expected in expected_paths)
            if not matches:
                diagnostics.append(
                    {
                        "reason_code": "support_topology_actual_path_mismatch",
                        "source_skill": normalized_surface,
                        "expected_path": _rel(project_root, expected_paths[0]),
                        "actual_path": _rel(project_root, actual_abs),
                    }
                )

    return {
        "schema_version": "1.0",
        "supported": supported,
        "status": "blocked" if diagnostics else "pass",
        "blocked": bool(diagnostics),
        "reason_code": "support_write_topology_unresolved" if diagnostics else "",
        "policy_class": policy_class,
        "source_skill": normalized_surface,
        "version": resolved_version,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "expected_path": _rel(project_root, expected_paths[0]) if expected_paths else "",
        "expected_paths": [_rel(project_root, path) for path in expected_paths],
        "actual_path": _rel(project_root, actual_abs) if actual_abs is not None else "",
        "repair_route": "beacon-change-refreeze" if diagnostics else "",
        "diagnostics": diagnostics,
    }


def assert_support_write_topology(
    project_root: Path,
    *,
    version: str,
    feature: str,
    surface: str,
    actual_path: str | Path = "",
) -> dict[str, Any]:
    topology = resolve_support_write_topology(
        project_root,
        version=version,
        feature=feature,
        surface=surface,
        actual_path=actual_path,
    )
    if topology.get("blocked"):
        message = (
            f"support write topology blocked: source_skill={topology.get('source_skill')} "
            f"expected={topology.get('expected_path')} actual={topology.get('actual_path')}"
        )
        raise ValueError(message)
    return topology


def _heading_re(title: str) -> re.Pattern[str]:
    escaped = re.escape(title)
    return re.compile(rf"^##\s+{escaped}\s*$", flags=re.IGNORECASE | re.MULTILINE)


def _replace_or_append_h2(text: str, title: str, body: str) -> str:
    section = f"## {title}\n\n{body.strip()}\n"
    match = _heading_re(title).search(text)
    if not match:
        return text.rstrip() + "\n\n" + section
    next_match = re.search(r"^##\s+", text[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[: match.start()] + section + text[end:].lstrip("\n")


def _previous_research_ref(project_root: Path, *, version: str, feature: str) -> str:
    root = project_root / "docs" / "beacon"
    current = release_line_key(version) or version
    slug = feature_slug(feature)
    refs: list[tuple[tuple[int, int, int], Path]] = []
    for candidate in root.glob("v*.*.*"):
        if not candidate.is_dir() or candidate.name == current:
            continue
        try:
            key = tuple(int(part) for part in candidate.name.lstrip("v").split("."))
        except Exception:  # noqa: BLE001
            continue
        if key >= tuple(int(part) for part in current.lstrip("v").split(".")):
            continue
        path = candidate / "research" / f"{slug}.md"
        if path.exists():
            refs.append((key, path))
    if not refs:
        return ""
    return _rel(project_root, sorted(refs)[-1][1])


def ensure_feature_research_document(project_root: Path, *, version: str, feature: str) -> Path:
    path = feature_research_path(project_root, version=version, feature=feature)
    if path.exists():
        return path
    previous = _previous_research_ref(project_root, version=version, feature=feature)
    lines = [
        f"# Research: {feature}",
        "",
        f"**Feature**: `{feature}`",
        f"**Version**: `{resolve_target_version(project_root, version)}`",
        f"**Status**: `support-research`",
        "",
        "## Support Findings",
        "",
        "## Deep Summary",
        "",
        "## Learning Influence Summary",
        "",
        "## Route Decisions",
        "",
        "## Version Evolution Notes",
        "",
    ]
    if previous:
        lines.extend(
            [
                f"- previous_research: `{previous}`",
                "- carried_forward: pending operator review",
                "- superseded: none recorded",
                "",
            ]
        )
    lines.extend(["## Promotion Log", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def upsert_support_finding_section(
    project_root: Path,
    *,
    version: str,
    feature: str,
    surface: str,
    finding_summary: str,
    source_refs: list[str] | None = None,
    route_decision: str = "read-only route-only",
    material_effect: str = "read_only_route_only",
    adoption_status: str = "route_only",
    round_id: str = "",
) -> dict[str, Any]:
    topology = assert_support_write_topology(project_root, version=version, feature=feature, surface=surface)
    path = ensure_feature_research_document(project_root, version=version, feature=feature)
    text = path.read_text(encoding="utf-8")
    if not _heading_re("Support Findings").search(text):
        text = text.rstrip() + "\n\n## Support Findings\n"
    normalized_surface = normalize_support_surface(surface)
    title = ORDINARY_SUPPORT_SURFACES.get(normalized_surface, normalized_surface)
    timestamp = round_id or now_iso()
    refs = [str(item).strip() for item in (source_refs or []) if str(item).strip()]
    entry_lines = [
        f"#### Round {timestamp}",
        "",
        f"- source_skill: `{normalized_surface}`",
        f"- round_id: `{timestamp}`",
        f"- material_effect: `{material_effect}`",
        f"- adoption_status: `{adoption_status}`",
        f"- route_decision: {route_decision}",
        f"- finding_summary: {finding_summary.strip() or 'No finding summary provided.'}",
    ]
    if refs:
        entry_lines.append(f"- source_refs: {', '.join(f'`{ref}`' for ref in refs)}")
    entry = "\n".join(entry_lines) + "\n"
    subsection = re.search(rf"^###\s+{re.escape(title)}\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if subsection:
        next_h3 = re.search(r"^###\s+", text[subsection.end() :], flags=re.MULTILINE)
        end = subsection.end() + next_h3.start() if next_h3 else len(text)
        text = text[:end].rstrip() + "\n\n" + entry + text[end:]
    else:
        support_match = _heading_re("Support Findings").search(text)
        insert_at = support_match.end() if support_match else len(text)
        text = text[:insert_at].rstrip() + f"\n\n### {title}\n\n{entry}" + text[insert_at:]
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return {"path": _rel(project_root, path), "topology": topology}


def upsert_deep_summary_index(project_root: Path, *, version: str, feature: str, payload: dict[str, Any]) -> dict[str, Any]:
    topology = assert_support_write_topology(project_root, version=version, feature=feature, surface="beacon-deep")
    path = ensure_feature_research_document(project_root, version=version, feature=feature)
    artifact_root = deep_artifact_root(project_root, version=version, feature=feature)
    machine_root = machine_deep_artifact_root(project_root, version=version, feature=feature)
    body = "\n".join(
        [
            f"- source_skill: `beacon-deep`",
            f"- updated_at: `{now_iso()}`",
            f"- deep_artifact_root: `{_rel(project_root, artifact_root)}`",
            f"- machine_artifact_root: `{_rel(project_root, machine_root)}`",
            f"- deep_requirement_state: `{payload.get('deep_requirement_state', '')}`",
            f"- status: `{payload.get('status', '')}`",
            f"- route_decision: `{payload.get('verdict', '')}`",
            f"- release_supplement_ref: `{_rel(project_root, machine_root / 'release-supplement.json')}`",
            "- adoption_status: `route_only`",
        ]
    )
    text = path.read_text(encoding="utf-8")
    path.write_text(_replace_or_append_h2(text, "Deep Summary", body), encoding="utf-8")
    return {"path": _rel(project_root, path), "topology": topology}


def write_learning_audit(project_root: Path, *, version: str, feature: str, payload: dict[str, Any]) -> str:
    path = learning_audit_path(project_root, version=version, feature=feature)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Learning Audit: {feature}",
        "",
        f"- source_skill: `beacon-learn`",
        f"- version: `{resolve_target_version(project_root, version)}`",
        f"- feature: `{feature}`",
        f"- updated_at: `{now_iso()}`",
        f"- applied_count: `{len(payload.get('applied_learning') or [])}`",
        f"- stale_count: `{len(payload.get('stale_learning') or [])}`",
        f"- conflicting_count: `{len(payload.get('conflicting_learning') or [])}`",
        f"- suppressed_count: `{len(payload.get('suppressed_learning') or [])}`",
        "- policy: learning is advisory; frozen truth wins",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return _rel(project_root, path)


def upsert_learning_influence_summary(project_root: Path, *, version: str, feature: str, payload: dict[str, Any]) -> dict[str, Any]:
    topology = assert_support_write_topology(project_root, version=version, feature=feature, surface="beacon-learn")
    path = ensure_feature_research_document(project_root, version=version, feature=feature)
    audit_ref = write_learning_audit(project_root, version=version, feature=feature, payload=payload)
    body = "\n".join(
        [
            "- source_skill: `beacon-learn`",
            f"- updated_at: `{now_iso()}`",
            f"- learning_audit_ref: `{audit_ref}`",
            f"- applied_count: `{len(payload.get('applied_learning') or [])}`",
            f"- stale_count: `{len(payload.get('stale_learning') or [])}`",
            f"- conflicting_count: `{len(payload.get('conflicting_learning') or [])}`",
            f"- suppressed_count: `{len(payload.get('suppressed_learning') or [])}`",
            "- policy: learning is advisory; frozen truth wins",
        ]
    )
    text = path.read_text(encoding="utf-8")
    path.write_text(_replace_or_append_h2(text, "Learning Influence Summary", body), encoding="utf-8")
    return {"path": _rel(project_root, path), "learning_audit_ref": audit_ref, "topology": topology}


def support_topology_diagnostics(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    if not support_research_topology_supported(resolved_version):
        return {"schema_version": "1.0", "supported": False, "status": "not_required", "blocked": False, "diagnostics": []}
    slug = feature_slug(feature)
    research_path = feature_research_path(project_root, version=resolved_version, feature=feature)
    diagnostics: list[dict[str, Any]] = []
    expected_research = _rel(project_root, research_path)
    prd_ref = f"docs/beacon/{resolved_version}/prd/{slug}.md"
    user_story_ref = f"docs/beacon/{resolved_version}/user-story/{slug}.md"
    test_case_ref = f"docs/beacon/{resolved_version}/qa/test-cases/{slug}.md"

    brainstorm_root = project_root / "docs" / "brainstorms"
    if brainstorm_root.exists():
        for path in sorted(brainstorm_root.rglob("*.md")):
            rel = _rel(project_root, path)
            text = path.read_text(encoding="utf-8", errors="ignore")[:4000]
            feature_line_match = re.search(r"^- feature:\s*`([^`]*)`\s*$", text, flags=re.MULTILINE)
            declared_feature = feature_line_match.group(1).strip() if feature_line_match else ""
            explicit_feature_match = declared_feature == feature or slug in path.name
            canonical_truth_ref_match = any(ref in text for ref in (prd_ref, user_story_ref, test_case_ref))
            if explicit_feature_match or (declared_feature and canonical_truth_ref_match):
                diagnostics.append(
                    {
                        "reason_code": "support_topology_legacy_brainstorm_fallback",
                        "source_skill": "beacon-brainstorm",
                        "expected_path": expected_research,
                        "actual_path": rel,
                        "repair_route": "move finding into research feature Support Findings / Brainstorm section",
                    }
                )

    research_dir = research_path.parent
    if research_dir.exists():
        for path in sorted(research_dir.glob(f"{slug}-*.md")):
            if path == research_path:
                continue
            diagnostics.append(
                {
                    "reason_code": "support_topology_duplicate_research_sibling",
                    "source_skill": "unknown",
                    "expected_path": expected_research,
                    "actual_path": _rel(project_root, path),
                    "repair_route": "merge sibling findings into the feature research document",
                }
            )

    research_text = research_path.read_text(encoding="utf-8") if research_path.exists() else ""
    deep_root = deep_artifact_root(project_root, version=resolved_version, feature=feature)
    machine_deep_root = machine_deep_artifact_root(project_root, version=resolved_version, feature=feature)
    deep_ran = (deep_root.exists() and any(deep_root.glob("*.md"))) or (machine_deep_root.exists() and any(machine_deep_root.glob("*.json")))
    if deep_ran and "## Deep Summary" not in research_text:
        diagnostics.append(
            {
                "reason_code": "support_topology_deep_index_missing",
                "source_skill": "beacon-deep",
                "expected_path": expected_research,
                "actual_path": _rel(project_root, deep_root),
                "repair_route": "add Deep Summary index to feature research",
            }
        )
    if "deep_analysis_report" in research_text:
        diagnostics.append(
            {
                "reason_code": "support_topology_deep_detail_in_research",
                "source_skill": "beacon-deep",
                "expected_path": _rel(project_root, deep_root),
                "actual_path": expected_research,
                "repair_route": "move deep details to deep/<feature>/ and keep only research index",
            }
        )

    learning_path = learning_audit_path(project_root, version=resolved_version, feature=feature)
    learn_tx = project_root / "docs" / "beacon" / resolved_version / ".machine" / "execution" / "beacon-learn-transaction.json"
    learning_ran = learning_path.exists() or learn_tx.exists()
    if learning_ran and "## Learning Influence Summary" not in research_text:
        diagnostics.append(
            {
                "reason_code": "support_topology_learning_index_missing",
                "source_skill": "beacon-learn",
                "expected_path": expected_research,
                "actual_path": _rel(project_root, learning_path if learning_path.exists() else learn_tx),
                "repair_route": "add Learning Influence Summary to feature research",
            }
        )
    if "learning_candidates" in research_text or "applied_learning" in research_text:
        diagnostics.append(
            {
                "reason_code": "support_topology_learning_detail_in_research",
                "source_skill": "beacon-learn",
                "expected_path": _rel(project_root, learning_path),
                "actual_path": expected_research,
                "repair_route": "move raw learning candidates to learning audit or transaction",
            }
        )

    return {
        "schema_version": "1.0",
        "supported": True,
        "status": "blocked" if diagnostics else "pass",
        "blocked": bool(diagnostics),
        "reason_code": "support_write_topology_violation" if diagnostics else "",
        "diagnostics": diagnostics,
    }
