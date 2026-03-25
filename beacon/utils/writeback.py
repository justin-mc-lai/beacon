"""Implementation/verification/acceptance writeback helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from beacon.utils.revision_state import load_revision_state, save_revision_state
from beacon.utils.runtime import now_iso
from beacon.utils.story_state import load_story_state, save_story_state
from beacon.utils.versioning import resolve_target_version


def _normalize_ids(values: Iterable[str] | None) -> set[str]:
    out: set[str] = set()
    for value in values or []:
        text = str(value or "").strip().upper()
        if text:
            out.add(text)
    return out


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

