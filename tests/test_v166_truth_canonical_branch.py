"""v1.6.6 canonical truth branch enforcement for loop-goal standard execution flow."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.change_refreeze import run_change_refreeze_chain
from beacon.utils.git_alignment import check_truth_authoring_branch
from beacon.utils.project_governance import commit_governance_payload
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.story_state import freeze_story_state
from beacon.utils.workspace_admission import (
    TIER_A_SKILLS,
    TRUTH_AUTHORING_SKILLS,
    inject_git_admission_into_skill_text,
)

VERSION = "v1.6.6"
FEATURE = "loop-goal-canonical-branch"
SLUG = "loop-goal-canonical-branch"

runner = CliRunner()


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
                "per_service_canonical_branch": {"beacon": f"beacon/{VERSION}/{SLUG}"},
                "truth_canonical": "main",
                "branch_guard_mode": "strict",
                "validation_state": "active",
                "previous_version_baseline_branch": "main",
                "next_version_feature_branch": f"beacon/{VERSION}/<feature-slug>",
                "worktree_mode": "dedicated",
                "worktree_path": f".beacon/worktrees/{VERSION}",
                "require_workspace_admission": True,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    docs = root / "docs" / "beacon"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "VERSION").write_text(f"{VERSION}\n", encoding="utf-8")
    (docs / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (docs / VERSION / "SUMMARY.md").parent.mkdir(parents=True, exist_ok=True)
    (docs / VERSION / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (docs / VERSION / "execution").mkdir(parents=True, exist_ok=True)
    (docs / VERSION / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")


def _seed_feature_package(root: Path) -> None:
    feature_dir = root / "docs" / "beacon" / VERSION / "features" / SLUG
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / "truth.md").write_text(
        "\n".join(
            [
                "---",
                f"slug: {SLUG}",
                f"version: {VERSION}",
                "status: frozen",
                "revision_id: R1",
                "parser_contract: beacon-feature-package-v2",
                "truth_source_model: feature_package_authoritative",
                "---",
                "",
                "# Truth",
                "",
                "## Acceptance Criteria",
                "",
                "| AC ID | Description |",
                "| --- | --- |",
                "| AC-001 | Canonical branch guard blocks feature-branch refreeze. |",
            ]
        ),
        encoding="utf-8",
    )
    (feature_dir / "tests.md").write_text(
        "# Tests\n\n| AC ID | TC ID | Layer | Command | Assertion |\n| --- | --- | --- | --- | --- |\n"
        "| AC-001 | TC-001 | contract | pytest | blocked on feature branch |\n",
        encoding="utf-8",
    )
    (feature_dir / "tasks.md").write_text("# Tasks\n\n- TASK-001 guard\n", encoding="utf-8")
    (feature_dir / "evidence.md").write_text("# Evidence\n\n- none\n", encoding="utf-8")
    freeze_revision_state(root, version=VERSION, feature=FEATURE)
    freeze_story_state(root, VERSION, FEATURE)


def test_truth_authoring_branch_passes_on_main(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    result = check_truth_authoring_branch(tmp_path, version=VERSION)
    assert result["status"] == "pass"
    assert result["truth_canonical"] == "main"
    assert result["on_truth_canonical"] is True


def test_truth_authoring_branch_blocks_feature_branch(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    feature_branch = f"beacon/{VERSION}/{SLUG}"
    _git(["git", "checkout", "-b", feature_branch], cwd=tmp_path)
    result = check_truth_authoring_branch(tmp_path, version=VERSION, operation="change_refreeze")
    assert result["status"] == "blocked"
    assert result["reason_code"] == "truth_canonical_branch_mismatch"
    assert result["current_branch"] == feature_branch


def test_change_refreeze_chain_blocks_on_feature_branch(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    _seed_feature_package(tmp_path)
    feature_branch = f"beacon/{VERSION}/{SLUG}"
    _git(["git", "checkout", "-b", feature_branch], cwd=tmp_path)
    payload = run_change_refreeze_chain(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        reason="canonical-branch-guard",
    )
    assert payload["refreeze_status"] == "blocked"
    assert payload["blocked_reason"] == "truth_canonical_branch_mismatch"
    assert payload["truth_authoring_branch"]["on_truth_canonical"] is False


def test_freeze_command_blocks_on_feature_branch(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    _seed_feature_package(tmp_path)
    feature_branch = f"beacon/{VERSION}/{SLUG}"
    _git(["git", "checkout", "-b", feature_branch], cwd=tmp_path)
    result = runner.invoke(
        app,
        ["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "truth_canonical_branch_mismatch"


def test_truth_authoring_skills_get_canonical_branch_preamble() -> None:
    text = "# Skill\n\n## Beacon v1.6.0 共享 Preamble\n\n1. item\n"
    for skill_id in TRUTH_AUTHORING_SKILLS:
        injected = inject_git_admission_into_skill_text(skill_id, text)
        assert "truth_canonical" in injected
        assert "truth_canonical_branch_mismatch" in injected
        assert "workspace admit" not in injected


def test_delivery_skills_keep_worktree_admission_preamble() -> None:
    text = "# Skill\n\n## Beacon v1.6.0 共享 Preamble\n\n1. item\n"
    for skill_id in TIER_A_SKILLS:
        injected = inject_git_admission_into_skill_text(skill_id, text)
        assert "workspace admit" in injected
        assert "truth_canonical_branch_mismatch" not in injected


def test_loop_goal_skill_declares_truth_canonical_gate() -> None:
    skill_path = Path(__file__).parent.parent / "skills" / "beacon" / "beacon-goal" / "references" / "modes" / "loop-goal.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "truth_canonical_branch_mismatch" in content
    assert "governance `truth_canonical`" in content


def test_truth_file_write_allowed_on_main(tmp_path: Path) -> None:
    from beacon.utils.workspace_admission import hook_should_deny_write

    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    target = tmp_path / "docs" / "beacon" / VERSION / "features" / SLUG / "truth.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# truth\n", encoding="utf-8")
    deny, reason = hook_should_deny_write(tmp_path, target_path=target, cwd=tmp_path)
    assert deny is False
    assert reason == ""


def test_truth_file_write_blocked_on_feature_branch(tmp_path: Path) -> None:
    from beacon.utils.workspace_admission import hook_should_deny_write

    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    feature_branch = f"beacon/{VERSION}/{SLUG}"
    _git(["git", "checkout", "-b", feature_branch], cwd=tmp_path)
    target = tmp_path / "docs" / "beacon" / VERSION / "features" / SLUG / "truth.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# truth\n", encoding="utf-8")
    deny, reason = hook_should_deny_write(tmp_path, target_path=target, cwd=tmp_path)
    assert deny is True
    assert reason == "truth_canonical_branch_mismatch"
