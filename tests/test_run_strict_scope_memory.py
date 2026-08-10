"""Tests for strict-mode scope memory constraints."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_user_story(project_root: Path, version: str = "v1.0.0") -> None:
    # Strict mode resolves requirement truth from the feature package (package-auth).
    pkg = project_root / "docs" / "beacon" / version / "features" / "workflow"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "truth.md").write_text(
        "---\n"
        "slug: workflow\n"
        f"version: {version}\n"
        "status: draft\n"
        "language: zh\n"
        "parser_contract: beacon-feature-package-v2\n"
        "---\n\n"
        "# Workflow\n\n"
        "## 验收标准\n\n"
        "| AC ID | Theme | Description |\n"
        "|-------|-------|-------------|\n"
        "| AC-001 | 执行 | 执行引擎可运行 |\n",
        encoding="utf-8",
    )
    (pkg / "tests.md").write_text("# Tests\n", encoding="utf-8")
    (pkg / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    (pkg / "evidence.md").write_text("# Evidence\n", encoding="utf-8")


def _latest_run_state(project_root: Path) -> dict:
    runs_dir = project_root / ".beacon" / "runs"
    states = sorted(runs_dir.glob("*/state.json"))
    assert states, "expected at least one run state file"
    return json.loads(states[-1].read_text(encoding="utf-8"))


def test_run_strict_should_block_when_high_risk_scope_unconfirmed(tmp_path: Path):
    _prepare_user_story(tmp_path)

    result = _invoke(
        [
            "run",
            "workflow",
            "--mode",
            "strict",
            "--feature",
            "workflow",
            "--proposal",
            "rewrite execution engine and drop schema",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason"] == "awaiting_human_confirmation"

    state = _latest_run_state(tmp_path)
    assert state["status"] == "blocked"
    assert state["reason"] == "awaiting_human_confirmation"

    deviations = tmp_path / ".beacon" / "memory" / "scope" / "deviations.json"
    confirmations = tmp_path / ".beacon" / "memory" / "scope" / "confirmations.json"
    assert deviations.exists() and confirmations.exists()

    conf = json.loads(confirmations.read_text(encoding="utf-8"))
    assert any(item.get("status") == "pending" for item in conf.get("items", []))


def test_run_strict_should_pass_when_high_risk_scope_confirmed(tmp_path: Path):
    _prepare_user_story(tmp_path)

    result = _invoke(
        [
            "run",
            "workflow",
            "--mode",
            "strict",
            "--feature",
            "workflow",
            "--proposal",
            "rewrite execution engine",
            "--confirm",
            "A",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"

    state = _latest_run_state(tmp_path)
    assert state["status"] == "completed"

    confirmations = tmp_path / ".beacon" / "memory" / "scope" / "confirmations.json"
    conf = json.loads(confirmations.read_text(encoding="utf-8"))
    assert any(item.get("status") == "confirmed" and item.get("decision") == "A" for item in conf.get("items", []))
