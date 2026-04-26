from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.implementation_plan import load_implementation_plan
from beacon.utils.revision_state import load_revision_state
from beacon.utils.story_state import load_story_state


runner = CliRunner()
VERSION = "v1.3.8"
FEATURE = "V138 Change Implement Closure Feature"
SLUG = "v138-change-implement-closure-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", f"beacon/{VERSION}"], cwd=root, check=True, capture_output=True, text=True)


def _version_root(root: Path) -> Path:
    return root / "docs" / "beacon" / VERSION


def _seed_docs(root: Path) -> None:
    _init_git_repo(root)
    version_root = _version_root(root)
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (version_root / "prd").mkdir(parents=True, exist_ok=True)
    (version_root / "user-story").mkdir(parents=True, exist_ok=True)
    (version_root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (version_root / "execution").mkdir(parents=True, exist_ok=True)
    (version_root / "release").mkdir(parents=True, exist_ok=True)
    (version_root / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (version_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (version_root / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (version_root / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (version_root / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    _write_r1_docs(root)


def _write_r1_docs(root: Path) -> None:
    version_root = _version_root(root)
    (version_root / "prd" / f"{SLUG}.md").write_text(
        (
            "# PRD\n\n"
            "## Functional Requirements\n\n"
            "### FR-001 Preserve frozen route\n"
            "- keep the original frozen implementation route stable\n"
        ),
        encoding="utf-8",
    )
    (version_root / "user-story" / f"{SLUG}.md").write_text(
        (
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | Route | Preserve the frozen implementation route |\n"
        ),
        encoding="utf-8",
    )
    (version_root / "qa" / "test-cases" / f"{SLUG}.md").write_text(
        (
            "# Test Cases\n\n"
            "## TC-001 Preserve frozen route\n"
            "- verify the original route remains stable\n"
        ),
        encoding="utf-8",
    )
    (version_root / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps({"entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_r2_docs(root: Path) -> None:
    version_root = _version_root(root)
    (version_root / "prd" / f"{SLUG}.md").write_text(
        (
            "# PRD\n\n"
            "## Functional Requirements\n\n"
            "### FR-001 Preserve frozen route\n"
            "- keep the original frozen implementation route stable\n\n"
            "### FR-002 Audit changed frozen requirements\n"
            "- verify the delta against the refrozen PRD, user-story, and test-case before coding\n"
        ),
        encoding="utf-8",
    )
    (version_root / "user-story" / f"{SLUG}.md").write_text(
        (
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | Route | Preserve the frozen implementation route |\n"
            "| AC-002 | Delta Audit | Audit the changed frozen requirements before coding |\n"
        ),
        encoding="utf-8",
    )
    (version_root / "qa" / "test-cases" / f"{SLUG}.md").write_text(
        (
            "# Test Cases\n\n"
            "## TC-001 Preserve frozen route\n"
            "- verify the original route remains stable\n\n"
            "## TC-002 Audit changed frozen requirements\n"
            "- verify the implementation plan binds only to the refrozen delta\n"
        ),
        encoding="utf-8",
    )
    (version_root / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"ac_id": "AC-001", "tc_id": "TC-001"},
                    {"ac_id": "AC-002", "tc_id": "TC-002"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_r2_prd_and_test_case_only(root: Path) -> None:
    version_root = _version_root(root)
    (version_root / "prd" / f"{SLUG}.md").write_text(
        (
            "# PRD\n\n"
            "## Functional Requirements\n\n"
            "### FR-001 Preserve frozen route\n"
            "- keep the original frozen implementation route stable\n\n"
            "### FR-002 Detect PRD-only and test-case-only delta\n"
            "- baseline hashing must detect non user-story requirement changes\n"
        ),
        encoding="utf-8",
    )
    (version_root / "qa" / "test-cases" / f"{SLUG}.md").write_text(
        (
            "# Test Cases\n\n"
            "## TC-001 Preserve frozen route\n"
            "- verify the original route remains stable\n\n"
            "## TC-002 Detect PRD and test-case delta\n"
            "- verify baseline hash changes even when user-story text does not\n"
        ),
        encoding="utf-8",
    )


def _sync_contract(root: Path, *, revision_id: str) -> None:
    result = _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            FEATURE,
            "--project-root",
            str(root),
            "--version",
            VERSION,
            "--revision-id",
            revision_id,
            "--review-status",
            "approved",
            "--approved-by",
            "tech-lead",
            "--reviewed-at",
            "2026-04-26T12:00:00+08:00",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout


def test_v138_change_refreeze_should_rebind_implement_to_changed_frozen_truth(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    freeze_r1 = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze_r1.exit_code == 0, freeze_r1.stdout
    _sync_contract(tmp_path, revision_id="R1")

    plan_r1 = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan_r1.exit_code == 0, plan_r1.stdout
    initial_plan = load_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)
    assert initial_plan["revision_id"] == "R1"
    assert not any("AC-002" in task.get("mapped_ac_ids", []) for task in initial_plan.get("tasks", []))

    reopened = _invoke(["reopen", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--reason", "change-request", "--json"])
    assert reopened.exit_code == 0, reopened.stdout
    assert json.loads(reopened.stdout)["new_revision_id"] == "R2"

    _write_r2_docs(tmp_path)
    freeze_r2 = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze_r2.exit_code == 0, freeze_r2.stdout
    _sync_contract(tmp_path, revision_id="R2")

    stale_run = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "single",
            "--runner",
            "native-single",
            "--dry-run",
            "--host-prompt",
            "Implement only the tasks already mapped in the refrozen implementation plan",
            "--json",
        ]
    )
    assert stale_run.exit_code == 2, stale_run.stdout
    stale_payload = json.loads(stale_run.stdout)
    assert stale_payload["reason_code"] == "implementation_plan_revision_mismatch"
    assert stale_payload["plan_preflight"]["expected_revision_id"] == "R2"

    plan_r2 = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan_r2.exit_code == 0, plan_r2.stdout
    plan = load_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)
    revision = load_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    story = load_story_state(tmp_path, version=VERSION, feature=FEATURE)
    assert plan["revision_id"] == "R2"
    assert plan["baseline_hash"] == revision["baseline_hash"]
    assert story is not None
    story_item_ids = [str(item.get("id", "") or "") for item in story.get("items", []) if isinstance(item, dict)]
    assert "AC-002" in story_item_ids
    assert "TEST-002" in story_item_ids
    changed_task = next(task for task in plan["tasks"] if task["title"] == "FR-002 Audit changed frozen requirements")
    assert "refrozen PRD, user-story, and test-case" in changed_task["description"]
    assert any("AC-002" in task.get("mapped_ac_ids", []) for task in plan["tasks"])
    assert any("TC-002" in task.get("mapped_test_ids", []) for task in plan["tasks"])

    rebound_run = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--mode",
            "single",
            "--runner",
            "native-single",
            "--dry-run",
            "--host-prompt",
            "Implement only the tasks already mapped in the refrozen implementation plan",
            "--json",
        ]
    )
    assert rebound_run.exit_code == 0, rebound_run.stdout
    rebound_payload = json.loads(rebound_run.stdout)
    assert rebound_payload["status"] == "dry_run"
    assert rebound_payload["plan_preflight"]["status"] == "pass"
    assert rebound_payload["prompt_boundary"]["classification"] == "in_scope_implementation"
    assert rebound_payload["implementation_plan"].endswith(f"implementation-plan-{SLUG}.json")


def test_v138_freeze_baseline_hash_should_include_prd_and_test_case_changes(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    freeze_r1 = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze_r1.exit_code == 0, freeze_r1.stdout
    baseline_r1 = json.loads(freeze_r1.stdout)["baseline_hash"]

    reopened = _invoke(["reopen", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--reason", "change-request", "--json"])
    assert reopened.exit_code == 0, reopened.stdout

    _write_r2_prd_and_test_case_only(tmp_path)
    freeze_r2 = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze_r2.exit_code == 0, freeze_r2.stdout
    freeze_r2_payload = json.loads(freeze_r2.stdout)

    assert freeze_r2_payload["revision_id"] == "R2"
    assert freeze_r2_payload["baseline_hash"] != baseline_r1
