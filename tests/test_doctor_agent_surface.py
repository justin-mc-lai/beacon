from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.agent_surface import list_host_visible_skills, packaged_beacon_skill_root


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_setup_agent_surface_for_trae_should_materialize_host_visible_skills(tmp_path: Path):
    result = _invoke(
        [
            "doctor",
            "setup-agent-surface",
            "--project-root",
            str(tmp_path),
            "--agent",
            "trae",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "setup-agent-surface"
    assert payload["status"] == "PASS"

    source_skills = list_host_visible_skills(packaged_beacon_skill_root())
    installed = payload["result"]["installed"]
    assert len(installed) == len(source_skills)

    for skill_name in ("using-beacon", "beacon-prd", "beacon-qa", "beacon-release", "beacon-doctor"):
        assert (tmp_path / ".trae" / "skills" / skill_name / "SKILL.md").exists()

    rules_text = (tmp_path / ".trae" / "rules" / "project_rules.md").read_text(encoding="utf-8")
    assert "Beacon Trae Project Rules" in rules_text
    assert "beacon doctor verify-agent-surface" in rules_text

    state = json.loads((tmp_path / ".beacon" / "state" / "agent-surfaces.json").read_text(encoding="utf-8"))
    assert "trae" in state["agents"]
    assert len(state["agents"]["trae"]["installed_skills"]) == len(source_skills)


def test_verify_agent_surface_should_pass_after_setup(tmp_path: Path):
    setup = _invoke(
        [
            "doctor",
            "setup-agent-surface",
            "--project-root",
            str(tmp_path),
            "--agent",
            "trae",
        ]
    )
    assert setup.exit_code == 0, setup.stdout

    verify = _invoke(
        [
            "doctor",
            "verify-agent-surface",
            "--project-root",
            str(tmp_path),
            "--agent",
            "trae",
            "--strict",
            "--json",
        ]
    )
    assert verify.exit_code == 0, verify.stdout
    payload = json.loads(verify.stdout)
    assert payload["action"] == "verify-agent-surface"
    assert payload["status"] == "PASS"
    assert all(item["status"] == "pass" for item in payload["result"]["checks"])
