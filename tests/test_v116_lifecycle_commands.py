from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.1.6"
FEATURE = "Lifecycle Feature"
SLUG = "lifecycle-feature"


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


def _seed_docs(root: Path) -> None:
    if not (root / ".git").exists():
        _init_git_repo(root)
    (root / "docs" / "beacon" / VERSION / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / VERSION / "prd").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / VERSION / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / VERSION / "user-story" / f"{SLUG}.md").write_text(
        """# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Lifecycle | Freeze before implement |\n| AC-002 | Navigation | Help suggests next step |\n""",
        encoding="utf-8",
    )
    (root / "docs" / "beacon" / VERSION / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (root / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")


def test_freeze_reopen_and_native_implement_should_write_machine_state(tmp_path: Path):
    _seed_docs(tmp_path)

    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    freeze_payload = json.loads(freeze.stdout)
    assert freeze_payload["status"] == "frozen"
    assert freeze_payload["requirement_package"]["status"] == "synced"
    assert (tmp_path / freeze_payload["requirement_package"]["qa_matrix_path"]).exists()
    assert (tmp_path / freeze_payload["requirement_package"]["story_scenario_map_path"]).exists()

    impl = _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "native-single", "--json"])
    assert impl.exit_code == 0, impl.stdout
    impl_payload = json.loads(impl.stdout)
    assert impl_payload["status"] == "completed"
    assert impl_payload["runner"] == "native-single"

    machine_story = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json"
    assert machine_story.exists()
    story_payload = json.loads(machine_story.read_text(encoding="utf-8"))
    assert story_payload["current_revision_id"] == "R1"

    reopen = _invoke(["reopen", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--reason", "change-request", "--json"])
    assert reopen.exit_code == 0, reopen.stdout
    reopen_payload = json.loads(reopen.stdout)
    assert reopen_payload["new_revision_id"] == "R2"
    assert reopen_payload["requirement_package"]["status"] == "synced"
    assert (tmp_path / reopen_payload["requirement_package"]["qa_matrix_path"]).exists()
    assert (tmp_path / reopen_payload["requirement_package"]["story_scenario_map_path"]).exists()
    story_payload = json.loads(machine_story.read_text(encoding="utf-8"))
    assert story_payload["current_revision_id"] == "R2"


def test_review_accept_should_require_frozen_revision_and_auto_test_pass(tmp_path: Path):
    _seed_docs(tmp_path)

    blocked = _invoke(["review", "accept", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert blocked.exit_code == 2
    blocked_payload = json.loads(blocked.stdout)
    assert blocked_payload["status"] == "blocked"

    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "native-single"])
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(json.dumps({"status": "passed", "summary": {"blocked": 0}}), encoding="utf-8")

    accepted = _invoke(["review", "accept", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert accepted.exit_code == 0, accepted.stdout
    payload = json.loads(accepted.stdout)
    assert payload["status"] == "accepted"


def test_native_team_should_materialize_multi_role_team_flow(tmp_path: Path):
    _seed_docs(tmp_path)

    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    result = _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "native-team", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    team_execution = payload.get("team_execution", {})
    assert team_execution.get("terminal_status") == "Pass"
    assert set(team_execution.get("roles", [])) == {"planner", "implementer", "reviewer", "tester"}
    state_path = tmp_path / team_execution["state_path"]
    assert state_path.exists()
    artifact_dir = tmp_path / team_execution["artifact_dir"]
    assert artifact_dir.exists()
    role_reports = team_execution.get("role_reports", {})
    assert set(role_reports) == {"planner", "implementer", "reviewer", "tester"}
    for report in role_reports.values():
        assert (tmp_path / report["json"]).exists()
        assert (tmp_path / report["markdown"]).exists()


def test_native_team_should_write_verification_when_auto_test_passes(tmp_path: Path):
    _seed_docs(tmp_path)
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "summary": {"blocked": 0}}),
        encoding="utf-8",
    )

    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    result = _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "native-team", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["verified_items"]
    verification = payload.get("verification", [])
    assert any(item.get("command") == "auto-test-status" and item.get("status") == "passed" for item in verification)

    machine_story = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json"
    story_payload = json.loads(machine_story.read_text(encoding="utf-8"))
    active_story = next(story for story in story_payload["stories"] if story["revision_id"] == story_payload["current_revision_id"])
    statuses = {item["id"]: item["status"] for item in active_story["items"]}
    assert statuses["AC-001"] == "verified"
    assert statuses["TEST-001"] == "passed"
