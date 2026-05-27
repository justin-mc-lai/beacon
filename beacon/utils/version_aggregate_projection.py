"""Version aggregate projection guard helpers.

These helpers maintain release-facing projection/read-model artifacts. They do
not define requirement truth and must not introduce a lifecycle stage.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import (
    change_docs_file,
    change_file_output,
    machine_execution_dir,
    qa_docs_file,
)
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.story_state import feature_slug


PROJECTION_ROLE = {
    "artifact_role": "version_aggregate_projection",
    "truth_source": False,
    "gate_source": False,
    "lifecycle_stage": False,
    "release_publish_action": False,
}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def version_aggregate_projection_repair_commands(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> list[str]:
    quoted_feature = f'"{feature}"'
    return [
        f"beacon doctor repair-version-aggregate-projection {quoted_feature} --project-root {project_root} --version {version} --json",
        f"beacon release create {version} --project {project_root}",
        f"beacon doctor build-test-contract-index {quoted_feature} --project-root {project_root} --version {version} --json",
        f"beacon doctor verify-test-contract-index {quoted_feature} --project-root {project_root} --version {version} --strict --json",
    ]


def feature_change_projection_status(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    slug = feature_slug(feature)
    path = change_file_output(project_root, version, f"{slug}.json")
    payload = _load_json(path)
    payload_version = str(payload.get("version") or "").strip()
    exists = bool(payload)
    version_match = bool(exists and (not payload_version or payload_version == version))
    status = "pass" if exists and version_match else "missing"
    reason_code = ""
    if not exists:
        reason_code = "feature_change_projection_missing"
    elif not version_match:
        status = "blocked"
        reason_code = "feature_change_projection_version_mismatch"
    return {
        "schema_version": "1.0",
        "status": status,
        "blocked": status == "blocked",
        "repairable": status in {"missing", "blocked"},
        "reason_code": reason_code,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "path": _rel(project_root, path),
        "exists": exists,
        "version_match": version_match,
        "projection_role": dict(PROJECTION_ROLE),
        "repair_commands": version_aggregate_projection_repair_commands(
            project_root,
            version=version,
            feature=feature,
        ),
    }


def _acceptance_payload(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    return _load_json(machine_execution_dir(project_root, version) / f"qa-acceptance-{feature_slug(feature)}.json")


def build_feature_change_projection(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    slug = feature_slug(feature)
    acceptance = _acceptance_payload(project_root, version=version, feature=feature)
    revision = load_revision_state(project_root, version=version, feature=feature, create_if_missing=False)
    accepted_at = str(acceptance.get("accepted_at") or acceptance.get("generated_at") or "").strip()
    status = "completed" if str(acceptance.get("verdict") or acceptance.get("status") or "").lower() in {"passed", "pass"} else "generated"
    summary = (
        "Maintains release-facing version aggregate projection guards so QA accepted "
        "features are included in version change scope before release check."
    )
    traceability_refs = [
        _rel(project_root, change_docs_file(project_root, version, f"{slug}.md")),
        _rel(project_root, project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md"),
        _rel(project_root, project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md"),
        _rel(project_root, qa_docs_file(project_root, version, f"{slug}.md")),
        _rel(project_root, machine_execution_dir(project_root, version) / f"{slug}.revision.json"),
    ]
    acceptance_path = machine_execution_dir(project_root, version) / f"qa-acceptance-{slug}.json"
    if acceptance_path.exists():
        traceability_refs.append(_rel(project_root, acceptance_path))
    return {
        "schema_version": "1.0",
        "version": version,
        "feature": feature,
        "feature_slug": slug,
        "summary": summary,
        "status": status,
        "accepted_at": accepted_at,
        "revision_id": str(revision.get("revision_id") or ""),
        "projection_role": dict(PROJECTION_ROLE),
        "truth_authority": False,
        "lifecycle_stage": False,
        "added": [
            "Feature-level release projection input for QA accepted current feature",
            "Version aggregate projection inclusion guard and repair metadata",
            "Repair-only projection rebuild path for release preflight artifacts",
        ],
        "removed": [
            "Manual-only version aggregate projection repair before release check"
        ],
        "fixed": [
            "Release check can route missing current feature projection to an actionable repair path",
            "Version aggregate projection remains a read model instead of requirement truth",
        ],
        "traceability_refs": [item for item in traceability_refs if item],
        "generated_at": _utc_now(),
    }


def write_feature_change_projection(
    project_root: Path,
    *,
    version: str,
    feature: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    slug = feature_slug(feature)
    payload = build_feature_change_projection(project_root, version=version, feature=feature)
    json_path = change_file_output(project_root, version, f"{slug}.json")
    md_path = change_docs_file(project_root, version, f"{slug}.md")
    wrote_json = overwrite or not json_path.exists()
    if wrote_json:
        write_json(json_path, payload)
    if not md_path.exists():
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(
            "\n".join(
                [
                    "# Beacon Feature Change Projection",
                    "",
                    f"- feature: `{feature}`",
                    f"- feature_slug: `{slug}`",
                    f"- version: `{version}`",
                    "- artifact_role: `release-facing projection/read model`",
                    "- truth_source: `false`",
                    "",
                    "## Scope",
                    f"- {payload['summary']}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return {
        "schema_version": "1.0",
        "status": "pass",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "json_path": _rel(project_root, json_path),
        "markdown_path": _rel(project_root, md_path),
        "json_written": wrote_json,
        "markdown_exists": md_path.exists(),
        "projection_role": dict(PROJECTION_ROLE),
        "payload": payload,
    }


def version_aggregate_projection_status(
    project_root: Path,
    *,
    version: str,
    current_feature: str,
) -> dict[str, Any]:
    slug = feature_slug(current_feature) if current_feature else ""
    markdown_path = change_docs_file(project_root, version, f"{version}.md")
    json_path = change_file_output(project_root, version, f"{version}.json")
    payload = _load_json(json_path)
    features = payload.get("features") if isinstance(payload.get("features"), list) else []
    feature_slugs = sorted(
        {
            str(item.get("feature_slug") or "").strip()
            for item in features
            if isinstance(item, dict) and str(item.get("feature_slug") or "").strip()
        }
    )
    markdown_exists = markdown_path.exists()
    json_exists = json_path.exists()
    version_match = bool(payload) and str(payload.get("version") or "").strip() == version
    includes_current_feature = (not slug) or slug in feature_slugs
    feature_projection = feature_change_projection_status(project_root, version=version, feature=current_feature) if slug else {}
    status = "pass" if markdown_exists and json_exists and version_match and includes_current_feature else "blocked"
    reason_code = ""
    if not markdown_exists or not json_exists or not payload:
        status = "missing"
        reason_code = "version_aggregate_projection_missing"
    elif not version_match:
        reason_code = "version_aggregate_projection_version_mismatch"
    elif not includes_current_feature:
        reason_code = "current_feature_missing_from_version_aggregate_projection"
        if str(feature_projection.get("status") or "") != "pass":
            reason_code = str(feature_projection.get("reason_code") or reason_code)
    return {
        "schema_version": "1.0",
        "status": status,
        "blocked": status != "pass",
        "reason_code": reason_code,
        "markdown_path": _rel(project_root, markdown_path),
        "json_path": _rel(project_root, json_path),
        "markdown_exists": markdown_exists,
        "json_exists": json_exists,
        "version_match": version_match,
        "feature_count": int(payload.get("feature_count") or len(feature_slugs) or 0),
        "feature_slugs": feature_slugs,
        "current_feature_slug": slug,
        "includes_current_feature": includes_current_feature,
        "feature_projection": feature_projection,
        "projection_role": dict(PROJECTION_ROLE),
        "repair_commands": version_aggregate_projection_repair_commands(
            project_root,
            version=version,
            feature=current_feature,
        ) if current_feature else [],
    }
