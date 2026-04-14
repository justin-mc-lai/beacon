from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.skill_drift import build_skill_drift_report


runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]


def _seed_repo_skill(root: Path) -> None:
    (root / "skills" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text("# root skill\n", encoding="utf-8")
    (root / "skills" / "beacon" / "SKILL.md").write_text("# packaged skill\n", encoding="utf-8")
    (root / "skills" / "beacon" / "metadata.json").write_text('{"name":"beacon"}\n', encoding="utf-8")


def _seed_claude_skill(home: Path, repo_root: Path) -> None:
    claude_root = home / ".claude" / "skills" / "beacon"
    (claude_root / "skills" / "beacon").mkdir(parents=True, exist_ok=True)
    (claude_root / "SKILL.md").write_text((repo_root / "SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
    for rel in ("SKILL.md", "metadata.json"):
        target = claude_root / "skills" / "beacon" / rel
        source = repo_root / "skills" / "beacon" / rel
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _seed_codex_skill(home: Path, repo_root: Path) -> None:
    codex_root = home / ".codex" / "skills" / "beacon"
    codex_root.mkdir(parents=True, exist_ok=True)
    for rel in ("SKILL.md", "metadata.json"):
        target = codex_root / rel
        source = repo_root / "skills" / "beacon" / rel
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _seed_agents_skill(home: Path, repo_root: Path) -> None:
    agents_root = home / ".agents" / "skills" / "beacon"
    agents_root.mkdir(parents=True, exist_ok=True)
    for rel in ("SKILL.md", "metadata.json"):
        target = agents_root / rel
        source = repo_root / "skills" / "beacon" / rel
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def test_build_skill_drift_report_should_pass_when_all_targets_match(tmp_path: Path, monkeypatch):
    repo_root = tmp_path / "repo"
    home = tmp_path / "home"
    _seed_repo_skill(repo_root)
    _seed_claude_skill(home, repo_root)
    _seed_agents_skill(home, repo_root)
    monkeypatch.setenv("HOME", str(home))

    payload = build_skill_drift_report(repo_root)
    assert payload["status"] == "pass"
    assert payload["drift_count"] == 0
    assert payload["missing_count"] == 0


def test_skill_sync_check_should_fail_when_legacy_codex_duplicate_exists(tmp_path: Path, monkeypatch):
    repo_root = tmp_path / "repo"
    home = tmp_path / "home"
    _seed_repo_skill(repo_root)
    _seed_claude_skill(home, repo_root)
    _seed_agents_skill(home, repo_root)
    _seed_codex_skill(home, repo_root)
    monkeypatch.setenv("HOME", str(home))

    result = runner.invoke(app, ["skill", "sync-check", "--project-root", str(repo_root), "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert any(item["name"] == "legacy_codex_duplicate_install" and item["status"] == "drift" for item in payload["checks"])


def test_check_skill_drift_script_should_emit_json(tmp_path: Path, monkeypatch):
    repo_root = tmp_path / "repo"
    home = tmp_path / "home"
    _seed_repo_skill(repo_root)
    _seed_claude_skill(home, repo_root)
    _seed_agents_skill(home, repo_root)
    monkeypatch.setenv("HOME", str(home))

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_skill_drift.py"), "--project-root", str(repo_root), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "HOME": str(home)},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
