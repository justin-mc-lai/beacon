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
    assert payload.get("docs_version") == "v0.0.1"
    assert payload.get("runtime_version") == __toolkit_version__
    assert payload.get("version_semantics", {}).get("resolver_contract", {}).get("version_context") == "describe_project_version_context()"
    result_payload = payload.get("result", {})

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    for content in (claude, agents):
        assert "<!-- BEACON:START -->" in content
        assert "<!-- BEACON:END -->" in content
        assert f"<!-- BEACON:VERSION:{__toolkit_version__} -->" in content
        assert f"<!-- BEACON:DOCS_VERSION:{payload.get('docs_version')} -->" in content
        assert "docs/beacon/global-boundaries.md" in content
    assert (tmp_path / "docs" / "beacon" / "global-boundaries.md").exists()
    assert (tmp_path / ".gitignore").exists()
    onboarding = json.loads((tmp_path / ".beacon" / "state" / "project-onboarding.json").read_text(encoding="utf-8"))
    assert "v1.6.12" in onboarding.get("runtime_capability_lines", [])
    actions = result_payload.get("actions", [])
    assert len(actions) == 5
    assert any(item.get("file") == ".gitignore" for item in actions)


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
    assert payload.get("docs_version") == "v0.0.1"
    assert payload.get("runtime_version") == __toolkit_version__
    assert payload.get("version_context", {}).get("version_semantics", {}).get("fields", {}).get("runtime_version", {}).get("kind") == "runtime"
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


def test_setup_context_with_explicit_docs_version_should_anchor_planning_line_without_runtime_drift(tmp_path: Path):
    (tmp_path / "docs" / "beacon" / "v1.3.4" / "execution").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.3.4" / "SUMMARY.md").write_text("# v1.3.4\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "v1.3.4" / "execution" / "index.md").write_text("# index\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "v1.3.4" / "execution" / "architecture-blueprint.md").write_text("# arch\n", encoding="utf-8")

    result = _invoke(
        ["doctor", "setup-context", "--project-root", str(tmp_path), "--version", "v1.3.4", "--json"]
    )
    assert result.exit_code == 0, result.stdout

    payload = json.loads(result.stdout)
    assert payload.get("docs_version") == "v1.3.4"
    assert payload.get("runtime_version") == __toolkit_version__

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    for content in (claude, agents):
        assert f"<!-- BEACON:VERSION:{__toolkit_version__} -->" in content
        assert "<!-- BEACON:DOCS_VERSION:v1.3.4 -->" in content
        assert f"Runtime target version: `{__toolkit_version__}`" in content
        assert "Docs target version: `v1.3.4`" in content

    onboarding = json.loads((tmp_path / ".beacon" / "state" / "project-onboarding.json").read_text(encoding="utf-8"))
    assert onboarding["docs_version"] == "v1.3.4"
    assert onboarding["runtime_version"] == __toolkit_version__


def test_setup_context_should_overwrite_stale_onboarding_docs_version_when_explicit_version_is_provided(tmp_path: Path):
    state_dir = tmp_path / ".beacon" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "project-onboarding.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "docs_version": "v1.3.1-功能开发",
                "runtime_version": "v1.1.12",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "beacon" / "v1.3.3" / "execution").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.3.3" / "SUMMARY.md").write_text("# v1.3.3\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "v1.3.3" / "execution" / "index.md").write_text("# index\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "v1.3.3" / "execution" / "architecture-blueprint.md").write_text("# arch\n", encoding="utf-8")

    result = _invoke(
        ["doctor", "setup-context", "--project-root", str(tmp_path), "--version", "v1.3.3", "--json"]
    )
    assert result.exit_code == 0, result.stdout

    onboarding = json.loads((state_dir / "project-onboarding.json").read_text(encoding="utf-8"))
    assert onboarding["docs_version"] == "v1.3.3"
    assert onboarding["runtime_version"] == __toolkit_version__
