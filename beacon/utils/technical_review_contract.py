"""Deterministic technical review contract gates for v1.3.1+ implementation flows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file
from beacon.utils.implement_adapters import load_beacon_config
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.runtime import read_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version
from beacon.utils.workflow_memory import append_lifecycle_event, record_stage_writeback, resolve_workflow_run_id


_REQUIRED_STRING_FIELDS = (
    "feature",
    "feature_slug",
    "version",
    "revision_id",
    "base_branch",
    "target_branch",
    "branch_prefix",
    "worktree_root",
    "environment_mode",
    "isolation_strategy",
    "review_status",
    "approved_by",
    "reviewed_at",
)
_REQUIRED_BOOL_FIELDS = ("use_git_worktree",)
_REQUIRED_LIST_FIELDS = (
    "service_directories",
    "writable_services",
    "reference_only_services",
)


def technical_review_contract_supported(version: str | None) -> bool:
    normalized_full = normalize_version(version) or "v0.0.0"
    normalized = release_line_key(version) or normalized_full
    if normalized_full != normalized:
        return False
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch)) >= (1, 3, 1)
    except Exception:  # noqa: BLE001
        return False


def technical_review_contract_json_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, f"deterministic-implementation-contract-{feature_slug(feature)}.json")


def technical_review_contract_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return human_execution_file(project_root, resolved_version, f"deterministic-implementation-contract-{feature_slug(feature)}.md")


def load_technical_review_contract(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    path = technical_review_contract_json_path(project_root, resolved_version, feature)
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def technical_review_state_path(project_root: Path, feature: str) -> Path:
    return project_root / ".beacon" / "state" / f"technical-review-contract-{feature_slug(feature)}.json"


def load_technical_review_state(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(technical_review_state_path(project_root, feature), {})
    return payload if isinstance(payload, dict) else {}


def approved_technical_review_contract(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    contract = load_technical_review_contract(project_root, version=resolved_version, feature=feature)
    if not isinstance(contract, dict) or not contract:
        return {}
    if str(contract.get("review_status") or "").strip().lower() not in {"approved", "accepted"}:
        return {}
    validation = validate_technical_review_contract(
        contract,
        version=resolved_version,
        feature=feature,
        revision_id=str(contract.get("revision_id", "") or ""),
    )
    return contract if validation.get("valid") else {}


def technical_review_git_workflow_seed(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    service_directories = [
        str(item).strip()
        for item in (
            contract.get("writable_services")
            if isinstance(contract.get("writable_services"), list) and contract.get("writable_services")
            else contract.get("service_directories")
            if isinstance(contract.get("service_directories"), list)
            else []
        )
        if str(item).strip()
    ]
    mode = "workspace" if service_directories and service_directories != ["."] else "single-repo"
    return {
        "schema_version": "1.0",
        "feature": str(contract.get("feature", "") or ""),
        "feature_slug": str(contract.get("feature_slug", "") or ""),
        "version": str(contract.get("version", "") or ""),
        "mode": mode,
        "expected_branch": str(contract.get("target_branch", "") or ""),
        "branch_prefix": str(contract.get("branch_prefix", "") or ""),
        "base_branch": str(contract.get("base_branch", "") or ""),
        "use_git_worktree": bool(contract.get("use_git_worktree", False)),
        "require_clean_worktree_for_switch": bool(contract.get("require_clean_worktree_for_switch", True)),
        "service_directories": service_directories,
        "git_roots": service_directories,
        "worktree_root": str(contract.get("worktree_root", "") or ""),
        "source": "technical_review_contract",
        "generated_at": now_iso(),
    }


def validate_technical_review_contract(payload: dict[str, Any], *, version: str, feature: str, revision_id: str = "") -> dict[str, Any]:
    missing_fields: list[str] = []
    invalid_fields: list[str] = []

    for field in _REQUIRED_STRING_FIELDS:
        if not str(payload.get(field) or "").strip():
            missing_fields.append(field)
    for field in _REQUIRED_BOOL_FIELDS:
        if field not in payload or not isinstance(payload.get(field), bool):
            missing_fields.append(field)
    for field in _REQUIRED_LIST_FIELDS:
        value = payload.get(field)
        if not isinstance(value, list) or not all(str(item).strip() for item in value):
            missing_fields.append(field)

    if str(payload.get("feature") or "").strip() and str(payload.get("feature") or "").strip() != feature:
        invalid_fields.append("feature")
    if str(payload.get("feature_slug") or "").strip() and str(payload.get("feature_slug") or "").strip() != feature_slug(feature):
        invalid_fields.append("feature_slug")
    if str(payload.get("version") or "").strip() and str(payload.get("version") or "").strip() != version:
        invalid_fields.append("version")
    if revision_id and str(payload.get("revision_id") or "").strip() and str(payload.get("revision_id") or "").strip() != revision_id:
        invalid_fields.append("revision_id")
    if str(payload.get("review_status") or "").strip().lower() not in {"approved", "accepted"}:
        invalid_fields.append("review_status")

    return {
        "missing_fields": sorted(set(missing_fields)),
        "invalid_fields": sorted(set(invalid_fields)),
        "valid": not missing_fields and not invalid_fields,
    }


def _default_technical_review_contract(project_root: Path, *, version: str, feature: str, revision_id: str = "") -> dict[str, Any]:
    config = load_beacon_config(project_root)
    implementation_cfg = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    branch_guard_cfg = implementation_cfg.get("branch_guard") if isinstance(implementation_cfg.get("branch_guard"), dict) else {}
    git_roots = [
        str(item).strip()
        for item in branch_guard_cfg.get("git_roots", [])
        if str(item).strip()
    ] if isinstance(branch_guard_cfg.get("git_roots"), list) else []
    target_branch = str(branch_guard_cfg.get("expected_branch", "") or "").strip() or f"beacon/{version}"
    branch_prefix = str(branch_guard_cfg.get("branch_prefix", "") or "").strip()
    if not branch_prefix:
        branch_prefix = target_branch.split("/", 1)[0] + "/" if "/" in target_branch else "beacon/"
    service_directories = git_roots or ["."]
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "revision_id": revision_id or "",
        "base_branch": str(branch_guard_cfg.get("base_branch", "") or "main").strip() or "main",
        "target_branch": target_branch,
        "branch_prefix": branch_prefix,
        "branch_strategy": "single-branch" if not git_roots else "workspace-multi-service",
        "use_git_worktree": bool(branch_guard_cfg.get("use_git_worktree", False)),
        "worktree_root": str(project_root),
        "service_worktrees": [],
        "workspace_root": str(project_root),
        "environment_mode": "local-dev",
        "isolation_strategy": "repo-local isolation",
        "shared_resources_allowed": [],
        "protected_resources": [],
        "service_directories": service_directories,
        "writable_services": service_directories,
        "reference_only_services": ["docs"],
        "excluded_services": [],
        "gateway_services": [],
        "bff_services": [],
        "downstream_services": [],
        "shared_schema_or_contracts": [],
        "cross_service_change_order": [],
        "review_status": "draft",
        "approved_by": "",
        "reviewed_at": "",
        "generated_at": now_iso(),
        "source": "project_config_seed" if branch_guard_cfg else "version_default",
        "notes": [
            "This draft contract must be reviewed and approved before formal implementation.",
            "Fill approved_by/reviewed_at and update review_status to approved or accepted.",
        ],
    }


def _render_technical_review_contract_markdown(payload: dict[str, Any]) -> str:
    def _list_block(title: str, values: list[str] | None) -> list[str]:
        lines = [f"## {title}"]
        items = [str(item).strip() for item in (values or []) if str(item).strip()]
        if not items:
            lines.append("- none")
        else:
            lines.extend(f"- `{item}`" for item in items)
        lines.append("")
        return lines

    lines = [
        "# Deterministic Implementation Contract",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- revision_id: `{payload.get('revision_id', '')}`",
        f"- review_status: `{payload.get('review_status', '')}`",
        f"- approved_by: `{payload.get('approved_by', '')}`",
        f"- reviewed_at: `{payload.get('reviewed_at', '')}`",
        "",
        "## Git",
        f"- base_branch: `{payload.get('base_branch', '')}`",
        f"- target_branch: `{payload.get('target_branch', '')}`",
        f"- branch_prefix: `{payload.get('branch_prefix', '')}`",
        f"- branch_strategy: `{payload.get('branch_strategy', '')}`",
        "",
        "## Worktree",
        f"- use_git_worktree: `{payload.get('use_git_worktree', False)}`",
        f"- worktree_root: `{payload.get('worktree_root', '')}`",
        f"- workspace_root: `{payload.get('workspace_root', '')}`",
        "",
        "## Environment Isolation",
        f"- environment_mode: `{payload.get('environment_mode', '')}`",
        f"- isolation_strategy: `{payload.get('isolation_strategy', '')}`",
        "",
    ]
    lines.extend(_list_block("Service Directories", payload.get("service_directories") if isinstance(payload.get("service_directories"), list) else []))
    lines.extend(_list_block("Writable Services", payload.get("writable_services") if isinstance(payload.get("writable_services"), list) else []))
    lines.extend(_list_block("Reference-only Services", payload.get("reference_only_services") if isinstance(payload.get("reference_only_services"), list) else []))
    notes = payload.get("notes") if isinstance(payload.get("notes"), list) else []
    lines.extend(_list_block("Notes", notes))
    return "\n".join(lines).rstrip() + "\n"


def write_technical_review_contract_writeback(
    project_root: Path,
    *,
    version: str,
    feature: str,
    contract: dict[str, Any],
    source: str = "doctor.sync-technical-review-contract",
    run_id: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    json_path = technical_review_contract_json_path(project_root, resolved_version, feature)
    markdown_path = technical_review_contract_markdown_path(project_root, resolved_version, feature)
    state_path = technical_review_state_path(project_root, feature)
    resolved_run_id = run_id or resolve_workflow_run_id(project_root, version=resolved_version, feature=feature) or ""
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "revision_id": str(contract.get("revision_id", "") or ""),
        "review_status": str(contract.get("review_status", "") or ""),
        "approved_by": str(contract.get("approved_by", "") or ""),
        "reviewed_at": str(contract.get("reviewed_at", "") or ""),
        "contract_json_path": str(json_path.relative_to(project_root)),
        "contract_markdown_path": str(markdown_path.relative_to(project_root)),
        "run_id": resolved_run_id,
        "source": source,
        "written_at": now_iso(),
    }
    write_json(state_path, payload)

    if resolved_run_id:
        evidence_ref = [
            str(json_path.relative_to(project_root)),
            str(markdown_path.relative_to(project_root)),
            str(state_path.relative_to(project_root)),
        ]
        append_lifecycle_event(
            project_root,
            run_id=resolved_run_id,
            stage="technical-review",
            event="contract_synced",
            source=source,
            evidence_ref=evidence_ref,
            details={"review_status": payload["review_status"]},
        )
        if payload["review_status"] in {"approved", "accepted"}:
            record_stage_writeback(
                project_root,
                run_id=resolved_run_id,
                stage="technical-review",
                feature=feature,
                evidence_ref=evidence_ref,
                status=payload["review_status"],
            )
    return {
        **payload,
        "state_path": str(state_path.relative_to(project_root)),
    }


def materialize_technical_review_contract(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    revision_id: str = "",
    force_refresh: bool = False,
    contract_overrides: dict[str, Any] | None = None,
    source: str = "doctor.sync-technical-review-contract",
    run_id: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    existing = load_technical_review_contract(project_root, version=resolved_version, feature=feature)
    if existing and not force_refresh:
        payload = dict(existing)
    else:
        payload = _default_technical_review_contract(
            project_root,
            version=resolved_version,
            feature=feature,
            revision_id=revision_id,
        )
    if contract_overrides:
        for key, value in contract_overrides.items():
            if value is None:
                continue
            payload[key] = value
    if revision_id:
        payload["revision_id"] = revision_id
    payload["feature"] = feature
    payload["feature_slug"] = feature_slug(feature)
    payload["version"] = resolved_version
    json_path = technical_review_contract_json_path(project_root, resolved_version, feature)
    markdown_path = technical_review_contract_markdown_path(project_root, resolved_version, feature)
    write_json(json_path, payload)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_technical_review_contract_markdown(payload), encoding="utf-8")
    writeback = write_technical_review_contract_writeback(
        project_root,
        version=resolved_version,
        feature=feature,
        contract=payload,
        source=source,
        run_id=run_id,
    )
    payload["writeback"] = writeback
    return payload


def build_technical_review_gate_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    revision_id: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    json_path = technical_review_contract_json_path(project_root, resolved_version, feature)
    markdown_path = technical_review_contract_markdown_path(project_root, resolved_version, feature)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "required": technical_review_contract_supported(resolved_version),
        "contract_json_path": str(json_path.relative_to(project_root)),
        "contract_markdown_path": str(markdown_path.relative_to(project_root)),
        "blocked": False,
        "status": "pass",
        "reason_code": "",
    }
    if not payload["required"]:
        return payload
    if not json_path.exists():
        payload.update(
            {
                "blocked": True,
                "status": "blocked",
                "reason_code": "technical_review_contract_missing",
            }
        )
        return payload
    contract = load_technical_review_contract(project_root, version=resolved_version, feature=feature)
    if not contract:
        payload.update(
            {
                "blocked": True,
                "status": "blocked",
                "reason_code": "technical_review_contract_invalid",
                "validation": {"missing_fields": ["payload"], "invalid_fields": [], "valid": False},
            }
        )
        return payload
    validation = validate_technical_review_contract(contract, version=resolved_version, feature=feature, revision_id=revision_id)
    payload["contract"] = contract
    payload["validation"] = validation
    if not validation["valid"]:
        payload.update(
            {
                "blocked": True,
                "status": "blocked",
                "reason_code": "technical_review_contract_invalid",
            }
        )
        return payload
    return payload
