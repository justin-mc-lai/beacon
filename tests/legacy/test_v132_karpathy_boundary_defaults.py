from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import CORE_COMMANDS, SUPPORT_COMMANDS
from beacon.main import app
from beacon.utils.context_files import setup_context_files, verify_context_files
from beacon.utils.global_boundaries import (
    global_boundary_prompt_lines,
    inspect_global_boundary_principles,
    load_installed_global_boundaries,
    project_global_boundaries_path,
)
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload


runner = CliRunner()
FEATURE = "beacon-v1.3.2-karpathy-boundary-defaults"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_feature_docs(project_root: Path, *, version: str = "v1.3.2") -> None:
    slug = FEATURE
    prd_dir = project_root / "docs" / "beacon" / version / "prd"
    us_dir = project_root / "docs" / "beacon" / version / "user-story"
    qa_dir = project_root / "docs" / "beacon" / version / "qa" / "test-cases"
    exec_dir = project_root / "docs" / "beacon" / version / "execution"
    for path in (prd_dir, us_dir, qa_dir, exec_dir):
        path.mkdir(parents=True, exist_ok=True)

    prd_dir.joinpath(f"{slug}.md").write_text(
        "\n".join(
            [
                f"# PRD: {FEATURE}",
                "",
                "## Goal",
                "- absorb Karpathy-style boundaries into Beacon global defaults",
                "",
                "## Scope",
                "- document inheritance",
                "- doctor coverage",
                "- implementation and QA evidence expectations",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    us_dir.joinpath(f"{slug}.md").write_text(
        "\n".join(
            [
                f"# User Story: {FEATURE}",
                "",
                "## Acceptance",
                "- 关键需求不明时必须回到 `prd / user-story` 收口",
                "- 默认采用最小正确改动",
                "- 非平凡任务必须保留验证证据",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    qa_dir.joinpath(f"{slug}.md").write_text(
        "\n".join(
            [
                f"# QA: {FEATURE}",
                "",
                "- verify global boundaries inheritance",
                "- verify no external dependency",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    exec_dir.joinpath("architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")


def test_requirement_clarity_should_not_treat_policy_phrasing_as_open_question(tmp_path: Path):
    _seed_feature_docs(tmp_path)

    payload = build_requirement_clarity_gate_payload(tmp_path, version="v1.3.2", feature=FEATURE)

    assert payload["required"] is True
    assert payload["blocked"] is False
    assert payload["reason_code"] == ""


def test_context_setup_should_sync_global_boundaries_and_managed_references(tmp_path: Path):
    result = setup_context_files(
        project_root=tmp_path,
        runtime_version="v1.3.1",
        dry_run=False,
        force=False,
        with_claude=True,
        with_agents=True,
    )

    assert result["project_root"] == str(tmp_path)
    global_boundaries = project_global_boundaries_path(tmp_path)
    assert global_boundaries.exists()
    assert global_boundaries.read_text(encoding="utf-8") == load_installed_global_boundaries()

    verification = verify_context_files(tmp_path, runtime_version="v1.3.1", strict=True)
    checks = {item["name"]: item for item in verification["checks"]}
    assert checks["global_boundaries_presence"]["status"] == "pass"
    assert checks["global_boundaries_inheritance"]["status"] == "pass"


def test_global_boundaries_should_expose_required_karpathy_principles():
    text = load_installed_global_boundaries()
    inspection = inspect_global_boundary_principles(text)

    assert inspection["ok"] is True
    assert inspection["missing_ids"] == []
    assert "要求默认安装外部 skill 仓库" in text
    assert "要求运行时调用外部 skill 才能满足 Beacon 默认规范" in text


def test_karpathy_defaults_should_not_expand_public_command_surface():
    assert CORE_COMMANDS == (
        "think",
        "user-story",
        "prd",
        "prototype",
        "test-case",
        "workflow",
        "qa",
        "auto-test",
        "gate",
        "release",
    )
    assert "implement" in SUPPORT_COMMANDS
    assert "doctor" in SUPPORT_COMMANDS


def test_karpathy_prompt_lines_should_include_trivial_task_lightweight_rule():
    lines = global_boundary_prompt_lines()

    assert any("typo" in line.lower() for line in lines)
    assert any("do not expand scope" in line.lower() for line in lines)


def test_doctor_should_report_global_boundaries_checks_as_pass(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    setup_context_files(
        project_root=tmp_path,
        runtime_version="v1.3.1",
        dry_run=False,
        force=False,
        with_claude=True,
        with_agents=True,
    )

    result = _invoke(["doctor", "--json", "--project-root", str(tmp_path)])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    checks = payload["compatibility_checks"]
    assert checks["global_boundaries_source"]["status"] == "PASS"
    assert checks["global_boundaries_principles"]["status"] == "PASS"
    assert checks["global_boundaries_inheritance"]["status"] == "PASS"
