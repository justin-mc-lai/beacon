from __future__ import annotations

import inspect
import subprocess
from pathlib import Path

import pytest

from beacon.utils.project_governance import (
    archive_version_contract,
    commit_governance_payload,
    governance_md_path,
    load_governance_payload,
    parse_governance_markdown,
    prune_archived_contracts,
    read_sqlite_projection_hash,
    render_governance_markdown,
    resolve_project_governance,
    verify_governance_projection,
)
from beacon.utils.project_metadata import _commit_payload, verify_project_metadata
from beacon.utils.truth_map import (
    GENERATED_GOVERNANCE_SURFACES,
    VERSION_GOVERNANCE_SURFACES,
    resolve_version_governance,
)


def _seed_governance_md(root: Path, *, version: str = "v9.9.9") -> None:
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "single_repo",
            "default_execution_service": "beacon",
            "service_bindings": [
                {
                    "service_key": "beacon",
                    "repo_root": str(root),
                    "repo_root_relative": "",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                }
            ],
        },
        "version_scoped_metadata": {
            version: {
                "version": version,
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": "beacon/feature"},
                "branch_guard_mode": "strict",
                "validation_state": "active",
            }
        },
    }
    _commit_payload(root, payload, event_type="test-seed")


def _git(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(result.stdout or "").strip()


def _seed_git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", "main"], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def test_truth_map_single_governance_truth_surface() -> None:
    path_template, role, required = VERSION_GOVERNANCE_SURFACES["project_governance"]
    assert path_template.endswith("project-version-governance.md")
    assert role == "version_governance_truth"
    assert required is True
    truth_like = [
        surface
        for surface, (template, surface_role, _) in VERSION_GOVERNANCE_SURFACES.items()
        if template.endswith("project-version-governance.md") and surface_role == "version_governance_truth"
    ]
    assert truth_like == ["project_governance"]


def test_truth_map_no_dual_role_on_governance_md() -> None:
    governance_md = VERSION_GOVERNANCE_SURFACES["project_governance"][0]
    for surface, (template, _, _) in GENERATED_GOVERNANCE_SURFACES.items():
        assert template != governance_md, f"{surface} still points at governance MD"


def test_truth_map_resolver_documents_projection_roles(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    payload = resolve_version_governance(tmp_path, version="v9.9.9")
    roles = payload.get("governance_projection_roles")
    assert isinstance(roles, dict)
    assert roles.get("canonical_role") == "version_governance_truth"
    assert roles.get("write_direction") == "governance_md_to_sqlite_only"
    assert "sqlite_projection_role" in roles
    assert roles.get("deprecated_legacy_json") == ".beacon/metadata/project-version-metadata.json"


def test_sqlite_stores_source_hash_from_md(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    md_hash = governance_md_path(tmp_path).read_text(encoding="utf-8")
    frontmatter_hash = parse_governance_markdown(md_hash, project_root=tmp_path)["transaction"]["source_hash"]
    sqlite_hash = read_sqlite_projection_hash(tmp_path)
    assert frontmatter_hash
    assert sqlite_hash == frontmatter_hash


def test_verify_fails_on_projection_drift(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    assert verify_governance_projection(tmp_path)["status"] == "pass"
    from beacon.utils.runtime_projection_store import _connect

    with _connect() as conn:
        conn.execute(
            "UPDATE project_metadata_current SET source_hash = ? WHERE project_root = ?",
            ("stale-hash", str(tmp_path.resolve())),
        )
        conn.commit()
    drift = verify_governance_projection(tmp_path)
    assert drift["status"] == "fail"
    assert drift["reason_code"] == "governance_projection_drift"
    verdict = verify_project_metadata(tmp_path, version="v9.9.9")
    projection_check = next(item for item in verdict["checks"] if item["name"] == "governance_projection_drift")
    assert projection_check["status"] == "fail"


def test_metadata_verify_accepts_truth_canonical_main_from_feature_worktree(tmp_path: Path) -> None:
    version = "v1.6.6"
    feature = "demo-change"
    root = tmp_path / "repo"
    worktree = tmp_path / "demo-change-worktree"
    _seed_git_repo(root)
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "single_repo",
            "default_execution_service": "beacon",
            "service_bindings": [
                {
                    "service_key": "beacon",
                    "repo_root": str(root),
                    "repo_root_relative": "",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                }
            ],
        },
        "version_scoped_metadata": {
            version: {
                "version": version,
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": f"beacon/{version}"},
                "truth_canonical": "main",
                "runtime_mirror": f"beacon/{version}",
                "branch_guard_mode": "strict",
                "validation_state": "active",
                "previous_version_baseline_branch": "main",
                "next_version_feature_branch": f"beacon/{version}/<feature-slug>",
                "worktree_mode": "dedicated",
                "worktree_path": f".beacon/worktrees/{version}",
                "require_workspace_admission": True,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    _commit_payload(root, payload, event_type="test-seed")
    _git(["git", "branch", f"beacon/{version}/{feature}"], cwd=root)
    _git(["git", "worktree", "add", str(worktree), f"beacon/{version}/{feature}"], cwd=root)

    verdict = verify_project_metadata(worktree, version=version)
    branch_check = next(item for item in verdict["checks"] if item["name"] == "branch_contract:beacon")

    assert verdict["project_root"] == str(root.resolve())
    assert branch_check["status"] == "pass"
    assert branch_check["details"]["current_branch"] == "main"
    assert branch_check["details"]["accepted_branches"] == [f"beacon/{version}", "main"]


def test_sqlite_payload_not_commit_authority() -> None:
    from beacon.utils import project_governance as governance_module
    from beacon.utils import project_metadata as metadata_module

    forbidden_sources = (
        governance_module.load_governance_payload,
        governance_module.commit_governance_payload,
        governance_module.parse_governance_markdown,
    )
    for function in forbidden_sources:
        source = inspect.getsource(function)
        assert "payload_json" not in source or "SELECT" not in source


def test_parser_accepts_archived_validation_state(tmp_path: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "project_root": str(tmp_path),
        "global_project_metadata": {
            "project_root": str(tmp_path),
            "topology_kind": "single_repo",
            "default_execution_service": "beacon",
            "service_bindings": [],
        },
        "version_scoped_metadata": {
            "v1.0.0": {
                "version": "v1.0.0",
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": "main"},
                "branch_guard_mode": "strict",
                "validation_state": "archived",
            }
        },
    }
    rendered = render_governance_markdown({**payload, "transaction": {}})
    parsed = parse_governance_markdown(rendered, project_root=tmp_path)
    contract = parsed["version_scoped_metadata"]["v1.0.0"]
    assert contract["validation_state"] == "archived"


def test_resolver_skips_archived_contract(tmp_path: Path) -> None:
    version = "v8.8.8"
    _seed_governance_md(tmp_path, version=version)
    archive_version_contract(tmp_path, version=version)
    active_view = resolve_project_governance(tmp_path, version=version)
    assert active_view.get("version_contract") == {}
    archived_view = resolve_project_governance(tmp_path, version=version, include_archived=True)
    assert archived_view.get("version_contract", {}).get("validation_state") == "archived"


def test_doctor_archive_version_marks_archived(tmp_path: Path) -> None:
    version = "v7.7.7"
    _seed_governance_md(tmp_path, version=version)
    result = archive_version_contract(tmp_path, version=version)
    assert result["status"] == "ok"
    payload = load_governance_payload(tmp_path)
    assert payload["version_scoped_metadata"][version]["validation_state"] == "archived"


def test_doctor_prune_archived_dry_run_and_apply(tmp_path: Path) -> None:
    keep_version = "v9.9.9"
    drop_version = "v1.0.0"
    payload = {
        "schema_version": "1.0",
        "project_root": str(tmp_path),
        "global_project_metadata": {
            "project_root": str(tmp_path),
            "topology_kind": "single_repo",
            "default_execution_service": "beacon",
            "service_bindings": [
                {
                    "service_key": "beacon",
                    "repo_root": str(tmp_path),
                    "repo_root_relative": "",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                }
            ],
        },
        "version_scoped_metadata": {
            keep_version: {
                "version": keep_version,
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": "main"},
                "branch_guard_mode": "strict",
                "validation_state": "active",
            },
            drop_version: {
                "version": drop_version,
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": "legacy"},
                "branch_guard_mode": "strict",
                "validation_state": "archived",
            },
        },
    }
    _commit_payload(tmp_path, payload, event_type="test-seed")
    dry_run = prune_archived_contracts(tmp_path, dry_run=True)
    assert dry_run["removed_versions"] == [drop_version]
    assert drop_version in load_governance_payload(tmp_path)["version_scoped_metadata"]
    applied = prune_archived_contracts(tmp_path, dry_run=False)
    assert applied["removed_count"] == 1
    remaining = load_governance_payload(tmp_path)["version_scoped_metadata"]
    assert drop_version not in remaining
    assert keep_version in remaining
    projection_check = verify_governance_projection(tmp_path)
    assert projection_check["status"] == "pass"
