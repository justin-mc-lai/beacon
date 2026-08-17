from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _init_runtime_repo(root: Path) -> None:
    _git(root, "init")
    _git(root, "config", "user.email", "beacon-tests@example.com")
    _git(root, "config", "user.name", "Beacon Tests")

    tracked_files = {
        ".beacon/auto-test-status.json": '{"status":"passed"}\n',
        ".beacon/memory/decisions.json": "[]\n",
        "docs/beacon/v1.1.11/.machine/execution/config.json": "{}\n",
        "docs/beacon/v1.1.11/.machine/execution/source.json": "{}\n",
    }
    for rel, content in tracked_files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    _git(root, "add", *tracked_files.keys())
    _git(root, "commit", "-m", "seed quiet worktree fixtures")


def test_doctor_quiet_worktree_apply_should_quiet_runtime_noise(tmp_path: Path):
    _init_runtime_repo(tmp_path)

    result = _invoke(["doctor", "quiet-worktree", "apply", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload.get("action") == "quiet-worktree"
    assert payload.get("mode") == "apply"
    quiet = payload.get("result", {})
    assert quiet.get("exclude_block_present") is True
    assert quiet.get("skip_worktree_count") >= 4

    (tmp_path / ".beacon" / "auto-test-status.json").write_text('{"status":"blocked"}\n', encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "v1.1.11" / ".machine" / "execution" / "config.json").write_text(
        '{"updated":true}\n',
        encoding="utf-8",
    )
    runtime_noise = tmp_path / ".beacon" / "state" / "evo" / "decision-engine.json"
    runtime_noise.parent.mkdir(parents=True, exist_ok=True)
    runtime_noise.write_text('{"decision":"keep"}\n', encoding="utf-8")

    status_result = _git(tmp_path, "status", "--short")
    assert status_result.stdout.strip() == ""

    ls_files = _git(
        tmp_path,
        "ls-files",
        "-v",
        "--",
        ".beacon/auto-test-status.json",
        "docs/beacon/v1.1.11/.machine/execution/config.json",
    )
    assert all(line.startswith("S ") for line in ls_files.stdout.splitlines() if line.strip())


def test_doctor_quiet_worktree_restore_should_reveal_runtime_noise_and_remove_block(tmp_path: Path):
    _init_runtime_repo(tmp_path)
    apply_result = _invoke(["doctor", "quiet-worktree", "apply", "--project-root", str(tmp_path), "--json"])
    assert apply_result.exit_code == 0, apply_result.stdout

    (tmp_path / ".beacon" / "auto-test-status.json").write_text('{"status":"blocked"}\n', encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "v1.1.11" / ".machine" / "execution" / "source.json").write_text(
        '{"updated":true}\n',
        encoding="utf-8",
    )
    runtime_noise = tmp_path / ".beacon" / "state" / "implementation-feature.json"
    runtime_noise.parent.mkdir(parents=True, exist_ok=True)
    runtime_noise.write_text('{"feature":"demo"}\n', encoding="utf-8")

    status_result = _invoke(["doctor", "quiet-worktree", "status", "--project-root", str(tmp_path), "--json"])
    assert status_result.exit_code == 0, status_result.stdout
    status_payload = json.loads(status_result.stdout)
    assert status_payload.get("result", {}).get("skip_worktree_count") >= 4

    restore_result = _invoke(["doctor", "quiet-worktree", "restore", "--project-root", str(tmp_path), "--json"])
    assert restore_result.exit_code == 0, restore_result.stdout
    restore_payload = json.loads(restore_result.stdout)
    restored = restore_payload.get("result", {})
    assert restored.get("exclude_block_present") is False
    assert restored.get("skip_worktree_count") == 0

    exclude_text = (tmp_path / ".git" / "info" / "exclude").read_text(encoding="utf-8")
    assert "BEACON-QUIET-WORKTREE" not in exclude_text

    git_status = _git(tmp_path, "status", "--short", "--untracked-files=all").stdout
    assert " M .beacon/auto-test-status.json" in git_status
    assert " M docs/beacon/v1.1.11/.machine/execution/source.json" in git_status
    assert "?? .beacon/state/implementation-feature.json" in git_status
