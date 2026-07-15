from __future__ import annotations

import json
from pathlib import Path

from tests.test_v162_workspace_admit import _git, _seed_repo

from beacon.utils.project_governance import commit_governance_payload
from beacon.utils.workspace_admission import (
    artifact_path,
    load_admission_contract,
    pool_state_path,
    release_workspace_lease,
    resolve_worktree_path,
    run_workspace_admit,
)

VERSION = "v1.6.5"
FEATURE = "beacon-workspace-pool-lease-v165"


def _seed_pooled_governance(root: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "single_repo",
            "default_execution_service": "beacon",
            "service_bindings": [{"service_key": "beacon", "repo_root": str(root), "repo_root_relative": ".", "role": "service", "writable": True}],
        },
        "version_scoped_metadata": {
            VERSION: {
                "version": VERSION,
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": f"beacon/{VERSION}"},
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
    (root / "docs/beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs/beacon/VERSION").write_text(f"{VERSION}\n", encoding="utf-8")


def test_pooled_contract_resolution(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="main")
    _seed_pooled_governance(tmp_path)
    contract = load_admission_contract(tmp_path, version=VERSION)
    assert contract["worktree_mode"] == "pooled"
    assert resolve_worktree_path(tmp_path, contract, feature=FEATURE).endswith(f".beacon/worktrees/{VERSION}/{FEATURE}")


def test_admit_reuses_released_pool_entry(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="main")
    _seed_pooled_governance(tmp_path)
    first = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    assert first["status"] == "pass"
    assert release_workspace_lease(tmp_path, version=VERSION, feature=FEATURE)["status"] == "pass"
    second = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    assert second["status"] == "pass"
    assert second["worktree_path"] == first["worktree_path"]


def test_pool_entry_schema(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="main")
    _seed_pooled_governance(tmp_path)
    payload = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    entry = payload["pool_entry"]
    for field in ("state", "feature_slug", "branch", "worktree_path", "lease_holder", "leased_at", "released_at", "git_head"):
        assert field in entry
    assert entry["state"] == "leased"
    assert entry["feature_slug"] == FEATURE


def test_workspace_release_marks_available_without_delete(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="main")
    _seed_pooled_governance(tmp_path)
    admit = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    worktree = Path(admit["worktree_path"])
    release = release_workspace_lease(tmp_path, version=VERSION, feature=FEATURE)
    assert release["status"] == "pass"
    assert release["pool_entry"]["state"] == "released"
    assert worktree.is_dir()


def test_foreign_active_lease_blocks_admit(tmp_path: Path, monkeypatch) -> None:
    _seed_repo(tmp_path, branch="main")
    _seed_pooled_governance(tmp_path)
    monkeypatch.setenv("BEACON_WORKSPACE_LEASE_HOLDER", "holder-a")
    assert run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)["status"] == "pass"
    monkeypatch.setenv("BEACON_WORKSPACE_LEASE_HOLDER", "holder-b")
    blocked = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    assert blocked["status"] == "blocked"
    assert blocked["reason_code"] == "workspace_pool_lease_in_use"


def test_corrupt_pool_state_fails_closed(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="main")
    _seed_pooled_governance(tmp_path)
    path = pool_state_path(tmp_path, version=VERSION)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not-json", encoding="utf-8")
    blocked = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    assert blocked["status"] == "blocked"
    assert blocked["reason_code"] == "workspace_pool_state_corrupt"
    assert path.read_text(encoding="utf-8") == "{not-json"


def test_dedicated_mode_remains_compatible(tmp_path: Path) -> None:
    from tests.test_v162_workspace_admit import FEATURE as OLD_FEATURE
    from tests.test_v162_workspace_admit import VERSION as OLD_VERSION
    from tests.test_v162_workspace_admit import _seed_governance

    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    payload = run_workspace_admit(tmp_path, version=OLD_VERSION, feature=OLD_FEATURE)
    assert payload["status"] == "pass"
    assert "pool_entry" not in payload
    assert artifact_path(tmp_path, version=OLD_VERSION, feature=OLD_FEATURE).is_file()
    assert _git(["git", "branch", "--show-current"], cwd=Path(payload["worktree_path"])) == f"beacon/{OLD_VERSION}/{OLD_FEATURE}"
