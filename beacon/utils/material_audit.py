from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import execution_file_candidates, qa_matrix_candidates
from beacon.utils.implementation_plan import list_implementation_git_workflow_contracts
from beacon.utils.revision_state import load_revision_state, revision_state_file
from beacon.utils.story_state import _baseline_hash, machine_story_path
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version


def _parse_semver_tuple(value: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(value) or normalize_version(value) or "v0.0.0"
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


_PROTOTYPE_SOURCE_STATUS_RE = re.compile(r"^\*\*Status\*\*:\s*`prototype-source`", re.MULTILINE)


def _is_prototype_source_material(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return False
    return bool(_PROTOTYPE_SOURCE_STATUS_RE.search(text))


def _feature_names(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    names: set[str] = set()
    for path in directory.glob("*.md"):
        if not path.is_file() or path.stem == "index":
            continue
        if _is_prototype_source_material(path):
            continue
        names.add(path.stem)
    return names


def _requirement_package_failure_summary(checks: list[dict[str, Any]]) -> dict[str, Any]:
    categories: list[str] = []
    details: list[dict[str, Any]] = []

    def _push(category: str, detail: dict[str, Any]) -> None:
        if category not in categories:
            categories.append(category)
        details.append({"category": category, **detail})

    for item in checks:
        if not isinstance(item, dict) or str(item.get("status") or "").lower() != "fail":
            continue
        name = str(item.get("name") or "").strip()
        info = item.get("details") if isinstance(item.get("details"), dict) else {}
        if name == "main_chain_feature_completeness":
            missing_by_feature = info.get("missing_by_feature") if isinstance(info.get("missing_by_feature"), dict) else {}
            for feature, missing in missing_by_feature.items():
                if not isinstance(missing, list):
                    continue
                for missing_item in missing:
                    category = {
                        "user-story": "missing_human_user_story",
                        "prd": "missing_human_prd",
                        "test-case": "missing_human_test_case",
                        "ac-test-matrix": "missing_machine_ac_matrix",
                        "machine-user-story": "missing_machine_user_story",
                        "story-scenario-map": "missing_machine_story_scenario_map",
                        "qa9-matrix": "missing_machine_qa9_matrix",
                    }.get(str(missing_item), "missing_requirement_artifact")
                    _push(category, {"feature": str(feature), "artifact": str(missing_item)})
        elif name == "change_loop_requirement_package_sync":
            drift_by_feature = info.get("drift_by_feature") if isinstance(info.get("drift_by_feature"), dict) else {}
            for feature, drift in drift_by_feature.items():
                if not isinstance(drift, dict):
                    continue
                reason = str(drift.get("reason") or "requirement_package_drift")
                category = {
                    "revision_state_missing": "missing_revision_state",
                    "baseline_hash_missing": "baseline_hash_missing",
                    "baseline_hash_mismatch": "baseline_hash_mismatch",
                }.get(reason, "requirement_package_drift")
                _push(
                    category,
                    {
                        "feature": str(feature),
                        "path": str(drift.get("path") or ""),
                        "expected_hash": str(drift.get("expected_hash") or ""),
                        "actual_hash": str(drift.get("actual_hash") or ""),
                    },
                )
        else:
            _push(f"material_check_failed:{name}", {"check": name})
    return {
        "categories": categories,
        "details": details,
    }


def build_material_audit(project_root: Path | str, *, version: str | None = None, strict: bool = False) -> dict[str, Any]:
    root = Path(project_root)
    resolved_version = resolve_target_version(root, version)
    requires_minimum_closure = _parse_semver_tuple(resolved_version) >= (1, 1, 3)
    requires_change_loop_dual_write = _parse_semver_tuple(resolved_version) >= (1, 3, 10)
    source_root = root / "docs" / "beacon" / resolved_version
    research_dir = source_root / "research"
    us_dir = source_root / "user-story"
    prd_dir = source_root / "prd"
    tc_dir = source_root / "qa" / "test-cases"
    release_dir = source_root / "release"
    boundaries_file = source_root / "execution" / "boundaries.md"
    project_skill_blueprint = source_root / "execution" / "project-skill-qa-evolution-blueprint.md"
    source_arch_index = source_root / "source-architecture" / "index.md"
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
        if requires_change_loop_dual_write and not machine_story_path(root, resolved_version, name).exists():
            missing.append("machine-user-story")
        if requires_change_loop_dual_write and not any(
            path.exists() for path in qa_matrix_candidates(root, resolved_version, name, "story-scenario-map")
        ):
            missing.append("story-scenario-map")
        if not requires_minimum_closure and not any(
            path.exists() for path in qa_matrix_candidates(root, resolved_version, name, "qa9-matrix")
        ):
            missing.append("qa9-matrix")
        if missing:
            missing_by_feature[name] = missing

    revision_drift_by_feature: dict[str, dict[str, Any]] = {}
    if requires_change_loop_dual_write:
        for name in feature_names:
            revision_path = revision_state_file(root, resolved_version, name)
            if not revision_path.exists():
                revision_drift_by_feature[name] = {
                    "reason": "revision_state_missing",
                    "path": str(revision_path.relative_to(root)),
                }
                continue
            revision = load_revision_state(root, version=resolved_version, feature=name, create_if_missing=False)
            expected_hash = str(revision.get("baseline_hash") or "").strip()
            actual_hash = str(_baseline_hash(root, resolved_version, name) or "").strip()
            if not expected_hash:
                revision_drift_by_feature[name] = {
                    "reason": "baseline_hash_missing",
                    "path": str(revision_path.relative_to(root)),
                    "actual_hash": actual_hash,
                }
                continue
            if expected_hash != actual_hash:
                revision_drift_by_feature[name] = {
                    "reason": "baseline_hash_mismatch",
                    "path": str(revision_path.relative_to(root)),
                    "expected_hash": expected_hash,
                    "actual_hash": actual_hash,
                }

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
    if requires_change_loop_dual_write:
        revision_drift_status = "pass" if not revision_drift_by_feature else ("fail" if strict else "warn")
        checks.append(
            {
                "name": "change_loop_requirement_package_sync",
                "status": revision_drift_status,
                "details": {
                    "feature_count": len(feature_names),
                    "drift_by_feature": revision_drift_by_feature,
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
    if _parse_semver_tuple(resolved_version) >= (1, 1, 10):
        checks.append(
            {
                "name": "formal_project_skill_blueprint_present",
                "status": "pass" if project_skill_blueprint.exists() else "fail",
                "details": {
                    "path": str(project_skill_blueprint.relative_to(root)),
                    "exists": project_skill_blueprint.exists(),
                },
            }
        )
        checks.append(
            {
                "name": "formal_source_architecture_present",
                "status": "pass" if source_arch_index.exists() else "fail",
                "details": {
                    "path": str(source_arch_index.relative_to(root)),
                    "exists": source_arch_index.exists(),
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

    workflow_contracts = list_implementation_git_workflow_contracts(root, version=resolved_version)
    workflow_required = _parse_semver_tuple(resolved_version) >= (1, 3, 0)
    workflow_missing: list[str] = []
    workflow_invalid: list[dict[str, Any]] = []
    workflow_markdown_missing: list[str] = []
    expected_branches: list[str] = []
    required_workflow_fields = {
        "feature",
        "feature_slug",
        "version",
        "mode",
        "expected_branch",
        "branch_prefix",
        "base_branch",
        "use_git_worktree",
        "require_clean_worktree_for_switch",
        "service_directories",
    }
    machine_exec_dir = root / "docs" / "beacon" / resolved_version / ".machine" / "execution"
    for plan_path in sorted(machine_exec_dir.glob("implementation-plan-*.json")):
        if str(plan_path.name).endswith(".progress.json"):
            continue
        expected_name = plan_path.name.replace("implementation-plan-", "git-workflow-")
        workflow_path = machine_exec_dir / expected_name
        if not workflow_path.exists():
            workflow_missing.append(str(workflow_path.relative_to(root)))
    for item in workflow_contracts:
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        path = str(item.get("path", "") or "")
        missing = sorted(field for field in required_workflow_fields if field not in payload)
        if missing:
            workflow_invalid.append({"path": path, "missing": missing})
        expected_branches.append(str(payload.get("expected_branch", "") or ""))
        markdown_path = root / path.replace("/.machine/execution/", "/execution/").replace(".json", ".md")
        if not markdown_path.exists():
            workflow_markdown_missing.append(str(markdown_path.relative_to(root)))
    workflow_status = "pass"
    if workflow_required and (workflow_missing or workflow_invalid or workflow_markdown_missing):
        workflow_status = "fail" if strict else "warn"
    checks.append(
        {
            "name": "execution_git_workflow_contract",
            "status": workflow_status,
            "details": {
                "required": workflow_required,
                "count": len(workflow_contracts),
                "paths": [str(item.get("path", "") or "") for item in workflow_contracts],
                "missing_contracts": workflow_missing,
                "invalid_contracts": workflow_invalid,
                "missing_markdown": workflow_markdown_missing,
            },
        }
    )
    if manifest_missing:
        manifest_branch_status = "pass"
        branch_mismatch_details: list[dict[str, Any]] = []
    else:
        normalized_expected_branches = sorted({item for item in expected_branches if item})
        branch_mismatch_details = []
        if normalized_expected_branches and isinstance(manifest_payload, dict):
            affected_projects = manifest_payload.get("affected_projects") if isinstance(manifest_payload.get("affected_projects"), list) else []
            for idx, item in enumerate(affected_projects):
                if not isinstance(item, dict):
                    continue
                target_branch = str(item.get("target_branch", "") or "")
                if target_branch and target_branch not in normalized_expected_branches:
                    branch_mismatch_details.append(
                        {
                            "index": idx,
                            "target_branch": target_branch,
                            "expected_branches": normalized_expected_branches,
                        }
                    )
        manifest_branch_status = "pass" if not branch_mismatch_details else ("fail" if strict else "warn")
    checks.append(
        {
            "name": "delivery_manifest_git_workflow_alignment",
            "status": manifest_branch_status,
            "details": {"branch_mismatches": branch_mismatch_details},
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


def build_requirement_package_gate(
    project_root: Path | str,
    *,
    version: str | None = None,
    feature: str = "",
    strict: bool = True,
) -> dict[str, Any]:
    root = Path(project_root)
    resolved_version = resolve_target_version(root, version)
    if _parse_semver_tuple(resolved_version) < (1, 3, 10):
        return {
            "schema_version": "1.0",
            "status": "pass",
            "enabled": False,
            "version": resolved_version,
            "feature": feature,
            "reason_code": "",
            "remediation_mode": "not_required",
            "recommended_action": "",
            "recommended_reason": "",
            "recommended_command": "",
            "audit": {},
        }
    audit = build_material_audit(root, version=resolved_version, strict=strict)
    status = str(audit.get("status") or "fail").lower()
    failing_checks = [
        item for item in audit.get("checks", [])
        if isinstance(item, dict) and str(item.get("status") or "").lower() == "fail"
    ]
    failure_summary = _requirement_package_failure_summary(failing_checks)
    failure_categories = failure_summary.get("categories", [])
    drift_categories = {"missing_human_user_story", "missing_human_prd", "missing_human_test_case", "missing_revision_state", "baseline_hash_missing", "baseline_hash_mismatch"}
    machine_repair_categories = {
        "missing_machine_ac_matrix",
        "missing_machine_user_story",
        "missing_machine_story_scenario_map",
        "missing_machine_qa9_matrix",
    }
    recommended_action = ""
    recommended_reason = ""
    remediation_mode = "none" if status == "pass" else "verify"
    recommended_command = ""
    if status != "pass":
        if str(feature or "").strip() and any(category in drift_categories for category in failure_categories):
            remediation_mode = "change-loop"
            recommended_action = "beacon-change"
            recommended_reason = "frozen requirement package drifted from the approved baseline and must re-enter the change loop"
            recommended_command = "beacon-change"
        elif str(feature or "").strip() and any(category in machine_repair_categories for category in failure_categories):
            remediation_mode = "repair"
            recommended_action = "doctor-sync-materials"
            recommended_reason = "machine requirement artifacts are missing and should be rebuilt from the current human package"
            recommended_command = (
                f"beacon doctor sync-materials --project-root {root} --version {resolved_version} "
                f"--feature {feature} --single-feature"
            )
        else:
            remediation_mode = "verify"
            recommended_action = "doctor-verify-materials"
            recommended_reason = "version-line requirement package closure is incomplete and must be diagnosed before repair"
            recommended_command = f"beacon doctor verify-materials --project-root {root} --version {resolved_version} --strict"
    return {
        "schema_version": "1.0",
        "status": "pass" if status == "pass" else "blocked",
        "enabled": True,
        "version": resolved_version,
        "feature": feature,
        "reason_code": "" if status == "pass" else "requirement_package_contract_blocked",
        "failing_checks": failing_checks,
        "failure_categories": failure_categories,
        "failure_details": failure_summary.get("details", []),
        "remediation_mode": remediation_mode,
        "recommended_action": recommended_action,
        "recommended_reason": recommended_reason,
        "audit": audit,
        "recommended_command": recommended_command,
    }
