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

    for skill_name in ("beacon-pln-brainstorm", "beacon-gen-implement", "beacon-eval-qa", "beacon-gov-doctor"):
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
        assert (skills_root / "beacon-pln-brainstorm" / "SKILL.md").exists()
        assert (skills_root / "beacon-gen-implement" / "SKILL.md").exists()
        assert (skills_root / "beacon-eval-qa" / "SKILL.md").exists()

        if rules_path is not None:
            rules_text = rules_path.read_text(encoding="utf-8")
            assert "Installed Beacon Skills" in rules_text
            for skill_name in ("beacon-pln-brainstorm", "beacon-gen-implement", "beacon-eval-qa", "beacon-eval-release"):
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
    assert (tmp_path / ".windsurf" / "skills" / "beacon-gov-router" / "SKILL.md").exists()


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

    assert "beacon-pln-brainstorm" in installed_names
    assert "beacon-gen-implement" in installed_names
    assert "beacon-eval-qa" in installed_names
    assert "beacon-gov-doctor" in installed_names
    for old_name in ("beacon-brainstorm", "beacon-prd", "beacon-user-story", "beacon-test-case", "beacon-implement", "beacon-qa", "beacon-release", "using-beacon"):
        assert old_name not in installed_names
        assert not (tmp_path / ".agents" / "skills" / old_name).exists()

    skill_text = (tmp_path / ".agents" / "skills" / "beacon-pln-brainstorm" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: beacon-pln-brainstorm" in skill_text
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
    assert checks["v160_canonical_route_references"]["status"] == "pass"


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

    skill_path = tmp_path / ".agents" / "skills" / "beacon-gen-implement" / "SKILL.md"
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
    assert "beacon-gen-implement" in checks["v160_shared_preamble_and_hard_gates"]["details"]["gate_errors"]


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


def test_verify_agent_surface_v160_should_fail_when_stale_route_reference_exists(tmp_path: Path):
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

    skill_path = tmp_path / ".agents" / "skills" / "beacon-gov-router" / "SKILL.md"
    skill_path.write_text(
        skill_path.read_text(encoding="utf-8") + "\n- route to `beacon-release` for release judgment.\n",
        encoding="utf-8",
    )

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
    assert checks["v160_canonical_route_references"]["status"] == "fail"
    errors = checks["v160_canonical_route_references"]["details"]["route_errors"]
    assert "beacon-gov-router" in errors
    assert any("`beacon-release` should be `beacon-eval-release`" in item for item in errors["beacon-gov-router"])


def test_setup_agent_surface_should_remove_beacon_skill_backup_directories(tmp_path: Path):
    skills_root = tmp_path / ".claude" / "skills"
    backup = skills_root / ".beacon-v160-legacy-backup-20260608T1410" / "beacon-qa"
    backup.mkdir(parents=True)
    (backup / "SKILL.md").write_text("---\nname: beacon-qa\n---\n# Backup\n", encoding="utf-8")

    setup = _invoke(
        [
            "doctor",
            "setup-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "claude",
            "--force",
        ]
    )
    assert setup.exit_code == 0, setup.stdout
    assert not backup.exists()

    verify = _invoke(
        [
            "doctor",
            "verify-agent-surface",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--agent",
            "claude",
            "--strict",
            "--json",
        ]
    )
    assert verify.exit_code == 0, verify.stdout
    payload = json.loads(verify.stdout)
    checks = {item["name"]: item for item in payload["result"]["checks"]}
    assert checks["v160_no_skill_backup_directories"]["status"] == "pass"


def test_cleanup_legacy_beacon_skills_should_remove_global_old_aliases(tmp_path: Path, monkeypatch):
    global_root = tmp_path / "global-claude-skills"
    alias = global_root / "beacon-qa"
    alias.mkdir(parents=True)
    (alias / "SKILL.md").write_text("---\nname: beacon-qa\n---\n# Old Alias\n", encoding="utf-8")
    monkeypatch.setattr(
        "beacon.utils.agent_surface._global_legacy_skill_roots",
        lambda home=None: {"claude": global_root},
    )

    cleanup = _invoke(
        [
            "doctor",
            "cleanup-legacy-beacon-skills",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--scope",
            "global",
            "--agent",
            "claude",
            "--json",
        ]
    )
    assert cleanup.exit_code == 0, cleanup.stdout
    payload = json.loads(cleanup.stdout)
    assert payload["result"]["removed_count"] >= 1
    assert not alias.exists()


def test_cleanup_legacy_beacon_skills_should_preserve_global_claude_flat_subskills(tmp_path: Path, monkeypatch):
    global_root = tmp_path / "global-claude-skills"
    global_root.mkdir(parents=True)
    packaged = tmp_path / "packaged-beacon"
    packaged.mkdir()
    canonical = global_root / "beacon"
    canonical.symlink_to(packaged)
    flat_subskill = global_root / "beacon-eval-qa"
    flat_subskill.symlink_to(packaged / "beacon-eval-qa")
    (packaged / "beacon-eval-qa").mkdir(parents=True)
    (packaged / "beacon-eval-qa" / "SKILL.md").write_text("---\nname: beacon-eval-qa\n---\n# QA\n", encoding="utf-8")
    monkeypatch.setattr(
        "beacon.utils.agent_surface._global_legacy_skill_roots",
        lambda home=None: {"claude": global_root},
    )

    cleanup = _invoke(
        [
            "doctor",
            "cleanup-legacy-beacon-skills",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--scope",
            "global",
            "--agent",
            "claude",
            "--force",
            "--json",
        ]
    )
    assert cleanup.exit_code == 0, cleanup.stdout
    assert flat_subskill.exists()
    assert flat_subskill.is_symlink()


def test_cleanup_legacy_beacon_skills_should_remove_global_materialized_duplicates(tmp_path: Path, monkeypatch):
    global_root = tmp_path / "global-agents-skills"
    global_root.mkdir(parents=True)
    packaged = tmp_path / "packaged-beacon"
    packaged.mkdir()
    canonical = global_root / "beacon"
    canonical.symlink_to(packaged)
    duplicate = global_root / "beacon-eval-qa"
    duplicate.mkdir()
    (duplicate / "SKILL.md").write_text("---\nname: beacon-eval-qa\n---\n# Duplicate\n", encoding="utf-8")
    monkeypatch.setattr(
        "beacon.utils.agent_surface._global_legacy_skill_roots",
        lambda home=None: {"agents": global_root},
    )

    cleanup = _invoke(
        [
            "doctor",
            "cleanup-legacy-beacon-skills",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--scope",
            "global",
            "--agent",
            "codex",
            "--force",
            "--json",
        ]
    )
    assert cleanup.exit_code == 0, cleanup.stdout
    payload = json.loads(cleanup.stdout)
    kinds = {item["kind"] for item in payload["result"]["removed"]}
    assert "global_materialized_duplicate" in kinds
    assert canonical.exists()
    assert not duplicate.exists()
