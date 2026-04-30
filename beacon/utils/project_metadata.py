"""Project topology and version-branch metadata support helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

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
                payload_json TEXT NOT NULL
            );
            """
        )


def _write_sqlite_projection(project_root: Path, payload: dict[str, Any], *, event_type: str) -> dict[str, Any]:
    _ensure_metadata_sqlite_schema()
    transaction = payload.get("transaction") if isinstance(payload.get("transaction"), dict) else {}
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
                str(project_root),
                str(payload.get("global_project_metadata", {}).get("topology_kind", "") or ""),
                str(payload.get("global_project_metadata", {}).get("default_execution_service", "") or ""),
                str(transaction.get("transaction_id", "") or ""),
                str(transaction.get("committed_at", "") or ""),
                str(transaction.get("source_hash", "") or ""),
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO project_metadata_events (
                transaction_id, project_root, event_type, committed_at, payload_json
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(transaction.get("transaction_id", "") or ""),
                str(project_root),
                event_type,
                str(transaction.get("committed_at", "") or ""),
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        conn.commit()
    return {"status": "ok", "db_path": str(runtime_ledger_db_path())}


def _commit_payload(project_root: Path, payload: dict[str, Any], *, event_type: str) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    machine_path = metadata_machine_path(root)
    human_path = metadata_human_path(root)
    machine_path.parent.mkdir(parents=True, exist_ok=True)
    base_payload = {
        "schema_version": payload.get("schema_version", "1.0"),
        "project_root": str(root),
        "global_project_metadata": payload.get("global_project_metadata", {}),
        "version_scoped_metadata": payload.get("version_scoped_metadata", {}),
    }
    source_hash = _stable_hash(base_payload)
    transaction_id = f"tx-project-metadata-{source_hash[:16]}"
    committed_at = now_iso()
    payload["transaction"] = {
        "transaction_id": transaction_id,
        "event_type": event_type,
        "committed_at": committed_at,
        "source_hash": source_hash,
    }
    write_json(machine_path, payload)
    human_path.write_text(_render_human(payload), encoding="utf-8")
    transaction_path = metadata_transactions_root(root) / f"{transaction_id}.json"
    write_json(transaction_path, payload)
    state_path = metadata_state_path(root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        state_path,
        {
            "schema_version": "1.0",
            "project_root": str(root),
            "transaction_id": transaction_id,
            "payload_path": str(machine_path.relative_to(root)),
            "markdown_path": str(human_path.relative_to(root)),
            "payload_abs_path": str(machine_path),
            "markdown_abs_path": str(human_path),
            "committed_at": committed_at,
        },
    )
    sqlite = _write_sqlite_projection(root, payload, event_type=event_type)
    return {
        "project_root": str(root),
        "payload_path": str(machine_path.relative_to(root)),
        "markdown_path": str(human_path.relative_to(root)),
        "payload_abs_path": str(machine_path),
        "markdown_abs_path": str(human_path),
        "transaction_path": str(transaction_path.relative_to(root)),
        "transaction_abs_path": str(transaction_path),
        "transaction_id": transaction_id,
        "committed_at": committed_at,
        "sqlite": sqlite,
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
    version: str,
    service_key: str,
    branch: str,
    branch_guard_mode: str,
    validation_state: str,
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
    version_map[version] = {
        "version": version,
        "participating_services": services,
        "per_service_canonical_branch": per_service,
        "branch_guard_mode": str(branch_guard_mode or contract.get("branch_guard_mode") or "strict").strip() or "strict",
        "validation_state": str(validation_state or contract.get("validation_state") or "active").strip() or "active",
    }
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
            version=version,
            service_key=service_key,
            branch=branch,
            branch_guard_mode=branch_guard_mode,
            validation_state=validation_state,
        )
    payload["version_scoped_metadata"] = versions
    summary = _commit_payload(root, payload, event_type=event_type)
    return {"status": "ok", "payload": payload, "summary": summary}


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


def resolve_project_metadata_view(project_root: Path, *, version: str = "") -> dict[str, Any]:
    root = project_root.expanduser().resolve()
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
    return {
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


def verify_project_metadata(project_root: Path, *, version: str = "") -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    view = resolve_project_metadata_view(root, version=version)
    checks: list[dict[str, Any]] = []
    topology_kind = str(view.get("topology_kind") or "").strip()
    checks.append(
        {
            "status": "pass" if topology_kind in {"single_repo", "monorepo"} else "fail",
            "name": "topology_kind",
            "details": {"value": topology_kind},
        }
    )
    bindings = view.get("service_bindings") if isinstance(view.get("service_bindings"), list) else []
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
            current_branch = _git_branch(repo_root) if repo_root and repo_root.exists() else ""
            checks.append(
                {
                    "status": "pass" if binding and expected_branch and current_branch == expected_branch else "fail",
                    "name": f"branch_contract:{service_key}",
                    "details": {
                        "repo_root": str(repo_root or ""),
                        "expected_branch": expected_branch,
                        "current_branch": current_branch,
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
