from __future__ import annotations

import subprocess
from pathlib import Path

from beacon.utils.execution_branch_contract import (
    coerce_aggregation_branch,
    coerce_aggregation_worktree_path,
    is_program_level_branch_contract,
    resolve_workspace_branch_targets,
)
from beacon.utils.workspace_admission import _detect_nested_ref_conflict, run_workspace_admit


VERSION = "v1.6.4"
FEATURE = "beacon-qa-chrome-extension-e2e-v164"


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


def _write_governance(root: Path) -> None:
    governance = root / "docs" / "beacon" / "governance"
    governance.mkdir(parents=True, exist_ok=True)
    (governance / "project-version-governance.md").write_text(
        "\n".join(
            [
                "---",
                'schema_version: "1.0"',
                f'project_root: "{root}"',
                'topology_kind: "single_repo"',
                'default_execution_service: "beacon"',
                'parser_contract: "beacon-project-governance-v1"',
                "---",
                "",
                "## Service Bindings",
                f'- `beacon` repo=`{root}` role=`service` writable=`true` worktree_policy=`follow-repo-root`',
                "",
                "## Version Contracts",
                "",
                f"### {VERSION}",
                "- participating_services: `beacon`",
                "- per_service_canonical_branch:",
                f"  - `beacon`: `beacon/{VERSION}`",
                "- previous_version_baseline_branch: `main`",
                f"- next_version_feature_branch: `beacon/{VERSION}/<feature-slug>`",
                "- worktree_mode: `dedicated`",
                f"- worktree_path: `.beacon/worktrees/{VERSION}`",
                "- require_workspace_admission: `true`",
                "- admission_invalidation: `dirty_only`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_deterministic_contract(root: Path, *, feature: str = FEATURE) -> None:
    exec_dir = root / "docs" / "beacon" / VERSION / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / f"deterministic-implementation-contract-{feature}.md").write_text(
        "\n".join(
            [
                "# Deterministic Implementation Contract",
                "",
                f"- feature: `{feature}`",
                f"- version: `{VERSION}`",
                f"- base_branch: `beacon/{VERSION}`",
                f"- target_branch: `beacon/{VERSION}`",
                "- branch_strategy: `single-branch`",
                f"- worktree_root: `{root}`",
                f"- workspace_root: `{root}`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_r7_nested_child_refs_select_non_conflicting_aggregation_branch(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _seed_repo(root)
    _git(["git", "branch", f"beacon/{VERSION}/demo-feature"], cwd=root)
    selected = coerce_aggregation_branch(root, version=VERSION, branch=f"beacon/{VERSION}")
    assert selected == f"beacon/{VERSION}/_agg"


def test_r7_per_feature_deterministic_contract_is_not_program_level(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _seed_repo(root)
    _write_governance(root)
    _write_deterministic_contract(root)
    _git(["git", "add", "docs"], cwd=root)
    _git(["git", "commit", "-m", "seed contracts"], cwd=root)

    contract = {
        "source": "execution_markdown",
        "loaded_material_types": ["deterministic-implementation-contract"],
        "material_paths": [
            f"docs/beacon/{VERSION}/execution/deterministic-implementation-contract-{FEATURE}.md"
        ],
        "expected_branch": f"beacon/{VERSION}",
        "worktree_root": str(root),
    }
    assert is_program_level_branch_contract(contract) is False

    targets = resolve_workspace_branch_targets(
        root,
        version=VERSION,
        feature=FEATURE,
        admission_contract={"require_workspace_admission": True, "version": VERSION},
    )
    assert targets["branch_resolution_mode"] == "per-feature"
    assert targets["feature_branch"] == f"beacon/{VERSION}/{FEATURE}"


def test_r7_aggregation_worktree_not_primary_checkout(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _seed_repo(root)
    coerced = coerce_aggregation_worktree_path(root, version=VERSION, worktree_path=str(root))
    assert Path(coerced).resolve() == (root / ".beacon" / "worktrees" / VERSION).resolve()
    assert Path(coerced).resolve() != root.resolve()


def test_r7_nested_ref_conflict_reason_code(tmp_path: Path) -> None:
    attempt = {
        "status": "failed",
        "switch_attempt": {
            "status": "failed",
            "attempts": [
                {
                    "command": ["git", "switch", "-c", f"beacon/{VERSION}"],
                    "exit_code": 128,
                    "stderr": (
                        f"fatal: cannot lock ref 'refs/heads/beacon/{VERSION}': "
                        f"'refs/heads/beacon/{VERSION}/demo-feature' exists; "
                        f"cannot create 'refs/heads/beacon/{VERSION}'"
                    ),
                }
            ],
        },
    }
    assert _detect_nested_ref_conflict(attempt, feature_branch=f"beacon/{VERSION}") is True

    root = tmp_path / "repo"
    _seed_repo(root)
    _write_governance(root)
    # Force program-level via explicit git-workflow, bare aggregation, and child refs.
    exec_dir = root / "docs" / "beacon" / VERSION / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "git-workflow-demo-program.md").write_text(
        "\n".join(
            [
                "# Git Workflow",
                "",
                "- feature: `demo-program`",
                f"- version: `{VERSION}`",
                "- branch_resolution_mode: `program-level`",
                f"- expected_branch: `beacon/{VERSION}`",
                f"- dedicated_worktree_path: `{root}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _git(["git", "branch", f"beacon/{VERSION}/child-feature"], cwd=root)
    _git(["git", "add", "docs"], cwd=root)
    _git(["git", "commit", "-m", "seed program workflow"], cwd=root)

    targets = resolve_workspace_branch_targets(
        root,
        version=VERSION,
        feature="child-feature",
        admission_contract={"require_workspace_admission": True, "version": VERSION},
    )
    # With child refs present, bare aggregation is coerced to _agg before admit.
    assert targets["branch_resolution_mode"] == "program-level"
    assert targets["feature_branch"] == f"beacon/{VERSION}/_agg"
    assert Path(targets["worktree_path"]).resolve() != root.resolve()

    # Direct reason-code mapping remains covered above; admit should succeed on _agg lane.
    payload = run_workspace_admit(root, version=VERSION, feature="child-feature")
    assert payload["status"] == "pass"
    assert payload["branch"] == f"beacon/{VERSION}/_agg"
