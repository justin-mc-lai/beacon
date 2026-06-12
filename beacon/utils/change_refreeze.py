"""Governed one-shot change refreeze helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import change_docs_file, machine_change_file
from beacon.utils.feature_package import sync_truth_frontmatter_status, validate_feature_package
from beacon.utils.legacy_cutover import build_legacy_cutover_preflight
from beacon.utils.material_sync import sync_change_loop_requirement_package
from beacon.utils.requirement_clarity import materialize_requirement_clarity, requirement_clarity_json_path
from beacon.utils.revision_delta import materialize_revision_delta
from beacon.utils.revision_state import freeze_revision_state, load_revision_state, reopen_revision_state
from beacon.utils.runtime import now_iso, utc_compact_ts, write_json
from beacon.utils.story_state import feature_slug, freeze_story_state, load_story_state, reopen_story_state
from beacon.utils.truth_map import feature_package_authoritative_feature, resolve_truth_read_refs
from beacon.utils.version_aggregate_projection import (
    write_feature_change_projection,
    write_version_aggregate_projection,
)
from beacon.utils.versioning import resolve_target_version


REQUIRED_REFREEZE_SURFACES = ("change", "prd", "user-story", "test-case", "requirement_clarity", "freeze")
FILE_REFREEZE_SURFACES = {"change", "prd", "user-story", "test-case"}
PACKAGE_REFREEZE_SURFACES = ("change", "truth", "tests", "tasks", "evidence", "requirement_clarity", "freeze")
PACKAGE_FILE_REFREEZE_SURFACES = {"truth", "tests", "tasks", "evidence"}


def change_refreeze_transaction_path(project_root: Path, *, version: str, feature: str) -> Path:
    return machine_change_file(project_root, version, f"{feature_slug(feature)}.refreeze-transaction.json")


def change_refreeze_summary_path(project_root: Path, *, version: str, feature: str) -> Path:
    return change_docs_file(project_root, version, f"{feature_slug(feature)}.refreeze-summary.md")


def _relative(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _surface_paths(project_root: Path, *, version: str, feature: str) -> dict[str, Path]:
    slug = feature_slug(feature)
    root = project_root / "docs" / "beacon" / version
    return {
        "change": root / "change" / f"{slug}.md",
        "prd": root / "prd" / f"{slug}.md",
        "user-story": root / "user-story" / f"{slug}.md",
        "test-case": root / "qa" / "test-cases" / f"{slug}.md",
    }


def _surface_statuses(project_root: Path, *, version: str, feature: str) -> dict[str, dict[str, Any]]:
    if feature_package_authoritative_feature(project_root, version=version, feature=feature):
        refs = resolve_truth_read_refs(
            project_root,
            version=version,
            feature=feature,
            consumer="change-refreeze",
        )["requirement_refs"]
        package_paths = {
            "truth": project_root / refs["truth"],
            "tests": project_root / refs["tests"],
            "tasks": project_root / refs["tasks"],
            "evidence": project_root / refs["evidence"],
        }
        change_path = change_docs_file(project_root, version, f"{feature_slug(feature)}.md")
        statuses = {
            "change": {
                "path": _relative(project_root, change_path),
                "exists": change_path.exists(),
                "status": "present" if change_path.exists() else "package_change_optional",
                "required": False,
                "authority": "change_record_not_requirement_truth",
            }
        }
        validation = validate_feature_package(project_root, version=version, feature=feature, write_report=True)
        validation_passed = validation.get("status") == "pass"
        for surface, path in package_paths.items():
            statuses[surface] = {
                "path": _relative(project_root, path),
                "exists": path.exists(),
                "status": "present" if path.exists() and validation_passed else ("invalid" if path.exists() else "missing"),
                "required": True,
                "authority": "markdown_feature_package",
            }
        statuses["requirement_clarity"] = {
            "path": _relative(project_root, requirement_clarity_json_path(project_root, version, feature)),
            "exists": False,
            "status": "pending",
            "required": True,
        }
        statuses["freeze"] = {
            "path": _relative(project_root, machine_change_file(project_root, version, f"{feature_slug(feature)}.refreeze-transaction.json")),
            "exists": False,
            "status": "pending",
            "required": True,
        }
        statuses["feature_package_validation"] = {
            "path": _relative(project_root, project_root / str(validation.get("report_path") or "")),
            "exists": validation_passed,
            "status": "passed" if validation_passed else "blocked",
            "required": True,
            "diagnostics": validation.get("diagnostics", []),
        }
        return statuses
    statuses: dict[str, dict[str, Any]] = {}
    for surface, path in _surface_paths(project_root, version=version, feature=feature).items():
        statuses[surface] = {
            "path": _relative(project_root, path),
            "exists": path.exists(),
            "status": "present" if path.exists() else "missing",
            "required": surface in REQUIRED_REFREEZE_SURFACES,
        }
    statuses["requirement_clarity"] = {
        "path": _relative(project_root, requirement_clarity_json_path(project_root, version, feature)),
        "exists": False,
        "status": "pending",
        "required": True,
    }
    statuses["freeze"] = {
        "path": _relative(project_root, machine_change_file(project_root, version, f"{feature_slug(feature)}.refreeze-transaction.json")),
        "exists": False,
        "status": "pending",
        "required": True,
    }
    return statuses


def _revision_ref(state: dict[str, Any]) -> dict[str, str]:
    return {
        "revision_id": str(state.get("revision_id") or ""),
        "doc_status": str(state.get("doc_status") or ""),
        "lifecycle_status": str(state.get("lifecycle_status") or ""),
        "baseline_hash": str(state.get("baseline_hash") or ""),
    }


def _uses_compact_skill_names(version: str) -> bool:
    text = str(version or "").strip().lower().lstrip("v")
    parts: list[int] = []
    for raw in text.split(".")[:3]:
        digits = "".join(ch for ch in raw if ch.isdigit())
        parts.append(int(digits or "0"))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3]) >= (1, 6, 0)


def _next_route_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    refreeze_status: str,
    blocked_reason: str,
) -> dict[str, Any]:
    implement_surface = "beacon-gen-implement" if _uses_compact_skill_names(version) else "beacon-implement"
    change_surface = "beacon-gen-change" if _uses_compact_skill_names(version) else "beacon-change"
    if refreeze_status == "complete":
        return {
            "target_surface": implement_surface,
            "command": f'beacon implement "{feature}" --project {project_root} --version {version}',
            "why": "refreeze transaction completed; implementation may plan against the refreshed frozen truth",
        }
    return {
        "target_surface": change_surface,
        "command": f'beacon change "{feature}" --project {project_root} --version {version}',
        "why": blocked_reason or "refreeze transaction did not complete",
    }


def _render_summary(payload: dict[str, Any]) -> str:
    statuses = payload.get("surface_statuses") if isinstance(payload.get("surface_statuses"), dict) else {}
    lines = [
        f"# Change Refreeze Summary: {payload.get('feature', '')}",
        "",
        f"- version: `{payload.get('version', '')}`",
        f"- change_reason: `{payload.get('change_reason', '')}`",
        f"- refreeze_status: `{payload.get('refreeze_status', '')}`",
        f"- blocked_reason: `{payload.get('blocked_reason', '')}`",
        f"- next_route: `{(payload.get('next_route') or {}).get('target_surface', '')}`",
        f"- revision_before: `{(payload.get('truth_revision_before') or {}).get('revision_id', '')}`",
        f"- revision_after: `{(payload.get('truth_revision_after') or {}).get('revision_id', '')}`",
        "",
        "## Surface Statuses",
    ]
    for surface, status in statuses.items():
        if not isinstance(status, dict):
            continue
        lines.append(
            f"- `{surface}`: `{status.get('status', '')}` "
            f"({status.get('path', '')})"
        )
    refreshed = [
        surface
        for surface, status in statuses.items()
        if isinstance(status, dict) and str(status.get("status") or "") in {"present", "passed", "complete"}
    ]
    lines.extend(
        [
            "",
            "## Refreshed Surfaces",
            "",
            f"- {', '.join(refreshed) if refreshed else 'none'}",
            "",
            "## Boundary",
            "",
            "- This transaction only refreshes and refreezes requirement truth.",
            "- It does not execute implementation, QA, or release.",
            "- Partial refresh keeps the feature blocked.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _write_transaction(project_root: Path, *, version: str, feature: str, payload: dict[str, Any]) -> dict[str, str]:
    machine_path = change_refreeze_transaction_path(project_root, version=version, feature=feature)
    human_path = change_refreeze_summary_path(project_root, version=version, feature=feature)
    write_json(machine_path, payload)
    human_path.parent.mkdir(parents=True, exist_ok=True)
    human_path.write_text(_render_summary(payload), encoding="utf-8")
    return {
        "machine_path": _relative(project_root, machine_path),
        "human_path": _relative(project_root, human_path),
    }


def _base_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    reason: str,
    before_revision: dict[str, Any],
    surface_statuses: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "transaction_id": f"tx-change-refreeze-{feature_slug(feature)}-{utc_compact_ts().lower()}",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "change_reason": reason,
        "touched_surfaces": list(surface_statuses.keys()),
        "surface_statuses": surface_statuses,
        "truth_revision_before": _revision_ref(before_revision),
        "truth_revision_after": {},
        "refreeze_status": "blocked",
        "next_route": {},
        "blocked_reason": "",
        "delivery_execution": {
            "implement_executed": False,
            "qa_executed": False,
            "release_executed": False,
        },
        "created_at": now_iso(),
    }


def run_change_refreeze_chain(
    project_root: Path,
    *,
    version: str,
    feature: str,
    reason: str = "change-refreeze",
) -> dict[str, Any]:
    """Run one governed change -> requirement package -> clarity -> freeze attempt."""

    resolved_version = resolve_target_version(project_root, version)
    package_authoritative = feature_package_authoritative_feature(project_root, version=resolved_version, feature=feature)
    surface_statuses = _surface_statuses(project_root, version=resolved_version, feature=feature)
    before_revision = load_revision_state(
        project_root,
        version=resolved_version,
        feature=feature,
        create_if_missing=True,
    )
    payload = _base_payload(
        project_root=project_root,
        version=resolved_version,
        feature=feature,
        reason=reason,
        before_revision=before_revision,
        surface_statuses=surface_statuses,
    )

    if package_authoritative:
        cutover_preflight = build_legacy_cutover_preflight(
            project_root,
            version=resolved_version,
            feature=feature,
            resume_intent="refreeze",
        )
        if bool(cutover_preflight.get("blocked")):
            payload["blocked_reason"] = "legacy_cutover_required"
            payload["legacy_cutover"] = cutover_preflight["legacy_cutover"]
            payload["next_route"] = cutover_preflight["next_route"]
            payload["artifacts"] = _write_transaction(project_root, version=resolved_version, feature=feature, payload=payload)
            return payload

    missing = [
        surface
        for surface, status in surface_statuses.items()
        if (
            (surface in (PACKAGE_FILE_REFREEZE_SURFACES if package_authoritative else FILE_REFREEZE_SURFACES))
            and status.get("required")
            and (not status.get("exists") or str(status.get("status") or "") == "invalid")
        )
    ]
    if missing:
        payload["blocked_reason"] = "missing_requirement_surfaces"
        payload["missing_surfaces"] = missing
        payload["next_route"] = _next_route_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            refreeze_status="blocked",
            blocked_reason=payload["blocked_reason"],
        )
        payload["artifacts"] = _write_transaction(project_root, version=resolved_version, feature=feature, payload=payload)
        return payload

    before_doc_status = str(before_revision.get("doc_status") or "")
    already_reopened = before_doc_status == "draft" and bool(str(before_revision.get("source_revision_id") or "").strip())
    if before_doc_status != "frozen" and not already_reopened:
        payload["blocked_reason"] = "revision_not_frozen"
        payload["next_route"] = _next_route_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            refreeze_status="blocked",
            blocked_reason=payload["blocked_reason"],
        )
        payload["artifacts"] = _write_transaction(project_root, version=resolved_version, feature=feature, payload=payload)
        return payload

    try:
        if already_reopened:
            previous_revision = {
                "revision_id": str(before_revision.get("source_revision_id") or ""),
                "doc_status": "superseded",
                "lifecycle_status": "superseded",
                "baseline_hash": "",
            }
            next_revision = before_revision
            story_state = load_story_state(project_root, resolved_version, feature, create_if_missing=True) or {}
            story_reopen = {
                "current_revision_id": str(story_state.get("revision_id") or before_revision.get("revision_id") or ""),
                "lifecycle_status": str(story_state.get("status") or before_revision.get("lifecycle_status") or ""),
            }
        else:
            previous_revision, next_revision = reopen_revision_state(
                project_root,
                version=resolved_version,
                feature=feature,
                reason=reason,
            )
            story_reopen = reopen_story_state(project_root, resolved_version, feature, reason=reason)
        requirement_package = sync_change_loop_requirement_package(
            project_root,
            version=resolved_version,
            feature=feature,
        )
        requirement_clarity = materialize_requirement_clarity(
            project_root,
            version=resolved_version,
            feature=feature,
            source="change.refreeze-chain",
        )
        clarity_gate = requirement_clarity.get("gate") if isinstance(requirement_clarity.get("gate"), dict) else {}
        payload.update(
            {
                "previous_revision": _revision_ref(previous_revision),
                "opened_revision": _revision_ref(next_revision),
                "story_reopen": {
                    "current_revision_id": str(story_reopen.get("current_revision_id") or ""),
                    "lifecycle_status": str(story_reopen.get("lifecycle_status") or ""),
                },
                "requirement_package": requirement_package,
                "requirement_clarity": requirement_clarity,
            }
        )
        if bool(clarity_gate.get("blocked")):
            payload["surface_statuses"]["requirement_clarity"]["status"] = "blocked"
            payload["surface_statuses"]["requirement_clarity"]["exists"] = True
            payload["surface_statuses"]["freeze"]["status"] = "blocked"
            payload["blocked_reason"] = str(clarity_gate.get("reason_code") or "requirement_clarity_open")
            payload["truth_revision_after"] = _revision_ref(
                load_revision_state(project_root, version=resolved_version, feature=feature)
            )
            payload["next_route"] = _next_route_payload(
                project_root=project_root,
                version=resolved_version,
                feature=feature,
                refreeze_status="blocked",
                blocked_reason=payload["blocked_reason"],
            )
            payload["artifacts"] = _write_transaction(project_root, version=resolved_version, feature=feature, payload=payload)
            return payload

        frozen_revision = freeze_revision_state(project_root, version=resolved_version, feature=feature)
        freeze_story_state(project_root, resolved_version, feature)
        truth_frontmatter_sync = sync_truth_frontmatter_status(
            project_root,
            version=resolved_version,
            feature=feature,
            status="frozen",
        )
        revision_delta = materialize_revision_delta(project_root, version=resolved_version, feature=feature)
        payload["surface_statuses"]["requirement_clarity"]["status"] = "passed"
        payload["surface_statuses"]["requirement_clarity"]["exists"] = True
        payload["surface_statuses"]["freeze"]["status"] = "complete"
        payload["surface_statuses"]["freeze"]["exists"] = True
        payload["refreeze_status"] = "complete"
        payload["truth_revision_after"] = _revision_ref(frozen_revision)
        payload["truth_frontmatter_sync"] = truth_frontmatter_sync
        payload["revision_delta"] = revision_delta
        feature_projection = write_feature_change_projection(
            project_root,
            version=resolved_version,
            feature=feature,
            overwrite=True,
        )
        version_aggregate_projection = write_version_aggregate_projection(
            project_root,
            version=resolved_version,
        )
        payload["release_projection_sync"] = {
            "status": "pass",
            "truth_authority": False,
            "lifecycle_stage": False,
            "release_publish_action": False,
            "feature_projection": feature_projection,
            "version_aggregate_projection": version_aggregate_projection,
        }
        payload["next_route"] = _next_route_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            refreeze_status="complete",
            blocked_reason="",
        )
    except Exception as exc:  # noqa: BLE001
        payload["blocked_reason"] = "refreeze_chain_failed"
        payload["error"] = str(exc)
        payload["truth_revision_after"] = _revision_ref(
            load_revision_state(project_root, version=resolved_version, feature=feature)
        )
        payload["next_route"] = _next_route_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            refreeze_status="blocked",
            blocked_reason=payload["blocked_reason"],
        )

    payload["artifacts"] = _write_transaction(project_root, version=resolved_version, feature=feature, payload=payload)
    return payload
