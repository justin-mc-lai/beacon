"""Scoring helpers for Beacon v1.1.6 navigator layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import execution_file_candidates
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.material_audit import build_material_audit
from beacon.utils.story_state import ensure_story_state, story_state_summary
from beacon.utils.workflow_memory import compute_memory_metrics, compute_workflow_progress


def _clamp_score(value: float) -> int:
    if value < 0:
        value = 0
    if value > 100:
        value = 100
    return int(round(value))


def compute_scores(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    coverage = compute_coverage_metrics(project_root, version=version, feature=feature)
    progress = compute_workflow_progress(project_root, version=version, feature=feature)
    memory = compute_memory_metrics(project_root, version=version, feature=feature)
    materials = build_material_audit(project_root, version=version, strict=False)
    state = story_state_summary(ensure_story_state(project_root, version, feature))

    verify_status = str(progress.get("stages", {}).get("verify", {}).get("status", "not_started"))
    material_ok = str(materials.get("status", "fail")).lower() == "pass"
    ac_coverage = float(coverage.get("ac_coverage", 0.0) or 0.0)
    tc_coverage = float(coverage.get("tc_coverage", 0.0) or 0.0)
    story_coverage = float(coverage.get("story_coverage", 0.0) or 0.0)

    test_score = _clamp_score(ac_coverage * 35 + tc_coverage * 35 + (20 if verify_status == "completed" else 0) + (10 if coverage.get("full_coverage") else 0))

    closure_score = _clamp_score(
        (15 if state.get("revision_id") else 0)
        + (15 if state.get("doc_status") == "frozen" else 0)
        + (20 if state.get("delivery_status") in {"implemented", "verified", "accepted", "released"} else 0)
        + (20 if verify_status == "completed" else 0)
        + (15 if bool(memory.get("closure_complete")) else 0)
        + (15 if material_ok else 0)
    )

    current_stage = str(progress.get("next_stage") or "")
    readiness_base = {
        "think": 35,
        "user-story": 45,
        "prd": 55,
        "test-case": 65,
        "implementation": 75 if state.get("doc_status") == "frozen" else 35,
        "verify": 80 if state.get("delivery_status") in {"implemented", "verified", "accepted"} else 40,
        "gate": 90 if verify_status == "completed" else 45,
    }.get(current_stage, 50)
    if not material_ok:
        readiness_base -= 20
    readiness_score = _clamp_score(readiness_base)

    quality_penalty = 0
    if verify_status == "failed":
        quality_penalty += 30
    if str(progress.get("gate_status", "unknown")).lower() == "blocked":
        quality_penalty += 25
    if not material_ok:
        quality_penalty += 15
    quality_score = _clamp_score(100 - quality_penalty - (0 if coverage.get("full_coverage") else 15))

    return {
        "test_score": test_score,
        "closure_score": closure_score,
        "readiness_score": readiness_score,
        "quality_score": quality_score,
        "basis": {
            "coverage": coverage,
            "workflow_progress": progress,
            "memory_metrics": memory,
            "material_audit_status": materials.get("status", "fail"),
            "story_state": state,
        },
    }



def compute_test_score(coverage_metrics: dict[str, Any], *, auto_test_status: dict[str, Any] | None = None, story_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    auto_status = str((auto_test_status or {}).get("status", "")).lower()
    ac_coverage = float(coverage_metrics.get("ac_coverage", 0.0) or 0.0)
    tc_coverage = float(coverage_metrics.get("tc_coverage", 0.0) or 0.0)
    blocked = int(((auto_test_status or {}).get("summary") or {}).get("blocked", 0) or 0)
    score = _clamp_score(ac_coverage * 35 + tc_coverage * 35 + (20 if auto_status == "passed" else 0) + (10 if coverage_metrics.get("full_coverage") else 0) - (blocked * 10))
    return {"score": score, "status": auto_status or "unknown", "blocked": blocked}


def compute_closure_score(*, revision_state: dict[str, Any], story_state: dict[str, Any] | None, workflow_progress: dict[str, Any]) -> dict[str, Any]:
    summary = story_state_summary(story_state or {})
    verify_status = str(workflow_progress.get("stages", {}).get("verify", {}).get("status", "not_started"))
    revision_id = str(revision_state.get("revision_id", "") or summary.get("revision_id", ""))
    doc_status = str(revision_state.get("doc_status", "") or summary.get("doc_status", "draft"))
    delivery_status = str(revision_state.get("delivery_status", "") or summary.get("delivery_status", "idle"))
    score = _clamp_score((15 if revision_id else 0) + (20 if doc_status == "frozen" else 0) + (20 if delivery_status in {"implemented", "verified", "accepted", "released"} else 0) + (20 if verify_status == "completed" else 0) + (25 if delivery_status in {"accepted", "released"} else 0))
    return {"score": score, "verify_status": verify_status}


def compute_readiness_score(*, target_stage: str, revision_state: dict[str, Any], coverage_metrics: dict[str, Any], workflow_progress: dict[str, Any], blocked: bool) -> dict[str, Any]:
    doc_status = str(revision_state.get("doc_status", "draft"))
    base = {
        "freeze": 55,
        "implement-plan": 75 if doc_status == "frozen" else 25,
        "implement": 85 if doc_status == "frozen" else 25,
        "review-quality": 70,
        "release-check": 85,
        "status": 50,
    }.get(target_stage, 50)
    if blocked:
        base -= 35
    if not coverage_metrics.get("planned_story"):
        base -= 20
    return {"score": _clamp_score(base), "target_stage": target_stage, "blocked": blocked}


def compute_quality_score(project_root: Path, *, version: str, feature_slug: str, workflow_progress: dict[str, Any]) -> dict[str, Any]:
    penalties = 0
    for name in (f"review-spec-{feature_slug}.json", f"review-quality-{feature_slug}.json"):
        path = next((candidate for candidate in execution_file_candidates(project_root, version, name) if candidate.exists()), None)
        if path is None:
            continue
        try:
            payload = __import__("json").loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        status = str(payload.get("status", "")).lower()
        if status == "fail":
            penalties += 25
        elif status == "warn":
            penalties += 10
    if str(workflow_progress.get("stages", {}).get("verify", {}).get("status", "")).lower() == "failed":
        penalties += 30
    return {"score": _clamp_score(100 - penalties), "penalties": penalties}
