from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.legacy_cutover import run_legacy_project_cutover
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.story_state import freeze_story_state
from beacon.utils.technical_review_contract import build_technical_review_gate_payload, materialize_technical_review_contract


VERSION = "v1.5.2"
FEATURE = "Legacy Cutover Demo"
SLUG = "legacy-cutover-demo"

runner = CliRunner()


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _init_git_repo(root: Path, branch: str = "main") -> None:
    subprocess.run(["git", "init", "-b", branch], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    _write(root, ".gitkeep", "test\n")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)


def _seed_v152_boundaries(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# Global Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# Summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/execution/project-skill-qa-evolution-blueprint.md", "# Skill Blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/index.md", "# Source Architecture\n")
    _write(root, f"docs/beacon/{VERSION}/release/{VERSION}.md", "# Release\n")


def _seed_governance(root: Path, branch: str = "main") -> None:
    _write(
        root,
        "docs/beacon/governance/project-version-governance.md",
        "\n".join(
            [
                "---",
                'schema_version: "1.0"',
                f'project_root: "{root}"',
                'topology_kind: "single_repo"',
                'default_execution_service: "beacon"',
                'transaction_id: "tx-test"',
                'committed_at: "2026-06-05T00:00:00+00:00"',
                'source_hash: "test-source-hash"',
                'parser_contract: "beacon-project-governance-v1"',
                "---",
                "# Project Version Governance",
                "",
                f"- project_root: `{root}`",
                "- topology_kind: `single_repo`",
                "- default_execution_service: `beacon`",
                "",
                "- topology_kind: `single_repo`",
                "- default_execution_service: `beacon`",
                "",
                "## Service Bindings",
                "",
                f"- `beacon` repo=`{root}` role=`service` writable=`true` worktree_policy=`follow-repo-root`",
                "",
                "## Version Contracts",
                "",
                f"### {VERSION}",
                "",
                "- validation_state: `active`",
                "- participating_services: `beacon`",
                "- branch_guard_mode: `strict`",
                "",
                "- per_service_canonical_branch:",
                f"  - `beacon`: `{branch}`",
                "",
            ]
        ),
    )


def _seed_legacy_triptych(root: Path) -> None:
    legacy = root / "docs" / "beacon" / "v0.0.1"
    _write(root, "docs/beacon/v0.0.1/SUMMARY.md", "# Old Summary\n")
    _write(root, f"docs/beacon/v0.0.1/prd/{SLUG}.md", "# Old PRD\n")
    _write(root, f"docs/beacon/v0.0.1/user-story/{SLUG}.md", "# Old Story\n")
    _write(root, f"docs/beacon/v0.0.1/qa/test-cases/{SLUG}.md", "# Old Tests\n")
    assert legacy.exists()


def _seed_complete_package(root: Path) -> None:
    _write(
        root,
        f"docs/beacon/{VERSION}/features/{SLUG}/truth.md",
        "\n".join(
            [
                "---",
                f"slug: {SLUG}",
                f"version: {VERSION}",
                "status: frozen",
                "language: en",
                "canonical_refs:",
                f"  prd: docs/beacon/{VERSION}/features/{SLUG}/truth.md",
                f"  user_story: docs/beacon/{VERSION}/features/{SLUG}/truth.md",
                f"  test_case: docs/beacon/{VERSION}/features/{SLUG}/tests.md",
                "parser_contract: beacon-feature-package-v1",
                "truth_source_model: feature_package_authoritative",
                "truth_map_contract: beacon-truth-map-v1",
                "---",
                "",
                "# Feature Truth",
                "",
                "## Acceptance Criteria",
                "",
                "| AC ID | Theme | Description |",
                "|---|---|---|",
                "| AC-001 | demo | Demo acceptance. |",
                "",
            ]
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/features/{SLUG}/tests.md",
        "\n".join(
            [
                "# Tests",
                "",
                "## Coverage Matrix",
                "",
                "| AC ID | TC ID | Layer | Assertion |",
                "|---|---|---|---|",
                "| AC-001 | TC-001 | unit | Demo covered. |",
                "",
            ]
        ),
    )
    _write(root, f"docs/beacon/{VERSION}/features/{SLUG}/tasks.md", "# Tasks\n\n- [ ] TASK-001 Demo\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/features/{SLUG}/evidence.md",
        "\n".join(
            [
                "# Evidence",
                "",
                "| Surface | Authority | Canonical Artifact | Status | Route |",
                "|---|---|---|---|---|",
                f"| feature-package | requirement_truth | docs/beacon/{VERSION}/features/{SLUG}/truth.md | authoritative | truth |",
                "",
            ]
        ),
    )


def _seed_project(root: Path, *, with_package: bool = False, with_governance: bool = False, branch: str = "main") -> None:
    _init_git_repo(root, branch=branch)
    _seed_v152_boundaries(root)
    _seed_legacy_triptych(root)
    if with_package:
        _seed_complete_package(root)
    if with_governance:
        _seed_governance(root, branch=branch)


def test_legacy_cutover_inventory_is_read_only_and_reports_blocked_phases(tmp_path: Path) -> None:
    _seed_project(tmp_path)

    payload = run_legacy_project_cutover(tmp_path, version=VERSION, feature=FEATURE, apply=False)

    assert payload["status"] == "blocked"
    assert payload["blocked"] is True
    assert payload["legacy_truth_present"] is True
    assert payload["phases"]["inventory"]["status"] == "blocked"
    assert payload["phases"]["package"]["status"] == "blocked"
    assert payload["phases"]["governance"]["status"] == "blocked"
    assert payload["phases"]["agent_surface"]["status"] == "blocked"
    assert "beacon materialize-feature-package" in payload["phases"]["package"]["next_command"]
    assert not (tmp_path / "docs" / "beacon" / VERSION / "features" / SLUG).exists()


def test_legacy_cutover_apply_materializes_package_and_keeps_repair_routes(tmp_path: Path) -> None:
    _seed_project(tmp_path)

    payload = run_legacy_project_cutover(tmp_path, version=VERSION, feature=FEATURE, apply=True)

    assert (tmp_path / "docs" / "beacon" / VERSION / "features" / SLUG / "truth.md").exists()
    assert payload["phases"]["package"]["materialized"]["status"] == "materialized"
    assert payload["phases"]["package"]["status"] == "blocked"
    assert payload["phases"]["governance"]["next_command"].startswith("beacon doctor metadata")


def test_legacy_cutover_passes_when_package_governance_projection_and_agent_surface_are_valid(tmp_path: Path) -> None:
    _seed_project(tmp_path, with_package=True, with_governance=True)
    setup = runner.invoke(app, ["doctor", "setup-agent-surface", "--project-root", str(tmp_path), "--version", VERSION, "--agent", "codex", "--json"])
    assert setup.exit_code == 0, setup.stdout

    payload = run_legacy_project_cutover(tmp_path, version=VERSION, feature=FEATURE, apply=True, agent="codex")

    assert payload["status"] == "pass"
    assert payload["blocked"] is False
    assert payload["phases"]["package"]["status"] == "pass"
    assert payload["phases"]["governance"]["status"] == "pass"
    assert payload["phases"]["agent_surface"]["status"] == "pass"
    assert payload["resume"]["next_command"] == f'beacon change "{FEATURE}" --project {tmp_path} --version {VERSION} --refreeze-chain'


def test_change_refreeze_intercepts_legacy_mixed_state_before_refreeze(tmp_path: Path) -> None:
    _seed_project(tmp_path, with_package=True)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    freeze_story_state(tmp_path, VERSION, FEATURE)

    result = runner.invoke(app, ["change", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--refreeze-chain", "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["blocked_reason"] == "legacy_cutover_required"
    assert payload["next_route"]["target_surface"] == "beacon-truth-cutover"
    assert "truth-cutover run" in payload["next_route"]["command"]
    assert payload["legacy_cutover"]["blocked"] is True


def test_implement_plan_intercepts_legacy_mixed_state_before_execution_plan(tmp_path: Path) -> None:
    _seed_project(tmp_path, with_package=True, with_governance=True)

    result = runner.invoke(app, ["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "legacy_cutover_required"
    assert payload["next_route"]["target_surface"] == "beacon-truth-cutover"
    assert "--resume-intent implement" in payload["recommended_command"]
    assert payload["task_alignment"]["status"] == "aligned"
    assert payload["task_alignment"]["package_tasks_path"].endswith(f"features/{SLUG}/tasks.md")
    assert payload["task_alignment"]["draft_implementation_tasks"][0]["source_task_id"] == "TASK-001"


def test_implement_run_intercepts_legacy_mixed_state_before_execution(tmp_path: Path) -> None:
    _seed_project(tmp_path, with_package=True, with_governance=True)

    result = runner.invoke(app, ["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--dry-run", "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "legacy_cutover_required"
    assert payload["next_route"]["target_surface"] == "beacon-truth-cutover"
    assert "--resume-intent implement" in payload["recommended_command"]


def test_qa_intercepts_legacy_mixed_state_before_verification(tmp_path: Path) -> None:
    _seed_project(tmp_path, with_package=True, with_governance=True)

    result = runner.invoke(app, ["qa", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_codes"] == ["legacy_cutover_required"]
    assert payload["next_route"]["target_surface"] == "beacon-truth-cutover"
    assert "--resume-intent qa" in payload["recommended_command"]


def test_truth_cutover_cli_emits_json_and_exact_next_commands(tmp_path: Path) -> None:
    _seed_project(tmp_path)

    result = runner.invoke(app, ["truth-cutover", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["feature_slug"] == SLUG
    assert payload["blocked"] is True
    assert payload["dry_run"] is True
    assert payload["phases"]["package"]["next_command"]
    assert payload["phases"]["governance"]["next_command"]


def test_truth_cutover_is_cli_route_without_public_skill_surface() -> None:
    result = runner.invoke(app, ["truth-cutover", "--help"])

    assert result.exit_code == 0
    assert "run" in result.stdout
    repo_root = Path(__file__).resolve().parents[1]
    assert not (repo_root / "skills" / "beacon" / "beacon-truth-cutover" / "SKILL.md").exists()
    assert not (repo_root / ".agents" / "skills" / "beacon-truth-cutover" / "SKILL.md").exists()


def test_change_relative_project_preserves_v152_refreeze_route(tmp_path: Path, monkeypatch) -> None:
    _seed_project(tmp_path, with_package=True, with_governance=True)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    freeze_story_state(tmp_path, VERSION, FEATURE)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["change", FEATURE, "--project", ".", "--version", VERSION, "--reason", "verify relative route", "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["version"] == VERSION
    assert f"--version {VERSION}" in payload["recommended_command"]


def test_technical_review_contract_relative_project_root_resolves_from_cwd(tmp_path: Path, monkeypatch) -> None:
    _seed_project(tmp_path, with_package=True, with_governance=True)
    materialize_technical_review_contract(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        revision_id="R1",
        contract_overrides={
            "review_status": "approved",
            "approved_by": "tech-lead",
            "reviewed_at": "2026-06-05T00:00:00+00:00",
        },
    )
    monkeypatch.chdir(tmp_path)

    payload = build_technical_review_gate_payload(Path("."), version=VERSION, feature=FEATURE)

    assert payload["status"] == "pass"
    assert payload["blocked"] is False
    assert payload["contract_json_path"].startswith(f"docs/beacon/{VERSION}/.machine/execution/")
