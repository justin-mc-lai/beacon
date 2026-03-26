from __future__ import annotations

from pathlib import Path
import json
import os

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.skill_config import load_yaml_like


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write_exec(path: Path, body: str = "#!/bin/sh\nexit 0\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def test_root_help_should_include_skill_and_implement():
    result = _invoke(["--help"])
    assert result.exit_code == 0
    assert "skill" in result.stdout
    assert "implement" in result.stdout


def test_skill_detect_should_find_omx_omc_and_gstack(monkeypatch, tmp_path: Path):
    bin_dir = tmp_path / "bin"
    _write_exec(bin_dir / "omx")
    _write_exec(bin_dir / "omc")
    (tmp_path / ".claude" / "skills" / "gstack").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PATH", str(bin_dir))

    result = _invoke(["skill", "detect", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    detected = {item["id"]: item["detected"] for item in payload["adapters"]}
    assert detected["omx"] is True
    assert detected["omc"] is True
    assert detected["gstack"] is True


def test_skill_register_and_prefer_should_write_project_config(tmp_path: Path):
    register = _invoke(
        [
            "skill",
            "register",
            "custom-runner",
            "--type",
            "command",
            "--command",
            "python3",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert register.exit_code == 0, register.stdout

    prefer = _invoke(
        [
            "skill",
            "prefer",
            "custom-runner",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert prefer.exit_code == 0, prefer.stdout

    config = load_yaml_like(tmp_path / "beacon.config.yaml")
    assert config["skill"]["preferred"] == "custom-runner"
    assert config["skill"]["adapters"]["custom-runner"]["adapter_type"] == "command"
    assert config["skill"]["adapters"]["custom-runner"]["command"] == "python3"


def test_skill_register_omx_should_scaffold_exec_based_args(tmp_path: Path):
    register = _invoke(
        [
            "skill",
            "register",
            "omx",
            "--type",
            "command-skill",
            "--command",
            "omx",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert register.exit_code == 0, register.stdout
    config = load_yaml_like(tmp_path / "beacon.config.yaml")
    args = config["skill"]["adapters"]["omx"]["args"]
    assert args[:5] == ["exec", "--full-auto", "--cd", "{project_root}", "--skip-git-repo-check"]
    assert config["skill"]["adapters"]["omx"]["skill_prefix"] == "$workflows-work"


def test_skill_doctor_should_fail_when_preferred_adapter_missing(tmp_path: Path):
    (tmp_path / "beacon.config.yaml").write_text(
        "skill:\n  preferred: missing-runner\n",
        encoding="utf-8",
    )
    result = _invoke(["skill", "doctor", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
