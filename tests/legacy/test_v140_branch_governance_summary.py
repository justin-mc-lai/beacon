from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _git(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _seed_repo(root: Path, branch: str) -> None:
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_metadata(root: Path) -> None:
    result = runner.invoke(
        app,
        [
            "doctor",
            "metadata",
            "create",
            "--project-root",
            str(root),
            "--topology-kind",
            "single_repo",
            "--default-execution-service",
            "beacon",
            "--service-key",
            "beacon",
            "--repo-root",
            str(root),
            "--version",
            "v1.4.0",
            "--branch",
            "feature/demo",
            "--branch-governance-template",
            "standard-feature",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout


def _show_payload(root: Path) -> dict:
    result = runner.invoke(
        app,
        ["doctor", "branch-governance", "show", "--project-root", str(root), "--version", "v1.4.0", "--json"],
    )
    assert result.exit_code == 0, result.stdout
    return json.loads(result.stdout)["result"]


def test_service_and_repo_visible(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/demo")
    _seed_metadata(tmp_path)
    payload = _show_payload(tmp_path)
    assert payload["service_key"] == "beacon"
    assert payload["repo_root"] == str(tmp_path.resolve())


def test_branch_state_visible(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/demo")
    _seed_metadata(tmp_path)
    payload = _show_payload(tmp_path)
    assert payload["base_branch"] == "feature/demo"
    assert payload["current_branch"] == "feature/demo"
    assert payload["target_branch"] == "feature/demo"


def test_worktree_state_visible(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/demo")
    _seed_metadata(tmp_path)
    payload = _show_payload(tmp_path)
    assert payload["worktree_mode"] == "branch-only"
    assert payload["worktree_path"] == str(tmp_path.resolve())


def test_verdict_and_recommendation_visible(tmp_path: Path) -> None:
    _seed_repo(tmp_path, "feature/demo")
    _seed_metadata(tmp_path)
    payload = _show_payload(tmp_path)
    assert payload["status"] == "pass"
    assert "blocked_reason" in payload
    assert "recommended_action" in payload
