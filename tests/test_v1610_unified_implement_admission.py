"""v1.6.10 unified implement admission — real Git topology + surface parity."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from beacon.utils.goal_implement_admission import ensure_goal_implement_admission
from beacon.utils.implement_admission import ensure_implement_admission, is_real_git_worktree
from beacon.utils.project_governance import commit_governance_payload
from beacon.utils.project_metadata import ensure_version_contract_from_feature_package


VERSION = "v1.6.10"
FEATURE = "unified-admit-demo"


def _git(cmd: list[str], cwd: Path) -> str:
    r = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(r.stdout or "").strip()


def _seed_repo(root: Path, *, branch: str = "main") -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_frozen_truth(root: Path, *, feature: str = FEATURE, version: str = VERSION) -> None:
    d = root / "docs" / "beacon" / version / "features" / feature
    d.mkdir(parents=True, exist_ok=True)
    (d / "truth.md").write_text(
        f"""---
slug: {feature}
version: {version}
status: frozen
revision_id: R1
language: en
parser_contract: beacon-feature-package-v2
participating_services: [beacon]
git_canonical_branch: main
---

# {feature}

## Acceptance Criteria
| AC | Desc |
|----|------|
| AC-001 | seeded frozen for UIA tests |
""",
        encoding="utf-8",
    )
    (d / "tests.md").write_text("# tests\n", encoding="utf-8")
    (d / "tasks.md").write_text("# tasks\n", encoding="utf-8")
    (d / "evidence.md").write_text(
        """| surface | authority | path |
|---------|-----------|------|
| package | requirement_truth | truth.md |
""",
        encoding="utf-8",
    )


def _seed_governance(
    root: Path,
    *,
    require: bool = True,
    mode: str = "dedicated",
    topology: str = "single_repo",
    services: list[dict] | None = None,
    per_service: dict[str, str] | None = None,
) -> None:
    bindings = services or [
        {
            "service_key": "beacon",
            "repo_root": str(root),
            "repo_root_relative": ".",
            "role": "service",
            "writable": True,
            "worktree_path_policy": "follow-repo-root",
        }
    ]
    participating = [str(item["service_key"]) for item in bindings]
    branch_map = per_service or {key: f"beacon/{VERSION}/{FEATURE}" for key in participating}
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": topology,
            "default_execution_service": participating[0],
            "service_bindings": bindings,
        },
        "version_scoped_metadata": {
            VERSION: {
                "version": VERSION,
                "participating_services": participating,
                "per_service_canonical_branch": branch_map,
                "branch_guard_mode": "strict",
                "validation_state": "active",
                "truth_canonical": "main",
                "previous_version_baseline_branch": "main",
                "next_version_feature_branch": f"beacon/{VERSION}/<feature-slug>",
                "worktree_mode": mode,
                "worktree_path": f".beacon/worktrees/{VERSION}",
                "require_workspace_admission": require,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    (root / "docs" / "beacon" / VERSION).mkdir(parents=True, exist_ok=True)


def test_direct_goal_team_ralph_share_admission_contract(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True, mode="dedicated")
    _seed_frozen_truth(tmp_path)
    results = {}
    for surface in ("direct", "goal", "team", "ralph"):
        if surface == "goal":
            results[surface] = ensure_goal_implement_admission(
                tmp_path, {"version": VERSION, "feature": FEATURE}
            )
        else:
            results[surface] = ensure_implement_admission(
                tmp_path,
                version=VERSION,
                feature=FEATURE,
                execution_surface=surface,
            )
        assert results[surface]["allow_implement"] is True, results[surface]
        assert results[surface]["worktree_path"]
        assert is_real_git_worktree(results[surface]["worktree_path"])
    paths = {results[s]["worktree_path"] for s in results}
    assert len(paths) == 1
    schemas = {results[s].get("schema") for s in ("direct", "team", "ralph")}
    assert "implement-admission.v1" in schemas


def test_branch_only_soft_skip_never_authorizes_write(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=False, mode="branch-only")
    _seed_frozen_truth(tmp_path)
    gate = ensure_implement_admission(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        execution_surface="direct",
    )
    assert gate["allow_implement"] is True, gate
    assert gate.get("forced_worktree") is True
    assert is_real_git_worktree(gate["worktree_path"])
    # skipped pass without force would be invalid; ensure not soft-only
    assert not (gate.get("admission") or {}).get("skipped") or gate.get("forced_worktree")


def test_single_repo_materializes_real_leaf_worktree(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True, mode="dedicated")
    _seed_frozen_truth(tmp_path)
    gate = ensure_implement_admission(
        tmp_path, version=VERSION, feature=FEATURE, execution_surface="direct"
    )
    assert gate["allow_implement"] is True
    wt = Path(gate["worktree_path"])
    listed = _git(["git", "worktree", "list", "--porcelain"], cwd=tmp_path)
    assert str(wt) in listed or wt.name in listed
    assert gate.get("merge_main") is not None or (gate.get("admission") or {}).get("merge_main") is not None
    assert gate.get("branch")


def test_monorepo_materializes_every_writable_service_worktree(tmp_path: Path) -> None:
    parent = tmp_path / "mono"
    _seed_repo(parent)
    svc_a = parent / "svc_a"
    svc_b = parent / "svc_b"
    _seed_repo(svc_a)
    _seed_repo(svc_b)
    _seed_governance(
        parent,
        require=True,
        mode="dedicated",
        topology="monorepo",
        services=[
            {
                "service_key": "svc_a",
                "repo_root": str(svc_a),
                "repo_root_relative": "svc_a",
                "role": "service",
                "writable": True,
                "worktree_path_policy": "follow-repo-root",
            },
            {
                "service_key": "svc_b",
                "repo_root": str(svc_b),
                "repo_root_relative": "svc_b",
                "role": "service",
                "writable": True,
                "worktree_path_policy": "follow-repo-root",
            },
        ],
        per_service={"svc_a": "feature/v1.6.10", "svc_b": "feature/v1.6.10"},
    )
    _seed_frozen_truth(parent)
    gate = ensure_implement_admission(
        parent, version=VERSION, feature=FEATURE, execution_surface="direct"
    )
    assert gate["allow_implement"] is True, gate
    smap = gate.get("service_worktree_map") or {}
    assert set(smap) == {"svc_a", "svc_b"}
    for key, path in smap.items():
        assert is_real_git_worktree(path), (key, path)


def test_monorepo_rejects_mkdir_only_and_empty_gitlink_services(tmp_path: Path) -> None:
    parent = tmp_path / "mono"
    _seed_repo(parent)
    # mkdir-only "service" directory (no git)
    fake = parent / "svc_fake"
    fake.mkdir()
    # empty gitlink-like path: empty dir pretending to be submodule
    empty = parent / "svc_empty"
    empty.mkdir()
    _seed_governance(
        parent,
        require=True,
        mode="dedicated",
        topology="monorepo",
        services=[
            {
                "service_key": "svc_fake",
                "repo_root": str(fake),
                "repo_root_relative": "svc_fake",
                "role": "service",
                "writable": True,
                "worktree_path_policy": "follow-repo-root",
            },
            {
                "service_key": "svc_empty",
                "repo_root": str(empty),
                "repo_root_relative": "svc_empty",
                "role": "service",
                "writable": True,
                "worktree_path_policy": "follow-repo-root",
            },
        ],
        per_service={"svc_fake": "feature/v1.6.10", "svc_empty": "feature/v1.6.10"},
    )
    _seed_frozen_truth(parent)
    gate = ensure_implement_admission(
        parent, version=VERSION, feature=FEATURE, execution_surface="direct"
    )
    assert gate["allow_implement"] is False, gate
    assert "service_worktree" in str(gate.get("reason_code") or "") or any(
        "service_worktree" in c for c in (gate.get("reason_codes") or [])
    )


def test_governance_overrides_stale_global_seed(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(
        tmp_path,
        require=True,
        mode="dedicated",
        topology="monorepo",
        services=[
            {
                "service_key": "svc_a",
                "repo_root": str(tmp_path / "svc_a"),
                "repo_root_relative": "svc_a",
                "role": "service",
                "writable": True,
                "worktree_path_policy": "follow-repo-root",
            },
            {
                "service_key": "svc_b",
                "repo_root": str(tmp_path / "svc_b"),
                "repo_root_relative": "svc_b",
                "role": "service",
                "writable": True,
                "worktree_path_policy": "follow-repo-root",
            },
        ],
        per_service={"svc_a": "feature/v1.6.10", "svc_b": "feature/v1.6.10"},
    )
    _seed_repo(tmp_path / "svc_a")
    _seed_repo(tmp_path / "svc_b")
    # stale global seed points at wrong version/branch/service
    (tmp_path / "beacon.config.yaml").write_text(
        """
implementation:
  branch_guard:
    expected_branch: beacon/v1.3.5
    git_roots: ["svc_a"]
""",
        encoding="utf-8",
    )
    from beacon.utils.implementation_plan import _default_git_workflow_contract

    contract = _default_git_workflow_contract(tmp_path, version=VERSION, feature=FEATURE)
    assert "svc_b" in contract.get("direct_delivery_services") or "svc_b" in contract.get("service_directories")
    assert contract.get("source") in {"version_governance", "version_governance_overrides_seed"}
    # must not keep only stale one-service seed as authority
    assert set(contract.get("direct_delivery_services") or []) >= {"svc_a", "svc_b"}


def test_strict_branch_cwd_and_head_mismatch_block_before_write(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True, mode="dedicated")
    _seed_frozen_truth(tmp_path)
    gate = ensure_implement_admission(
        tmp_path, version=VERSION, feature=FEATURE, execution_surface="direct"
    )
    assert gate["allow_implement"] is True
    wrong_cwd = tmp_path / "not-the-worktree"
    wrong_cwd.mkdir()
    blocked = ensure_implement_admission(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        execution_surface="direct",
        cwd=wrong_cwd,
    )
    # re-admit succeeds for worktree; cwd mismatch should block
    assert blocked["allow_implement"] is False
    assert any(
        code in (blocked.get("reason_codes") or [blocked.get("reason_code")])
        for code in ("implement_admission_cwd_mismatch", "implement_admission_branch_mismatch")
    ) or "cwd" in str(blocked.get("reason_code") or "")


def test_worker_dispatch_requires_prewrite_admission(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    # no governance / no freeze package -> shared admission must block before writes
    from beacon.commands.implement.commands import run_implement_stage

    code, payload = run_implement_stage(
        feature=FEATURE,
        project_root=tmp_path,
        version=VERSION,
        mode="single",
        dry_run=False,
    )
    assert code == 2
    assert payload.get("status") == "blocked"
    assert payload.get("reason_code")
    # blocked before implementation marker/native write artifacts
    runs = list((tmp_path / ".beacon").rglob("state.json")) if (tmp_path / ".beacon").exists() else []
    # if a state exists it must still be blocked
    for state in runs:
        data = json.loads(state.read_text(encoding="utf-8"))
        assert data.get("status") == "blocked" or data.get("blocked") is True


def test_artifact_records_parent_and_service_reconcile_evidence(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, require=True, mode="dedicated")
    _seed_frozen_truth(tmp_path)
    gate = ensure_implement_admission(
        tmp_path, version=VERSION, feature=FEATURE, execution_surface="direct"
    )
    assert gate["allow_implement"] is True
    art = gate.get("artifact") or {}
    assert art.get("service_worktree_map") is not None or gate.get("service_worktree_map")
    assert art.get("parent_reconcile") is not None or gate.get("merge_main") is not None
    path = tmp_path / ".beacon/state/workspace-admission" / VERSION / f"{FEATURE.replace('_', '-')}.json"
    # feature_slug may normalize underscores
    from beacon.utils.story_state import feature_slug

    path = tmp_path / ".beacon/state/workspace-admission" / VERSION / f"{feature_slug(FEATURE)}.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("worktree_path")
    assert "service_worktree_map" in data or gate.get("service_worktree_map") is not None


def test_freeze_auto_register_enables_dedicated_admission(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    root.mkdir()
    (root / "docs" / "beacon" / "governance").mkdir(parents=True)
    feat = root / "docs" / "beacon" / VERSION / "features" / "demo"
    feat.mkdir(parents=True)
    (feat / "truth.md").write_text(
        f"""---
slug: demo
version: {VERSION}
status: frozen
language: zh
parser_contract: beacon-feature-package-v2
git_canonical_branch: beacon/{VERSION}/demo
participating_services: [beacon]
canonical_refs: {{}}
---

# truth
""",
        encoding="utf-8",
    )
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
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                }
            ],
        },
        "version_scoped_metadata": {},
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    result = ensure_version_contract_from_feature_package(root, version=VERSION, feature="demo")
    assert result["status"] == "ok"
    from beacon.utils.project_metadata import load_project_metadata

    contract = load_project_metadata(root)["version_scoped_metadata"][VERSION]
    mode = str(contract.get("worktree_mode") or (contract.get("branch_governance") or {}).get("worktree_mode") or "")
    assert mode in {"dedicated", "dedicated-worktree"}
    assert contract.get("require_workspace_admission") is True or (
        contract.get("branch_governance") or {}
    ).get("require_workspace_admission") is True
