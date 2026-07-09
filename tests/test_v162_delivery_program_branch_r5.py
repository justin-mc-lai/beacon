from __future__ import annotations

import os
import json
import subprocess
from pathlib import Path

import pytest

from beacon.commands import qa as qa_command
from beacon.utils.branch_governance import evaluate_branch_governance, resolve_branch_governance_view
from beacon.utils.execution_branch_contract import (
    find_program_level_git_workflow,
    resolve_workspace_branch_targets,
)
from beacon.utils.workspace_admission import load_admission_contract, run_workspace_admit, validate_workspace_admission

VERSION = "v0.0.9"
FEATURE_LAKE = "cloud-llm-gateway"
PROGRAM_SLUG = "cloud-platform"
VERSION_R6 = "v0.0.12"
PROGRAM_LAKE_R6 = "content-hub-foundation"
PROGRAM_SLUG_R6 = "sidepilot-pi-host"


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


def _seed_program_topology_fixture(
    root: Path,
    *,
    worktree: Path,
    version: str = VERSION_R6,
    require_admission: bool = True,
    include_git_workflow: bool = False,
    include_version_contract: bool = True,
) -> None:
    _seed_repo(root)
    worktree.mkdir(parents=True, exist_ok=True)
    branch = f"beacon/{version}"
    _git(["git", "branch", branch], cwd=root)
    _git(["git", "worktree", "add", str(worktree), branch], cwd=root)
    governance = root / "docs" / "beacon" / "governance"
    governance.mkdir(parents=True, exist_ok=True)
    version_contract_lines = [
        "",
        f"### {version}",
        "- participating_services: `.`",
        "- branch_guard_mode: `strict`",
        "- validation_state: `active`",
        "- per_service_canonical_branch:",
        f"  - `.`: `{branch}`",
        "- previous_version_baseline_branch: `main`",
        "- branch_resolution_mode: `program-level`",
        f"- aggregation_branch: `{branch}`",
        f"- program_slug: `{PROGRAM_SLUG_R6}`",
        "- worktree_mode: `dedicated`",
        f"- worktree_path: `{worktree}`",
        f"- require_workspace_admission: `{'true' if require_admission else 'false'}`",
        "- admission_invalidation: `dirty_only`",
        "",
    ] if include_version_contract else []
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
                *version_contract_lines,
            ]
        ),
        encoding="utf-8",
    )
    program_root = root / "docs" / "beacon" / version / "programs" / PROGRAM_SLUG_R6
    program_root.mkdir(parents=True, exist_ok=True)
    (program_root / "program-manifest.md").write_text(
        "\n".join(
            [
                "---",
                f"program_slug: {PROGRAM_SLUG_R6}",
                f"version: {version}",
                "lake_or_ocean: 海",
                "program_plan_frozen: true",
                "lake_package_truth_frozen: true",
                "lakes_truth_frozen: 1",
                "lakes_planned: 1",
                "---",
                "",
                f"# Program Manifest - {PROGRAM_SLUG_R6}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (program_root / "feature-graph.json").write_text(
        (
            "{\n"
            '  "schema_version": "1.0",\n'
            f'  "program_slug": "{PROGRAM_SLUG_R6}",\n'
            f'  "version": "{version}",\n'
            '  "scope_mode": "full_parity",\n'
            '  "program_plan_frozen": true,\n'
            '  "lake_or_ocean": "海",\n'
            '  "lakes": [\n'
            f'    {{"slug": "{PROGRAM_LAKE_R6}", "feature_slug": "{PROGRAM_LAKE_R6}", "depends_on": [], "parity_subset": ["content_hub"], "status": "frozen", "truth_status": "frozen"}}\n'
            "  ]\n"
            "}\n"
        ),
        encoding="utf-8",
    )
    (program_root / "program-truth-freeze.json").write_text(
        (
            "{\n"
            '  "schema_version": "1.0",\n'
            f'  "program_slug": "{PROGRAM_SLUG_R6}",\n'
            f'  "version": "{version}",\n'
            '  "status": "frozen",\n'
            '  "blocked": false,\n'
            '  "lakes": [\n'
            f'    {{"slug": "{PROGRAM_LAKE_R6}", "status": "frozen", "truth_promotion_complete": true}}\n'
            "  ]\n"
            "}\n"
        ),
        encoding="utf-8",
    )
    if include_git_workflow:
        exec_dir = root / "docs" / "beacon" / version / "execution"
        exec_dir.mkdir(parents=True, exist_ok=True)
        (exec_dir / f"git-workflow-{PROGRAM_SLUG_R6}.md").write_text(
            "\n".join(
                [
                    "# Git Workflow",
                    "",
                    f"- feature: `{PROGRAM_SLUG_R6}`",
                    f"- version: `{version}`",
                    "- branch_resolution_mode: `program-level`",
                    f"- expected_branch: `{branch}`",
                    f"- dedicated_worktree_path: `{worktree}`",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    _git(["git", "add", "docs"], cwd=root)
    _git(["git", "commit", "-m", "seed program topology"], cwd=root)
    _git(["git", "checkout", branch], cwd=worktree)
    _git(["git", "merge", "main", "-m", "sync program topology"], cwd=worktree)


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


def test_r6_program_topology_without_git_workflow_resolves_aggregation_branch(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "sidepilot-v0.0.12"
    _seed_program_topology_fixture(root, worktree=worktree, include_git_workflow=False)
    contract = load_admission_contract(root, version=VERSION_R6)

    targets = resolve_workspace_branch_targets(
        root,
        version=VERSION_R6,
        feature=PROGRAM_LAKE_R6,
        admission_contract={**contract, "version": VERSION_R6},
    )

    assert targets["branch_resolution_mode"] == "program-level"
    assert targets["feature_branch"] == "beacon/v0.0.12"
    assert targets["worktree_path"] == str(worktree.resolve())
    assert targets["program_slug"] == PROGRAM_SLUG_R6
    assert targets["source"] in {"project_governance", "program_topology"}


def test_r6_program_topology_resolves_program_slug_to_aggregation_branch(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "sidepilot-v0.0.12"
    _seed_program_topology_fixture(
        root,
        worktree=worktree,
        include_git_workflow=False,
        include_version_contract=False,
    )
    contract = load_admission_contract(root, version=VERSION_R6)

    targets = resolve_workspace_branch_targets(
        root,
        version=VERSION_R6,
        feature=PROGRAM_SLUG_R6,
        admission_contract={**contract, "version": VERSION_R6, "requested_project_root": str(worktree)},
    )

    assert targets["branch_resolution_mode"] == "program-level"
    assert targets["feature_branch"] == "beacon/v0.0.12"
    assert targets["worktree_path"] == str(worktree.resolve())
    assert targets["program_slug"] == PROGRAM_SLUG_R6
    assert targets["source"] == "program_topology"


def test_r6_program_topology_without_version_governance_block_resolves_aggregation_branch(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "sidepilot-v0.0.12"
    _seed_program_topology_fixture(
        root,
        worktree=worktree,
        include_git_workflow=False,
        include_version_contract=False,
    )
    contract = load_admission_contract(root, version=VERSION_R6)

    targets = resolve_workspace_branch_targets(
        root,
        version=VERSION_R6,
        feature=PROGRAM_LAKE_R6,
        admission_contract={**contract, "version": VERSION_R6, "requested_project_root": str(worktree)},
    )
    validation = validate_workspace_admission(worktree, version=VERSION_R6, feature=PROGRAM_LAKE_R6)

    assert contract["require_workspace_admission"] is False
    assert targets["branch_resolution_mode"] == "program-level"
    assert targets["feature_branch"] == "beacon/v0.0.12"
    assert targets["worktree_path"] == str(worktree.resolve())
    assert targets["source"] == "program_topology"
    assert validation["status"] == "pass"


def test_r6_program_topology_with_git_workflow_resolves_aggregation_branch(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "sidepilot-v0.0.12"
    _seed_program_topology_fixture(root, worktree=worktree, include_git_workflow=True)
    contract = load_admission_contract(root, version=VERSION_R6)

    targets = resolve_workspace_branch_targets(
        root,
        version=VERSION_R6,
        feature=PROGRAM_LAKE_R6,
        admission_contract={**contract, "version": VERSION_R6},
    )

    assert targets["branch_resolution_mode"] == "program-level"
    assert targets["feature_branch"] == "beacon/v0.0.12"
    assert targets["worktree_path"] == str(worktree.resolve())
    assert targets["program_slug"] == PROGRAM_SLUG_R6


def test_r6_qa_run_lake_accepts_aggregation_branch_after_admission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "sidepilot-v0.0.12"
    _seed_program_topology_fixture(root, worktree=worktree, include_git_workflow=False)
    admit = run_workspace_admit(worktree, version=VERSION_R6, feature=PROGRAM_LAKE_R6)
    assert admit["status"] == "pass"
    assert admit["branch"] == "beacon/v0.0.12"
    assert admit["worktree_path"] == str(worktree.resolve())

    monkeypatch.setattr(qa_command, "build_requirement_package_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "build_requirement_completeness_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "load_current_qa_session", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_command, "resolve_profile_for_feature", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "evaluate_project_profile_gate", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "build_feature_qa_plan", lambda *args, **kwargs: {
        "schema_version": "1.0",
        "feature": PROGRAM_LAKE_R6,
        "feature_slug": PROGRAM_LAKE_R6,
        "version": VERSION_R6,
        "status": "blocked",
        "implementation_done": False,
        "reason_codes": ["implementation_not_recorded"],
        "targeted_entries": [],
    })
    monkeypatch.setattr(qa_command, "qa_team_contract", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "detect_host_runtime", lambda value=None: value or "codex")

    previous = Path.cwd()
    os.chdir(worktree)
    try:
        exit_code, payload = qa_command._run_feature_aware_qa(
            [
                PROGRAM_LAKE_R6,
                "--project",
                str(worktree),
                "--version",
                VERSION_R6,
                "--json",
            ]
        )
    finally:
        os.chdir(previous)

    assert exit_code == 2
    assert payload["status"] == "blocked"
    assert payload["reason_codes"] == ["implementation_not_recorded"]
    assert "workspace_admission" not in payload
    assert "branch_alignment_required" not in payload.get("reason_codes", [])


def test_r6_qa_run_program_slug_aggregates_lake_statuses(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "sidepilot-v0.0.12"
    _seed_program_topology_fixture(
        root,
        worktree=worktree,
        include_git_workflow=False,
        include_version_contract=False,
    )
    for lake in (PROGRAM_LAKE_R6,):
        status_dir = worktree / ".beacon" / "qa" / "features" / lake
        status_dir.mkdir(parents=True, exist_ok=True)
        status_payload = {
            "schema_version": "1.0",
            "feature": lake,
            "version": VERSION_R6,
            "status": "passed",
            "release_ready": True,
            "run_id": f"run-{lake}",
            "reason_codes": [],
        }
        (status_dir / "status.json").write_text(json.dumps(status_payload), encoding="utf-8")
        (status_dir / "scorecard.json").write_text(
            json.dumps({"release_ready": True, "continue_decision": "ready_for_release"}),
            encoding="utf-8",
        )

    monkeypatch.setattr(qa_command, "build_requirement_package_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "build_requirement_completeness_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "load_current_qa_session", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_command, "resolve_profile_for_feature", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "evaluate_project_profile_gate", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "detect_host_runtime", lambda value=None: value or "codex")

    previous = Path.cwd()
    os.chdir(worktree)
    try:
        exit_code, payload = qa_command._run_feature_aware_qa(
            [
                PROGRAM_SLUG_R6,
                "--project",
                str(worktree),
                "--version",
                VERSION_R6,
                "--json",
            ]
        )
    finally:
        os.chdir(previous)

    assert exit_code == 0
    assert payload["status"] == "passed"
    assert payload["execution_mode"] == "program-level"
    assert payload["program_qa_aggregation"]["lake_count"] == 1
    assert payload["program_qa_aggregation"]["passed_lake_count"] == 1
    assert "implementation_not_recorded" not in payload.get("reason_codes", [])


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


def test_r6_soft_admission_still_blocks_wrong_aggregation_branch(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "sidepilot-v0.0.12"
    _seed_program_topology_fixture(root, worktree=worktree, require_admission=False)

    validation = validate_workspace_admission(
        root,
        version=VERSION_R6,
        feature=PROGRAM_LAKE_R6,
        cwd=root,
    )

    assert validation["status"] == "blocked"
    assert validation["expected_branch"] == "beacon/v0.0.12"
    assert validation["current_branch"] == "main"
    assert "branch_alignment_required" in validation.get("reason_codes", [])
