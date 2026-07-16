"""GitScopeGraph unified topology for single_repo / monorepo / multi_git_workspace (v1.6.7)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.project_governance import governance_json_path
from beacon.utils.project_metadata import resolve_project_metadata_view
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version
from beacon.utils.workspace_admission import (
    artifact_path as admission_artifact_path,
    run_workspace_admit,
    validate_workspace_admission,
)

SCHEMA_VERSION = "git-scope-graph.v1"
PRODUCED_BY = "beacon.workspace.topology-resolve"

TOPOLOGY_SINGLE = "single_repo"
TOPOLOGY_MONOREPO = "monorepo"
TOPOLOGY_MULTI = "multi_git_workspace"

VALID_TOPOLOGIES = frozenset({TOPOLOGY_SINGLE, TOPOLOGY_MONOREPO, TOPOLOGY_MULTI})


def _semver_tuple(value: str) -> tuple[int, int, int]:
    text = str(value or "").strip().lower()
    if text.startswith("v"):
        text = text[1:]
    numbers: list[int] = []
    for part in text.split(".")[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        numbers.append(int(digits or "0"))
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers[:3])


def topology_gate_required(version: str) -> bool:
    return _semver_tuple(resolve_target_version(Path.cwd(), version)) >= (1, 6, 7)


def artifact_path(project_root: Path, *, version: str, feature: str) -> Path:
    slug = feature_slug(feature)
    return (
        project_root.expanduser().resolve()
        / ".beacon"
        / "state"
        / "git-scope-graph"
        / version
        / f"{slug}.json"
    )


def resolve_project_topology(project_root: Path) -> str:
    view = resolve_project_metadata_view(project_root, version="")
    kind = str(view.get("topology_kind") or "").strip()
    if kind in VALID_TOPOLOGIES:
        return kind
    bindings = view.get("service_bindings") if isinstance(view.get("service_bindings"), list) else []
    repo_roots = set()
    root = project_root.expanduser().resolve()
    for item in bindings:
        if not isinstance(item, dict):
            continue
        rel = str(item.get("repo_root_relative") or item.get("repo_root") or ".").strip()
        git_root = Path(rel)
        if not git_root.is_absolute():
            git_root = (root / rel).resolve()
        repo_roots.add(str(git_root))
    if len(repo_roots) > 1:
        return TOPOLOGY_MULTI
    if kind == TOPOLOGY_MONOREPO:
        return TOPOLOGY_MONOREPO
    return TOPOLOGY_SINGLE


def _git_porcelain(repo_root: Path, pathspec: str = "") -> list[str]:
    args = ["git", "status", "--porcelain"]
    if pathspec:
        args.extend(["--", pathspec])
    try:
        result = subprocess.run(
            args,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except Exception:
        return ["error"]
    if result.returncode != 0:
        return ["error"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _scope_from_binding(
    project_root: Path,
    *,
    binding: dict[str, Any],
    scope_id: str,
    role: str,
    version: str,
    feature: str,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    rel = str(binding.get("repo_root_relative") or binding.get("repo_root") or ".").strip()
    git_root = Path(rel)
    if not git_root.is_absolute():
        git_root = (root / rel).resolve()
    dirty_lines = _git_porcelain(git_root)
    dirty = bool(dirty_lines) and dirty_lines != ["error"]
    admission_ref = ""
    status = "pass"
    reason_codes: list[str] = []
    if git_root == root or scope_id == "primary":
        from beacon.utils.workspace_admission import load_admission_contract

        validation = validate_workspace_admission(root, version=version, feature=feature, cwd=root)
        contract = load_admission_contract(root, version=version)
        admission_required = bool(contract.get("require_workspace_admission"))
        if validation.get("valid"):
            path = admission_artifact_path(root, version=version, feature=feature)
            if path.exists():
                try:
                    admission_ref = str(path.relative_to(root))
                except ValueError:
                    admission_ref = str(path)
        elif admission_required:
            status = "blocked"
            reason_codes.append(str(validation.get("reason_code") or "workspace_admission_blocked"))
    elif dirty:
        policy = str(binding.get("dirty_policy") or "fail_closed")
        if policy == "fail_closed":
            status = "blocked"
            reason_codes.append("satellite_worktree_dirty")
    return {
        "scope_id": scope_id,
        "git_root": str(git_root),
        "role": role,
        "branch_resolution_mode": str(binding.get("branch_resolution_mode") or "per-feature"),
        "target_branch": str(binding.get("target_branch") or ""),
        "worktree_path": str(binding.get("worktree_path") or git_root),
        "admission_artifact_ref": admission_ref,
        "dirty_policy": str(binding.get("dirty_policy") or "fail_closed"),
        "status": status,
        "reason_codes": reason_codes,
        "dirty": dirty,
    }


def build_scope_list(
    project_root: Path,
    *,
    version: str,
    feature: str,
    project_topology: str,
) -> list[dict[str, Any]]:
    root = project_root.expanduser().resolve()
    view = resolve_project_metadata_view(root, version=version)
    bindings = view.get("service_bindings") if isinstance(view.get("service_bindings"), list) else []
    if not bindings:
        gov_path = governance_json_path(root)
        if gov_path.is_file():
            try:
                gov_payload = json.loads(gov_path.read_text(encoding="utf-8"))
                global_meta = gov_payload.get("global_project_metadata") if isinstance(gov_payload.get("global_project_metadata"), dict) else {}
                bindings = global_meta.get("service_bindings") if isinstance(global_meta.get("service_bindings"), list) else []
            except Exception:
                bindings = []
    scopes: list[dict[str, Any]] = []
    if not bindings:
        scopes.append(
            _scope_from_binding(
                root,
                binding={"repo_root_relative": ".", "role": "primary"},
                scope_id="primary",
                role="primary",
                version=version,
                feature=feature,
            )
        )
        return scopes

    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            continue
        rel = str(binding.get("repo_root_relative") or binding.get("repo_root") or ".").strip()
        git_root = Path(rel)
        if not git_root.is_absolute():
            git_root = (root / rel).resolve()
        role = str(binding.get("role") or "service").strip()
        if git_root == root or role == "primary" or index == 0:
            scope_id = "primary"
            scope_role = "primary"
        else:
            scope_role = "satellite" if project_topology == TOPOLOGY_MULTI else "service"
            scope_id = str(binding.get("service_key") or f"scope-{index}")
        binding_with_topo = {**binding, "_project_topology": project_topology}
        scope = _scope_from_binding(
            root,
            binding=binding_with_topo,
            scope_id=scope_id,
            role=scope_role,
            version=version,
            feature=feature,
        )
        if project_topology == TOPOLOGY_MONOREPO and git_root == root and binding.get("writable"):
            service_key = str(binding.get("service_key") or "").strip()
            if service_key:
                dirty_lines = _git_porcelain(root, service_key)
                if dirty_lines and dirty_lines != ["error"]:
                    scope["status"] = "blocked"
                    scope.setdefault("reason_codes", []).append(f"monorepo_service_dirty:{service_key}")
        scopes.append(scope)
    if not scopes:
        scopes.append(
            _scope_from_binding(
                root,
                binding={"repo_root_relative": "."},
                scope_id="primary",
                role="primary",
                version=version,
                feature=feature,
            )
        )
    return scopes


def aggregate_topology_gate(scopes: list[dict[str, Any]]) -> tuple[str, list[str]]:
    reason_codes: list[str] = []
    blocked = False
    for scope in scopes:
        if str(scope.get("status") or "") == "blocked":
            blocked = True
            reason_codes.extend(list(scope.get("reason_codes") or []))
    if blocked:
        return "blocked", sorted(dict.fromkeys(reason_codes))
    if not scopes:
        return "blocked", ["no_scopes"]
    return "pass", []


def build_git_scope_graph(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    project_topology = resolve_project_topology(root)
    scopes = build_scope_list(root, version=resolved_version, feature=feature, project_topology=project_topology)
    topology_gate_status, reason_codes = aggregate_topology_gate(scopes)
    ref_path = artifact_path(root, version=resolved_version, feature=feature)
    try:
        artifact_ref = str(ref_path.relative_to(root))
    except ValueError:
        artifact_ref = str(ref_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "produced_by": PRODUCED_BY,
        "generated_at": now_iso(),
        "version": resolved_version,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "project_topology": project_topology,
        "scopes": scopes,
        "topology_gate_status": topology_gate_status,
        "reason_codes": reason_codes,
        "topology_gate_ref": artifact_ref,
    }


def run_topology_resolve(
    project_root: Path,
    *,
    version: str,
    feature: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    admit = run_workspace_admit(root, version=resolved_version, feature=feature, dry_run=dry_run)
    graph = build_git_scope_graph(root, version=resolved_version, feature=feature)
    if str(admit.get("status") or "") != "pass" and graph["topology_gate_status"] == "pass":
        graph["topology_gate_status"] = "blocked"
        graph.setdefault("reason_codes", []).append(
            str(admit.get("reason_code") or "workspace_admission_blocked")
        )
    graph["workspace_admit"] = {
        "status": admit.get("status"),
        "reason_code": admit.get("reason_code", ""),
        "worktree_path": admit.get("worktree_path", ""),
    }
    if not dry_run:
        out = artifact_path(root, version=resolved_version, feature=feature)
        write_json(out, graph)
        try:
            graph["artifact_path"] = str(out.relative_to(root))
        except ValueError:
            graph["artifact_path"] = str(out)
    graph["status"] = graph["topology_gate_status"]
    return graph


def load_topology_graph(project_root: Path, *, version: str, feature: str) -> dict[str, Any] | None:
    path = artifact_path(project_root, version=version, feature=feature)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def topology_gate_check(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> tuple[dict[str, Any], str]:
    resolved_version = resolve_target_version(project_root, version)
    graph = load_topology_graph(project_root, version=resolved_version, feature=feature)
    if not graph:
        graph = run_topology_resolve(project_root, version=resolved_version, feature=feature, dry_run=False)
    status = str(graph.get("topology_gate_status") or "blocked")
    ref = str(graph.get("topology_gate_ref") or "")
    reason = ""
    if status != "pass":
        codes = graph.get("reason_codes") or ["topology_gate_blocked"]
        reason = str(codes[0]) if codes else "topology_gate_blocked"
    check = {
        "status": "pass" if status == "pass" else "fail",
        "reason_code": reason,
        "details": {
            "project_topology": graph.get("project_topology"),
            "scope_count": len(graph.get("scopes") or []),
        },
    }
    return check, ref
