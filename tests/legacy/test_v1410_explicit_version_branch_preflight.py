from __future__ import annotations

import subprocess
from pathlib import Path

from beacon.commands.implement.commands import _branch_guard_inputs, _run_branch_preflight
from beacon.utils.execution_branch_contract import load_execution_branch_contract


FEATURE = "msq-part1-dossier"
VERSION = "v2.0.0"
OLD_BRANCH = "feature/v1.3.5-truth-engine-cutover"
CANONICAL_BRANCH = "feature/v2.0.0-all"


def _git(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(result.stdout or "").strip()


def _seed_repo(root: Path, branch: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_rolo_services(workspace: Path, *, branch: str = OLD_BRANCH, canonical_worktrees: bool = False) -> None:
    for service in ("marketing_sys", "marketing_primary_fe"):
        root = workspace / service
        if canonical_worktrees:
            root = workspace / service / ".worktrees" / "feature-v2.0.0-all"
        _seed_repo(root, branch)


def _write_execution_materials(workspace: Path) -> None:
    execution = workspace / "docs" / "beacon" / VERSION / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / f"git-workflow-{FEATURE}.md").write_text(
        """# Beacon Git Workflow Contract

- feature: `msq-part1-dossier`
- version: `v2.0.0`
- mode: `workspace`
- expected_branch: `per-service`
- branch_prefix: `feature/`
- base_branch: `master`
- use_git_worktree: `True`
- require_clean_worktree_for_switch: `True`
- worktree_root: `.`

## Service Directories
- `marketing_primary_fe`
- `marketing_sys`

## Direct Delivery Services
- `marketing_primary_fe`
- `marketing_sys`

## Per-Service Branch / Worktree Map
| Service | Expected branch | Expected worktree |
| --- | --- | --- |
| `marketing_primary_fe` | `feature/v2.0.0-all` | `marketing_primary_fe/.worktrees/feature-v2.0.0-all` |
| `marketing_sys` | `feature/v2.0.0-all` | `marketing_sys/.worktrees/feature-v2.0.0-all` |
""",
        encoding="utf-8",
    )
    (execution / f"deterministic-implementation-contract-{FEATURE}.md").write_text(
        """# Deterministic Implementation Contract

## Git
- base_branch: `master`
- target_branch: `per-service`
- branch_prefix: `feature/`

## Worktree
- use_git_worktree: `True`
- worktree_root: `.`

## Direct Delivery Services
- `marketing_primary_fe`
- `marketing_sys`

## Service Branch Map
| Service | Canonical development branch | Canonical worktree |
| --- | --- | --- |
| `marketing_primary_fe` | `feature/v2.0.0-all` | `marketing_primary_fe/.worktrees/feature-v2.0.0-all` |
| `marketing_sys` | `feature/v2.0.0-all` | `marketing_sys/.worktrees/feature-v2.0.0-all` |
""",
        encoding="utf-8",
    )
    (execution / f"branch-governance-{FEATURE}.md").write_text(
        """# MSQ v2.0.0 Branch Governance Note

| 服务 | canonical development branch | canonical worktree | 当前主工作树角色 |
| --- | --- | --- | --- |
| `marketing_sys` | `feature/v2.0.0-all` | `marketing_sys/.worktrees/feature-v2.0.0-all` | `feature/v1.3.5-truth-engine-cutover` |
| `marketing_primary_fe` | `feature/v2.0.0-all` | `marketing_primary_fe/.worktrees/feature-v2.0.0-all` | `feature/v1.3.5-truth-engine-cutover` |
""",
        encoding="utf-8",
    )


def _run_with_inputs(workspace: Path) -> dict:
    inputs = _branch_guard_inputs(workspace, version=VERSION, feature=FEATURE)
    return _run_branch_preflight(
        project_root=workspace,
        version=VERSION,
        run_id="run-test",
        feature=FEATURE,
        auto_switch_branch=False,
        require_clean_worktree_for_switch=bool(inputs["require_clean_worktree_for_switch"]),
        expected_branch=str(inputs["expected_branch"]),
        branch_prefix=str(inputs["branch_prefix"]),
        base_branch=str(inputs["base_branch"]),
        git_roots=list(inputs["git_roots"]),
        direct_delivery_services=list(inputs["direct_delivery_services"]),
        branch_governance=inputs["branch_governance"],
        service_branch_map=inputs.get("service_branch_map", {}),
        service_worktree_map=inputs.get("service_worktree_map", {}),
    )


def test_explicit_version_loads_execution_materials_before_mutation(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    contract = load_execution_branch_contract(tmp_path, version=VERSION, feature=FEATURE)
    assert "git-workflow" in contract["loaded_material_types"]
    assert "deterministic-implementation-contract" in contract["loaded_material_types"]
    assert "branch-governance" in contract["loaded_material_types"]
    assert contract["expected_branch"] == "per-service"


def test_branch_governance_git_workflow_and_deterministic_contract_are_sources(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    inputs = _branch_guard_inputs(tmp_path, version=VERSION, feature=FEATURE)
    assert set(inputs["execution_branch_contract"]["loaded_material_types"]) == {
        "branch-governance",
        "git-workflow",
        "deterministic-implementation-contract",
    }
    assert inputs["service_branch_map"]["marketing_sys"] == CANONICAL_BRANCH
    assert inputs["service_worktree_map"]["marketing_primary_fe"].endswith(".worktrees/feature-v2.0.0-all")


def test_target_service_branch_and_worktree_are_validated(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    _seed_rolo_services(tmp_path)
    payload = _run_with_inputs(tmp_path)
    repos = {item["service"]: item for item in payload["git_alignment"]["workspace_repos"]}
    assert repos["marketing_sys"]["current_branch"] == OLD_BRANCH
    assert repos["marketing_sys"]["expected_branch"] == CANONICAL_BRANCH
    assert repos["marketing_sys"]["worktree_matches_expected"] is False


def test_per_service_expected_branch_resolves_map(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    _seed_rolo_services(tmp_path)
    payload = _run_with_inputs(tmp_path)
    assert payload["expected_branch"] == "per-service"
    assert payload["blocked"] is True
    assert payload["branch_exists"] is False
    assert "git_branch_target_mismatch" in payload["reason_codes"]


def test_canonical_mismatch_blocks_before_code_edit_or_commit(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    _seed_rolo_services(tmp_path)
    payload = _run_with_inputs(tmp_path)
    assert payload["status"] == "blocked"
    assert "explicit_version_canonical_branch_mismatch" in payload["reason_codes"]
    assert "explicit_version_canonical_worktree_mismatch" in payload["reason_codes"]


def test_origin_master_ancestry_pass_does_not_override_canonical_mismatch(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    _seed_rolo_services(tmp_path)
    payload = _run_with_inputs(tmp_path)
    payload["origin_master_ancestry"] = {"status": "pass"}
    assert payload["origin_master_ancestry"]["status"] == "pass"
    assert payload["blocked"] is True
    assert "explicit_version_canonical_branch_mismatch" in payload["reason_codes"]


def test_rolo_v200_marketing_services_on_v135_branch_block(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    _seed_rolo_services(tmp_path)
    payload = _run_with_inputs(tmp_path)
    assert payload["blocked"] is True
    assert "feature/v2.0.0-all" in " ".join(payload["recommended_commands"])
    assert "marketing_sys/.worktrees/feature-v2.0.0-all" in " ".join(payload["recommended_commands"])
    assert "marketing_primary_fe/.worktrees/feature-v2.0.0-all" in " ".join(payload["recommended_commands"])


def test_blocked_output_names_expected_branch_and_worktree(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    _seed_rolo_services(tmp_path)
    payload = _run_with_inputs(tmp_path)
    for item in payload["git_alignment"]["workspace_repos"]:
        assert item["expected_branch"] == CANONICAL_BRANCH
        assert item["expected_worktree"].endswith(f"{item['service']}/.worktrees/feature-v2.0.0-all")
    assert payload["recommended_command"].startswith("cd ")


def test_per_service_map_missing_blocks(tmp_path: Path) -> None:
    _seed_rolo_services(tmp_path)
    payload = _run_branch_preflight(
        project_root=tmp_path,
        version=VERSION,
        run_id="run-test",
        feature=FEATURE,
        auto_switch_branch=False,
        require_clean_worktree_for_switch=True,
        expected_branch="per-service",
        branch_prefix="feature/",
        base_branch="master",
        git_roots=["marketing_sys", "marketing_primary_fe"],
        direct_delivery_services=["marketing_sys", "marketing_primary_fe"],
        branch_governance={},
        service_branch_map={},
        service_worktree_map={},
    )
    assert payload["blocked"] is True
    assert "explicit_version_per_service_map_missing" in payload["reason_codes"]


def test_canonical_worktree_passes_when_branch_and_worktree_match(tmp_path: Path) -> None:
    _write_execution_materials(tmp_path)
    _seed_rolo_services(tmp_path, branch=CANONICAL_BRANCH, canonical_worktrees=True)
    payload = _run_branch_preflight(
        project_root=tmp_path,
        version=VERSION,
        run_id="run-test",
        feature=FEATURE,
        auto_switch_branch=False,
        require_clean_worktree_for_switch=True,
        expected_branch="per-service",
        branch_prefix="feature/",
        base_branch="master",
        git_roots=[
            "marketing_sys/.worktrees/feature-v2.0.0-all",
            "marketing_primary_fe/.worktrees/feature-v2.0.0-all",
        ],
        direct_delivery_services=["marketing_sys", "marketing_primary_fe"],
        branch_governance={},
        service_branch_map={
            "marketing_sys": CANONICAL_BRANCH,
            "marketing_primary_fe": CANONICAL_BRANCH,
        },
        service_worktree_map={
            "marketing_sys": "marketing_sys/.worktrees/feature-v2.0.0-all",
            "marketing_primary_fe": "marketing_primary_fe/.worktrees/feature-v2.0.0-all",
        },
    )
    assert payload["blocked"] is False
