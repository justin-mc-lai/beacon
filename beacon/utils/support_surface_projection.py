"""Shared explanation-layer projection for Beacon support surfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


_OPTIONAL_DERIVED_PATTERNS = (
    "requirement-clarity-{slug}.md",
    "revision-delta-{slug}.md",
    "implementation-plan-{slug}.md",
    "git-workflow-{slug}.md",
    "deterministic-implementation-contract-{slug}.md",
    "implementation-brief-{slug}.md",
    "qa-acceptance-brief-{slug}.md",
    "release-closure-brief-{slug}.md",
)

_DEPRECATED_TEMPLATE_PATTERNS = (
    "implementation-summary-{slug}.md",
    "technical-implementation-{slug}.md",
    "qa-acceptance-{slug}.md",
)


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except Exception:  # noqa: BLE001
        return str(path)


def _existing_refs(project_root: Path, candidates: list[Path]) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate.exists():
            continue
        ref = _rel(project_root, candidate)
        if ref in seen:
            continue
        seen.add(ref)
        refs.append(ref)
    return refs


def build_support_surface_projection(project_root: Path, *, version: str, feature: str = "") -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    docs_root = project_root / "docs" / "beacon" / resolved_version
    execution_root = docs_root / "execution"
    machine_execution_root = docs_root / ".machine" / "execution"
    archive_machine_root = docs_root / ".machine" / "archive"
    feature_name = str(feature or "").strip()
    slug = feature_slug(feature_name) if feature_name else ""

    required_human_refs = _existing_refs(
        project_root,
        [
            project_root / "docs" / "beacon" / "global-boundaries.md",
            execution_root / "index.md",
            execution_root / "architecture-blueprint.md",
        ],
    )
    optional_derived_refs = _existing_refs(
        project_root,
        [execution_root / pattern.format(slug=slug) for pattern in _OPTIONAL_DERIVED_PATTERNS if slug],
    )
    deprecated_template_refs = _existing_refs(
        project_root,
        [execution_root / pattern.format(slug=slug) for pattern in _DEPRECATED_TEMPLATE_PATTERNS if slug],
    )

    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "feature": feature_name,
        "support_mode": "explanation-layer",
        "primary_operator_doc_ref": _rel(project_root, execution_root / "index.md"),
        "artifact_taxonomy": {
            "canonical_envelope": {
                "class": "canonical_envelope",
                "role": "machine/source truth consumed by support surfaces",
                "default_root": _rel(project_root, machine_execution_root),
                "refs": _existing_refs(
                    project_root,
                    [
                        machine_execution_root,
                        archive_machine_root,
                    ],
                ),
            },
            "required_human_projection": {
                "class": "required_human_projection",
                "role": "human-facing explanation docs that operators should read first",
                "refs": required_human_refs,
            },
            "optional_derived_projection": {
                "class": "optional_derived_projection",
                "role": "feature-specific execution summaries that may exist but are not the default support entrypoint",
                "refs": optional_derived_refs,
            },
            "deprecated_template_artifact": {
                "class": "deprecated_template_artifact",
                "role": "legacy templates that should not expand by default in v1.3.9",
                "refs": deprecated_template_refs,
            },
        },
        "operator_surfaces": [
            {
                "surface": "help",
                "role": "next-step explanation over canonical delivery truth",
                "command_ref": 'beacon help --project-root <root> --version <version> --feature "<feature>" --json',
            },
            {
                "surface": "status",
                "role": "workflow/read-model explanation without creating execution templates",
                "command_ref": 'beacon status --project-root <root> --version <version> --feature "<feature>"',
            },
            {
                "surface": "doctor",
                "role": "diagnose and explain context/package/runtime drift against the same support read-model",
                "command_ref": 'beacon doctor advise --project-root <root> --version <version> --feature "<feature>" --json',
            },
            {
                "surface": "archive",
                "role": "archive governance explanation and readback, not a new lifecycle stage",
                "command_ref": 'beacon archive explain --project-root <root> --version <version> --json',
            },
        ],
    }
