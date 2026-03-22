"""Coverage metrics helpers for Story/AC/TC execution traceability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_qa_dir, qa_docs_dir, uses_machine_surface
from beacon.utils.versioning import resolve_target_version


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def _story_files(project_root: Path, version: str, feature: str | None = None) -> list[Path]:
    roots = [
        project_root / "docs" / "beacon" / version / "user-story",
    ]
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        out.extend(root.glob("*.md"))
    if feature:
        target = _slug(feature)
        out = [p for p in out if p.stem == target]
    # de-duplicate by filename
    unique: dict[str, Path] = {}
    for path in out:
        unique[path.name] = path
    return sorted(unique.values(), key=lambda p: p.name)


def _matrix_files(project_root: Path, version: str, feature: str | None = None) -> list[Path]:
    roots = []
    if uses_machine_surface(version):
        roots.append(machine_qa_dir(project_root, version))
    roots.append(qa_docs_dir(project_root, version))
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        out.extend(root.glob("*.ac-test-matrix.json"))
    if feature:
        target = _slug(feature)
        out = [p for p in out if p.name == f"{target}.ac-test-matrix.json"]
    unique: dict[str, Path] = {}
    for path in out:
        unique.setdefault(path.name, path)
    return sorted(unique.values(), key=lambda p: p.name)


def compute_coverage_metrics(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str | None = None,
) -> dict[str, Any]:
    """Compute story/ac/tc coverage metrics from docs + evidence artifacts."""
    ver = resolve_target_version(project_root, version)
    feature_filter = _slug(feature or "")

    story_files = _story_files(project_root, ver, feature=feature_filter or None)
    planned_story = len(story_files)
    story_slugs = {p.stem for p in story_files}

    implementation_dir = project_root / ".beacon" / "state"
    impl_markers = list(implementation_dir.glob("implementation-*.json")) if implementation_dir.exists() else []
    impl_slugs = {p.stem.replace("implementation-", "", 1) for p in impl_markers}
    if feature_filter:
        impl_slugs = {x for x in impl_slugs if x == feature_filter}
    implemented_story = len(story_slugs & impl_slugs) if story_slugs else 0

    matrix_files = _matrix_files(project_root, ver, feature=feature_filter or None)
    total_tc = 0
    executed_tc = 0
    ac_all: set[str] = set()
    ac_tested: set[str] = set()
    matrix_errors: list[str] = []

    for matrix in matrix_files:
        try:
            payload = json.loads(matrix.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            matrix_errors.append(str(matrix))
            continue
        entries = payload.get("entries")
        if not isinstance(entries, list):
            matrix_errors.append(str(matrix))
            continue
        for item in entries:
            if not isinstance(item, dict):
                continue
            ac_id = str(item.get("ac_id", "")).strip()
            tc_id = str(item.get("tc_id", "")).strip()
            evidence_path = str(item.get("evidence_path", "")).strip()
            if not tc_id:
                continue
            total_tc += 1
            if ac_id:
                ac_all.add(ac_id)
            if not evidence_path:
                continue
            p = Path(evidence_path)
            evidence_file = p if p.is_absolute() else project_root / p
            if evidence_file.exists():
                executed_tc += 1
                if ac_id:
                    ac_tested.add(ac_id)

    total_ac = len(ac_all)
    tested_ac = len(ac_tested)

    story_coverage = _safe_ratio(implemented_story, planned_story)
    ac_coverage = _safe_ratio(tested_ac, total_ac)
    tc_coverage = _safe_ratio(executed_tc, total_tc)

    full_coverage = (
        planned_story > 0
        and total_ac > 0
        and total_tc > 0
        and story_coverage >= 1.0
        and ac_coverage >= 1.0
        and tc_coverage >= 1.0
    )

    return {
        "version": ver,
        "feature": feature_filter,
        "planned_story": planned_story,
        "implemented_story": implemented_story,
        "story_coverage": story_coverage,
        "total_ac": total_ac,
        "tested_ac": tested_ac,
        "ac_coverage": ac_coverage,
        "total_tc": total_tc,
        "executed_tc": executed_tc,
        "tc_coverage": tc_coverage,
        "full_coverage": full_coverage,
        "matrix_errors": matrix_errors,
    }
