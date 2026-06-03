"""Package-aware requirement reference helpers."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.story_state import feature_slug
from beacon.utils.truth_map import feature_package_authoritative, resolve_truth_read_refs


def requirement_truth_paths(project_root: Path, *, version: str, feature: str, consumer: str) -> dict[str, Path]:
    """Return requirement truth paths for the active version's authority model."""

    slug = feature_slug(feature)
    if feature_package_authoritative(version):
        refs = resolve_truth_read_refs(
            project_root,
            version=version,
            feature=feature,
            consumer=consumer,
        )["requirement_refs"]
        truth = project_root / str(refs["truth"])
        tests = project_root / str(refs["tests"])
        return {
            "prd": truth,
            "user_story": truth,
            "user-story": truth,
            "test_case": tests,
            "test-case": tests,
            "truth": truth,
            "tests": tests,
            "tasks": project_root / str(refs["tasks"]),
            "evidence": project_root / str(refs["evidence"]),
        }
    base = project_root / "docs" / "beacon" / version
    return {
        "prd": base / "prd" / f"{slug}.md",
        "user_story": base / "user-story" / f"{slug}.md",
        "user-story": base / "user-story" / f"{slug}.md",
        "test_case": base / "qa" / "test-cases" / f"{slug}.md",
        "test-case": base / "qa" / "test-cases" / f"{slug}.md",
    }


def existing_requirement_truth_refs(project_root: Path, *, version: str, feature: str, consumer: str) -> list[Path]:
    refs = requirement_truth_paths(project_root, version=version, feature=feature, consumer=consumer)
    unique: list[Path] = []
    seen: set[Path] = set()
    for key in ("truth", "tests", "tasks", "evidence", "prd", "user_story", "test_case"):
        path = refs.get(key)
        if path is None or path in seen or not path.exists():
            continue
        seen.add(path)
        unique.append(path)
    return unique
