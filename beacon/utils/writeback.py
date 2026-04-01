"""Implementation/verification/acceptance writeback helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from beacon.utils.revision_state import load_revision_state, save_revision_state
from beacon.utils.runtime import load_run_state, now_iso, save_run_state
from beacon.utils.story_state import feature_slug, load_story_state, save_story_state
from beacon.utils.versioning import resolve_target_version
from beacon.utils.workflow_memory import (
    append_lifecycle_event,
    compute_workflow_progress,
    record_stage_writeback,
    resolve_workflow_run_id,
    workflow_stages_for_run,
    write_stage_context,
)


def _normalize_ids(values: Iterable[str] | None) -> set[str]:
    out: set[str] = set()
    for value in values or []:
        text = str(value or "").strip().upper()
        if text:
            out.add(text)
    return out


def _existing_relative_paths(project_root: Path, candidates: Iterable[Path]) -> list[str]:
    refs: list[str] = []
    for candidate in candidates:
        path = Path(candidate)
        if not path.exists():
            continue
        refs.append(str(path.relative_to(project_root)))
    return refs


def _workflow_stage_evidence(project_root: Path, *, version: str, feature: str) -> dict[str, list[str]]:
    slug = feature_slug(feature)
    docs_root = project_root / "docs" / "beacon" / version
    execution_root = docs_root / "execution"
    machine_root = docs_root / ".machine"
    prototype_root = docs_root / "prototype" / slug
    state_root = project_root / ".beacon" / "state"
    qa_root = project_root / ".beacon" / "qa" / "features" / slug

    return {
        "think": _existing_relative_paths(
            project_root,
            [
                docs_root / "SUMMARY.md",
                execution_root / "index.md",
                execution_root / "architecture-blueprint.md",
            ],
        ),
        "user-story": _existing_relative_paths(
            project_root,
            [
                docs_root / "user-story" / f"{slug}.md",
                machine_root / "user-story" / f"{slug}.json",
            ],
        ),
        "prd": _existing_relative_paths(
            project_root,
            [
                docs_root / "prd" / f"{slug}.md",
                machine_root / "execution" / f"{slug}.revision.json",
            ],
        ),
        "prototype": _existing_relative_paths(
            project_root,
            [
                prototype_root / "prototype-plan.json",
                prototype_root / "manifest.json",
                prototype_root / "prototype-review.json",
                prototype_root / "freeze.json",
            ],
        ),
        "test-case": _existing_relative_paths(
            project_root,
            [
                docs_root / "qa" / "test-cases" / f"{slug}.md",
                machine_root / "qa" / f"{slug}.ac-test-matrix.json",
                machine_root / "qa" / f"{slug}.qa9-matrix.json",
                machine_root / "qa" / f"{slug}.story-scenario-map.json",
            ],
        ),
        "implementation": _existing_relative_paths(
            project_root,
            [
                execution_root / f"technical-implementation-{slug}.md",
                execution_root / f"technical-implementation-{slug}.json",
                execution_root / f"implementation-summary-{slug}.md",
                execution_root / f"implementation-summary-{slug}.json",
                state_root / f"implementation-{slug}.json",
            ],
        ),
        "verify": _existing_relative_paths(
            project_root,
            [
                project_root / ".beacon" / "auto-test-status.json",
                execution_root / f"review-quality-{slug}.md",
                execution_root / f"review-quality-{slug}.json",
                execution_root / f"review-spec-{slug}.md",
                execution_root / f"review-spec-{slug}.json",
                qa_root / "scorecard.json",
            ],
        ),
        "gate": _existing_relative_paths(
            project_root,
            [
                project_root / ".beacon" / "gate-report.json",
                project_root / ".beacon" / "evidence-manifest.json",
                execution_root / "terminal.json",
            ],
        ),
    }


def _update_items(
    items: list[dict[str, Any]],
    *,
    target_ids: set[str],
    field: str,
    value: str,
    status: str,
    revision_id: str,
) -> int:
    updated = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", "") or "").upper()
        if target_ids and item_id not in target_ids:
            continue
        item["status"] = status
        item[field] = value
        item["changed_in_revision"] = revision_id
        updated += 1
    return updated


def record_implementation_writeback(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str,
    implemented_item_ids: Iterable[str] | None = None,
    changed_files: Iterable[str] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True, revision_id=str(revision.get("revision_id", "R1")))
    target_ids = _normalize_ids(implemented_item_ids)
    updated = _update_items(
        story.get("items", []),
        target_ids=target_ids,
        field="implemented_by_run_id",
        value=run_id,
        status="implemented",
        revision_id=str(revision.get("revision_id", "R1")),
    )
    story["status"] = "implemented" if updated else story.get("status", "draft")
    story["last_changed_files"] = [str(x) for x in (changed_files or []) if str(x).strip()]
    save_story_state(project_root, version=resolved_version, feature=feature, state=story)

    revision["delivery_status"] = "implemented"
    revision["last_implementation_run_id"] = run_id
    if changed_files is not None:
        revision["changed_files"] = [str(x) for x in changed_files if str(x).strip()]
    save_revision_state(project_root, version=resolved_version, feature=feature, state=revision)
    return {"updated_items": updated, "story": story, "revision": revision}


def record_verification_writeback(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str,
    verified_item_ids: Iterable[str] | None = None,
    failed_item_ids: Iterable[str] | None = None,
    evidence_ref: Iterable[str] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True, revision_id=str(revision.get("revision_id", "R1")))
    verified_ids = _normalize_ids(verified_item_ids)
    failed_ids = _normalize_ids(failed_item_ids)
    verified = 0
    failed = 0
    for item in story.get("items", []):
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", "") or "").upper()
        if item_id in failed_ids:
            item["status"] = "failed"
            item["verified_by_run_id"] = run_id
            item["changed_in_revision"] = str(revision.get("revision_id", "R1"))
            failed += 1
            continue
        if item_id in verified_ids:
            kind = str(item.get("kind", ""))
            item["status"] = "passed" if kind == "test" else "verified"
            item["verified_by_run_id"] = run_id
            item["changed_in_revision"] = str(revision.get("revision_id", "R1"))
            verified += 1
    story["verification_evidence"] = [str(x) for x in (evidence_ref or []) if str(x).strip()]
    story["status"] = "verified" if failed == 0 and verified > 0 else ("blocked" if failed > 0 else story.get("status", "draft"))
    save_story_state(project_root, version=resolved_version, feature=feature, state=story)

    revision["delivery_status"] = "verified" if failed == 0 else "blocked"
    revision["last_verification_run_id"] = run_id
    revision["verification_evidence"] = [str(x) for x in (evidence_ref or []) if str(x).strip()]
    save_revision_state(project_root, version=resolved_version, feature=feature, state=revision)
    return {"verified_items": verified, "failed_items": failed, "story": story, "revision": revision}


def record_acceptance_writeback(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    accepted_by: str = "system",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    if str(revision.get("doc_status", "draft")) != "frozen":
        raise ValueError("acceptance_revision_not_frozen")
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True, revision_id=str(revision.get("revision_id", "R1") or "R1"))
    items = [item for item in story.get("items", []) if isinstance(item, dict)]
    required_acs = [i for i in items if i.get("kind") == "ac" and bool(i.get("required", True))]
    required_tests = [i for i in items if i.get("kind") == "test" and bool(i.get("required", True))]
    if any(str(i.get("status", "")) != "verified" for i in required_acs):
        raise ValueError("acceptance_ac_not_verified")
    if any(str(i.get("status", "")) not in {"passed", "verified"} for i in required_tests):
        raise ValueError("acceptance_tests_not_passed")
    accepted_at = now_iso()
    for item in items:
        if str(item.get("status", "")).lower() in {"verified", "implemented", "passed"}:
            item["status"] = "accepted"
            item["accepted_at"] = accepted_at
            item["changed_in_revision"] = str(revision.get("revision_id", "R1"))
    story["status"] = "accepted"
    story["accepted_at"] = accepted_at
    story["accepted_by"] = accepted_by
    save_story_state(project_root, version=resolved_version, feature=feature, state=story)

    revision["delivery_status"] = "accepted"
    revision["lifecycle_status"] = "accepted"
    revision["accepted_at"] = accepted_at
    revision["accepted_by"] = accepted_by
    save_revision_state(project_root, version=resolved_version, feature=feature, state=revision)
    return {"story": story, "revision": revision}


def sync_acceptance_workflow_closure(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str | None = None,
    source: str = "review.accept.sync",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    resolved_run_id = resolve_workflow_run_id(
        project_root,
        run_id=run_id,
        version=resolved_version,
        feature=feature,
    )
    if not resolved_run_id:
        return {
            "run_id": "",
            "version": resolved_version,
            "feature": feature,
            "synced_stages": [],
            "closure_complete": False,
            "gate_pass": False,
            "reason": "run_not_found",
        }

    run_state = load_run_state(project_root, resolved_run_id) or {}
    stage_order = workflow_stages_for_run(project_root, run_id=resolved_run_id, run_state=run_state)
    stage_evidence = _workflow_stage_evidence(project_root, version=resolved_version, feature=feature)
    progress = compute_workflow_progress(
        project_root,
        run_id=resolved_run_id,
        version=resolved_version,
        feature=feature,
    )
    synced_stages: list[str] = []

    for stage in stage_order:
        refs = stage_evidence.get(stage, [])
        if not refs:
            continue
        stage_state = progress.get("stages", {}).get(stage, {}) if isinstance(progress.get("stages"), dict) else {}
        changed = False
        if not bool(stage_state.get("has_started")):
            append_lifecycle_event(
                project_root,
                run_id=resolved_run_id,
                stage=stage,
                event="stage_started",
                source=source,
                evidence_ref=refs,
                details={"backfilled": True, "feature": feature, "version": resolved_version},
            )
            changed = True
        if not bool(stage_state.get("has_context")):
            write_stage_context(
                project_root,
                run_id=resolved_run_id,
                stage=stage,
                feature=feature,
            )
            changed = True
        if not bool(stage_state.get("has_finished")):
            append_lifecycle_event(
                project_root,
                run_id=resolved_run_id,
                stage=stage,
                event="stage_finished",
                source=source,
                evidence_ref=refs,
                details={"backfilled": True, "feature": feature, "version": resolved_version},
            )
            changed = True
        if not bool(stage_state.get("has_writeback")):
            record_stage_writeback(
                project_root,
                run_id=resolved_run_id,
                stage=stage,
                feature=feature,
                evidence_ref=refs,
                status="completed",
            )
            changed = True
        if changed:
            synced_stages.append(stage)
            progress = compute_workflow_progress(
                project_root,
                run_id=resolved_run_id,
                version=resolved_version,
                feature=feature,
            )

    final_progress = compute_workflow_progress(
        project_root,
        run_id=resolved_run_id,
        version=resolved_version,
        feature=feature,
    )
    if bool(final_progress.get("closure_complete")) and bool(final_progress.get("gate_pass")):
        updated_state = dict(run_state)
        updated_state["status"] = "completed"
        updated_state["reason"] = "synced_from_acceptance"
        updated_state["ended_at"] = now_iso()
        events = updated_state.get("events")
        if not isinstance(events, list):
            events = []
        if not any(isinstance(item, dict) and str(item.get("event", "")) == "workflow_completed" for item in events):
            events.append({"event": "workflow_completed", "ts": now_iso()})
        updated_state["events"] = events
        save_run_state(project_root, resolved_run_id, updated_state)

    return {
        "run_id": resolved_run_id,
        "version": resolved_version,
        "feature": feature,
        "synced_stages": synced_stages,
        "closure_complete": bool(final_progress.get("closure_complete")),
        "gate_pass": bool(final_progress.get("gate_pass")),
        "missing_closure_stages": final_progress.get("missing_closure_stages", []),
    }
