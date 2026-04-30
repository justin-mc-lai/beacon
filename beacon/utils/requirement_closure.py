"""Requirement-closure helpers for Beacon implementation/review enforcement."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import execution_file_candidates, qa_matrix_candidates
from beacon.utils.requirement_parsing import build_feature_ac_items, extract_explicit_ac_items
from beacon.utils.revision_delta import load_revision_delta, revision_delta_json_path, revision_delta_supported
from beacon.utils.revision_state import load_revision_state
from beacon.utils.versioning import normalize_version


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    text = str(normalize_version(version) or version or "").strip().lstrip("v")
    try:
        major, minor, patch = text.split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def requirement_closure_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 3, 4)


def _slug(text: str) -> str:
    return "-".join(str(text or "").strip().lower().split())


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _dedupe_strings(values: list[Any]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return _dedupe_strings(list(value))


def _normalize_cleanup_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = ""
        if isinstance(item, dict):
            text = str(item.get("label", "") or item.get("text", "") or item.get("id", "") or "").strip()
        else:
            text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _feature_paths(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    slug = _slug(feature)
    base = project_root / "docs" / "beacon" / version
    return {
        "slug": slug,
        "base": base,
        "user_story": base / "user-story" / f"{slug}.md",
        "prd": base / "prd" / f"{slug}.md",
        "test_case": base / "qa" / "test-cases" / f"{slug}.md",
        "ac_matrix_candidates": qa_matrix_candidates(project_root, version, slug, "ac-test-matrix"),
        "implementation_summary_candidates": execution_file_candidates(project_root, version, f"implementation-summary-{slug}.json"),
    }


def _resolve_first_json(candidates: list[Path]) -> tuple[dict[str, Any], str]:
    for path in candidates:
        payload = _read_json(path)
        if payload:
            return payload, str(path)
    return {}, ""


def _collect_matrix_ac_ids(payload: dict[str, Any]) -> list[str]:
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return []
    out: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        out.append(str(entry.get("ac_id", "") or "").strip().upper())
        for value in entry.get("ac_ids", []) if isinstance(entry.get("ac_ids"), list) else []:
            out.append(str(value or "").strip().upper())
        for value in entry.get("covers", []) if isinstance(entry.get("covers"), list) else []:
            out.append(str(value or "").strip().upper())
    return _dedupe_strings([item for item in out if item.startswith("AC-")])


def build_requirement_closure(
    project_root: Path,
    version: str,
    feature: str,
    *,
    implementation_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not requirement_closure_supported(version):
        return {
            "enabled": False,
            "status": "not_applicable",
            "issues": [],
            "coverage": {},
        }

    paths = _feature_paths(project_root, version, feature)
    user_story_path = paths["user_story"]
    prd_path = paths["prd"]
    test_case_path = paths["test_case"]

    user_story_content = _read_text(user_story_path)
    prd_content = _read_text(prd_path)
    test_case_content = _read_text(test_case_path)

    ac_matrix_payload, ac_matrix_path = _resolve_first_json(list(paths["ac_matrix_candidates"]))
    implementation_summary_payload = implementation_summary if isinstance(implementation_summary, dict) else None
    if implementation_summary_payload is None:
        implementation_summary_payload, _ = _resolve_first_json(list(paths["implementation_summary_candidates"]))

    issues: list[dict[str, Any]] = []

    user_story_ac_ids = _dedupe_strings(
        [
            str(item.get("ac_id", "") or "").strip().upper()
            for item in build_feature_ac_items(
                user_story_content=user_story_content,
                prd_content=prd_content,
                qa_content=test_case_content,
                user_story_source=f"user-story:{user_story_path.name}",
                prd_source=f"prd:{prd_path.name}",
                qa_source=f"qa:test-cases:{test_case_path.name}",
            )
            if isinstance(item, dict)
        ]
    )
    qa_markdown_ac_ids = _dedupe_strings(
        [
            str(item.get("ac_id", "") or "").strip().upper()
            for item in extract_explicit_ac_items(test_case_content, f"qa:test-cases:{test_case_path.name}")
            if isinstance(item, dict)
        ]
    )
    matrix_ac_ids = _collect_matrix_ac_ids(ac_matrix_payload)
    covered_ac_ids = _dedupe_strings(matrix_ac_ids + qa_markdown_ac_ids)

    if user_story_path.exists() and prd_path.exists() and not user_story_ac_ids:
        issues.append(
            {
                "reason_code": "user_story_acceptance_missing",
                "severity": "critical",
                "message": "user story / PRD materials do not expose parseable acceptance criteria",
                "evidence": [
                    str(user_story_path.relative_to(project_root)),
                    str(prd_path.relative_to(project_root)),
                ],
            }
        )

    if user_story_ac_ids and test_case_path.exists() and not covered_ac_ids:
        evidence = [str(test_case_path.relative_to(project_root))]
        if ac_matrix_path:
            evidence.append(str(Path(ac_matrix_path).relative_to(project_root)))
        issues.append(
            {
                "reason_code": "test_case_traceability_missing",
                "severity": "critical",
                "message": "test-case materials do not provide AC traceability coverage",
                "evidence": evidence,
            }
        )
    elif user_story_ac_ids and covered_ac_ids:
        missing_ac_ids = [ac_id for ac_id in user_story_ac_ids if ac_id not in set(covered_ac_ids)]
        if missing_ac_ids:
            issues.append(
                {
                    "reason_code": "prd_user_story_test_case_traceability_broken",
                    "severity": "critical",
                    "message": f"acceptance criteria missing from test-case coverage: {missing_ac_ids}",
                    "evidence": [
                        str(user_story_path.relative_to(project_root)) if user_story_path.exists() else "",
                        str(test_case_path.relative_to(project_root)) if test_case_path.exists() else "",
                    ],
                    "missing_ac_ids": missing_ac_ids,
                }
            )

    requirement_traceability = (
        implementation_summary_payload.get("requirement_traceability")
        if isinstance(implementation_summary_payload.get("requirement_traceability"), dict)
        else {}
    )
    delivery_surfaces = (
        implementation_summary_payload.get("delivery_surfaces")
        if isinstance(implementation_summary_payload.get("delivery_surfaces"), dict)
        else {}
    )
    revision_cleanup = (
        implementation_summary_payload.get("revision_cleanup")
        if isinstance(implementation_summary_payload.get("revision_cleanup"), dict)
        else {}
    )
    revision_state = load_revision_state(project_root, version=version, feature=feature, create_if_missing=False)
    revision_delta: dict[str, Any] = {}
    if revision_delta_supported(version) and str(revision_state.get("source_revision_id", "") or "").strip():
        revision_delta = load_revision_delta(project_root, version=version, feature=feature)
        if not revision_delta:
            issues.append(
                {
                    "reason_code": "revision_cleanup_delta_missing",
                    "severity": "critical",
                    "message": "changed frozen revision is missing the revision cleanup delta artifact",
                    "evidence": [
                        str(revision_delta_json_path(project_root, version, feature).relative_to(project_root)),
                    ],
                }
            )
    if implementation_summary_payload:
        required_traceability_keys = [
            "source_of_truth_root",
            "prd",
            "user_story",
            "test_case",
            "ac_matrix",
        ]
        missing_traceability_keys = [
            key for key in required_traceability_keys if not str(requirement_traceability.get(key, "") or "").strip()
        ]
        if missing_traceability_keys:
            issues.append(
                {
                    "reason_code": "implementation_requirement_traceability_missing",
                    "severity": "critical",
                    "message": f"implementation summary is missing requirement traceability keys: {missing_traceability_keys}",
                    "evidence": _normalize_string_list(implementation_summary_payload.get("traceability_refs")),
                    "missing_keys": missing_traceability_keys,
                }
            )

        missing_delivery_keys: list[str] = []
        runtime_mode = str(delivery_surfaces.get("runtime_mode", "") or "").strip()
        if not runtime_mode:
            missing_delivery_keys.append("runtime_mode")
        for key in ("shipped_surfaces", "partial_surfaces", "deferred_surfaces"):
            if not isinstance(delivery_surfaces.get(key), list):
                missing_delivery_keys.append(key)
        if "downgrade_rationale" not in delivery_surfaces:
            missing_delivery_keys.append("downgrade_rationale")
        if missing_delivery_keys:
            issues.append(
                {
                    "reason_code": "implementation_delivery_summary_missing",
                    "severity": "critical",
                    "message": f"implementation summary is missing stable delivery summary fields: {missing_delivery_keys}",
                    "evidence": _normalize_string_list(implementation_summary_payload.get("traceability_refs")),
                    "missing_keys": missing_delivery_keys,
                }
            )

        partial_or_deferred = _normalize_string_list(delivery_surfaces.get("partial_surfaces")) + _normalize_string_list(
            delivery_surfaces.get("deferred_surfaces")
        )
        if partial_or_deferred and not str(delivery_surfaces.get("downgrade_rationale", "") or "").strip():
            issues.append(
                {
                    "reason_code": "delivery_surface_downgrade_unapproved",
                    "severity": "warn",
                    "message": "partial/deferred delivery surfaces exist without downgrade rationale",
                    "surfaces": partial_or_deferred,
                }
            )
    if bool(revision_delta.get("cleanup_required", False)):
        removed_requirement_surfaces = _normalize_cleanup_list(revision_delta.get("removed_requirement_surfaces"))
        if not implementation_summary_payload:
            issues.append(
                {
                    "reason_code": "superseded_surface_cleanup_missing",
                    "severity": "critical",
                    "message": "changed frozen revision requires cleanup evidence but no implementation summary was found",
                    "surfaces": removed_requirement_surfaces,
                    "evidence": [
                        str(revision_delta_json_path(project_root, version, feature).relative_to(project_root)),
                    ],
                }
            )
        else:
            cleanup_review_completed = bool(revision_cleanup.get("cleanup_review_completed", False))
            removed_surfaces = _normalize_cleanup_list(revision_cleanup.get("removed_surfaces"))
            retained_legacy_surfaces = _normalize_cleanup_list(revision_cleanup.get("retained_legacy_surfaces"))
            cleanup_rationale = str(revision_cleanup.get("cleanup_rationale", "") or "").strip()
            if (
                str(revision_cleanup.get("revision_id", "") or "") != str(revision_delta.get("revision_id", "") or "")
                or str(revision_cleanup.get("source_revision_id", "") or "") != str(revision_delta.get("source_revision_id", "") or "")
                or not str(revision_cleanup.get("revision_delta_ref", "") or "").strip()
            ):
                issues.append(
                    {
                        "reason_code": "superseded_surface_cleanup_missing",
                        "severity": "critical",
                        "message": "implementation summary cleanup evidence is not bound to the latest revision delta",
                        "evidence": _normalize_string_list(implementation_summary_payload.get("traceability_refs")),
                    }
                )
            elif not cleanup_review_completed or (not removed_surfaces and not retained_legacy_surfaces):
                issues.append(
                    {
                        "reason_code": "superseded_surface_cleanup_missing",
                        "severity": "critical",
                        "message": "superseded frozen requirement surfaces were not explicitly removed or retained with evidence",
                        "surfaces": removed_requirement_surfaces,
                        "evidence": _normalize_string_list(implementation_summary_payload.get("traceability_refs")),
                    }
                )
            elif retained_legacy_surfaces and not cleanup_rationale:
                issues.append(
                    {
                        "reason_code": "superseded_surface_retention_unjustified",
                        "severity": "critical",
                        "message": "retained legacy implementation surfaces require cleanup rationale after refreeze",
                        "surfaces": retained_legacy_surfaces,
                        "evidence": _normalize_string_list(implementation_summary_payload.get("traceability_refs")),
                    }
                )

    status = "pass"
    if any(str(item.get("severity", "")).lower() == "critical" for item in issues):
        status = "fail"
    elif issues:
        status = "warn"

    return {
        "enabled": True,
        "status": status,
        "issues": issues,
        "coverage": {
            "user_story_ac_ids": user_story_ac_ids,
            "matrix_ac_ids": matrix_ac_ids,
            "qa_markdown_ac_ids": qa_markdown_ac_ids,
            "covered_ac_ids": covered_ac_ids,
            "implementation_summary_present": bool(implementation_summary_payload),
            "requirement_traceability_keys": sorted(requirement_traceability.keys()),
            "delivery_surface_keys": sorted(delivery_surfaces.keys()),
            "revision_cleanup_required": bool(revision_delta.get("cleanup_required", False)),
            "removed_requirement_count": int(revision_delta.get("removed_requirement_count") or 0),
        },
    }
