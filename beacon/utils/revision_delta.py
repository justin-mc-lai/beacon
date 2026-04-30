"""Revision delta helpers for change/refreeze cleanup closure."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug, machine_story_path
from beacon.utils.versioning import normalize_version, resolve_target_version


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    text = str(normalize_version(version) or version or "").strip().lstrip("v")
    try:
        major, minor, patch = text.split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def revision_delta_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 3, 8)


def revision_delta_json_path(project_root: Path, version: str, feature: str) -> Path:
    return machine_execution_file(project_root, version, f"revision-delta-{feature_slug(feature)}.json")


def revision_delta_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    return human_execution_file(project_root, version, f"revision-delta-{feature_slug(feature)}.md")


def _computed_revision_delta_payload(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=False)
    revision_id = str(revision.get("revision_id", "") or "")
    source_revision_id = str(revision.get("source_revision_id", "") or "")
    story_path = machine_story_path(project_root, resolved_version, feature)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "revision_id": revision_id,
        "source_revision_id": source_revision_id,
        "status": "not_applicable",
        "cleanup_required": False,
        "removed_requirement_count": 0,
        "added_requirement_count": 0,
        "retained_requirement_count": 0,
        "removed_requirement_surfaces": [],
        "added_requirement_surfaces": [],
        "retained_requirement_surfaces": [],
        "current_baseline_hash": str(revision.get("baseline_hash", "") or ""),
        "source_baseline_hash": "",
        "story_state_ref": str(story_path.relative_to(project_root)) if story_path.exists() else "",
        "generated_at": now_iso(),
        "json_ref": str(revision_delta_json_path(project_root, resolved_version, feature).relative_to(project_root)),
        "markdown_ref": str(revision_delta_markdown_path(project_root, resolved_version, feature).relative_to(project_root)),
    }
    if not revision_delta_supported(resolved_version):
        return payload
    if not revision_id or not source_revision_id:
        return payload

    story_root = _read_story_root(project_root, resolved_version, feature)
    previous_story = _story_for_revision(story_root, source_revision_id)
    current_story = _story_for_revision(story_root, revision_id)
    previous_surfaces = _required_requirement_surfaces(previous_story, source_revision_id)
    current_surfaces = _required_requirement_surfaces(current_story, revision_id)
    removed, added, retained = _compare_surfaces(previous_surfaces, current_surfaces)

    previous_revision = next(
        (
            item
            for item in (story_root.get("revisions") if isinstance(story_root.get("revisions"), list) else [])
            if isinstance(item, dict) and str(item.get("revision_id", "") or "") == source_revision_id
        ),
        {},
    )
    payload.update(
        {
            "status": "ready",
            "cleanup_required": bool(removed),
            "removed_requirement_count": len(removed),
            "added_requirement_count": len(added),
            "retained_requirement_count": len(retained),
            "removed_requirement_surfaces": removed,
            "added_requirement_surfaces": added,
            "retained_requirement_surfaces": retained,
            "source_baseline_hash": str(previous_revision.get("baseline_hash", "") or ""),
        }
    )
    return payload


def load_revision_delta(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    materialize_if_missing: bool = False,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    payload = read_json(revision_delta_json_path(project_root, resolved_version, feature), {})
    if isinstance(payload, dict) and payload:
        payload.setdefault(
            "json_ref",
            str(revision_delta_json_path(project_root, resolved_version, feature).relative_to(project_root)),
        )
        payload.setdefault(
            "markdown_ref",
            str(revision_delta_markdown_path(project_root, resolved_version, feature).relative_to(project_root)),
        )
        return payload
    if not revision_delta_supported(resolved_version):
        return {}
    revision = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=False)
    if not str(revision.get("source_revision_id", "") or "").strip():
        return {}
    if materialize_if_missing:
        payload = materialize_revision_delta(project_root, version=resolved_version, feature=feature)
        return payload if isinstance(payload, dict) else {}
    payload = _computed_revision_delta_payload(project_root, version=resolved_version, feature=feature)
    return payload if isinstance(payload, dict) else {}


def _read_story_root(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    path = machine_story_path(project_root, version, feature)
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def _story_for_revision(root_state: dict[str, Any], revision_id: str) -> dict[str, Any]:
    for story in root_state.get("stories", []):
        if isinstance(story, dict) and str(story.get("revision_id", "") or "") == revision_id:
            return story
    return {}


def _normalize_text(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip()).strip().lower()
    return text


def _surface_signature(item: dict[str, Any]) -> str:
    details = item.get("details") if isinstance(item.get("details"), list) else []
    normalized_details = "|".join(_normalize_text(entry) for entry in details if _normalize_text(entry))
    return "::".join(
        [
            _normalize_text(item.get("kind")),
            _normalize_text(item.get("story_id")),
            _normalize_text(item.get("theme")),
            _normalize_text(item.get("text")),
            normalized_details,
        ]
    )


def _required_requirement_surfaces(story: dict[str, Any], revision_id: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in story.get("items", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("kind", "") or "") != "ac":
            continue
        if not bool(item.get("required", True)):
            continue
        payload = {
            "revision_id": revision_id,
            "id": str(item.get("id", "") or "").strip().upper(),
            "story_id": str(item.get("story_id", "") or "").strip().upper(),
            "kind": "ac",
            "theme": str(item.get("theme", "") or "").strip(),
            "text": str(item.get("text", "") or "").strip(),
            "details": [str(entry).strip() for entry in (item.get("details") or []) if str(entry).strip()],
            "source": str(item.get("source", "") or "").strip(),
        }
        payload["signature"] = _surface_signature(payload)
        out.append(payload)
    return out


def _compare_surfaces(previous: list[dict[str, Any]], current: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    previous_by_signature = {str(item.get("signature", "") or ""): item for item in previous if str(item.get("signature", "") or "").strip()}
    current_by_signature = {str(item.get("signature", "") or ""): item for item in current if str(item.get("signature", "") or "").strip()}
    removed_signatures = sorted(set(previous_by_signature) - set(current_by_signature))
    added_signatures = sorted(set(current_by_signature) - set(previous_by_signature))
    retained_signatures = sorted(set(previous_by_signature) & set(current_by_signature))
    return (
        [previous_by_signature[signature] for signature in removed_signatures],
        [current_by_signature[signature] for signature in added_signatures],
        [current_by_signature[signature] for signature in retained_signatures],
    )


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Beacon Revision Delta",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- revision_id: `{payload.get('revision_id', '')}`",
        f"- source_revision_id: `{payload.get('source_revision_id', '')}`",
        f"- status: `{payload.get('status', '')}`",
        f"- cleanup_required: `{bool(payload.get('cleanup_required', False))}`",
        f"- removed_requirement_count: `{payload.get('removed_requirement_count', 0)}`",
        f"- added_requirement_count: `{payload.get('added_requirement_count', 0)}`",
        "",
        "## Removed Requirement Surfaces",
    ]
    removed = payload.get("removed_requirement_surfaces") if isinstance(payload.get("removed_requirement_surfaces"), list) else []
    if removed:
        for item in removed:
            if not isinstance(item, dict):
                continue
            lines.append(f"- `{item.get('id', '')}` {item.get('text', '')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Added Requirement Surfaces"])
    added = payload.get("added_requirement_surfaces") if isinstance(payload.get("added_requirement_surfaces"), list) else []
    if added:
        for item in added:
            if not isinstance(item, dict):
                continue
            lines.append(f"- `{item.get('id', '')}` {item.get('text', '')}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def materialize_revision_delta(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    payload = _computed_revision_delta_payload(project_root, version=resolved_version, feature=feature)
    if not revision_delta_supported(resolved_version):
        return payload
    json_path = revision_delta_json_path(project_root, resolved_version, feature)
    markdown_path = revision_delta_markdown_path(project_root, resolved_version, feature)
    write_json(json_path, payload)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return payload
