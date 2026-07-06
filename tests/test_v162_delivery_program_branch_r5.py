from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from beacon.utils.branch_governance import evaluate_branch_governance, resolve_branch_governance_view
from beacon.utils.execution_branch_contract import (
    find_program_level_git_workflow,
    resolve_workspace_branch_targets,
)
from beacon.utils.workspace_admission import load_admission_contract, run_workspace_admit, validate_workspace_admission

VERSION = "v0.0.9"
FEATURE_LAKE = "cloud-llm-gateway"
PROGRAM_SLUG = "cloud-platform"


def _git(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(result.stdout or "").strip()


def _seed_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", "main"], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_sidepilot_fixture(root: Path, *, worktree: Path) -> None:
    _seed_repo(root)
    worktree.mkdir(parents=True, exist_ok=True)
    _git(["git", "branch", "beacon/v0.0.9"], cwd=root)
    _git(["git", "worktree", "add", str(worktree), "beacon/v0.0.9"], cwd=root)
    governance = root / "docs" / "beacon" / "governance"
    governance.mkdir(parents=True, exist_ok=True)
    (governance / "project-version-governance.md").write_text(
        "\n".join(
            [
                "---",
                'schema_version: "1.0"',
                f'project_root: "{root}"',
                'topology_kind: "single_repo"',
                'default_execution_service: "."',
                'parser_contract: "beacon-project-governance-v1"',
                "---",
                "",
                "## Service Bindings",
                f'- `.` repo=`{root}` role=`service` writable=`true` worktree_policy=`follow-repo-root`',
                "",
                "## Version Contracts",
                "",
                f"### {VERSION}",
                "- participating_services: `.`",
                "- per_service_canonical_branch:",
                "  - `.`: `beacon/v0.0.9`",
                "- previous_version_baseline_branch: `main`",
                "- next_version_feature_branch: `beacon/v0.0.9`",
                "- worktree_mode: `dedicated`",
                f"- worktree_path: `{worktree}`",
                "- require_workspace_admission: `true`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    exec_dir = root / "docs" / "beacon" / VERSION / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / f"git-workflow-{PROGRAM_SLUG}.md").write_text(
        "\n".join(
            [
                "# Git Workflow",
                "",
                f"- feature: `{PROGRAM_SLUG}`",
                f"- version: `{VERSION}`",
                "- branch_resolution_mode: `program-level`",
                "- expected_branch: `beacon/v0.0.9`",
                f"- dedicated_worktree_path: `{worktree}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _git(["git", "add", "docs"], cwd=root)
    _git(["git", "commit", "-m", "seed sidepilot fixture"], cwd=root)
    _git(["git", "checkout", "beacon/v0.0.9"], cwd=worktree)
    _git(["git", "merge", "main", "-m", "sync main"], cwd=worktree)


def test_program_level_git_workflow_discovery(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "cloud-platform"
    _seed_sidepilot_fixture(root, worktree=worktree)
    program = find_program_level_git_workflow(root, version=VERSION)
    assert program is not None
    assert program.get("expected_branch") == "beacon/v0.0.9"
    assert program.get("dedicated_worktree_path") == str(worktree.resolve())


def test_ac019_program_level_admit_resolves_lake_slug(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "cloud-platform"
    _seed_sidepilot_fixture(root, worktree=worktree)
    contract = load_admission_contract(root, version=VERSION)
    targets = resolve_workspace_branch_targets(
        root, version=VERSION, feature=FEATURE_LAKE, admission_contract={**contract, "version": VERSION}
    )
    assert targets["branch_resolution_mode"] == "program-level"
    assert targets["feature_branch"] == "beacon/v0.0.9"
    assert targets["worktree_path"] == str(worktree.resolve())


def test_ac019_workspace_admit_passes_for_lake_slug(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "cloud-platform"
    _seed_sidepilot_fixture(root, worktree=worktree)
    payload = run_workspace_admit(root, version=VERSION, feature=FEATURE_LAKE)
    assert payload.get("skipped") is not True
    assert payload["status"] == "pass"
    assert payload["branch"] == "beacon/v0.0.9"
    assert payload["worktree_path"] == str(worktree.resolve())


def test_ac021_doctor_branch_mismatch_reason_code(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "cloud-platform"
    _seed_sidepilot_fixture(root, worktree=worktree)
    _git(["git", "checkout", "main"], cwd=root)
    view = resolve_branch_governance_view(
        project_root=root,
        version=VERSION,
        metadata_view={
            "version_contract": {
                "per_service_canonical_branch": {".": "beacon/v0.0.9"},
                "next_version_feature_branch": "beacon/v0.0.9",
            },
            "selected_service": ".",
            "selected_branch": "beacon/v0.0.9",
        },
        git_workflow=find_program_level_git_workflow(root, version=VERSION) or {},
    )
    evaluated = evaluate_branch_governance(view, strict=False)
    assert "branch_governance_branch_mismatch" in evaluated.get("reason_codes", [])
    assert evaluated.get("status") == "pass"


def test_ac022_per_feature_default_unchanged(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _seed_repo(root)
    contract = {
        "version": "v9.9.9",
        "feature_branch_pattern": "beacon/v9.9.9/<feature-slug>",
        "worktree_base": str(root / ".beacon" / "worktrees" / "v9.9.9"),
    }
    targets = resolve_workspace_branch_targets(
        root,
        version="v9.9.9",
        feature="demo-feature",
        admission_contract=contract,
    )
    assert targets["branch_resolution_mode"] == "per-feature"
    assert targets["feature_branch"] == "beacon/v9.9.9/demo-feature"


def test_ac019_governance_only_program_level_without_git_workflow_md(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "cloud-platform"
    _seed_repo(root)
    worktree.mkdir(parents=True, exist_ok=True)
    _git(["git", "branch", "beacon/v0.0.9"], cwd=root)
    _git(["git", "worktree", "add", str(worktree), "beacon/v0.0.9"], cwd=root)
    governance = root / "docs" / "beacon" / "governance"
    governance.mkdir(parents=True, exist_ok=True)
    (governance / "project-version-governance.md").write_text(
        "\n".join(
            [
                "---",
                'schema_version: "1.0"',
                f'project_root: "{root}"',
                'topology_kind: "single_repo"',
                'default_execution_service: "."',
                'parser_contract: "beacon-project-governance-v1"',
                "---",
                "",
                "## Service Bindings",
                f'- `.` repo=`{root}` role=`service` writable=`true` worktree_policy=`follow-repo-root`',
                "",
                "## Version Contracts",
                "",
                f"### {VERSION}",
                "- participating_services: `.`",
                "- per_service_canonical_branch:",
                "  - `.`: `beacon/v0.0.9`",
                "- next_version_feature_branch: `beacon/v0.0.9`",
                "- worktree_mode: `dedicated`",
                f"- worktree_path: `{worktree}`",
                "- require_workspace_admission: `true`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _git(["git", "add", "docs"], cwd=root)
    _git(["git", "commit", "-m", "governance only"], cwd=root)
    contract = load_admission_contract(root, version=VERSION)
    targets = resolve_workspace_branch_targets(
        root, version=VERSION, feature=FEATURE_LAKE, admission_contract={**contract, "version": VERSION}
    )
    assert targets["branch_resolution_mode"] == "program-level"
    assert targets["worktree_path"] == str(worktree.resolve())
    payload = run_workspace_admit(root, version=VERSION, feature=FEATURE_LAKE)
    assert payload["status"] == "pass"
    assert payload["worktree_path"] == str(worktree.resolve())


def test_ac020_soft_admission_branch_alignment_blocks(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "cloud-platform"
    _seed_sidepilot_fixture(root, worktree=worktree)
    soft_contract = {
        "version": VERSION,
        "require_workspace_admission": False,
        "previous_version_baseline_branch": "main",
        "feature_branch_pattern": "beacon/v0.0.9",
        "worktree_base": str(worktree),
    }
    validation = validate_workspace_admission(
        root,
        version=VERSION,
        feature=FEATURE_LAKE,
        cwd=root,
        contract=soft_contract,
    )
    assert validation["status"] == "blocked"
    assert "branch_alignment_required" in validation.get("reason_codes", [])
