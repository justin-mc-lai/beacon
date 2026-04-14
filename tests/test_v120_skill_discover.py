from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from beacon.commands.test_case import _infer_layer_from_ac
from beacon.main import app
from beacon.utils.qa_feature import _load_source_matrix
from beacon.utils.skill_config import load_yaml_like


runner = CliRunner()
FEATURE = "v120 skill feature"
SLUG = "v120-skill-feature"


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


@pytest.mark.smoke
def test_skill_discover_preview_should_write_state_but_not_config(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")

    result = _invoke(["skill", "discover", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "preview"
    assert payload["recommended_templates"]
    assert (tmp_path / payload["state_path"]).exists()
    assert not (tmp_path / "beacon.config.yaml").exists()


def test_skill_discover_apply_should_merge_profile_into_config(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")

    result = _invoke(
        [
            "skill",
            "discover",
            "--project-root",
            str(tmp_path),
            "--apply-recommended",
            "--no-dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "applied"
    config = load_yaml_like(tmp_path / "beacon.config.yaml")
    assert config["project_skills"]["discovery"]["preferred_templates"]
    assert "python-cli-default" in config["project_skills"]["profiles"]

    show = _invoke(["profile", "show", "python-cli-default", "--project-root", str(tmp_path), "--json"])
    assert show.exit_code == 0, show.stdout
    profile_payload = json.loads(show.stdout)
    assert profile_payload["profile"]["project"] == tmp_path.name


def test_profile_discovery_should_show_latest_discovery_payload(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")
    _invoke(["skill", "discover", "--project-root", str(tmp_path)])

    result = _invoke(["profile", "discovery", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["selected_template"] == "python-cli"


def test_skill_doctor_should_include_discovery_validation(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")
    _invoke(["skill", "discover", "--project-root", str(tmp_path), "--apply-recommended", "--no-dry-run"])

    result = _invoke(["skill", "doctor", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    discovery_check = next(item for item in payload["checks"] if item["adapter_id"] == "skill-discovery")
    assert discovery_check["status"] == "pass"


def test_help_should_recommend_skill_discover_before_implementation_when_profile_missing(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BEACON_ALLOW_CONTEXT_VERSION_DRIFT", "1")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")
    _seed_v120_docs(tmp_path)
    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", "v1.2.0", "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    result = _invoke(["help", "--project-root", str(tmp_path), "--version", "v1.2.0", "--feature", FEATURE, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["next_step"]["action"] == "skill-discover"
    assert "beacon skill discover" in payload["next_step"]["command"]
    assert f"--project-root {tmp_path}" in payload["next_step"]["command"]


def test_help_human_output_should_render_skill_discovery_hint(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BEACON_ALLOW_CONTEXT_VERSION_DRIFT", "1")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")
    _seed_v120_docs(tmp_path)
    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", "v1.2.0", "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    result = _invoke(["help", "--project-root", str(tmp_path), "--version", "v1.2.0", "--feature", FEATURE])
    assert result.exit_code == 0, result.stdout
    assert "skill discovery" in result.stdout
    assert "beacon skill discover" in result.stdout


def test_requirement_freeze_closure_ac_should_not_be_classified_as_ui():
    text = "当前 requirement package 必须可生成 machine baseline bundle、完成 freeze，并清晰说明冻结的是需求包，不是已实现代码"
    assert _infer_layer_from_ac(text) == "unit"


def test_skill_discover_exception_should_fail_profile_discovery_when_state_missing(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")

    result = _invoke(["profile", "discovery", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 2
    assert "No skill discovery result found" in result.stdout


def test_root_help_should_prioritize_mainline_before_skill_surface():
    result = _invoke(["--help"])
    assert result.exit_code == 0
    lines = [line.strip() for line in result.stdout.splitlines()]
    think_idx = next(i for i, line in enumerate(lines) if line.startswith("│ think"))
    skill_idx = next(i for i, line in enumerate(lines) if line.startswith("│ skill"))
    implement_idx = next(i for i, line in enumerate(lines) if line.startswith("│ implement"))
    debug_idx = next(i for i, line in enumerate(lines) if line.startswith("│ debug"))
    assert think_idx < skill_idx
    assert implement_idx < debug_idx
    assert "labs" not in result.stdout.lower()


def test_v120_feature_qa_should_prefer_qa9_matrix_when_present(tmp_path: Path):
    docs = tmp_path / "docs" / "beacon" / "v1.2.0" / ".machine" / "qa"
    docs.mkdir(parents=True, exist_ok=True)
    slug = "demo-feature"
    ac_matrix = docs / f"{slug}.ac-test-matrix.json"
    qa9_matrix = docs / f"{slug}.qa9-matrix.json"
    ac_matrix.write_text(
        json.dumps({"schema_version": "1.0", "entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    qa9_matrix.write_text(
        json.dumps({"schema_version": "1.0", "entries": [{"ac_id": "AC-001", "tc_id": "TC-021", "qa_type": "functional"}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    path, payload = _load_source_matrix(
        tmp_path,
        version="v1.2.0",
        feature="Demo Feature",
        story={"items": [{"kind": "ac", "id": "AC-001", "text": "demo"}]},
    )

    assert path == qa9_matrix
    assert payload["entries"][0]["tc_id"] == "TC-021"


def test_skill_discover_exception_should_keep_preview_mode_without_no_dry_run(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\ndependencies=['typer']\n", encoding="utf-8")

    result = _invoke(
        [
            "skill",
            "discover",
            "--project-root",
            str(tmp_path),
            "--apply-recommended",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "preview"
    assert payload["applied"] is False
    assert not (tmp_path / "beacon.config.yaml").exists()
