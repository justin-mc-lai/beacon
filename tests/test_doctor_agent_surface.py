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

    for skill_name in ("beacon-planner-brainstorm", "beacon-generator-implementation", "beacon-evaluator-qa", "beacon-governor-doctor"):
        assert (tmp_path / ".trae" / "skills" / skill_name / "SKILL.md").exists()

    rules_text = (tmp_path / ".trae" / "rules" / "project_rules.md").read_text(encoding="utf-8")
    assert "Beacon Trae Project Rules" in rules_text
    assert "beacon doctor verify-agent-surface" in rules_text

    state = json.loads((tmp_path / ".beacon" / "state" / "agent-surfaces.json").read_text(encoding="utf-8"))
    assert "trae" in state["agents"]
    assert len(state["agents"]["trae"]["installed_skills"]) == len(source_skills)


def test_setup_agent_surface_for_all_supported_hosts_should_materialize_host_visible_skills(tmp_path: Path):
    source_skills = list_host_visible_skills(packaged_beacon_skill_root())
    expected_names = {item.name for item in source_skills}
    targets = {
        "claude": (tmp_path / ".claude" / "skills", None),
        "codex": (tmp_path / ".agents" / "skills", None),
        "cursor": (tmp_path / ".cursor" / "skills", tmp_path / ".cursor" / "rules" / "beacon-agent-surface.mdc"),
        "windsurf": (tmp_path / ".windsurf" / "skills", tmp_path / ".windsurf" / "workflows" / "beacon-agent-surface.md"),
    }

    for agent, (skills_root, rules_path) in targets.items():
        result = _invoke(
            [
                "doctor",
                "setup-agent-surface",
                "--project-root",
                str(tmp_path),
                "--agent",
                agent,
                "--json",
            ]
        )
        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert payload["status"] == "PASS"
        installed_names = {item["id"] for item in payload["result"]["installed"]}
        assert expected_names <= installed_names
        assert (skills_root / "beacon-planner-brainstorm" / "SKILL.md").exists()
        assert (skills_root / "beacon-generator-implementation" / "SKILL.md").exists()
        assert (skills_root / "beacon-evaluator-qa" / "SKILL.md").exists()

        if rules_path is not None:
            rules_text = rules_path.read_text(encoding="utf-8")
            assert "Installed Beacon Skills" in rules_text
            for skill_name in ("beacon-planner-brainstorm", "beacon-generator-implementation", "beacon-evaluator-qa", "beacon-evaluator-release"):
                assert f"`{skill_name}`" in rules_text

    state = json.loads((tmp_path / ".beacon" / "state" / "agent-surfaces.json").read_text(encoding="utf-8"))
    for agent in targets:
        assert agent in state["agents"]
        assert len(state["agents"][agent]["installed_skills"]) == len(source_skills)


def test_setup_agent_surface_should_accept_winsurf_alias(tmp_path: Path):
    result = _invoke(
        [
            "doctor",
            "setup-agent-surface",
            "--project-root",
            str(tmp_path),
            "--agent",
            "winsurf",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["result"]["agent"] == "windsurf"
    assert (tmp_path / ".windsurf" / "skills" / "beacon-governor-router" / "SKILL.md").exists()


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


def test_setup_agent_surface_v160_should_materialize_harness_taxonomy(tmp_path: Path):
    result = _invoke(
        [
            "doctor",
            "setup-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "codex",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    installed_names = {item["id"] for item in payload["result"]["installed"]}

    assert "beacon-planner-brainstorm" in installed_names
    assert "beacon-generator-implementation" in installed_names
    assert "beacon-evaluator-qa" in installed_names
    assert "beacon-governor-doctor" in installed_names
    for old_name in ("beacon-brainstorm", "beacon-prd", "beacon-user-story", "beacon-test-case", "beacon-implement", "beacon-qa", "beacon-release", "using-beacon"):
        assert old_name not in installed_names
        assert not (tmp_path / ".agents" / "skills" / old_name).exists()

    skill_text = (tmp_path / ".agents" / "skills" / "beacon-planner-brainstorm" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: beacon-planner-brainstorm" in skill_text
    assert "Beacon v1.6.0 共享 Preamble" in skill_text
    assert "HARD GATE:" in skill_text
    assert "你正在运行 planner skill" in skill_text
    assert skill_text.index("Beacon v1.6.0 共享 Preamble") < skill_text.index("HARD GATE:")

    state = json.loads((tmp_path / ".beacon" / "state" / "agent-surfaces.json").read_text(encoding="utf-8"))
    assert state["agents"]["codex"]["taxonomy_version"] == "v1.6.0"
    assert state["agents"]["codex"]["source_kind"] == "migrated_v160_harness_taxonomy_preserve_skill_content"


def test_verify_agent_surface_v160_should_pass_after_setup(tmp_path: Path):
    setup = _invoke(
        [
            "doctor",
            "setup-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "codex",
        ]
    )
    assert setup.exit_code == 0, setup.stdout

    verify = _invoke(
        [
            "doctor",
            "verify-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "codex",
            "--strict",
            "--json",
        ]
    )
    assert verify.exit_code == 0, verify.stdout
    payload = json.loads(verify.stdout)
    assert payload["status"] == "PASS"
    checks = {item["name"]: item for item in payload["result"]["checks"]}
    assert checks["v160_harness_skill_names"]["status"] == "pass"
    assert checks["v160_no_old_host_visible_aliases"]["status"] == "pass"
    assert checks["v160_shared_preamble_and_hard_gates"]["status"] == "pass"


def test_verify_agent_surface_v160_should_fail_when_hard_gate_is_missing(tmp_path: Path):
    setup = _invoke(
        [
            "doctor",
            "setup-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "codex",
        ]
    )
    assert setup.exit_code == 0, setup.stdout

    skill_path = tmp_path / ".agents" / "skills" / "beacon-generator-implementation" / "SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8")
    start = skill_text.index("HARD GATE:")
    end = skill_text.index("## v1.6.0 Harness Migration")
    skill_path.write_text(skill_text[:start] + skill_text[end:], encoding="utf-8")

    verify = _invoke(
        [
            "doctor",
            "verify-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "codex",
            "--strict",
            "--json",
        ]
    )
    assert verify.exit_code == 2, verify.stdout
    payload = json.loads(verify.stdout)
    assert payload["status"] == "BLOCKED"
    checks = {item["name"]: item for item in payload["result"]["checks"]}
    assert checks["v160_shared_preamble_and_hard_gates"]["status"] == "fail"
    assert "beacon-generator-implementation" in checks["v160_shared_preamble_and_hard_gates"]["details"]["gate_errors"]


def test_verify_agent_surface_v160_should_fail_when_old_alias_exists(tmp_path: Path):
    setup = _invoke(
        [
            "doctor",
            "setup-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "codex",
        ]
    )
    assert setup.exit_code == 0, setup.stdout

    alias_dir = tmp_path / ".agents" / "skills" / "beacon-qa"
    alias_dir.mkdir(parents=True)
    (alias_dir / "SKILL.md").write_text("---\nname: beacon-qa\n---\n# Old Alias\n", encoding="utf-8")

    verify = _invoke(
        [
            "doctor",
            "verify-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "codex",
            "--strict",
            "--json",
        ]
    )
    assert verify.exit_code == 2, verify.stdout
    payload = json.loads(verify.stdout)
    checks = {item["name"]: item for item in payload["result"]["checks"]}
    assert checks["v160_no_old_host_visible_aliases"]["status"] == "fail"
    assert "beacon-qa" in checks["v160_no_old_host_visible_aliases"]["details"]["old_aliases"]
