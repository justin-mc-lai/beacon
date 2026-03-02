"""Regression tests for README/SKILL documented command examples."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_readme_contains_core_command_examples():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "beacon workflow start" in text
    assert "beacon think start" in text


def test_documented_think_start_example_is_executable(tmp_path: Path):
    result = _invoke(["think", "start", "用户登录优化", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "Starting think session" in result.stdout


def test_readme_doctor_example_should_run_flat():
    result = _invoke(["doctor"])
    assert result.exit_code in (0, 2)
    assert "Missing command" not in result.stdout


def test_readme_gate_stage_example_should_run_flat():
    result = _invoke(["gate", "think"])
    assert result.exit_code in (0, 2)
    assert "No such command" not in result.stdout


def test_readme_status_verbose_example_should_work():
    result = _invoke(["status", "--verbose"])
    assert result.exit_code == 0


def test_skill_work_alias_example_should_work():
    result = _invoke(["work", "登录功能"])
    assert result.exit_code in (0, 2)
    assert "No such command" not in result.stdout


def test_pyproject_should_expose_ptk_console_script():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "\nptk = " in pyproject
