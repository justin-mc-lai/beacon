"""v1.6.11 service-scoped worktree pool (AC-SSP-001..007)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from beacon.utils.git_scope_graph import (
    TOPOLOGY_MULTI,
    build_git_scope_graph,
    build_scope_list,
    run_topology_resolve,
)
from beacon.utils.implement_admission import (
    REASON_PARENT_ONLY_SERVICE_WRITE,
    assert_service_write_authorized,
    ensure_implement_admission,
    is_real_git_worktree,
    resolve_service_worktree_path,
)
from beacon.utils.project_governance import (
    commit_governance_payload,
    is_feature_worktree_binding_path,
    migrate_feature_worktree_service_bindings,
    parse_governance_markdown,
    render_governance_markdown,
    resolve_primary_binding,
)
from beacon.utils.project_metadata import verify_project_metadata
from beacon.utils.workspace_admission import (
    pool_state_path,
    release_workspace_lease,
    run_workspace_admit,
    upsert_service_pool_leases,
)

VERSION = "v1.6.11"
FEATURE = "service-scoped-worktree-pool-v1611"


def _git(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(result.stdout or "").strip()


def _seed_repo(root: Path, *, branch: str = "main") -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_frozen_truth(root: Path) -> None:
    d = root / "docs" / "beacon" / VERSION / "features" / FEATURE
    d.mkdir(parents=True, exist_ok=True)
    (d / "truth.md").write_text(
        f"""---
slug: {FEATURE}
version: {VERSION}
status: frozen
revision_id: R0
language: zh
parser_contract: beacon-feature-package-v2
participating_services: [svc_a, svc_b]
git_canonical_branch: main
---

# {FEATURE}
""",
        encoding="utf-8",
    )
    for name in ("tests.md", "tasks.md", "evidence.md"):
        (d / name).write_text(f"# {name}\n", encoding="utf-8")
    docs = root / "docs" / "beacon"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "VERSION").write_text(f"{VERSION}\n", encoding="utf-8")


def _seed_multi_git(
    root: Path,
    *,
    service_a: Path,
    service_b: Path,
    primary_first: bool = False,
    worktree_mode: str = "pooled",
) -> None:
    bindings = [
        {
            "service_key": "svc_a",
            "repo_root": str(service_a),
            "repo_root_relative": str(service_a),
            "role": "service",
            "writable": True,
            "worktree_path_policy": "follow-repo-root",
        },
        {
            "service_key": "svc_b",
            "repo_root": str(service_b),
            "repo_root_relative": str(service_b),
            "role": "service",
            "writable": True,
            "worktree_path_policy": "follow-repo-root",
        },
        {
            "service_key": "rolo",
            "repo_root": str(root),
            "repo_root_relative": ".",
            "role": "primary",
            "writable": False,
            "worktree_path_policy": "follow-repo-root",
        },
    ]
    if primary_first:
        bindings = [bindings[-1], *bindings[:-1]]
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "multi_git_workspace",
            "default_execution_service": "svc_a",
            "service_bindings": bindings,
        },
        "version_scoped_metadata": {
            VERSION: {
                "version": VERSION,
                "participating_services": ["svc_a", "svc_b"],
                "per_service_canonical_branch": {
                    "svc_a": f"beacon/{VERSION}/{FEATURE}",
                    "svc_b": f"beacon/{VERSION}/{FEATURE}",
                },
                "per_service_baseline_branch": {
                    "svc_a": "main",
                    "svc_b": "main",
                },
                "service_worktree_path_pattern": ".beacon/worktrees/<version>/<feature_slug>/services/<service_key>",
                "previous_version_baseline_branch": "main",
                "next_version_feature_branch": f"beacon/{VERSION}/<feature-slug>",
                "worktree_mode": worktree_mode,
                "worktree_path": f".beacon/worktrees/{VERSION}",
                "require_workspace_admission": True,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")


def test_governance_uses_explicit_primary_and_stable_service_roots(tmp_path: Path) -> None:
    root = tmp_path / "rolo"
    svc = tmp_path / "svc"
    _seed_repo(root)
    _seed_repo(svc)
    bad = str(root / ".worktrees" / "feature-demo" / "svc")
    bindings = [
        {
            "service_key": "svc",
            "repo_root": bad,
            "role": "service",
            "writable": True,
            "worktree_path_policy": "follow-repo-root",
        },
        {
            "service_key": "rolo",
            "repo_root": str(root),
            "role": "primary",
            "writable": False,
            "worktree_path_policy": "follow-repo-root",
        },
    ]
    assert resolve_primary_binding(bindings)["service_key"] == "rolo"
    assert is_feature_worktree_binding_path(bad)
    migration = migrate_feature_worktree_service_bindings(bindings)
    assert migration["status"] == "action_required"
    assert migration["findings"][0]["service_key"] == "svc"
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "multi_git_workspace",
            "default_execution_service": "svc",
            "service_bindings": [
                {
                    "service_key": "svc",
                    "repo_root": str(svc),
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                },
                {
                    "service_key": "rolo",
                    "repo_root": str(root),
                    "role": "primary",
                    "writable": False,
                    "worktree_path_policy": "follow-repo-root",
                },
            ],
        },
        "version_scoped_metadata": {
            VERSION: {
                "version": VERSION,
                "participating_services": ["svc"],
                "per_service_canonical_branch": {"svc": "main"},
                "per_service_baseline_branch": {"svc": "main"},
                "service_worktree_path_pattern": ".beacon/worktrees/<version>/<feature_slug>/services/<service_key>",
            }
        },
    }
    text = render_governance_markdown(payload)
    parsed = parse_governance_markdown(text, project_root=root)
    assert parsed["global_project_metadata"]["topology_kind"] == "multi_git_workspace"
    assert resolve_primary_binding(parsed["global_project_metadata"]["service_bindings"])["service_key"] == "rolo"
    contract = parsed["version_scoped_metadata"][VERSION]
    assert contract["per_service_baseline_branch"]["svc"] == "main"
    assert "services/<service_key>" in contract["service_worktree_path_pattern"]


def test_metadata_verify_accepts_multi_git_workspace_and_primary_role(tmp_path: Path) -> None:
    root = tmp_path / "rolo"
    svc_a = tmp_path / "svc_a"
    svc_b = tmp_path / "svc_b"
    _seed_repo(root)
    _seed_repo(svc_a)
    _seed_repo(svc_b)
    _seed_multi_git(root, service_a=svc_a, service_b=svc_b, primary_first=False)
    result = verify_project_metadata(root, version="")
    topology = next(item for item in result["checks"] if item["name"] == "topology_kind")
    primary = next(item for item in result["checks"] if item["name"] == "explicit_primary_binding")
    stable = next(item for item in result["checks"] if item["name"] == "stable_service_repo_roots")
    assert topology["status"] == "pass"
    assert primary["status"] == "pass"
    assert primary["details"]["primary_service_key"] == "rolo"
    assert stable["status"] == "pass"


def test_workspace_pool_v2_parent_and_service_lease_lifecycle(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    _seed_repo(root)
    _seed_frozen_truth(root)
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
                    "repo_root_relative": ".",
                    "role": "primary",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                }
            ],
        },
        "version_scoped_metadata": {
            VERSION: {
                "version": VERSION,
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": f"beacon/{VERSION}/{FEATURE}"},
                "previous_version_baseline_branch": "main",
                "next_version_feature_branch": f"beacon/{VERSION}/<feature-slug>",
                "worktree_mode": "pooled",
                "worktree_path": f".beacon/worktrees/{VERSION}",
                "require_workspace_admission": True,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    admit = run_workspace_admit(root, version=VERSION, feature=FEATURE)
    assert admit["status"] == "pass"
    parent_wt = Path(admit["worktree_path"])
    assert parent_wt.exists()
    lease = upsert_service_pool_leases(
        root,
        version=VERSION,
        feature=FEATURE,
        service_leases={
            "beacon": {
                "repo_root": str(root),
                "branch": admit["branch"],
                "base_branch": "main",
                "worktree_path": str(parent_wt),
                "git_head": admit["git_head"],
                "state": "leased",
            }
        },
    )
    assert lease["status"] == "pass"
    pool = json.loads(pool_state_path(root, version=VERSION).read_text(encoding="utf-8"))
    assert pool["schema_version"] == "workspace-pool-v2"
    entry = pool["entries"][FEATURE]
    assert entry["state"] == "leased"
    assert entry["services"]["beacon"]["state"] == "leased"
    released = release_workspace_lease(root, version=VERSION, feature=FEATURE)
    assert released["status"] == "pass"
    assert released["worktree_deleted"] is False
    assert parent_wt.exists()
    pool2 = json.loads(pool_state_path(root, version=VERSION).read_text(encoding="utf-8"))
    assert pool2["entries"][FEATURE]["state"] == "released"
    assert pool2["entries"][FEATURE]["services"]["beacon"]["state"] == "released"
    # corrupt state fails closed
    pool_state_path(root, version=VERSION).write_text("{not-json", encoding="utf-8")
    bad = upsert_service_pool_leases(root, version=VERSION, feature=FEATURE, service_leases={})
    assert bad["status"] == "blocked"
    assert bad["reason_code"] == "workspace_pool_state_corrupt"


def test_implement_admission_materializes_every_participating_service_worktree(tmp_path: Path) -> None:
    root = tmp_path / "rolo"
    svc_a = tmp_path / "svc_a"
    svc_b = tmp_path / "svc_b"
    _seed_repo(root)
    _seed_repo(svc_a)
    _seed_repo(svc_b)
    _seed_frozen_truth(root)
    _seed_multi_git(root, service_a=svc_a, service_b=svc_b, worktree_mode="dedicated")
    gate = ensure_implement_admission(
        root,
        version=VERSION,
        feature=FEATURE,
        execution_surface="direct",
        require_freeze=True,
    )
    assert gate["status"] == "pass", gate
    mapping = gate["service_worktree_map"]
    assert set(mapping) == {"svc_a", "svc_b"}
    for key, path in mapping.items():
        assert is_real_git_worktree(Path(path))
        assert key in path
        expected = resolve_service_worktree_path(root, version=VERSION, feature=FEATURE, service_key=key)
        assert Path(path) == expected
    pool = json.loads(pool_state_path(root, version=VERSION).read_text(encoding="utf-8"))
    assert pool["schema_version"] == "workspace-pool-v2"
    services = pool["entries"][FEATURE]["services"]
    assert set(services) == {"svc_a", "svc_b"}
    assert services["svc_a"]["base_branch"] == "main"


def test_topology_gate_and_write_guard_reject_parent_only_service_write(tmp_path: Path) -> None:
    root = tmp_path / "rolo"
    svc_a = tmp_path / "svc_a"
    svc_b = tmp_path / "svc_b"
    _seed_repo(root)
    _seed_repo(svc_a)
    _seed_repo(svc_b)
    _seed_frozen_truth(root)
    _seed_multi_git(root, service_a=svc_a, service_b=svc_b, primary_first=False, worktree_mode="dedicated")
    gate = ensure_implement_admission(
        root,
        version=VERSION,
        feature=FEATURE,
        execution_surface="direct",
        require_freeze=True,
    )
    assert gate["status"] == "pass", gate
    parent = Path(gate["worktree_path"])
    mapping = gate["service_worktree_map"]
    graph = build_git_scope_graph(root, version=VERSION, feature=FEATURE)
    assert graph["project_topology"] == TOPOLOGY_MULTI
    primary_scopes = [s for s in graph["scopes"] if s["role"] == "primary"]
    assert len(primary_scopes) == 1
    assert Path(primary_scopes[0]["git_root"]).resolve() == root.resolve()
    assert "svc_a" in graph.get("service_worktree_map") or any(s["scope_id"] == "svc_a" for s in graph["scopes"])

    ok = assert_service_write_authorized(
        target_path=mapping["svc_a"],
        service_worktree_map=mapping,
        parent_worktree=parent,
    )
    assert ok["status"] == "pass"
    blocked = assert_service_write_authorized(
        target_path=parent,
        service_worktree_map=mapping,
        parent_worktree=parent,
    )
    assert blocked["status"] == "blocked"
    assert blocked["reason_code"] == REASON_PARENT_ONLY_SERVICE_WRITE

    parent_cwd_gate = ensure_implement_admission(
        root,
        version=VERSION,
        feature=FEATURE,
        execution_surface="direct",
        require_freeze=True,
        cwd=parent,
    )
    assert parent_cwd_gate["status"] == "blocked"
    assert parent_cwd_gate["reason_code"] == REASON_PARENT_ONLY_SERVICE_WRITE


def test_rolo_v233_v234_fixture_topology_resolve(tmp_path: Path) -> None:
    # Synthetic Rolo-shaped fixture (paths are local; contract mirrors Company/rolo layout).
    root = tmp_path / "Users" / "apple" / "Developer" / "Company" / "rolo"
    marketing = tmp_path / "Users" / "apple" / "Developer" / "Company" / "marketing_sys"
    partner = tmp_path / "Users" / "apple" / "Developer" / "Company" / "app_partner"
    _seed_repo(root)
    _seed_repo(marketing)
    _seed_repo(partner)
    _seed_frozen_truth(root)
    # Intentionally list services before primary to catch first-service-primary regressions.
    _seed_multi_git(root, service_a=marketing, service_b=partner, primary_first=False, worktree_mode="dedicated")
    # Rename keys in governance to Rolo-like service names via direct overwrite of bindings text is heavy;
    # instead assert topology resolve uses root primary regardless of binding order.
    scopes = build_scope_list(root, version=VERSION, feature=FEATURE, project_topology=TOPOLOGY_MULTI)
    primary = [s for s in scopes if s["role"] == "primary"]
    assert len(primary) == 1
    assert Path(primary[0]["git_root"]).resolve() == root.resolve()
    assert primary[0]["scope_id"] == "primary"
    # First binding is a service, must not become primary.
    assert scopes[0]["role"] != "primary" or Path(scopes[0]["git_root"]).resolve() == root.resolve()

    admit = run_workspace_admit(root, version=VERSION, feature=FEATURE)
    assert admit["status"] == "pass"
    graph = run_topology_resolve(root, version=VERSION, feature=FEATURE)
    assert graph["topology_gate_status"] == "pass"
    assert "workspace_admission_cwd_mismatch" not in (graph.get("reason_codes") or [])
    assert Path(graph["workspace_admit"]["worktree_path"]).resolve() == Path(admit["worktree_path"]).resolve()


def test_illegal_service_pool_transitions_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "rolo"
    svc = tmp_path / "svc"
    _seed_repo(root)
    _seed_repo(svc)
    _seed_frozen_truth(root)
    _seed_multi_git(root, service_a=svc, service_b=svc, worktree_mode="dedicated")

    # mkdir-only fake service path is rejected by write guard / is_real_git_worktree
    fake = root / ".beacon" / "worktrees" / VERSION / FEATURE / "services" / "svc_a"
    fake.mkdir(parents=True, exist_ok=True)
    assert not is_real_git_worktree(fake)

    # parent-only write rejected when distinct service map exists
    blocked = assert_service_write_authorized(
        target_path=root,
        service_worktree_map={"svc_a": str(svc)},
        parent_worktree=root,
    )
    assert blocked["reason_code"] == REASON_PARENT_ONLY_SERVICE_WRITE

    # missing service map when required
    missing = assert_service_write_authorized(
        target_path=root,
        service_worktree_map={},
        require_service_map=True,
    )
    assert missing["reason_code"] == "service_worktree_map_missing"

    # feature-worktree binding rejected by migration helper (no soft accept)
    migration = migrate_feature_worktree_service_bindings(
        [{"service_key": "x", "repo_root": str(root / ".worktrees" / "feature-x" / "svc")}]
    )
    assert migration["status"] == "action_required"
