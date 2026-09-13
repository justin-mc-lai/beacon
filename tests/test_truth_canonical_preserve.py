"""Regression (issue #20): never downgrade an explicit truth_canonical to `main`.

`ensure_version_contract_from_feature_package` (freeze path) used to hardcode
`truth_canonical="main"` / `previous_version_baseline_branch="main"`, clobbering
projects whose canonical/production branch is not `main` (e.g. `master`).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from beacon.utils.git_alignment import resolve_default_branch
from beacon.utils.project_governance import commit_governance_payload
from beacon.utils.project_metadata import (
    ensure_version_contract_from_feature_package,
    load_project_metadata,
)

VERSION = "v1.1.0"
FEATURE = "demo"


def _git(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(result.stdout or "").strip()


def _seed_governance(root: Path, *, truth_canonical: str = "", baseline: str = "") -> None:
    (root / "docs" / "beacon" / "governance").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / VERSION / "features" / FEATURE).mkdir(parents=True, exist_ok=True)
    (root / "svc").mkdir(exist_ok=True)
    contract: dict = {
        "version": VERSION,
        "participating_services": ["svc"],
        "per_service_canonical_branch": {"svc": f"feature/{VERSION}"},
        "branch_guard_mode": "strict",
        "validation_state": "active",
    }
    if truth_canonical:
        contract["truth_canonical"] = truth_canonical
    if baseline:
        contract["previous_version_baseline_branch"] = baseline
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "monorepo",
            "default_execution_service": "svc",
            "service_bindings": [
                {
                    "service_key": "svc",
                    "repo_root": str(root / "svc"),
                    "repo_root_relative": "svc",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                }
            ],
        },
        "version_scoped_metadata": {VERSION: contract},
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    (root / "docs" / "beacon" / VERSION / "features" / FEATURE / "truth.md").write_text(
        "---\n"
        f"slug: {FEATURE}\n"
        f"version: {VERSION}\n"
        "status: frozen\n"
        "language: zh\n"
        "parser_contract: beacon-feature-package-v2\n"
        f"git_canonical_branch: feature/{VERSION}\n"
        "participating_services: [svc]\n"
        "canonical_refs: {}\n"
        "---\n\n# truth\n",
        encoding="utf-8",
    )


def _git_repo_on_branch(root: Path, branch: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / ".keep").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", ".keep"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def test_explicit_truth_canonical_preserved(tmp_path: Path) -> None:
    """Declared `master` must survive the freeze-path contract sync."""
    root = tmp_path / "proj"
    _seed_governance(root, truth_canonical="master", baseline="master")
    before = load_project_metadata(root)["version_scoped_metadata"][VERSION]
    assert before["truth_canonical"] == "master"

    result = ensure_version_contract_from_feature_package(root, version=VERSION, feature=FEATURE)

    assert result["status"] == "ok"
    after = load_project_metadata(root)["version_scoped_metadata"][VERSION]
    assert after["truth_canonical"] == "master"
    assert after["previous_version_baseline_branch"] == "master"


def test_omitted_defaults_to_main_without_git(tmp_path: Path) -> None:
    """Backward compat: no declaration + no git -> `main` (existing tests rely on this)."""
    root = tmp_path / "proj"
    _seed_governance(root)

    result = ensure_version_contract_from_feature_package(root, version=VERSION, feature=FEATURE)

    assert result["status"] == "ok"
    after = load_project_metadata(root)["version_scoped_metadata"][VERSION]
    assert after["truth_canonical"] == "main"


def test_omitted_defaults_to_git_default_branch(tmp_path: Path) -> None:
    """No declaration but repo default is `master` -> default resolves to `master`, not `main`."""
    root = tmp_path / "proj"
    _git_repo_on_branch(root, "master")
    _seed_governance(root)

    result = ensure_version_contract_from_feature_package(root, version=VERSION, feature=FEATURE)

    assert result["status"] == "ok"
    after = load_project_metadata(root)["version_scoped_metadata"][VERSION]
    assert after["truth_canonical"] == "master"


def test_resolve_default_branch_prefers_origin_head(tmp_path: Path) -> None:
    """origin/HEAD symref wins over a locally-present `main`."""
    root = tmp_path / "proj"
    _git_repo_on_branch(root, "master")
    sha = _git(["git", "rev-parse", "HEAD"], cwd=root)
    _git(["git", "update-ref", "refs/remotes/origin/master", sha], cwd=root)
    _git(["git", "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master"], cwd=root)
    _git(["git", "branch", "main"], cwd=root)

    assert resolve_default_branch(root) == "master"


def test_resolve_default_branch_non_git_falls_back_to_main(tmp_path: Path) -> None:
    assert resolve_default_branch(tmp_path / "not-a-repo") == "main"
