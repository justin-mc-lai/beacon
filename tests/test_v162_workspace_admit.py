from __future__ import annotations

import json
import subprocess
from pathlib import Path

from beacon.utils.project_governance import commit_governance_payload
from beacon.utils.workspace_admission import (
    SCHEMA_VERSION,
    artifact_path,
    gate_workspace_admission_or_block,
    inject_git_admission_into_skill_text,
    load_admission_contract,
    run_workspace_admit,
    validate_workspace_admission,
    write_admission_artifact,
)

VERSION = "v1.6.2"
FEATURE = "beacon-global-workspace-git-admission-v162"


def _git(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(result.stdout or "").strip()


def _seed_repo(root: Path, *, branch: str = "pre-main") -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_governance(root: Path) -> None:
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
        "version_scoped_metadata": {
            VERSION: {
                "version": VERSION,
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": "beacon/v1.6.2"},
                "branch_guard_mode": "strict",
                "validation_state": "active",
                "previous_version_baseline_branch": "pre-main",
                "next_version_feature_branch": "beacon/v1.6.2/<feature-slug>",
                "worktree_mode": "dedicated",
                "worktree_path": ".beacon/worktrees/v1.6.2",
                "require_workspace_admission": True,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    docs = root / "docs" / "beacon"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "VERSION").write_text(f"{VERSION}\n", encoding="utf-8")


def test_load_admission_contract_v162(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    contract = load_admission_contract(tmp_path, version=VERSION)
    assert contract["require_workspace_admission"] is True
    assert contract["admission_invalidation"] == "dirty_only"
    assert contract["worktree_mode"] == "dedicated-worktree"


def test_workspace_admit_issues_artifact_without_expires_at(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    payload = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    assert payload.get("status") == "pass"
    assert payload.get("worktree_path")
    artifact_file = artifact_path(tmp_path, version=VERSION, feature=FEATURE)
    assert artifact_file.is_file()
    artifact = json.loads(artifact_file.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == SCHEMA_VERSION
    assert "expires_at" not in artifact
    assert artifact.get("git_head")


def test_admit_json_schema_no_expires_at(tmp_path: Path) -> None:
    test_workspace_admit_issues_artifact_without_expires_at(tmp_path)


def test_governance_v162_dirty_only(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    md = (tmp_path / "docs" / "beacon" / "governance" / "project-version-governance.md").read_text(encoding="utf-8")
    assert "require_workspace_admission: `true`" in md or "require_workspace_admission: true" in md
    assert "admission_invalidation: `dirty_only`" in md or "admission_invalidation: dirty_only" in md
    contract = load_admission_contract(tmp_path, version=VERSION)
    assert contract["admission_invalidation"] == "dirty_only"


def test_dirty_invalidation_branch_change(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    admit = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    worktree = Path(str(admit["worktree_path"]))
    _git(["git", "checkout", "-b", "wrong-branch"], cwd=worktree)
    validation = validate_workspace_admission(tmp_path, version=VERSION, feature=FEATURE, cwd=worktree)
    assert validation["valid"] is False
    assert "workspace_admission_dirty_branch" in validation["reason_codes"]


def test_dirty_head_invalidates_admission(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    admit = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    worktree = Path(str(admit["worktree_path"]))
    (worktree / "dirty.txt").write_text("x\n", encoding="utf-8")
    _git(["git", "add", "dirty.txt"], cwd=worktree)
    _git(["git", "commit", "-m", "dirty"], cwd=worktree)
    validation = validate_workspace_admission(tmp_path, version=VERSION, feature=FEATURE, cwd=worktree)
    assert validation["valid"] is False
    assert "workspace_admission_dirty_head" in validation["reason_codes"]


def test_gate_blocks_without_artifact(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    block = gate_workspace_admission_or_block(tmp_path, version=VERSION, feature=FEATURE)
    assert block is not None
    assert block["status"] == "blocked"
    assert block["reason_code"] == "workspace_admission_missing"


def test_inject_git_admission_into_tier_a_skill() -> None:
    text = "# Skill\n\n## Beacon v1.6.0 共享 Preamble\n\n1. item\n"
    injected = inject_git_admission_into_skill_text("beacon-gen-implement", text)
    assert "GIT_ADMISSION" in injected
    assert "workspace admit" in injected


def test_manual_artifact_still_valid_without_ttl(tmp_path: Path) -> None:
    _seed_repo(tmp_path, branch="pre-main")
    _seed_governance(tmp_path)
    admit = run_workspace_admit(tmp_path, version=VERSION, feature=FEATURE)
    worktree = Path(str(admit["worktree_path"]))
    path = artifact_path(tmp_path, version=VERSION, feature=FEATURE)
    artifact = json.loads(path.read_text(encoding="utf-8"))
    artifact["issued_at"] = "2020-01-01T00:00:00+00:00"
    write_admission_artifact(path, artifact)
    validation = validate_workspace_admission(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        cwd=worktree,
    )
    assert validation["valid"] is True


def test_no_ttl_still_valid(tmp_path: Path) -> None:
    test_manual_artifact_still_valid_without_ttl(tmp_path)
