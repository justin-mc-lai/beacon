"""Markdown-only project version / topology / Git governance truth."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso

PARSER_CONTRACT = "beacon-project-governance-v1"
GOVERNANCE_MD_REL = Path("docs/beacon/governance/project-version-governance.md")
GOVERNANCE_JSON_REL = Path(".beacon/metadata/project-version-metadata.json")
GOVERNANCE_JSON_HUMAN_REL = Path(".beacon/metadata/project-version-metadata.md")

_BINDING_RE = re.compile(
    r"^\s*-\s+`([^`]+)`\s+repo=`([^`]+)`\s+role=`([^`]+)`\s+writable=`([^`]+)`\s+worktree_policy=`([^`]+)`\s*$"
)
_KV_BULLET_RE = re.compile(r"^\s*-\s+`?([A-Za-z0-9_ -]+)`?:\s*`?([^`\n]+?)`?\s*$")
_VERSION_HEADING_RE = re.compile(r"^###\s+(v\d+\.\d+\.\d+)\s*$", re.IGNORECASE)
_BRANCH_MAP_RE = re.compile(r"^\s*-\s+`([^`]+)`:\s+`([^`]+)`\s*$")


def governance_md_path(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / GOVERNANCE_MD_REL


def governance_json_path(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / GOVERNANCE_JSON_REL


def governance_md_authoritative(project_root: Path) -> bool:
    return governance_md_path(project_root).is_file()


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _default_payload(project_root: Path) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    return {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "",
            "default_execution_service": "",
            "service_bindings": [],
        },
        "version_scoped_metadata": {},
        "transaction": {},
    }


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    frontmatter: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter, parts[2]


def _parse_service_bindings(body: str) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    in_section = False
    for line in body.splitlines():
        if line.strip() == "## Service Bindings":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        match = _BINDING_RE.match(line)
        if not match:
            continue
        bindings.append(
            {
                "service_key": match.group(1).strip(),
                "repo_root": match.group(2).strip(),
                "repo_root_relative": "",
                "role": match.group(3).strip() or "service",
                "writable": match.group(4).strip().lower() == "true",
                "worktree_path_policy": match.group(5).strip() or "follow-repo-root",
            }
        )
    return bindings


def _assign_version_kv(contract: dict[str, Any], key: str, value: str) -> None:
    if key == "participating_services":
        contract["participating_services"] = [item.strip() for item in value.split(",") if item.strip()]
        return
    if key in {"branch_guard_mode", "validation_state", "branch_governance_template"}:
        contract[key] = value
        return
    if key in {
        "previous_version_baseline_branch",
        "next_version_feature_branch",
        "branch_resolution_mode",
        "aggregation_branch",
        "program_aggregation_branch",
        "expected_branch",
        "program_slug",
        "hotfix_branch_naming_rule",
        "worktree_mode",
        "worktree_path",
        "admission_invalidation",
        "truth_canonical",
        "runtime_mirror",
    }:
        contract[key] = value
        return
    if key == "require_workspace_admission":
        contract[key] = value.lower() in {"true", "1", "yes", "on"}
        return
    if key == "allow_worktree_when_feature_dirty":
        contract[key] = value.lower() in {"true", "1", "yes"}
        return
    if key in {"merge_direction_policy", "forbidden_directions", "evidence_contract"}:
        items = contract.setdefault(key, [])
        if isinstance(items, list):
            items.append(value)
        return
    if key.startswith("evidence_") and key != "evidence_contract":
        evidence = contract.setdefault("evidence", {})
        if isinstance(evidence, dict):
            evidence[key.removeprefix("evidence_")] = value
        return


def _parse_version_contracts(body: str) -> dict[str, Any]:
    versions: dict[str, Any] = {}
    current_version = ""
    current: dict[str, Any] = {}
    in_versions = False
    in_branch_map = False
    for line in body.splitlines():
        if line.strip() == "## Version Contracts":
            in_versions = True
            continue
        if not in_versions:
            continue
        version_match = _VERSION_HEADING_RE.match(line.strip())
        if version_match:
            if current_version:
                versions[current_version] = current
            current_version = version_match.group(1)
            current = {
                "version": current_version,
                "participating_services": [],
                "per_service_canonical_branch": {},
                "branch_guard_mode": "strict",
                "validation_state": "active",
                "branch_governance": {},
            }
            in_branch_map = False
            continue
        if not current_version:
            continue
        if line.strip().startswith("## "):
            break
        if line.strip().lower() == "- per_service_canonical_branch:":
            in_branch_map = True
            continue
        if in_branch_map:
            branch_match = _BRANCH_MAP_RE.match(line)
            if branch_match:
                current.setdefault("per_service_canonical_branch", {})[branch_match.group(1)] = branch_match.group(2)
                continue
            if line.strip() and not line.startswith("  "):
                in_branch_map = False
        kv = _KV_BULLET_RE.match(line)
        if kv:
            key = kv.group(1).strip().lower().replace(" ", "_")
            value = kv.group(2).strip()
            _assign_version_kv(current, key, value)
    if current_version:
        current["validation_state"] = _normalize_validation_state(str(current.get("validation_state") or "active"))
        versions[current_version] = current
    return versions


def parse_governance_markdown(text: str, *, project_root: Path) -> dict[str, Any]:
    frontmatter, body = _parse_frontmatter(text)
    root = project_root.expanduser().resolve()
    payload = _default_payload(root)
    payload["schema_version"] = frontmatter.get("schema_version", "1.0")
    payload["project_root"] = frontmatter.get("project_root", str(root))
    global_meta = payload["global_project_metadata"]
    global_meta["project_root"] = payload["project_root"]
    global_meta["topology_kind"] = frontmatter.get("topology_kind", "")
    global_meta["default_execution_service"] = frontmatter.get("default_execution_service", "")
    bindings = _parse_service_bindings(body)
    if bindings:
        global_meta["service_bindings"] = bindings
    versions = _parse_version_contracts(body)
    if versions:
        payload["version_scoped_metadata"] = versions
    payload["transaction"] = {
        "transaction_id": frontmatter.get("transaction_id", ""),
        "committed_at": frontmatter.get("committed_at", ""),
        "source_hash": frontmatter.get("source_hash", ""),
        "event_type": frontmatter.get("event_type", ""),
    }
    for contract in payload.get("version_scoped_metadata", {}).values():
        if not isinstance(contract, dict):
            continue
        nested = contract.get("branch_governance") if isinstance(contract.get("branch_governance"), dict) else {}
        contract["branch_governance"] = {
            **nested,
            "template_name": str(contract.get("branch_governance_template") or nested.get("template_name") or "").strip(),
            "previous_version_baseline_branch": str(
                contract.get("previous_version_baseline_branch") or nested.get("previous_version_baseline_branch") or ""
            ).strip(),
            "next_version_feature_branch": str(
                contract.get("next_version_feature_branch") or nested.get("next_version_feature_branch") or ""
            ).strip(),
            "hotfix_branch_naming_rule": str(
                contract.get("hotfix_branch_naming_rule") or nested.get("hotfix_branch_naming_rule") or ""
            ).strip(),
            "allow_worktree_when_feature_dirty": bool(
                contract.get("allow_worktree_when_feature_dirty", nested.get("allow_worktree_when_feature_dirty", False))
            ),
            "merge_direction_policy": contract.get("merge_direction_policy") or nested.get("merge_direction_policy") or [],
            "forbidden_directions": contract.get("forbidden_directions") or nested.get("forbidden_directions") or [],
            "evidence_contract": contract.get("evidence_contract") or nested.get("evidence_contract") or [],
            "evidence": contract.get("evidence") if isinstance(contract.get("evidence"), dict) else nested.get("evidence") or {},
            "worktree_mode": str(contract.get("worktree_mode") or nested.get("worktree_mode") or "").strip(),
            "worktree_path": str(contract.get("worktree_path") or nested.get("worktree_path") or "").strip(),
        }
    return payload


def load_governance_payload(project_root: Path) -> dict[str, Any]:
    path = governance_md_path(project_root)
    if not path.is_file():
        return _default_payload(project_root)
    return parse_governance_markdown(path.read_text(encoding="utf-8"), project_root=project_root)


def render_governance_markdown(payload: dict[str, Any]) -> str:
    global_meta = payload.get("global_project_metadata") if isinstance(payload.get("global_project_metadata"), dict) else {}
    version_meta = payload.get("version_scoped_metadata") if isinstance(payload.get("version_scoped_metadata"), dict) else {}
    transaction = payload.get("transaction") if isinstance(payload.get("transaction"), dict) else {}
    base = {
        "schema_version": payload.get("schema_version", "1.0"),
        "project_root": payload.get("project_root", ""),
        "topology_kind": global_meta.get("topology_kind", ""),
        "default_execution_service": global_meta.get("default_execution_service", ""),
        "transaction_id": transaction.get("transaction_id", ""),
        "committed_at": transaction.get("committed_at", ""),
        "source_hash": transaction.get("source_hash", ""),
        "event_type": transaction.get("event_type", ""),
        "parser_contract": PARSER_CONTRACT,
    }
    frontmatter = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in base.items())
    lines = [
        "---",
        frontmatter,
        "---",
        "",
        "# Project Version Governance",
        "",
        f"- project_root: `{payload.get('project_root', '')}`",
        f"- topology_kind: `{global_meta.get('topology_kind', '')}`",
        f"- default_execution_service: `{global_meta.get('default_execution_service', '')}`",
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
                f"- `{item.get('service_key', '')}` "
                f"repo=`{item.get('repo_root', '')}` "
                f"role=`{item.get('role', 'service')}` "
                f"writable=`{str(bool(item.get('writable', True))).lower()}` "
                f"worktree_policy=`{item.get('worktree_path_policy', 'follow-repo-root')}`"
            )
    lines.extend(["", "## Version Contracts", ""])
    for version in sorted(version_meta.keys()):
        contract = version_meta.get(version)
        if not isinstance(contract, dict):
            continue
        lines.append(f"### {version}")
        participating = contract.get("participating_services") if isinstance(contract.get("participating_services"), list) else []
        lines.append(f"- participating_services: `{', '.join(str(item) for item in participating)}`")
        lines.append(f"- branch_guard_mode: `{contract.get('branch_guard_mode', 'strict')}`")
        lines.append(f"- validation_state: `{contract.get('validation_state', 'active')}`")
        per_service = contract.get("per_service_canonical_branch") if isinstance(contract.get("per_service_canonical_branch"), dict) else {}
        if per_service:
            lines.append("- per_service_canonical_branch:")
            for service_key, branch in sorted(per_service.items()):
                lines.append(f"  - `{service_key}`: `{branch}`")
        truth_canonical = str(contract.get("truth_canonical") or "").strip()
        if truth_canonical:
            lines.append(f"- truth_canonical: `{truth_canonical}`")
        runtime_mirror = str(contract.get("runtime_mirror") or "").strip()
        if runtime_mirror:
            lines.append(f"- runtime_mirror: `{runtime_mirror}`")
        governance = contract.get("branch_governance") if isinstance(contract.get("branch_governance"), dict) else {}
        template = str(contract.get("branch_governance_template") or governance.get("template_name") or "").strip()
        previous_baseline = str(
            contract.get("previous_version_baseline_branch") or governance.get("previous_version_baseline_branch") or ""
        ).strip()
        next_feature = str(contract.get("next_version_feature_branch") or governance.get("next_version_feature_branch") or "").strip()
        branch_resolution_mode = str(contract.get("branch_resolution_mode") or governance.get("branch_resolution_mode") or "").strip()
        aggregation_branch = str(
            contract.get("aggregation_branch")
            or contract.get("program_aggregation_branch")
            or governance.get("aggregation_branch")
            or governance.get("program_aggregation_branch")
            or ""
        ).strip()
        expected_branch = str(contract.get("expected_branch") or governance.get("expected_branch") or "").strip()
        program_slug = str(contract.get("program_slug") or governance.get("program_slug") or "").strip()
        hotfix_rule = str(contract.get("hotfix_branch_naming_rule") or governance.get("hotfix_branch_naming_rule") or "").strip()
        if template:
            lines.append(f"- branch_governance_template: `{template}`")
        if previous_baseline:
            lines.append(f"- previous_version_baseline_branch: `{previous_baseline}`")
        if next_feature:
            lines.append(f"- next_version_feature_branch: `{next_feature}`")
        if branch_resolution_mode:
            lines.append(f"- branch_resolution_mode: `{branch_resolution_mode}`")
        if aggregation_branch:
            lines.append(f"- aggregation_branch: `{aggregation_branch}`")
        if expected_branch:
            lines.append(f"- expected_branch: `{expected_branch}`")
        if program_slug:
            lines.append(f"- program_slug: `{program_slug}`")
        if hotfix_rule:
            lines.append(f"- hotfix_branch_naming_rule: `{hotfix_rule}`")
        if contract.get("allow_worktree_when_feature_dirty"):
            lines.append("- allow_worktree_when_feature_dirty: `true`")
        worktree_mode = str(contract.get("worktree_mode") or governance.get("worktree_mode") or "").strip()
        worktree_path = str(contract.get("worktree_path") or governance.get("worktree_path") or "").strip()
        if worktree_mode:
            lines.append(f"- worktree_mode: `{worktree_mode}`")
        if worktree_path:
            lines.append(f"- worktree_path: `{worktree_path}`")
        if contract.get("require_workspace_admission") is not None:
            lines.append(
                f"- require_workspace_admission: `{str(bool(contract.get('require_workspace_admission'))).lower()}`"
            )
        invalidation = str(contract.get("admission_invalidation") or "").strip()
        if invalidation:
            lines.append(f"- admission_invalidation: `{invalidation}`")
        for policy in contract.get("merge_direction_policy") or []:
            lines.append(f"- merge_direction_policy: `{policy}`")
        for forbidden in contract.get("forbidden_directions") or []:
            lines.append(f"- forbidden_directions: `{forbidden}`")
        for evidence_item in contract.get("evidence_contract") or []:
            lines.append(f"- evidence_contract: `{evidence_item}`")
        evidence = contract.get("evidence") if isinstance(contract.get("evidence"), dict) else {}
        for key, value in sorted(evidence.items()):
            lines.append(f"- evidence_{key}: `{value}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def commit_governance_payload(project_root: Path, payload: dict[str, Any], *, event_type: str) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    path = governance_md_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    base_payload = {
        "schema_version": payload.get("schema_version", "1.0"),
        "project_root": str(root),
        "global_project_metadata": payload.get("global_project_metadata", {}),
        "version_scoped_metadata": payload.get("version_scoped_metadata", {}),
    }
    source_hash = _stable_hash(base_payload)
    transaction_id = f"tx-project-governance-{source_hash[:16]}"
    committed_at = now_iso()
    payload["transaction"] = {
        "transaction_id": transaction_id,
        "event_type": event_type,
        "committed_at": committed_at,
        "source_hash": source_hash,
    }
    path.write_text(render_governance_markdown(payload), encoding="utf-8")
    for legacy in (governance_json_path(root), root / GOVERNANCE_JSON_HUMAN_REL):
        if legacy.is_file():
            legacy.unlink()
    _sync_sqlite_projection(root, event_type=event_type)
    return {
        "governance_md_path": str(path.relative_to(root)),
        "transaction_id": transaction_id,
        "committed_at": committed_at,
        "source_hash": source_hash,
    }


def _sync_sqlite_projection(project_root: Path, *, event_type: str) -> None:
    """Keep sqlite hash projection aligned after every governance MD commit."""

    from beacon.utils.project_metadata import _write_sqlite_projection

    root = project_root.expanduser().resolve()
    payload = load_governance_payload(root)
    _write_sqlite_projection(root, payload, event_type=event_type)


def migrate_json_to_governance_md(project_root: Path) -> dict[str, Any]:
    from beacon.utils.runtime import read_json

    root = project_root.expanduser().resolve()
    json_path = governance_json_path(root)
    if not json_path.is_file():
        if governance_md_authoritative(root):
            return {"status": "ok", "reason": "governance_md_already_authoritative"}
        return {"status": "skipped", "reason": "no_legacy_json"}
    payload = read_json(json_path, {})
    if not isinstance(payload, dict) or not payload:
        return {"status": "fail", "reason": "legacy_json_unreadable"}
    summary = commit_governance_payload(root, payload, event_type="migrate-to-governance-md")
    return {"status": "ok", "summary": summary, "removed_json": True}


def read_governance_md_source_hash(project_root: Path) -> str:
    root = project_root.expanduser().resolve()
    if not governance_md_authoritative(root):
        return ""
    frontmatter, _body = _parse_frontmatter(governance_md_path(root).read_text(encoding="utf-8"))
    return str(frontmatter.get("source_hash") or "").strip()


def read_sqlite_projection_hash(project_root: Path) -> str:
    from beacon.utils.runtime_projection_store import _connect

    root = str(project_root.expanduser().resolve())
    with _connect() as conn:
        row = conn.execute(
            "SELECT source_hash FROM project_metadata_current WHERE project_root = ?",
            (root,),
        ).fetchone()
    if not row:
        return ""
    return str(row[0] or "").strip()


def verify_governance_projection(project_root: Path) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    if not governance_md_authoritative(root):
        return {"status": "pass", "blocked": False, "reason_code": ""}
    md_hash = read_governance_md_source_hash(root)
    sqlite_hash = read_sqlite_projection_hash(root)
    if not md_hash:
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "governance_projection_drift",
            "details": {"issue": "governance_md_missing_source_hash"},
        }
    if not sqlite_hash:
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "governance_projection_drift",
            "details": {"issue": "sqlite_projection_missing", "md_source_hash": md_hash},
        }
    if md_hash != sqlite_hash:
        return {
            "status": "fail",
            "blocked": True,
            "reason_code": "governance_projection_drift",
            "details": {"md_source_hash": md_hash, "sqlite_source_hash": sqlite_hash},
        }
    return {"status": "pass", "blocked": False, "reason_code": "", "details": {"source_hash": md_hash}}


def _normalize_validation_state(value: str) -> str:
    normalized = str(value or "active").strip().lower()
    return normalized if normalized in {"active", "archived"} else "active"


def archive_version_contract(project_root: Path, *, version: str) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    payload = load_governance_payload(root)
    versions = payload.get("version_scoped_metadata")
    versions = versions if isinstance(versions, dict) else {}
    contract = versions.get(version)
    if not isinstance(contract, dict):
        return {"status": "fail", "reason": "version_contract_not_found", "version": version}
    contract = dict(contract)
    contract["validation_state"] = "archived"
    versions[version] = contract
    payload["version_scoped_metadata"] = versions
    summary = commit_governance_payload(root, payload, event_type="archive-version")
    return {"status": "ok", "version": version, "validation_state": "archived", "summary": summary}


def prune_archived_contracts(project_root: Path, *, dry_run: bool = True) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    payload = load_governance_payload(root)
    versions = payload.get("version_scoped_metadata")
    versions = dict(versions) if isinstance(versions, dict) else {}
    removed = sorted(
        version
        for version, contract in versions.items()
        if isinstance(contract, dict) and _normalize_validation_state(str(contract.get("validation_state") or "")) == "archived"
    )
    if dry_run:
        return {"status": "ok", "dry_run": True, "removed_versions": removed, "removed_count": len(removed)}
    kept = {version: contract for version, contract in versions.items() if version not in removed}
    payload["version_scoped_metadata"] = kept
    summary = commit_governance_payload(root, payload, event_type="prune-archived")
    return {
        "status": "ok",
        "dry_run": False,
        "removed_versions": removed,
        "removed_count": len(removed),
        "summary": summary,
    }


def governance_json_forbidden(project_root: Path, *, strict: bool = True) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    if not governance_md_authoritative(root):
        return {"status": "pass", "blocked": False, "reason_code": ""}
    offenders = [rel for rel in (GOVERNANCE_JSON_REL, GOVERNANCE_JSON_HUMAN_REL) if (root / rel).is_file()]
    if not offenders:
        return {"status": "pass", "blocked": False, "reason_code": ""}
    return {
        "status": "fail",
        "blocked": strict,
        "reason_code": "governance_json_forbidden",
        "offenders": [str(item) for item in offenders],
    }


def resolve_project_governance(project_root: Path, *, version: str = "", include_archived: bool = False) -> dict[str, Any]:
    from beacon.utils.branch_governance import resolve_branch_governance_view
    from beacon.utils.execution_branch_contract import find_program_level_git_workflow, infer_program_level_from_governance

    root = project_root.expanduser().resolve()
    payload = load_governance_payload(root)
    global_meta = payload.get("global_project_metadata") if isinstance(payload.get("global_project_metadata"), dict) else {}
    version_meta = payload.get("version_scoped_metadata") if isinstance(payload.get("version_scoped_metadata"), dict) else {}
    version_contract = version_meta.get(version) if version else {}
    version_contract = version_contract if isinstance(version_contract, dict) else {}
    if version and not include_archived and _normalize_validation_state(str(version_contract.get("validation_state") or "")) == "archived":
        version_contract = {}
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
    json_guard = governance_json_forbidden(root, strict=True)
    result = {
        "schema_version": "1.0",
        "authority": "markdown_project_governance",
        "parser_contract": PARSER_CONTRACT,
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
            "governance_md": str(governance_md_path(root)),
            "machine": "",
            "human": "",
            "state": "",
        },
        "transaction": payload.get("transaction", {}),
        "governance_md_exists": governance_md_authoritative(root),
        "governance_json_forbidden": json_guard,
        "include_archived": include_archived,
        "version_contract_archived": bool(
            version
            and isinstance(version_meta.get(version), dict)
            and _normalize_validation_state(str(version_meta[version].get("validation_state") or "")) == "archived"
        ),
    }
    service_branch_map = dict(per_service)
    if service_branch_map:
        result["service_branch_map"] = service_branch_map
    participating = version_contract.get("participating_services") if isinstance(version_contract.get("participating_services"), list) else []
    if participating:
        result["participating_services"] = [str(item) for item in participating]
        result["git_roots"] = [
            str(item.get("repo_root") or "")
            for item in bindings
            if isinstance(item, dict) and str(item.get("service_key") or "") in participating and str(item.get("repo_root") or "").strip()
        ]
    if version and governance_md_authoritative(root):
        metadata_view = {
            "project_root": str(root),
            "topology_kind": result["topology_kind"],
            "default_execution_service": default_service,
            "service_bindings": bindings,
            "service_bindings_by_key": bindings_by_key,
            "version": version,
            "version_contract": version_contract,
            "selected_service": selected_service,
            "selected_service_binding": bindings_by_key.get(selected_service, {}),
            "selected_branch": result["selected_branch"],
            "paths": result["paths"],
            "transaction": payload.get("transaction", {}),
        }
        git_workflow = (
            find_program_level_git_workflow(root, version=version)
            or infer_program_level_from_governance(root, version=version)
            or {}
        )
        result["branch_governance"] = resolve_branch_governance_view(
            project_root=root,
            version=version,
            metadata_view=metadata_view,
            git_workflow=git_workflow,
        )
    return result
