from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
FEATURE = "v120 interface contract feature"
SLUG = "v120-interface-contract-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_v120_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / "v1.2.0"
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (base / "release" / "v1.2.0.md").write_text("# Release\n", encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text(
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Discover | discovery path exists |\n",
        encoding="utf-8",
    )
    (base / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")


def test_v120_interface_help_surface_should_prioritize_mainline():
    result = _invoke(["--help"])
    assert result.exit_code == 0
    lines = [line.strip() for line in result.stdout.splitlines()]
    prd_idx = next(i for i, line in enumerate(lines) if line.startswith("│ prd"))
    prototype_idx = next(i for i, line in enumerate(lines) if line.startswith("│ prototype"))
    implement_idx = next(i for i, line in enumerate(lines) if line.startswith("│ implement"))
    qa_idx = next(i for i, line in enumerate(lines) if line.startswith("│ qa"))
    release_idx = next(i for i, line in enumerate(lines) if line.startswith("│ release"))
    assert prd_idx < prototype_idx < implement_idx < qa_idx < release_idx
    assert "think" not in result.stdout.lower()
    assert "labs" not in result.stdout.lower()


def test_v120_contract_help_json_should_surface_skill_discovery_hint(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BEACON_ALLOW_CONTEXT_VERSION_DRIFT", "1")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")
    _seed_v120_docs(tmp_path)

    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", "v1.2.0", "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    result = _invoke(["help", "--project-root", str(tmp_path), "--version", "v1.2.0", "--feature", FEATURE, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    hint = payload["skill_discovery_hint"]
    assert hint["recommended"] is True
    assert "beacon skill discover" in hint["command"]
