from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str], *, env: dict[str, str] | None = None):
    return runner.invoke(app, args, env=env)


def _seed_feature_docs(root: Path, *, version: str = "v1.0.0", feature: str = "Friend Match", slug: str = "friend-match") -> None:
    base = root / "docs" / "beacon" / version
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{version}.md").write_text("# Release\n", encoding="utf-8")
    (base / "user-story" / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
    (base / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "execution" / f"implementation-plan-{slug}.json").write_text('{"tasks":[]}\n', encoding="utf-8")
    (base / ".machine" / "execution" / f"git-workflow-{slug}.json").write_text('{"mode":"single-repo"}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{slug}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{slug}.qa9-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{slug}.story-scenario-map.json").write_text('{"scenarios":[]}\n', encoding="utf-8")


def test_doctor_setup_agent_md_should_alias_setup_context(tmp_path: Path):
    result = _invoke(["doctor", "setup-agent-md", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "setup-context"
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "AGENTS.md").exists()


def test_doctor_verify_agent_md_should_alias_verify_context(tmp_path: Path):
    assert _invoke(["doctor", "setup-agent-md", "--project-root", str(tmp_path)]).exit_code == 0
    result = _invoke(["doctor", "verify-agent-md", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "verify-context"
    names = {item["name"] for item in payload["result"]["checks"]}
    assert "context_files_presence" in names


def test_doctor_verify_subagent_runtime_should_report_pass_with_ready_codex_surface(monkeypatch, tmp_path: Path):
    fake_home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(fake_home))
    skill_root = fake_home / ".agents" / "skills" / "beacon"
    skill_root.mkdir(parents=True, exist_ok=True)

    assert _invoke(["doctor", "setup-context", "--project-root", str(tmp_path)]).exit_code == 0
    result = _invoke(
        ["doctor", "verify-subagent-runtime", "--project-root", str(tmp_path), "--host-runtime", "codex", "--json"],
        env={"HOME": str(fake_home)},
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "verify-subagent-runtime"
    assert payload["status"] == "PASS"
    assert any(item["name"] == "skill_root_present" for item in payload["result"]["checks"])


def test_doctor_verify_subagent_delegation_should_block_when_feature_is_not_ready(tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.0.0", feature="Friend Match", slug="friend-match")
    (tmp_path / "docs" / "beacon" / "v1.0.0" / ".machine" / "execution" / "implementation-plan-friend-match.json").unlink()

    result = _invoke(
        [
            "doctor",
            "verify-subagent-delegation",
            "Friend Match",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.0.0",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "verify-subagent-delegation"
    assert payload["status"] == "BLOCKED"
    assert "implement plan" in payload["result"]["recommended_command"]
