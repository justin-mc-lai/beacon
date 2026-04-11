from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.3.0"
FEATURE = "V130 Team Feature"
SLUG = "v130-team-feature"


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
    base = root / "docs" / "beacon" / VERSION
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text(f"# Release {VERSION}\n", encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text(
        """# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Team | Implement team surface |\n| TEST-001 | Verify | QA should stay isolated |\n""",
        encoding="utf-8",
    )
    (base / "prd" / f"{SLUG}.md").write_text(
        """# PRD\n\n## 功能需求\n\n- FR-001 Team Surface: add stable implement team routing.\n- FR-002 QA Isolation: keep qa isolated from implement context.\n""",
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")


def test_v130_implement_plan_should_emit_team_mode_contract(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    result = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    team_mode = payload.get("team_mode", {})
    assert team_mode["preferred_surface"] == "implement-team"
    assert team_mode["preferred_runner"] == "codex-subagents"
    assert "qa team-run" in team_mode["qa_team_command"]
    assert team_mode["context_isolation"]["qa_surface"] == "qa-team"


def test_v130_implement_run_auto_should_use_codex_subagents_team_surface(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    result = _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "auto", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["runner"] == "codex-subagents"
    assert payload["team_surface"] == "implement-team"
    team_execution = payload.get("team_execution", {})
    assert team_execution.get("team_surface") == "implement-team"
    assert team_execution.get("terminal_status") == "Pass"
    assert "qa-team" in team_execution.get("context_isolation", {}).get("isolated_from", [])
    assert "codex-subagents" in team_execution.get("artifact_dir", "")


def test_v130_help_should_prefer_codex_subagents_and_qa_team_run(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    help_before = _invoke(["help", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    assert help_before.exit_code == 0, help_before.stdout
    help_before_payload = json.loads(help_before.stdout)
    assert "beacon implement team-run" in help_before_payload["next_step"]["command"]

    _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "codex-subagents"])
    qa_status_dir = tmp_path / ".beacon" / "qa"
    qa_status_dir.mkdir(parents=True, exist_ok=True)
    feature_dir = qa_status_dir / "features" / SLUG
    feature_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(json.dumps({"status": "passed", "summary": {"blocked": 0}}), encoding="utf-8")
    scorecard = {
        "continue_decision": "continue",
        "coverage_current": {"executed_scenarios": 1, "required_scenarios": 2, "coverage_rate": 0.5},
        "stop_reasons": [],
    }
    feature_status = {
        "status": "blocked",
        "feature": FEATURE,
        "feature_scorecard": scorecard,
    }
    (qa_status_dir / f"{SLUG}.json").write_text(json.dumps(feature_status), encoding="utf-8")
    (feature_dir / "scorecard.json").write_text(json.dumps(scorecard), encoding="utf-8")

    help_after = _invoke(["help", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    assert help_after.exit_code == 0, help_after.stdout
    help_after_payload = json.loads(help_after.stdout)
    assert "beacon qa team-run" in help_after_payload["next_step"]["command"]


def test_v130_qa_team_run_should_materialize_isolated_team_surface(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "codex-subagents"])
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "summary": {"blocked": 0}}),
        encoding="utf-8",
    )

    result = _invoke(["qa", "team-run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["team_mode"] is True
    assert payload["execution_surface"] == "qa-team"
    team_execution = payload.get("team_execution", {})
    assert team_execution.get("team_surface") == "qa-team"
    assert "implement-team" in team_execution.get("context_isolation", {}).get("isolated_from", [])
    assert Path(tmp_path / team_execution["state_path"]).exists()


def test_v130_team_commands_should_be_explicit_and_stable(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    plan_result = _invoke(["implement", "team-plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert plan_result.exit_code == 0, plan_result.stdout
    plan_payload = json.loads(plan_result.stdout)
    assert plan_payload["team_surface"] == "implement-team"
    assert "beacon implement team-run" in plan_payload["recommended_command"]

    run_result = _invoke(["implement", "team-run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert run_result.exit_code == 0, run_result.stdout
    run_payload = json.loads(run_result.stdout)
    assert run_payload["runner"] == "codex-subagents"
    assert run_payload["team_surface"] == "implement-team"

    qa_plan = _invoke(["qa", "team-plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert qa_plan.exit_code == 0, qa_plan.stdout
    qa_plan_payload = json.loads(qa_plan.stdout)
    assert qa_plan_payload["team_surface"] == "qa-team"
    assert "beacon qa team-run" in qa_plan_payload["team_contract"]["run_command"]
