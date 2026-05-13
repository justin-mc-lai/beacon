"""v1.4.5 docs semantics and progressive materialization contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.versioning import normalize_version, resolve_target_version


SEMANTIC_LAYERS = (
    "context",
    "truth",
    "guidance",
    "delivery",
    "evidence",
    ".machine",
)

_SURFACE_TO_LAYER = {
    "prd": "truth",
    "user-story": "truth",
    "test-case": "truth",
    "change": "truth",
    "ceo-review": "guidance",
    "brainstorm": "guidance",
    "design-review": "guidance",
    "deep": "guidance",
    "prototype": "delivery",
    "implement": "delivery",
    "qa": "evidence",
    "release": "evidence",
    ".machine": ".machine",
}


def semantic_layer_for_surface(surface: str) -> str:
    return _SURFACE_TO_LAYER.get(str(surface or "").strip(), "")


def build_docs_structure_contract(*, version: str) -> dict[str, Any]:
    resolved_version = normalize_version(version) or str(version or "").strip()
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "semantic_layers": list(SEMANTIC_LAYERS),
        "surface_layer_mapping": {
            "truth": ["prd", "user-story", "test-case", "change"],
            "guidance": ["ceo-review", "brainstorm", "design-review", "deep"],
            "delivery": ["prototype", "implement"],
            "evidence": ["qa", "release"],
            ".machine": [".machine"],
        },
        "policies": {
            "paired_human_machine_projection_default": False,
            "machine_layer_role": "projection_only",
            "historical_versions_compatible": True,
            "progressive_materialization_default": True,
            "eager_full_tree_creation": False,
        },
        "preferred_roots": {
            "truth": f"docs/beacon/{resolved_version}/truth/",
            "guidance": f"docs/beacon/{resolved_version}/guidance/",
            "delivery": f"docs/beacon/{resolved_version}/delivery/",
            "evidence": f"docs/beacon/{resolved_version}/evidence/",
            ".machine": f"docs/beacon/{resolved_version}/.machine/",
        },
        "compatibility_projection_roots": {
            "truth": [
                f"docs/beacon/{resolved_version}/prd/",
                f"docs/beacon/{resolved_version}/user-story/",
                f"docs/beacon/{resolved_version}/qa/test-cases/",
                f"docs/beacon/{resolved_version}/change/",
            ],
            "guidance": [
                f"docs/beacon/{resolved_version}/execution/",
                "docs/brainstorms/",
            ],
            "delivery": [
                f"docs/beacon/{resolved_version}/execution/",
                f"docs/beacon/{resolved_version}/prototype/",
            ],
            "evidence": [
                f"docs/beacon/{resolved_version}/release/",
                ".beacon/evidence/",
            ],
        },
    }


def active_materialization_roots(
    project_root: Path,
    *,
    version: str,
    feature: str = "",
) -> dict[str, list[str]]:
    resolved_version = resolve_target_version(project_root, version)
    contract = build_docs_structure_contract(version=resolved_version)
    roots: dict[str, list[str]] = {layer: [] for layer in SEMANTIC_LAYERS}
    base = project_root / "docs" / "beacon" / resolved_version
    slug = str(feature or "").strip()

    if (base / "prd").exists() or (base / "user-story").exists() or (base / "qa" / "test-cases").exists() or (base / "change").exists():
        roots["truth"] = list(contract["compatibility_projection_roots"]["truth"])
    if (base / "execution").exists() or (project_root / "docs" / "brainstorms").exists():
        roots["guidance"] = list(contract["compatibility_projection_roots"]["guidance"])
    if (base / "prototype").exists() or (base / "execution").exists():
        roots["delivery"] = list(contract["compatibility_projection_roots"]["delivery"])
    release_root = base / "release"
    release_files = [path for path in release_root.glob("*") if path.is_file()] if release_root.exists() else []
    release_stub_name = f"{resolved_version}.md"
    has_substantive_release_surface = bool(
        [path for path in release_files if path.name != release_stub_name]
    ) or (release_root / release_stub_name).exists() and len(release_files) > 1
    if has_substantive_release_surface or (project_root / ".beacon" / "evidence").exists():
        roots["evidence"] = list(contract["compatibility_projection_roots"]["evidence"])
    if (base / ".machine").exists():
        roots[".machine"] = [contract["preferred_roots"][".machine"]]
    if base.exists():
        roots["context"] = [f"docs/beacon/{resolved_version}/"]
    if slug and not any(roots.values()):
        roots["context"] = [f"docs/beacon/{resolved_version}/"]
    return roots
