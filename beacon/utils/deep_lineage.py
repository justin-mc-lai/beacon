"""Lightweight lineage projection for deep support artifacts."""

from __future__ import annotations

from typing import Any

from beacon.utils.requirement_parsing import extract_explicit_ac_items, extract_qa_case_rows, extract_story_sections

LINEAGE_MODES = {
    "source_bound",
    "machine_inferred",
    "adoption_required",
    "canonical_promoted",
}
TRUTH_IMPACTS = {
    "none",
    "acceptance_delta",
    "requirement_meaning_delta",
}


def _candidate(ref_type: str, ref_id: str, *, confidence: str = "medium") -> dict[str, Any]:
    return {
        "ref_type": ref_type,
        "ref_id": ref_id,
        "confidence": confidence,
        "inferred": True,
    }


def _normalize_candidate_parent_refs(candidate_parent_refs: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not isinstance(candidate_parent_refs, list):
        return []
    normalized: list[dict[str, Any]] = []
    for item in candidate_parent_refs:
        if not isinstance(item, dict):
            continue
        ref_type = str(item.get("ref_type") or "").strip().upper()
        ref_id = str(item.get("ref_id") or "").strip().upper()
        if not ref_type or not ref_id:
            continue
        confidence = str(item.get("confidence") or "medium").strip().lower()
        if confidence not in {"low", "medium", "high"}:
            confidence = "medium"
        normalized.append(_candidate(ref_type, ref_id, confidence=confidence))
    return normalized


def infer_candidate_parent_refs(
    *,
    user_story_content: str,
    qa_content: str,
    limit: int = 8,
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add(ref_type: str, ref_id: str, *, confidence: str = "medium") -> None:
        normalized_type = str(ref_type or "").strip().upper()
        normalized_id = str(ref_id or "").strip().upper()
        if not normalized_type or not normalized_id:
            return
        key = (normalized_type, normalized_id)
        if key in seen:
            return
        seen.add(key)
        refs.append(_candidate(normalized_type, normalized_id, confidence=confidence))

    for section in extract_story_sections(user_story_content, "user-story"):
        add("US", str(section.get("story_id") or ""), confidence="medium")

    for ac in extract_explicit_ac_items(user_story_content, "user-story"):
        add("AC", str(ac.get("ac_id") or ""), confidence="medium")

    for row in extract_qa_case_rows(qa_content, "test-case"):
        add("TC", str(row.get("tc_id") or ""), confidence="high")
        add("AC", str(row.get("ac_id") or ""), confidence="high")
        add("US", str(row.get("story_id") or ""), confidence="medium")

    return refs[:limit]


def truth_impact_for_route(*, route_target: str = "", classification: str = "") -> str:
    route = str(route_target or "").strip().lower().replace("_", "-")
    klass = str(classification or "").strip().lower().replace("_", "-")
    if route in {"change", "change/refreeze", "change-refreeze"} or "requirement" in klass:
        return "requirement_meaning_delta"
    if route == "test-case" or "test-delta" in klass or "acceptance" in klass:
        return "acceptance_delta"
    return "none"


def lineage_mode_for_impact(*, truth_impact: str, candidate_parent_refs: list[dict[str, Any]] | None = None) -> str:
    impact = str(truth_impact or "none").strip()
    if impact in {"acceptance_delta", "requirement_meaning_delta"}:
        return "adoption_required"
    if candidate_parent_refs:
        return "machine_inferred"
    return "source_bound"


def build_deep_lineage_projection(
    *,
    source_truth_refs: list[str],
    candidate_parent_refs: list[dict[str, Any]] | None = None,
    route_target: str = "",
    truth_impact: str = "none",
    promotion_required: bool = False,
) -> dict[str, Any]:
    refs = [str(item).strip() for item in source_truth_refs if str(item).strip()]
    candidates = _normalize_candidate_parent_refs(candidate_parent_refs)
    normalized_impact = str(truth_impact or "none").strip()
    if normalized_impact not in TRUTH_IMPACTS:
        normalized_impact = "none"
    mode = lineage_mode_for_impact(truth_impact=normalized_impact, candidate_parent_refs=candidates)
    return {
        "lineage_mode": mode,
        "source_truth_refs": refs,
        "candidate_parent_refs": candidates,
        "route_target": str(route_target or "").strip(),
        "truth_impact": normalized_impact,
        "promotion_required": bool(promotion_required),
        "canonical": mode == "canonical_promoted",
        "gate_trust": "canonical_only" if mode != "canonical_promoted" else "canonical",
        "blocking": mode == "adoption_required",
    }
