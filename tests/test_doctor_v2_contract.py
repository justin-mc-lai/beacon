"""Doctor v2 diagnostics and setup/uninstall contract tests."""

from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from beacon import __toolkit_version__, __version__
from beacon.main import app
from beacon.utils.doctor_setup import resolve_bin_dir


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_basic_project(tmp_path: Path) -> None:
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "skills").mkdir(parents=True, exist_ok=True)


def test_doctor_json_should_report_runtime_real_versions(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    runtime = payload.get("runtime", {})
    assert runtime.get("package_version")
    assert runtime.get("toolkit_version")
    assert str(runtime.get("package_version")).lstrip("v") == str(__version__).lstrip("v")
    assert str(runtime.get("toolkit_version")).lstrip("v") == str(__toolkit_version__).lstrip("v")
    # Guard against historical hard-coded value drift.
    assert payload.get("beacon_version") == runtime.get("toolkit_version")


def test_doctor_should_detect_latest_iteration_version_from_docs(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    (tmp_path / "docs" / "beacon" / "v1.0.0").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.2.0").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.2.0" / "SUMMARY.md").write_text("# latest\n", encoding="utf-8")

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    project = payload.get("project", {})

    assert project.get("latest_iteration_version") == "v1.2.0"
    assert "v1.2.0" in project.get("available_versions", [])


def test_doctor_should_detect_material_incompatibilities(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    version = "v1.0.0"

    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    tc_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    tc_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / "feature.md").write_text("Use /beacon:workflow for legacy trigger\n", encoding="utf-8")
    (prd_dir / "feature.md").write_text("# prd\n", encoding="utf-8")
    (tc_dir / "feature.md").write_text("# tc\n", encoding="utf-8")

    # stale .ptk version history reference
    ptk_state = tmp_path / ".ptk" / "state"
    ptk_state.mkdir(parents=True, exist_ok=True)
    (ptk_state / "version-history.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "versions": [
                    {
                        "version": "v3.8.4",
                        "coverage_file": "docs/product/v3.8.4/execution/command-coverage.json",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    incompatibilities = payload.get("incompatibilities", [])
    codes = {item.get("code") for item in incompatibilities}

    assert "COMP-201" in codes  # docs progressed but no workflow run lifecycle
    assert "COMP-203" in codes  # stale ptk refs
    assert "COMP-205" in codes  # legacy trigger syntax


def test_doctor_should_not_treat_project_iteration_version_as_runtime_incompatibility(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    (tmp_path / "docs" / "beacon" / "v9.9.9").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v9.9.9" / "SUMMARY.md").write_text("# future\n", encoding="utf-8")

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    incompatibilities = payload.get("incompatibilities", [])
    names = {item.get("name") for item in incompatibilities}
    assert payload.get("project", {}).get("latest_iteration_version") == "v9.9.9"
    assert "material_skill_semver_compatibility" not in names


def test_doctor_should_accept_formal_delivery_package_without_workflow_lifecycle_run(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    version = "v1.3.0"
    base = tmp_path / "docs" / "beacon" / version

    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "execution").mkdir(parents=True, exist_ok=True)

    (base / "user-story" / "feature.md").write_text("# us\n", encoding="utf-8")
    (base / "prd" / "feature.md").write_text("# prd\n", encoding="utf-8")
    (base / "qa" / "test-cases" / "feature.md").write_text("# tc\n", encoding="utf-8")
    (base / ".machine" / "execution" / "source.json").write_text(
        json.dumps({"run_id": "run-v1.3.0-doc-upgrade", "status": "completed"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (base / ".machine" / "execution" / "delivery-manifest.json").write_text(
        json.dumps({"run_id": "run-v1.3.0-doc-upgrade", "delivery_status": "completed"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (base / ".machine" / "execution" / "terminal.json").write_text(
        json.dumps({"run_id": "run-v1.3.0-doc-upgrade", "status": "Pass"}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    incompatibilities = payload.get("incompatibilities", [])
    codes = {item.get("code") for item in incompatibilities}

    assert "COMP-201" not in codes
    assert "COMP-202" not in codes


def test_doctor_should_detect_installed_skill_copy_version_drift(monkeypatch, tmp_path: Path):
    _prepare_basic_project(tmp_path)

    fake_home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(fake_home))
    skill_layout = {
        fake_home / ".agents" / "skills" / "beacon" / "SKILL.md": "Skill Version: v1.0.3\n",
        fake_home / ".codex" / "skills" / "beacon" / "SKILL.md": "Skill Version: v1.0.2\n",
        fake_home / ".claude" / "skills" / "beacon" / "SKILL.md": "Skill Version: v1.0.1\n",
    }
    for path, content in skill_layout.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    incompatibilities = payload.get("incompatibilities", [])
    codes = {item.get("code") for item in incompatibilities}
    assert "COMP-206" in codes


def test_doctor_should_allow_multiple_suffixed_iteration_roots_without_canonical_collision(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    (tmp_path / "docs" / "beacon" / "v1.2.1-feature-a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.2.1-feature-b").mkdir(parents=True, exist_ok=True)

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    incompatibilities = payload.get("incompatibilities", [])
    codes = {item.get("code") for item in incompatibilities}
    assert "COMP-210" not in codes


def test_doctor_should_flag_version_root_semantics_drift_when_canonical_and_suffixed_roots_mix(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    (tmp_path / "docs" / "beacon" / "v1.2.1").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / "v1.2.1-feature-a").mkdir(parents=True, exist_ok=True)

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    incompatibilities = payload.get("incompatibilities", [])
    codes = {item.get("code") for item in incompatibilities}
    assert "COMP-210" in codes


def test_doctor_setup_should_install_beacon_launchers(tmp_path: Path):
    bin_dir = tmp_path / "bin"

    setup = _invoke(
        [
            "doctor",
            "setup",
            "--bin-dir",
            str(bin_dir),
            "--json",
        ]
    )
    assert setup.exit_code == 0
    setup_payload = json.loads(setup.stdout)
    installed = setup_payload.get("result", {}).get("installed", [])
    assert any(path.endswith("/beacon") for path in installed)
    assert any(path.endswith("/beacon-cli") for path in installed)
    assert (bin_dir / "beacon").exists()
    assert (bin_dir / "beacon-cli").exists()


def test_doctor_uninstall_should_remove_installed_launchers(tmp_path: Path):
    bin_dir = tmp_path / "bin"

    setup = _invoke(["doctor", "setup", "--bin-dir", str(bin_dir), "--json"])
    assert setup.exit_code == 0
    assert (bin_dir / "beacon").exists()
    assert (bin_dir / "beacon-cli").exists()

    uninstall = _invoke(
        [
            "doctor",
            "uninstall",
            "--bin-dir",
            str(bin_dir),
            "--json",
        ]
    )
    assert uninstall.exit_code == 0
    uninstall_payload = json.loads(uninstall.stdout)
    removed = uninstall_payload.get("result", {}).get("removed", [])
    assert any(path.endswith("/beacon") for path in removed)
    assert any(path.endswith("/beacon-cli") for path in removed)
    assert not (bin_dir / "beacon").exists()
    assert not (bin_dir / "beacon-cli").exists()


def test_resolve_bin_dir_should_skip_transient_path_entries(monkeypatch, tmp_path: Path):
    home = tmp_path / "home"
    preferred = home / ".local" / "bin"
    transient = tmp_path / ".codex" / "tmp" / "session-bin"
    preferred.mkdir(parents=True, exist_ok=True)
    transient.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))

    monkeypatch.setenv("PATH", f"{transient}{os.pathsep}{preferred}")
    resolved = resolve_bin_dir()
    assert resolved.resolve() == preferred.resolve()


def test_doctor_advise_should_report_next_step_and_scores(tmp_path: Path):
    _prepare_basic_project(tmp_path)
    result = _invoke(["doctor", "advise", "--json", "--project-root", str(tmp_path), "--feature", "My Feature"])
    assert result.exit_code in {0, 2}
    payload = json.loads(result.stdout)
    assert payload.get("action") == "advise"
    assert isinstance(payload.get("scores"), dict)
    assert "test_score" in payload.get("scores", {})
    assert isinstance(payload.get("next_step"), dict)
    assert payload.get("next_step", {}).get("command")


def test_doctor_advise_should_prefer_context_repair_when_context_missing(tmp_path: Path):
    # project root exists but managed context files do not
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    result = _invoke(["doctor", "advise", "--json", "--project-root", str(tmp_path), "--feature", "My Feature"])
    assert result.exit_code in {0, 2}
    payload = json.loads(result.stdout)
    next_step = payload.get("next_step", {})
    assert isinstance(next_step, dict)
    assert "doctor" in str(next_step.get("command", ""))
