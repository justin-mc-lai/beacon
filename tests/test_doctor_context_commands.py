"""Contract tests for doctor context lifecycle commands."""

from __future__ import annotations

import json
from pathlib import Path

from beacon import __toolkit_version__
from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_setup_context_creates_context_files_with_beacon_markers(tmp_path: Path):
    result = _invoke(["doctor", "setup-context", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0

    payload = json.loads(result.stdout)
    assert payload.get("action") == "setup-context"
    assert payload.get("status") == "PASS"
    assert payload.get("docs_version") == "v1.0.0"
    assert payload.get("runtime_version") == __toolkit_version__
    result_payload = payload.get("result", {})

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    for content in (claude, agents):
        assert "<!-- BEACON:START -->" in content
        assert "<!-- BEACON:END -->" in content
    assert len(result_payload.get("actions", [])) == 2


def test_setup_context_dry_run_reports_planned_and_keeps_filesystem_unchanged(tmp_path: Path):
    result = _invoke(["doctor", "setup-context", "--project-root", str(tmp_path), "--dry-run", "--json"])
    assert result.exit_code == 0

    payload = json.loads(result.stdout)
    actions = payload.get("result", {}).get("actions", [])
    assert any(item.get("action") == "planned" for item in actions)
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / "AGENTS.md").exists()


def test_verify_context_reports_pass_after_setup_context(tmp_path: Path):
    setup = _invoke(["doctor", "setup-context", "--project-root", str(tmp_path)])
    assert setup.exit_code == 0

    verify = _invoke(["doctor", "verify-context", "--project-root", str(tmp_path), "--json"])
    assert verify.exit_code == 0
    payload = json.loads(verify.stdout)
    assert payload.get("status") == "PASS"
    assert payload.get("docs_version") == "v1.0.0"
    assert payload.get("runtime_version") == __toolkit_version__
    checks = payload.get("result", {}).get("checks", [])
    assert all(item.get("status") == "pass" for item in checks)


def test_verify_context_strict_blocks_on_corrupted_markers(tmp_path: Path):
    setup = _invoke(["doctor", "setup-context", "--project-root", str(tmp_path)])
    assert setup.exit_code == 0

    claude_path = tmp_path / "CLAUDE.md"
    claude = claude_path.read_text(encoding="utf-8")
    claude_path.write_text(claude.replace("<!-- BEACON:END -->", ""), encoding="utf-8")

    verify = _invoke(["doctor", "verify-context", "--project-root", str(tmp_path), "--strict", "--json"])
    assert verify.exit_code == 2
    payload = json.loads(verify.stdout)
    assert payload.get("status") == "BLOCKED"
    checks = payload.get("result", {}).get("checks", [])
    assert any(item.get("status") == "fail" for item in checks)


def test_verify_context_json_includes_required_check_names(tmp_path: Path):
    setup = _invoke(["doctor", "setup-context", "--project-root", str(tmp_path)])
    assert setup.exit_code == 0

    verify = _invoke(["doctor", "verify-context", "--project-root", str(tmp_path), "--json"])
    assert verify.exit_code == 0
    payload = json.loads(verify.stdout)
    names = {item.get("name") for item in payload.get("result", {}).get("checks", [])}
    assert {
        "context_files_presence",
        "managed_block_integrity",
        "managed_block_version_drift",
    }.issubset(names)
