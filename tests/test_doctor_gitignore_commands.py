from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_doctor_sync_gitignore_dry_run_should_not_write_file(tmp_path: Path):
    result = _invoke(["doctor", "sync-gitignore", "--project-root", str(tmp_path), "--dry-run", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "sync-gitignore"
    assert payload["status"] == "PASS"
    assert payload["result"]["action"] == "planned"
    assert not (tmp_path / ".gitignore").exists()


def test_doctor_sync_gitignore_should_write_managed_block(tmp_path: Path):
    result = _invoke(["doctor", "sync-gitignore", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["result"]["action"] in {"created", "updated", "unchanged"}

    gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "# BEACON:GITIGNORE:START" in gitignore
    assert "# BEACON:GITIGNORE:END" in gitignore


def test_doctor_verify_gitignore_should_pass_after_sync(tmp_path: Path):
    assert _invoke(["doctor", "sync-gitignore", "--project-root", str(tmp_path)]).exit_code == 0
    result = _invoke(["doctor", "verify-gitignore", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "verify-gitignore"
    assert payload["status"] == "PASS"
    assert payload["result"]["checks"][0]["name"] == "beacon_gitignore_policy"


def test_doctor_verify_gitignore_strict_should_block_when_missing(tmp_path: Path):
    result = _invoke(["doctor", "verify-gitignore", "--project-root", str(tmp_path), "--strict", "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED"
    assert payload["result"]["checks"][0]["details"]["exists"] is False
