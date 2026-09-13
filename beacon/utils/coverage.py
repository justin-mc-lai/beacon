"""Coverage metrics helpers for Story/AC/TC execution traceability."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_qa_dir, qa_docs_dir, uses_machine_surface
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


_PROTOTYPE_SOURCE_STATUS_RE = re.compile(r"^\*\*Status\*\*:\s*`prototype-source`", re.MULTILINE)


def _is_prototype_source_material(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return False
    return bool(_PROTOTYPE_SOURCE_STATUS_RE.search(text))


def _resolve_evidence_path(raw_path: str, run_id: str) -> str:
    value = str(raw_path or "").strip()
    if not value:
        return value
    if run_id:
        value = value.replace("{run_id}", run_id)
        value = value.replace("$RUN_ID", run_id)
        value = value.replace("__RUN_ID__", run_id)
    return value


def _auto_test_run_id(project_root: Path) -> str:
    payload = _read_json(project_root / ".beacon" / "auto-test-status.json")
    execution = payload.get("execution")
    if isinstance(execution, dict):
        run_id = str(execution.get("run_id", "")).strip()
        if run_id:
            return run_id
    return str(payload.get("run_id", "")).strip()


def _projected_coverage_metrics(project_root: Path, version: str, feature: str | None) -> dict[str, Any] | None:
    if feature:
        return None
    payload = _read_json(project_root / ".beacon" / "coverage-summary.json")
    details = payload.get("details")
    if not isinstance(details, dict):
        return None
    artifact_version = str(payload.get("version") or details.get("version") or "").strip()
    if artifact_version != version:
        return None
    return {
        "version": artifact_version,
        "feature": str(details.get("feature") or "").strip(),
        "planned_story": int(details.get("planned_story", 0) or 0),
        "implemented_story": int(details.get("implemented_story", 0) or 0),
        "story_coverage": float(details.get("story_coverage", 0.0) or 0.0),
        "total_ac": int(details.get("total_ac", 0) or 0),
        "tested_ac": int(details.get("tested_ac", 0) or 0),
        "ac_coverage": float(details.get("ac_coverage", 0.0) or 0.0),
        "total_tc": int(details.get("total_tc", 0) or 0),
        "executed_tc": int(details.get("executed_tc", 0) or 0),
        "tc_coverage": float(details.get("tc_coverage", 0.0) or 0.0),
        "full_coverage": bool(details.get("full_coverage", payload.get("full_coverage", False))),
        "matrix_errors": list(details.get("matrix_errors", [])) if isinstance(details.get("matrix_errors"), list) else [],
    }


def _feature_scorecard_coverage_metrics(
    project_root: Path,
    *,
    version: str,
    feature: str | None,
    planned_story: int,
    implemented_story: int,
) -> dict[str, Any] | None:
    qa_status = _read_json(project_root / ".beacon" / "qa" / "status.json")
    qa_version = str(qa_status.get("version") or "").strip()
    if qa_version and qa_version != version:
        return None

    feature_name = str(feature or qa_status.get("feature") or "").strip()
    if not feature_name:
        return None
    if not feature and planned_story > 1:
        return None

    feature_key = _slug(feature_name)
    scorecard = _read_json(project_root / ".beacon" / "qa" / "features" / feature_key / "scorecard.json")
    if not scorecard:
        return None
    # Issue #23: coverage is a reporting signal, not a release verdict. When a
    # specific feature is requested, report its scorecard coverage even when the
    # feature is not yet release_ready. The aggregate (feature-less) path keeps
    # the release gates for backward compatibility.
    if not feature:
        if not bool(scorecard.get("release_ready", False)):
            return None
        if str(scorecard.get("continue_decision") or "").strip() != "ready_for_release":
            return None
        unresolved = [str(item).strip() for item in (scorecard.get("unresolved_closure_outcomes") or []) if str(item).strip()]
        if unresolved:
            return None
    if planned_story <= 0 and feature_key:
        feature_package_truth = project_root / "docs" / "beacon" / version / "features" / feature_key / "truth.md"
        if feature_package_truth.exists():
            planned_story = 1
            implemented_story = 1

    coverage_current = scorecard.get("coverage_current") if isinstance(scorecard.get("coverage_current"), dict) else {}
    total_ac = int(scorecard.get("ac_total") or 0)
    tested_ac = int(scorecard.get("ac_accepted") or 0)
    total_tc = int(
        coverage_current.get("required_scenarios")
        or scorecard.get("scenario_total")
        or 0
    )
    executed_tc = int(
        coverage_current.get("executed_scenarios")
        or scorecard.get("scenario_passed")
        or 0
    )

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
        "version": version,
        "feature": feature_key if feature else "",
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
        "matrix_errors": [],
        "release_ready": bool(scorecard.get("release_ready", False)),
        "source": "feature_qa_scorecard",
    }


def _aggregate_feature_scorecard_coverage_metrics(
    project_root: Path,
    *,
    version: str,
    story_slugs: set[str],
    planned_story: int,
    implemented_story: int,
) -> dict[str, Any] | None:
    if not story_slugs or planned_story <= 1:
        return None

    qa_root = project_root / ".beacon" / "qa" / "features"
    if not qa_root.exists():
        return None

    total_ac = 0
    tested_ac = 0
    total_tc = 0
    executed_tc = 0

    for story_slug in sorted(story_slugs):
        scorecard = _read_json(qa_root / story_slug / "scorecard.json")
        if not scorecard:
            return None
        if not bool(scorecard.get("release_ready", False)):
            return None
        if str(scorecard.get("continue_decision") or "").strip() != "ready_for_release":
            return None
        unresolved = [str(item).strip() for item in (scorecard.get("unresolved_closure_outcomes") or []) if str(item).strip()]
        if unresolved:
            return None

        total_ac += int(scorecard.get("ac_total") or 0)
        tested_ac += int(scorecard.get("ac_accepted") or 0)
        coverage_current = scorecard.get("coverage_current") if isinstance(scorecard.get("coverage_current"), dict) else {}
        total_tc += int(coverage_current.get("required_scenarios") or scorecard.get("scenario_total") or 0)
        executed_tc += int(coverage_current.get("executed_scenarios") or scorecard.get("scenario_passed") or 0)

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
        "version": version,
        "feature": "",
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
        "matrix_errors": [],
        "source": "feature_qa_scorecard_aggregate",
    }


def _story_files(project_root: Path, version: str, feature: str | None = None) -> list[Path]:
    roots = [
        project_root / "docs" / "beacon" / version / "user-story",
    ]
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        out.extend(path for path in root.glob("*.md") if not _is_prototype_source_material(path))
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
    preferred_by_feature: dict[str, Path] = {}
    fallback_by_feature: dict[str, Path] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.qa9-matrix.json"):
            slug = path.name.removesuffix(".qa9-matrix.json")
            preferred_by_feature.setdefault(slug, path)
        for path in root.glob("*.ac-test-matrix.json"):
            slug = path.name.removesuffix(".ac-test-matrix.json")
            fallback_by_feature.setdefault(slug, path)
    feature_slugs = sorted(set(preferred_by_feature) | set(fallback_by_feature))
    if feature:
        target = _slug(feature)
        feature_slugs = [slug for slug in feature_slugs if slug == target]
    resolved: list[Path] = []
    for slug in feature_slugs:
        chosen = preferred_by_feature.get(slug) or fallback_by_feature.get(slug)
        if chosen is not None:
            resolved.append(chosen)
    return sorted(resolved, key=lambda p: p.name)


def _implementation_slugs(project_root: Path, version: str, feature: str | None = None) -> set[str]:
    state_dir = project_root / ".beacon" / "state"
    impl_markers = list(state_dir.glob("implementation-*.json")) if state_dir.exists() else []
    marker_slugs = {p.stem.replace("implementation-", "", 1) for p in impl_markers}

    # Older release lines may only materialize implementation evidence under
    # docs/.machine execution archives rather than .beacon/state markers.
    machine_exec_dir = project_root / "docs" / "beacon" / version / ".machine" / "execution"
    archive_slugs = {
        p.stem.replace("technical-implementation-", "", 1)
        for p in machine_exec_dir.glob("technical-implementation-*.json")
        if p.is_file()
    } if machine_exec_dir.exists() else set()

    combined = marker_slugs | archive_slugs
    if feature:
        combined = {slug for slug in combined if slug == feature}
    return combined


def _accepted_revision_slugs(project_root: Path, version: str, feature: str | None = None) -> set[str]:
    machine_exec_dir = project_root / "docs" / "beacon" / version / ".machine" / "execution"
    if not machine_exec_dir.exists():
        return set()

    accepted: set[str] = set()
    for path in machine_exec_dir.glob("*.revision.json"):
        payload = _read_json(path)
        if not payload:
            continue
        payload_version = str(payload.get("version") or "").strip()
        if payload_version and payload_version != version:
            continue
        delivery_status = str(payload.get("delivery_status") or "").strip().lower()
        lifecycle_status = str(payload.get("lifecycle_status") or "").strip().lower()
        doc_status = str(payload.get("doc_status") or "").strip().lower()
        if delivery_status not in {"accepted", "implemented"} and lifecycle_status not in {"accepted", "implemented"}:
            continue
        if doc_status not in {"frozen", "accepted", "implemented"}:
            continue
        slug = str(payload.get("feature_slug") or "").strip()
        if slug:
            accepted.add(slug)

    if feature:
        accepted = {slug for slug in accepted if slug == feature}
    return accepted


def compute_coverage_metrics(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str | None = None,
    use_projected: bool = True,
) -> dict[str, Any]:
    """Compute story/ac/tc coverage metrics from docs + evidence artifacts."""
    ver = resolve_target_version(project_root, version)
    feature_filter = _slug(feature or "")

    story_files = _story_files(project_root, ver, feature=feature_filter or None)
    planned_story = len(story_files)
    story_slugs = {p.stem for p in story_files}

    impl_slugs = _implementation_slugs(project_root, ver, feature=feature_filter or None)
    accepted_revision_slugs = _accepted_revision_slugs(project_root, ver, feature=feature_filter or None)
    implemented_story_slugs = story_slugs & (impl_slugs | accepted_revision_slugs) if story_slugs else set()
    if feature_filter and not implemented_story_slugs and planned_story == 1:
        only_story = next(iter(story_slugs), "")
        if only_story == feature_slug(feature_filter):
            feature_scorecard = _read_json(project_root / ".beacon" / "qa" / "features" / feature_filter / "scorecard.json")
            if bool(feature_scorecard.get("release_ready", False)) and str(feature_scorecard.get("continue_decision") or "").strip() == "ready_for_release":
                implemented_story_slugs = {only_story}
    implemented_story = len(implemented_story_slugs)

    feature_scorecard_metrics = _feature_scorecard_coverage_metrics(
        project_root,
        version=ver,
        feature=feature_filter or None,
        planned_story=planned_story,
        implemented_story=implemented_story,
    )
    if feature_scorecard_metrics is not None:
        return feature_scorecard_metrics

    aggregate_feature_scorecard_metrics = _aggregate_feature_scorecard_coverage_metrics(
        project_root,
        version=ver,
        story_slugs=story_slugs,
        planned_story=planned_story,
        implemented_story=implemented_story,
    )
    if aggregate_feature_scorecard_metrics is not None:
        return aggregate_feature_scorecard_metrics

    projected = _projected_coverage_metrics(project_root, ver, feature_filter or None) if use_projected else None
    if projected is not None:
        return projected

    matrix_files = _matrix_files(project_root, ver, feature=feature_filter or None)
    total_tc = 0
    executed_tc = 0
    ac_all: set[str] = set()
    ac_tested: set[str] = set()
    matrix_errors: list[str] = []
    run_id = _auto_test_run_id(project_root)

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
            p = Path(_resolve_evidence_path(evidence_path, run_id))
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


def write_coverage_summary(
    project_root: Path,
    *,
    version: str = "auto",
    run_id: str = "",
) -> Path:
    """Persist project-level coverage metrics for release/read-only consumers."""
    metrics = compute_coverage_metrics(project_root, version=version, use_projected=False)
    coverage_rate = min(
        float(metrics.get("story_coverage", 0.0) or 0.0),
        float(metrics.get("ac_coverage", 0.0) or 0.0),
        float(metrics.get("tc_coverage", 0.0) or 0.0),
    )
    payload = {
        "schema_version": "1.0",
        "run_id": str(run_id or _auto_test_run_id(project_root)).strip(),
        "version": str(metrics.get("version") or resolve_target_version(project_root, version)),
        "coverage_rate": round(coverage_rate, 4),
        "full_coverage": bool(metrics.get("full_coverage", False)),
        "details": metrics,
    }
    path = project_root / ".beacon" / "coverage-summary.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def project_qa_layer_confidence(profile_completeness: dict[str, Any] | None) -> dict[str, Any]:
    """Project confidence_chain / state_machine_coverage from qa profile completeness."""
    payload = profile_completeness if isinstance(profile_completeness, dict) else {}
    return {
        "schema_version": "1.0",
        "confidence_chain": payload.get("confidence_chain") if isinstance(payload.get("confidence_chain"), dict) else {},
        "state_machine_coverage": payload.get("state_machine_coverage") if isinstance(payload.get("state_machine_coverage"), dict) else {},
    }
