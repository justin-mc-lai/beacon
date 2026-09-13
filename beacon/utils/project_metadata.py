"""Project topology and version-branch metadata support helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.branch_governance import resolve_branch_governance_view
from beacon.utils.project_governance import (
    commit_governance_payload,
    governance_json_forbidden,
    governance_md_authoritative,
    governance_md_path,
    load_governance_payload,
    migrate_json_to_governance_md,
    read_governance_md_source_hash,
    resolve_project_governance,
    verify_governance_projection,
)
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.runtime_projection_store import _connect, runtime_ledger_db_path


def metadata_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "metadata"


def metadata_machine_path(project_root: Path) -> Path:
    return metadata_root(project_root) / "project-version-metadata.json"


def metadata_human_path(project_root: Path) -> Path:
    return metadata_root(project_root) / "project-version-metadata.md"


def metadata_state_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "project-metadata" / "latest.json"


def metadata_transactions_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "transactions"


def _default_payload(project_root: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "project_root": str(project_root.resolve()),
        "global_project_metadata": {
            "project_root": str(project_root.resolve()),
            "topology_kind": "",
            "default_execution_service": "",
            "service_bindings": [],
        },
        "version_scoped_metadata": {},
        "transaction": {},
    }


def load_project_metadata(project_root: Path) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    if governance_md_authoritative(root):
        return load_governance_payload(root)
    payload = read_json(metadata_machine_path(root), {})
    if not isinstance(payload, dict) or not payload:
        return _default_payload(root)
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("project_root", str(root))
    global_meta = payload.get("global_project_metadata")
    if not isinstance(global_meta, dict):
        global_meta = {}
    global_meta.setdefault("project_root", str(root))
    global_meta.setdefault("topology_kind", "")
    global_meta.setdefault("default_execution_service", "")
    global_meta.setdefault("service_bindings", [])
    payload["global_project_metadata"] = global_meta
    version_meta = payload.get("version_scoped_metadata")
    payload["version_scoped_metadata"] = version_meta if isinstance(version_meta, dict) else {}
    payload.setdefault("transaction", {})
    return payload


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _normalize_service_binding(
    *,
    project_root: Path,
    service_key: str,
    repo_root: str,
    role: str,
    writable: bool,
    worktree_path_policy: str,
) -> dict[str, Any]:
    resolved_repo = Path(repo_root).expanduser().resolve()
    return {
        "service_key": str(service_key).strip(),
        "repo_root": str(resolved_repo),
        "repo_root_relative": str(resolved_repo.relative_to(project_root)) if resolved_repo.is_relative_to(project_root) else "",
        "role": str(role or "service").strip() or "service",
        "writable": bool(writable),
        "worktree_path_policy": str(worktree_path_policy or "follow-repo-root").strip() or "follow-repo-root",
    }


def _render_human(payload: dict[str, Any]) -> str:
    global_meta = payload.get("global_project_metadata") if isinstance(payload.get("global_project_metadata"), dict) else {}
    version_meta = payload.get("version_scoped_metadata") if isinstance(payload.get("version_scoped_metadata"), dict) else {}
    transaction = payload.get("transaction") if isinstance(payload.get("transaction"), dict) else {}
    lines = [
        "# Project Version Metadata",
        "",
        f"- project_root: `{payload.get('project_root', '')}`",
        f"- topology_kind: `{global_meta.get('topology_kind', '')}`",
        f"- default_execution_service: `{global_meta.get('default_execution_service', '')}`",
        f"- transaction_id: `{transaction.get('transaction_id', '')}`",
        f"- committed_at: `{transaction.get('committed_at', '')}`",
        "",
        "## Service Bindings",
    ]
    bindings = global_meta.get("service_bindings") if isinstance(global_meta.get("service_bindings"), list) else []
    if not bindings:
        lines.append("- none")
    else:
        for item in bindings:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"`{item.get('service_key', '')}` "
                f"repo_root=`{item.get('repo_root', '')}` "
                f"role=`{item.get('role', '')}` "
                f"writable=`{item.get('writable', False)}`"
            )
    lines.extend(["", "## Version Contracts"])
    if not version_meta:
        lines.append("- none")
    else:
        for version in sorted(version_meta):
            contract = version_meta.get(version)
            if not isinstance(contract, dict):
                continue
            lines.append(
                "- "
                f"`{version}` "
                f"services=`{', '.join(contract.get('participating_services', []))}` "
                f"branch_guard_mode=`{contract.get('branch_guard_mode', '')}` "
                f"validation_state=`{contract.get('validation_state', '')}`"
            )
            per_service = contract.get("per_service_canonical_branch")
            if isinstance(per_service, dict):
                for service_key, branch in sorted(per_service.items()):
                    lines.append(f"  - `{service_key}` -> `{branch}`")
            governance = contract.get("branch_governance") if isinstance(contract.get("branch_governance"), dict) else {}
            template_name = str(contract.get("branch_governance_template") or governance.get("template_name") or "").strip()
            previous_baseline = str(contract.get("previous_version_baseline_branch") or governance.get("previous_version_baseline_branch") or "").strip()
            next_feature = str(contract.get("next_version_feature_branch") or governance.get("next_version_feature_branch") or "").strip()
            if template_name or previous_baseline or next_feature:
                lines.append(
                    "  - "
                    f"template=`{template_name}` "
                    f"previous=`{previous_baseline}` "
                    f"next=`{next_feature}`"
                )
    return "\n".join(lines) + "\n"


def _ensure_metadata_sqlite_schema() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS project_metadata_current (
                project_root TEXT PRIMARY KEY,
                topology_kind TEXT NOT NULL,
                default_execution_service TEXT NOT NULL,
                transaction_id TEXT NOT NULL,
                committed_at TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS project_metadata_events (
                transaction_id TEXT PRIMARY KEY,
                project_root TEXT NOT NULL,
                event_type TEXT NOT NULL,
                committed_at TEXT NOT NULL,
                source_hash TEXT NOT NULL DEFAULT '',
                payload_json TEXT NOT NULL
            );
            """
        )
        columns = {
            str(row[1])
            for row in conn.execute("PRAGMA table_info(project_metadata_events)").fetchall()
        }
        if "source_hash" not in columns:
            conn.execute("ALTER TABLE project_metadata_events ADD COLUMN source_hash TEXT NOT NULL DEFAULT ''")
            conn.commit()


def _write_sqlite_projection(project_root: Path, payload: dict[str, Any], *, event_type: str) -> dict[str, Any]:
    _ensure_metadata_sqlite_schema()
    transaction = payload.get("transaction") if isinstance(payload.get("transaction"), dict) else {}
    root = project_root.expanduser().resolve()
    source_hash = read_governance_md_source_hash(root) or str(transaction.get("source_hash", "") or "")
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO project_metadata_current (
                project_root, topology_kind, default_execution_service, transaction_id, committed_at, source_hash, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_root) DO UPDATE SET
                topology_kind=excluded.topology_kind,
                default_execution_service=excluded.default_execution_service,
                transaction_id=excluded.transaction_id,
                committed_at=excluded.committed_at,
                source_hash=excluded.source_hash,
                payload_json=excluded.payload_json
            """,
            (
                str(root),
                str(payload.get("global_project_metadata", {}).get("topology_kind", "") or ""),
                str(payload.get("global_project_metadata", {}).get("default_execution_service", "") or ""),
                str(transaction.get("transaction_id", "") or ""),
                str(transaction.get("committed_at", "") or ""),
                source_hash,
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO project_metadata_events (
                transaction_id, project_root, event_type, committed_at, source_hash, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(transaction.get("transaction_id", "") or ""),
                str(root),
                event_type,
                str(transaction.get("committed_at", "") or ""),
                source_hash,
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        conn.commit()
    return {"status": "ok", "db_path": str(runtime_ledger_db_path()), "source_hash": source_hash}


def _commit_payload(project_root: Path, payload: dict[str, Any], *, event_type: str) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    governance_summary = commit_governance_payload(root, payload, event_type=event_type)
    sqlite = _write_sqlite_projection(root, load_governance_payload(root), event_type=event_type)
    md_path = governance_md_path(root)
    return {
        "project_root": str(root),
        "payload_path": governance_summary["governance_md_path"],
        "markdown_path": governance_summary["governance_md_path"],
        "payload_abs_path": str(md_path),
        "markdown_abs_path": str(md_path),
        "transaction_path": "",
        "transaction_abs_path": "",
        "transaction_id": governance_summary["transaction_id"],
        "committed_at": governance_summary["committed_at"],
        "authority": "markdown_project_governance",
        "sqlite": sqlite,
        "governance_summary": governance_summary,
    }


def _upsert_service_binding(service_bindings: list[dict[str, Any]], binding: dict[str, Any]) -> list[dict[str, Any]]:
    key = str(binding.get("service_key") or "").strip()
    updated = [item for item in service_bindings if str(item.get("service_key") or "").strip() != key]
    updated.append(binding)
    updated.sort(key=lambda item: str(item.get("service_key") or ""))
    return updated


def _upsert_version_contract(
    version_map: dict[str, Any],
    *,
    root: Path,
    version: str,
    service_key: str,
    branch: str,
    branch_guard_mode: str,
    validation_state: str,
    truth_canonical: str = "",
    branch_governance_template: str = "",
    previous_version_baseline_branch: str = "",
    next_version_feature_branch: str = "",
    hotfix_branch_naming_rule: str = "",
    allow_worktree_when_feature_dirty: bool | None = None,
    merge_direction_policy: list[str] | None = None,
    forbidden_directions: list[str] | None = None,
    evidence_contract: list[str] | None = None,
    evidence: dict[str, str] | None = None,
    worktree_mode: str = "",
    worktree_path: str = "",
    require_workspace_admission: bool | None = None,
) -> dict[str, Any]:
    contract = version_map.get(version)
    if not isinstance(contract, dict):
        contract = {}
    services = contract.get("participating_services")
    services = list(services) if isinstance(services, list) else []
    if service_key and service_key not in services:
        services.append(service_key)
    services = sorted({str(item).strip() for item in services if str(item).strip()})
    per_service = contract.get("per_service_canonical_branch")
    per_service = dict(per_service) if isinstance(per_service, dict) else {}
    if service_key and branch:
        per_service[service_key] = branch
    current_governance = contract.get("branch_governance") if isinstance(contract.get("branch_governance"), dict) else {}
    normalized_governance = {
        **current_governance,
        "template_name": str(branch_governance_template or current_governance.get("template_name") or contract.get("branch_governance_template") or "").strip(),
        "previous_version_baseline_branch": str(previous_version_baseline_branch or current_governance.get("previous_version_baseline_branch") or contract.get("previous_version_baseline_branch") or "").strip(),
        "next_version_feature_branch": str(next_version_feature_branch or current_governance.get("next_version_feature_branch") or contract.get("next_version_feature_branch") or "").strip(),
        "hotfix_branch_naming_rule": str(hotfix_branch_naming_rule or current_governance.get("hotfix_branch_naming_rule") or contract.get("hotfix_branch_naming_rule") or "").strip(),
        "allow_worktree_when_feature_dirty": (
            bool(allow_worktree_when_feature_dirty)
            if allow_worktree_when_feature_dirty is not None
            else bool(current_governance.get("allow_worktree_when_feature_dirty", contract.get("allow_worktree_when_feature_dirty", False)))
        ),
        "merge_direction_policy": [str(item).strip() for item in (merge_direction_policy or current_governance.get("merge_direction_policy") or contract.get("merge_direction_policy") or []) if str(item).strip()],
        "forbidden_directions": [str(item).strip() for item in (forbidden_directions or current_governance.get("forbidden_directions") or contract.get("forbidden_directions") or []) if str(item).strip()],
        "evidence_contract": [str(item).strip() for item in (evidence_contract or current_governance.get("evidence_contract") or contract.get("evidence_contract") or []) if str(item).strip()],
        "evidence": {
            str(key).strip(): str(value).strip()
            for key, value in (evidence or current_governance.get("evidence") or contract.get("evidence") or {}).items()
            if str(key).strip()
        },
        "worktree_mode": str(worktree_mode or current_governance.get("worktree_mode") or "").strip(),
        "worktree_path": str(worktree_path or current_governance.get("worktree_path") or "").strip(),
    }
    resolved_require = (
        bool(require_workspace_admission)
        if require_workspace_admission is not None
        else (
            bool(contract.get("require_workspace_admission"))
            if contract.get("require_workspace_admission") is not None
            else None
        )
    )
    resolved_truth_canonical = str(
        truth_canonical
        or current_governance.get("truth_canonical")
        or contract.get("truth_canonical")
        or ""
    ).strip()
    if not resolved_truth_canonical and (service_key or branch or not contract):
        from beacon.utils.git_alignment import resolve_default_branch

        resolved_truth_canonical = resolve_default_branch(root)
    version_map[version] = {
        "version": version,
        "participating_services": services,
        "per_service_canonical_branch": per_service,
        "branch_guard_mode": str(branch_guard_mode or contract.get("branch_guard_mode") or "strict").strip() or "strict",
        "validation_state": str(validation_state or contract.get("validation_state") or "active").strip() or "active",
        "truth_canonical": resolved_truth_canonical,
        "branch_governance_template": normalized_governance.get("template_name", ""),
        "previous_version_baseline_branch": normalized_governance.get("previous_version_baseline_branch", ""),
        "next_version_feature_branch": normalized_governance.get("next_version_feature_branch", ""),
        "hotfix_branch_naming_rule": normalized_governance.get("hotfix_branch_naming_rule", ""),
        "allow_worktree_when_feature_dirty": normalized_governance.get("allow_worktree_when_feature_dirty", False),
        "merge_direction_policy": normalized_governance.get("merge_direction_policy", []),
        "forbidden_directions": normalized_governance.get("forbidden_directions", []),
        "evidence_contract": normalized_governance.get("evidence_contract", []),
        "evidence": normalized_governance.get("evidence", {}),
        "branch_governance": normalized_governance,
    }
    if resolved_require is not None:
        version_map[version]["require_workspace_admission"] = resolved_require
        version_map[version]["branch_governance"]["require_workspace_admission"] = resolved_require
    # promote worktree fields to contract root for markdown render
    if normalized_governance.get("worktree_mode"):
        version_map[version]["worktree_mode"] = normalized_governance["worktree_mode"]
    if normalized_governance.get("worktree_path"):
        version_map[version]["worktree_path"] = normalized_governance["worktree_path"]
    return version_map


def create_or_update_project_metadata(
    project_root: Path,
    *,
    topology_kind: str = "",
    default_execution_service: str = "",
    service_key: str = "",
    repo_root: str = "",
    role: str = "service",
    writable: bool = True,
    worktree_path_policy: str = "follow-repo-root",
    version: str = "",
    branch: str = "",
    branch_guard_mode: str = "strict",
    validation_state: str = "active",
    truth_canonical: str = "",
    branch_governance_template: str = "",
    previous_version_baseline_branch: str = "",
    next_version_feature_branch: str = "",
    hotfix_branch_naming_rule: str = "",
    allow_worktree_when_feature_dirty: bool | None = None,
    merge_direction_policy: list[str] | None = None,
    forbidden_directions: list[str] | None = None,
    evidence_contract: list[str] | None = None,
    evidence: dict[str, str] | None = None,
    worktree_mode: str = "",
    worktree_path: str = "",
    require_workspace_admission: bool | None = None,
    event_type: str = "update",
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    payload = load_project_metadata(root)
    global_meta = payload["global_project_metadata"]
    if topology_kind:
        global_meta["topology_kind"] = topology_kind
    if default_execution_service:
        global_meta["default_execution_service"] = default_execution_service
    bindings = global_meta.get("service_bindings")
    bindings = list(bindings) if isinstance(bindings, list) else []
    if service_key and repo_root:
        bindings = _upsert_service_binding(
            bindings,
            _normalize_service_binding(
                project_root=root,
                service_key=service_key,
                repo_root=repo_root,
                role=role,
                writable=writable,
                worktree_path_policy=worktree_path_policy,
            ),
        )
    global_meta["service_bindings"] = bindings
    versions = payload.get("version_scoped_metadata")
    versions = dict(versions) if isinstance(versions, dict) else {}
    if version:
        versions = _upsert_version_contract(
            versions,
            root=root,
            version=version,
            service_key=service_key,
            branch=branch,
            branch_guard_mode=branch_guard_mode,
            validation_state=validation_state,
            truth_canonical=truth_canonical,
            branch_governance_template=branch_governance_template,
            previous_version_baseline_branch=previous_version_baseline_branch,
            next_version_feature_branch=next_version_feature_branch,
            hotfix_branch_naming_rule=hotfix_branch_naming_rule,
            allow_worktree_when_feature_dirty=allow_worktree_when_feature_dirty,
            merge_direction_policy=merge_direction_policy,
            forbidden_directions=forbidden_directions,
            evidence_contract=evidence_contract,
            evidence=evidence,
            worktree_mode=worktree_mode,
            worktree_path=worktree_path,
            require_workspace_admission=require_workspace_admission,
        )
    payload["version_scoped_metadata"] = versions
    summary = _commit_payload(root, payload, event_type=event_type)
    return {"status": "ok", "payload": payload, "summary": summary}


def _normalize_service_dev_branch(*, version: str, git_canonical_branch: str, topology_kind: str) -> str:
    """Map feature-package git_canonical_branch to service development branch.

    Monorepo product delivery commonly uses ``feature/<version>`` while package
    frontmatter may still carry program docs branches ``beacon/<version>/<slug>``.
    """
    raw = str(git_canonical_branch or "").strip()
    version_key = str(version or "").strip()
    topology = str(topology_kind or "").strip().lower()
    if raw.startswith("feature/"):
        return raw
    if topology == "monorepo" and version_key:
        if raw.startswith("beacon/") or not raw:
            return f"feature/{version_key}"
    if raw:
        return raw
    if version_key:
        return f"feature/{version_key}" if topology == "monorepo" else f"beacon/{version_key}"
    return ""


def ensure_version_contract_from_feature_package(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> dict[str, Any]:
    """Register/refresh version branch contract from feature package frontmatter.

    Called by freeze so monorepo delivery cannot leave ``per_service_canonical_branch``
    empty after a successful freeze. Existing contracts are upserted in place.
    """
    from beacon.utils.feature_package import _parse_frontmatter, feature_package_file
    from beacon.utils.story_state import feature_slug

    root = project_root.expanduser().resolve()
    slug = feature_slug(feature)
    truth_path = feature_package_file(root, version, slug, "truth.md")
    if not truth_path.is_file():
        return {
            "status": "skipped",
            "reason_code": "feature_truth_missing",
            "version": version,
            "feature": slug,
            "path": str(truth_path),
        }
    frontmatter, _body, errors = _parse_frontmatter(truth_path.read_text(encoding="utf-8"))
    if errors and not frontmatter:
        return {
            "status": "fail",
            "reason_code": "feature_truth_frontmatter_invalid",
            "version": version,
            "feature": slug,
            "errors": errors,
        }
    raw_services = frontmatter.get("participating_services")
    services: list[str] = []
    if isinstance(raw_services, list):
        services = [str(item).strip() for item in raw_services if str(item).strip()]
    elif isinstance(raw_services, str):
        cleaned = raw_services.strip().strip("[]")
        services = [item.strip().strip("'\"") for item in cleaned.split(",") if item.strip().strip("'\"")]
    git_canonical = str(frontmatter.get("git_canonical_branch") or "").strip()
    current = load_project_metadata(root)
    global_meta = current.get("global_project_metadata") if isinstance(current.get("global_project_metadata"), dict) else {}
    topology = str(global_meta.get("topology_kind") or "").strip()
    branch = _normalize_service_dev_branch(
        version=version,
        git_canonical_branch=git_canonical,
        topology_kind=topology,
    )
    if not services:
        default_service = str(global_meta.get("default_execution_service") or "").strip()
        if default_service:
            services = [default_service]
    if not services or not branch:
        return {
            "status": "skipped",
            "reason_code": "insufficient_package_branch_fields",
            "version": version,
            "feature": slug,
            "participating_services": services,
            "branch": branch,
            "git_canonical_branch": git_canonical,
        }
    versions_map = current.get("version_scoped_metadata") if isinstance(current.get("version_scoped_metadata"), dict) else {}
    existing = versions_map.get(version) if isinstance(versions_map.get(version), dict) else {}
    existing_governance = existing.get("branch_governance") if isinstance(existing.get("branch_governance"), dict) else {}
    from beacon.utils.git_alignment import resolve_default_branch

    git_default = resolve_default_branch(root)
    declared_truth = str(existing.get("truth_canonical") or "").strip()
    declared_baseline = str(
        existing.get("previous_version_baseline_branch")
        or existing_governance.get("previous_version_baseline_branch")
        or ""
    ).strip()
    # Explicit declaration wins; fall back to git reality only when absent.
    resolved_truth_canonical = declared_truth or git_default
    resolved_baseline = declared_baseline or declared_truth or git_default
    summary: dict[str, Any] = {
        "services": [],
        "branch": branch,
        "truth_canonical": resolved_truth_canonical,
        "truth_canonical_source": "existing" if declared_truth else "git_default",
    }
    if declared_truth and declared_truth != git_default:
        # Never silently downgrade an explicit canonical branch; surface the conflict.
        summary["truth_canonical_conflict"] = {
            "declared": declared_truth,
            "git_default": git_default,
            "reason_code": "truth_canonical_conflicts_with_git_default",
            "resolution": "preserved_declared",
        }
    last_result: dict[str, Any] = {}
    for service_key in services:
        last_result = create_or_update_project_metadata(
            root,
            version=version,
            service_key=service_key,
            branch=branch,
            truth_canonical=resolved_truth_canonical,
            branch_guard_mode="strict",
            validation_state="active",
            branch_governance_template="standard-feature",
            merge_direction_policy=[f"master->{branch}", f"{branch}->uat"],
            forbidden_directions=[f"uat->{branch}", "uat_as_feature_base"],
            previous_version_baseline_branch=resolved_baseline,
            next_version_feature_branch=(
                f"feature/{version}" if topology == "monorepo" else f"beacon/{version}/<feature-slug>"
            ),
            worktree_mode="dedicated",
            worktree_path=f".beacon/worktrees/{version}",
            require_workspace_admission=True,
            event_type="freeze-version-contract",
        )
        summary["services"].append(service_key)
    summary["status"] = "ok"
    summary["result"] = last_result
    summary["version"] = version
    summary["feature"] = slug
    summary["git_canonical_branch"] = git_canonical
    return summary


def delete_project_metadata(
    project_root: Path,
    *,
    service_key: str = "",
    version: str = "",
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    payload = load_project_metadata(root)
    global_meta = payload["global_project_metadata"]
    if service_key:
        bindings = global_meta.get("service_bindings")
        bindings = list(bindings) if isinstance(bindings, list) else []
        global_meta["service_bindings"] = [
            item for item in bindings if str(item.get("service_key") or "").strip() != str(service_key).strip()
        ]
    if version:
        versions = payload.get("version_scoped_metadata")
        versions = dict(versions) if isinstance(versions, dict) else {}
        versions.pop(version, None)
        payload["version_scoped_metadata"] = versions
    summary = _commit_payload(root, payload, event_type="delete")
    return {"status": "ok", "payload": payload, "summary": summary}


def resolve_project_metadata_view(
    project_root: Path,
    *,
    version: str = "",
    include_archived: bool = False,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    if governance_md_authoritative(root):
        governance = resolve_project_governance(root, version=version, include_archived=include_archived)
        return {
            "project_root": governance.get("project_root", str(root)),
            "topology_kind": governance.get("topology_kind", ""),
            "default_execution_service": governance.get("default_execution_service", ""),
            "service_bindings": governance.get("service_bindings", []),
            "service_bindings_by_key": governance.get("service_bindings_by_key", {}),
            "version": governance.get("version", version),
            "version_contract": governance.get("version_contract", {}),
            "selected_service": governance.get("selected_service", ""),
            "selected_service_binding": governance.get("selected_service_binding", {}),
            "selected_branch": governance.get("selected_branch", ""),
            "paths": {
                "machine": "",
                "human": governance.get("paths", {}).get("governance_md", str(governance_md_path(root))),
                "state": "",
                "governance_md": governance.get("paths", {}).get("governance_md", str(governance_md_path(root))),
            },
            "transaction": governance.get("transaction", {}),
            "branch_governance": governance.get("branch_governance", {}),
            "authority": governance.get("authority", "markdown_project_governance"),
            "parser_contract": governance.get("parser_contract", ""),
        }
    payload = load_project_metadata(root)
    global_meta = payload.get("global_project_metadata") if isinstance(payload.get("global_project_metadata"), dict) else {}
    version_meta = payload.get("version_scoped_metadata") if isinstance(payload.get("version_scoped_metadata"), dict) else {}
    version_contract = version_meta.get(version) if version else {}
    version_contract = version_contract if isinstance(version_contract, dict) else {}
    bindings = global_meta.get("service_bindings") if isinstance(global_meta.get("service_bindings"), list) else []
    bindings_by_key = {
        str(item.get("service_key") or "").strip(): item
        for item in bindings
        if isinstance(item, dict) and str(item.get("service_key") or "").strip()
    }
    default_service = str(global_meta.get("default_execution_service") or "").strip()
    selected_service = default_service
    if not selected_service and isinstance(version_contract.get("participating_services"), list) and version_contract["participating_services"]:
        selected_service = str(version_contract["participating_services"][0] or "").strip()
    per_service = version_contract.get("per_service_canonical_branch") if isinstance(version_contract.get("per_service_canonical_branch"), dict) else {}
    result = {
        "project_root": str(root),
        "topology_kind": str(global_meta.get("topology_kind") or "").strip(),
        "default_execution_service": default_service,
        "service_bindings": bindings,
        "service_bindings_by_key": bindings_by_key,
        "version": version,
        "version_contract": version_contract,
        "selected_service": selected_service,
        "selected_service_binding": bindings_by_key.get(selected_service, {}),
        "selected_branch": str(per_service.get(selected_service) or "").strip(),
        "paths": {
            "machine": str(metadata_machine_path(root)),
            "human": str(metadata_human_path(root)),
            "state": str(metadata_state_path(root)),
        },
        "transaction": payload.get("transaction", {}),
    }
    if version:
        result["branch_governance"] = resolve_branch_governance_view(
            project_root=root,
            version=version,
            metadata_view=result,
        )
    return result


def _git_branch(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:  # noqa: BLE001
        return ""
    return str(result.stdout or "").strip() if result.returncode == 0 else ""


def _primary_git_root(project_root: Path) -> Path:
    root = project_root.expanduser().resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:  # noqa: BLE001
        return root
    if result.returncode != 0:
        return root
    git_common = Path(str(result.stdout or "").strip())
    if not git_common:
        return root
    if not git_common.is_absolute():
        git_common = (root / git_common).resolve()
    else:
        git_common = git_common.resolve()
    if git_common.name == ".git":
        return git_common.parent.resolve()
    return root


def verify_project_metadata(project_root: Path, *, version: str = "") -> dict[str, Any]:
    root = _primary_git_root(project_root)
    view = resolve_project_metadata_view(root, version=version)
    checks: list[dict[str, Any]] = []
    json_guard = governance_json_forbidden(root, strict=True)
    checks.append(
        {
            "status": "pass" if json_guard.get("status") == "pass" else "fail",
            "name": "governance_json_forbidden",
            "details": json_guard,
        }
    )
    projection_guard = verify_governance_projection(root)
    checks.append(
        {
            "status": "pass" if projection_guard.get("status") == "pass" else "fail",
            "name": "governance_projection_drift",
            "details": projection_guard,
        }
    )
    topology_kind = str(view.get("topology_kind") or "").strip()
    checks.append(
        {
            "status": "pass" if topology_kind in {"single_repo", "monorepo", "multi_git_workspace"} else "fail",
            "name": "topology_kind",
            "details": {"value": topology_kind},
        }
    )
    bindings = view.get("service_bindings") if isinstance(view.get("service_bindings"), list) else []
    from beacon.utils.project_governance import (
        migrate_feature_worktree_service_bindings,
        resolve_primary_binding,
    )

    primary = resolve_primary_binding(bindings)
    if topology_kind == "multi_git_workspace":
        checks.append(
            {
                "status": "pass" if primary is not None else "fail",
                "name": "explicit_primary_binding",
                "details": {
                    "primary_service_key": str((primary or {}).get("service_key") or ""),
                    "reason_code": "" if primary is not None else "multi_git_primary_missing",
                },
            }
        )
    else:
        checks.append(
            {
                "status": "pass",
                "name": "explicit_primary_binding",
                "details": {
                    "primary_service_key": str((primary or {}).get("service_key") or ""),
                    "optional": True,
                },
            }
        )
    migration = migrate_feature_worktree_service_bindings(bindings)
    checks.append(
        {
            "status": "pass" if migration.get("status") == "pass" else "fail",
            "name": "stable_service_repo_roots",
            "details": migration,
        }
    )
    default_service = str(view.get("default_execution_service") or "").strip()
    checks.append(
        {
            "status": "pass" if default_service and any(str(item.get("service_key") or "").strip() == default_service for item in bindings if isinstance(item, dict)) else "warn",
            "name": "default_execution_service",
            "details": {"value": default_service},
        }
    )
    if version:
        contract = view.get("version_contract") if isinstance(view.get("version_contract"), dict) else {}
        participating = contract.get("participating_services") if isinstance(contract.get("participating_services"), list) else []
        per_service = contract.get("per_service_canonical_branch") if isinstance(contract.get("per_service_canonical_branch"), dict) else {}
        checks.append(
            {
                "status": "pass" if participating else "fail",
                "name": "version_contract",
                "details": {"version": version, "services": participating},
            }
        )
        for service_key in participating:
            binding = view.get("service_bindings_by_key", {}).get(service_key, {})
            repo_root = Path(str(binding.get("repo_root") or "")).expanduser() if binding else None
            expected_branch = str(per_service.get(service_key) or "").strip()
            truth_canonical = str(contract.get("truth_canonical") or "").strip()
            current_branch = _git_branch(repo_root) if repo_root and repo_root.exists() else ""
            accepted_branches = [item for item in (expected_branch, truth_canonical) if item]
            checks.append(
                {
                    "status": "pass" if binding and expected_branch and current_branch in accepted_branches else "fail",
                    "name": f"branch_contract:{service_key}",
                    "details": {
                        "repo_root": str(repo_root or ""),
                        "expected_branch": expected_branch,
                        "truth_canonical": truth_canonical,
                        "accepted_branches": accepted_branches,
                        "current_branch": current_branch,
                    },
                }
            )
        branch_governance = view.get("branch_governance") if isinstance(view.get("branch_governance"), dict) else {}
        if branch_governance:
            checks.append(
                {
                    "status": "pass" if not branch_governance.get("blocked") else "fail",
                    "name": "branch_governance",
                    "details": {
                        "template_name": branch_governance.get("template_name", ""),
                        "blocked_reason": branch_governance.get("blocked_reason", ""),
                        "reason_codes": branch_governance.get("reason_codes", []),
                    },
                }
            )
    status = "pass"
    if any(item["status"] == "fail" for item in checks):
        status = "fail"
    elif any(item["status"] == "warn" for item in checks):
        status = "warn"
    return {
        "status": status,
        "project_root": str(root),
        "version": version,
        "resolved_metadata_view": view,
        "checks": checks,
    }
