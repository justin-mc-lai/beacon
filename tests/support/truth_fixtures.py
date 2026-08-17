"""Minimal legacy requirement truth fixtures for tests that still need success paths."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.story_state import feature_slug


def seed_legacy_prd(project_root: Path, version: str, feature: str, *, body: str | None = None) -> Path:
    slug = feature_slug(feature)
    path = project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body or f"# PRD: {feature}\n", encoding="utf-8")
    return path


def seed_legacy_requirement_triple(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = feature_slug(feature)
    base = project_root / "docs" / "beacon" / version
    paths = {
        "prd": base / "prd" / f"{slug}.md",
        "user-story": base / "user-story" / f"{slug}.md",
        "test-case": base / "qa" / "test-cases" / f"{slug}.md",
    }
    for kind, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {kind}: {feature}\n", encoding="utf-8")
    return paths
