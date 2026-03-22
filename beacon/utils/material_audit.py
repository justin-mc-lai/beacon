from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import execution_file_candidates, qa_matrix_candidates
from beacon.utils.versioning import normalize_version, resolve_target_version


def _parse_semver_tuple(value: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(value) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    return data if isinstance(data, dict) else None


def _status_from_checks(checks: list[dict[str, Any]]) -> str:
    if any(str(item.get("status", "")).lower() == "fail" for item in checks):
        return "fail"
    if any(str(item.get("status", "")).lower() == "warn" for item in checks):
        return "warn"
    return "pass"


def _feature_names(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    return {path.stem for path in directory.glob("*.md") if path.is_file() and path.stem != "index"}


def build_material_audit(project_root: Path | str, *, version: str | None = None, strict: bool = False) -> dict[str, Any]:
    root = Path(project_root)
    resolved_version = resolve_target_version(root, version)
    requires_minimum_closure = _parse_semver_tuple(resolved_version) >= (1, 1, 3)
    source_root = root / "docs" / "beacon" / resolved_version
    research_dir = source_root / "research"
    us_dir = source_root / "user-story"
    prd_dir = source_root / "prd"
    tc_dir = source_root / "qa" / "test-cases"
    release_dir = source_root / "release"
    boundaries_file = source_root / "execution" / "boundaries.md"
    summary_file = source_root / "SUMMARY.md"

    checks: list[dict[str, Any]] = []
    research_docs = sorted(str(path.relative_to(root)) for path in research_dir.glob("*.md")) if research_dir.exists() else []
    checks.append(
        {
            "name": "research_directory_present",
            "status": "pass" if requires_minimum_closure or research_dir.exists() else "fail",
            "details": {
                "path": str(research_dir.relative_to(root)),
                "exists": research_dir.exists(),
                "required": not requires_minimum_closure,
            },
        }
    )
    if requires_minimum_closure:
        research_status = "pass"
    else:
        research_status = "pass" if research_docs else ("fail" if strict else "warn")
    checks.append(
        {
            "name": "research_documents_present",
            "status": research_status,
            "details": {
                "count": len(research_docs),
                "documents": research_docs,
                "required": not requires_minimum_closure,
            },
        }
    )

    us_features = _feature_names(us_dir)
    prd_features = _feature_names(prd_dir)
    tc_features = _feature_names(tc_dir)
    feature_names = sorted(us_features | prd_features | tc_features)
    missing_by_feature: dict[str, list[str]] = {}
    for name in feature_names:
        missing: list[str] = []
        if name not in us_features:
            missing.append("user-story")
        if name not in prd_features:
            missing.append("prd")
        if name not in tc_features:
            missing.append("test-case")
        if not any(path.exists() for path in qa_matrix_candidates(root, resolved_version, name, "ac-test-matrix")):
            missing.append("ac-test-matrix")
        if not requires_minimum_closure and not any(
            path.exists() for path in qa_matrix_candidates(root, resolved_version, name, "qa9-matrix")
        ):
            missing.append("qa9-matrix")
        if missing:
            missing_by_feature[name] = missing

    feature_status = "pass"
    if not feature_names:
        feature_status = "fail"
    elif missing_by_feature:
        feature_status = "fail" if strict else "warn"
    checks.append(
        {
            "name": "main_chain_feature_completeness",
            "status": feature_status,
            "details": {
                "feature_count": len(feature_names),
                "features": feature_names,
                "missing_by_feature": missing_by_feature,
            },
        }
    )

    checks.append(
        {
            "name": "formal_summary_present",
            "status": "pass" if summary_file.exists() else "fail",
            "details": {"path": str(summary_file.relative_to(root)), "exists": summary_file.exists()},
        }
    )
    checks.append(
        {
            "name": "formal_boundaries_present",
            "status": "pass" if (boundaries_file.exists() or not requires_minimum_closure) else "fail",
            "details": {
                "path": str(boundaries_file.relative_to(root)),
                "exists": boundaries_file.exists(),
                "required": requires_minimum_closure,
            },
        }
    )

    release_docs = sorted(str(path.relative_to(root)) for path in release_dir.glob("*.md")) if release_dir.exists() else []
    checks.append(
        {
            "name": "formal_release_present",
            "status": "pass" if release_docs else "fail",
            "details": {"count": len(release_docs), "documents": release_docs},
        }
    )

    overall = _status_from_checks(checks)
    return {
        "schema_version": "1.0",
        "action": "verify-materials",
        "project_root": str(root),
        "version": resolved_version,
        "strict": strict,
        "status": overall,
        "ok": overall == "pass",
        "checks": checks,
    }


def build_delivery_audit(project_root: Path | str, *, version: str | None = None, strict: bool = False) -> dict[str, Any]:
    root = Path(project_root)
    resolved_version = resolve_target_version(root, version)
    exec_dir = root / "docs" / "beacon" / resolved_version / "execution"
    checks: list[dict[str, Any]] = []

    required_files = [
        "boundaries.md",
        "delivery-manifest.json",
        "change-impact.json",
        "config.json",
        "source.json",
        "git-alignment.json",
    ]
    missing = [
        name
        for name in required_files
        if not any(path.exists() for path in execution_file_candidates(root, resolved_version, name))
    ]
    checks.append(
        {
            "name": "execution_required_files_present",
            "status": "pass" if not missing else "fail",
            "details": {"missing": missing, "execution_dir": str(exec_dir.relative_to(root))},
        }
    )

    config_payload = next(
        (_read_json(path) for path in execution_file_candidates(root, resolved_version, "config.json") if path.exists()),
        None,
    )
    config_missing = []
    for key in ("resolved_project", "docs", "implementation", "source_info", "git", "research", "delivery"):
        if not isinstance(config_payload, dict) or key not in config_payload:
            config_missing.append(key)
    checks.append(
        {
            "name": "execution_config_schema",
            "status": "pass" if not config_missing else "fail",
            "details": {"missing_keys": config_missing},
        }
    )

    source_payload = next(
        (_read_json(path) for path in execution_file_candidates(root, resolved_version, "source.json") if path.exists()),
        None,
    )
    source_missing = []
    for key in ("project_name", "project_root", "workspace_root", "repo_url", "branch", "commit", "run_id", "version"):
        if not isinstance(source_payload, dict) or key not in source_payload:
            source_missing.append(key)
    checks.append(
        {
            "name": "execution_source_schema",
            "status": "pass" if not source_missing else "fail",
            "details": {"missing_keys": source_missing},
        }
    )

    git_payload = next(
        (_read_json(path) for path in execution_file_candidates(root, resolved_version, "git-alignment.json") if path.exists()),
        None,
    )
    git_missing = []
    for key in ("git_refs", "alignment", "version_ref", "blocked"):
        if not isinstance(git_payload, dict) or key not in git_payload:
            git_missing.append(key)
    git_status = "pass" if not git_missing else "fail"
    if not git_missing and isinstance(git_payload, dict) and bool(git_payload.get("blocked")):
        git_status = "fail" if strict else "warn"
    checks.append(
        {
            "name": "execution_git_alignment_schema",
            "status": git_status,
            "details": {
                "missing_keys": git_missing,
                "blocked": None if not isinstance(git_payload, dict) else bool(git_payload.get("blocked")),
                "reason_codes": [] if not isinstance(git_payload, dict) else git_payload.get("reason_codes", []),
            },
        }
    )

    manifest_payload = next(
        (_read_json(path) for path in execution_file_candidates(root, resolved_version, "delivery-manifest.json") if path.exists()),
        None,
    )
    manifest_missing = []
    affected_projects = []
    if not isinstance(manifest_payload, dict):
        manifest_missing.append("root")
    else:
        affected_projects = manifest_payload.get("affected_projects") if isinstance(manifest_payload.get("affected_projects"), list) else []
        if not affected_projects:
            manifest_missing.append("affected_projects")
        required_project_fields = {
            "name",
            "project_root",
            "repo_url",
            "change_scope",
            "changed_layers",
            "base_branch",
            "target_branch",
            "current_branch",
            "commit",
            "tag",
            "worktree_path",
        }
        incomplete = []
        for idx, item in enumerate(affected_projects):
            if not isinstance(item, dict):
                incomplete.append({"index": idx, "missing": sorted(required_project_fields)})
                continue
            missing_fields = sorted(k for k in required_project_fields if k not in item)
            if missing_fields:
                incomplete.append({"index": idx, "missing": missing_fields})
        if incomplete:
            manifest_missing.append({"affected_project_fields": incomplete})
    checks.append(
        {
            "name": "delivery_manifest_schema",
            "status": "pass" if not manifest_missing else "fail",
            "details": {"issues": manifest_missing},
        }
    )

    change_payload = next(
        (_read_json(path) for path in execution_file_candidates(root, resolved_version, "change-impact.json") if path.exists()),
        None,
    )
    change_missing = []
    pending_tasks: list[str] = []
    if not isinstance(change_payload, dict):
        change_missing.append("root")
    else:
        for key in ("changed_layers", "tasks", "research_converged", "main_chain_converged", "delivery_manifest_ready"):
            if key not in change_payload:
                change_missing.append(key)
        tasks = change_payload.get("tasks") if isinstance(change_payload.get("tasks"), list) else []
        pending_tasks = [
            str(item.get("task", ""))
            for item in tasks
            if isinstance(item, dict) and str(item.get("status", "pending")).strip().lower() != "completed"
        ]
    change_status = "pass" if not change_missing and not pending_tasks else ("fail" if strict else "warn")
    checks.append(
        {
            "name": "change_impact_schema_and_closure",
            "status": change_status,
            "details": {"missing_keys": change_missing, "pending_tasks": pending_tasks},
        }
    )

    terminal_path = execution_file_candidates(root, resolved_version, "terminal.json")[0]
    terminal_exists = any(path.exists() for path in execution_file_candidates(root, resolved_version, "terminal.json"))
    checks.append(
        {
            "name": "terminal_artifact_presence",
            "status": "pass" if terminal_exists else "warn",
            "details": {"exists": terminal_exists, "path": str(terminal_path.relative_to(root))},
        }
    )

    overall = _status_from_checks(checks)
    return {
        "schema_version": "1.0",
        "action": "verify-delivery",
        "project_root": str(root),
        "version": resolved_version,
        "strict": strict,
        "status": overall,
        "ok": overall == "pass",
        "checks": checks,
    }
