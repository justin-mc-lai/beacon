from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.3.8"
FEATURE = "V138 Archive Feature"
SLUG = "v138-archive-feature"


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
    _init_git_repo(root)
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text(
        "# PRD\n\n## 功能需求\n\n- FR-001 Archive command should isolate historical truth.\n",
        encoding="utf-8",
    )
    (base / "user-story" / f"{SLUG}.md").write_text(
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Archive | Archive should isolate the feature |\n",
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json").write_text('{"scenarios":[]}\n', encoding="utf-8")


def test_v138_archive_command_should_materialize_governance_and_block_delivery(tmp_path: Path):
    _seed_docs(tmp_path)

    plan_result = _invoke(
        [
            "archive",
            "plan",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--archive-status",
            "archived-learnable",
            "--reason",
            "preserve historical learning only",
            "--json",
        ]
    )
    assert plan_result.exit_code == 0, plan_result.stdout
    plan_payload = json.loads(plan_result.stdout)
    assert plan_payload["status"] == "planned"
    assert plan_payload["archive_plan"]["planned_feature_archive"]["status"] == "archived-learnable"

    apply_result = _invoke(
        [
            "archive",
            "apply",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--archive-status",
            "archived-learnable",
            "--reason",
            "preserve historical learning only",
            "--json",
        ]
    )
    assert apply_result.exit_code == 0, apply_result.stdout
    apply_payload = json.loads(apply_result.stdout)
    assert (tmp_path / apply_payload["plan_ref"]).exists()
    assert (tmp_path / apply_payload["index_ref"]).exists()
    assert (tmp_path / apply_payload["feature_ref"]).exists()

    status_result = _invoke(
        [
            "archive",
            "status",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--json",
        ]
    )
    assert status_result.exit_code == 0, status_result.stdout
    status_payload = json.loads(status_result.stdout)
    assert status_payload["feature"]["status"] == "archived-learnable"

    workflow_status = _invoke(
        [
            "status",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
        ]
    )
    assert workflow_status.exit_code == 0, workflow_status.stdout
    workflow_payload = json.loads(workflow_status.stdout)
    assert workflow_payload["archive"]["feature"]["status"] == "archived-learnable"

    implement_result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert implement_result.exit_code == 2, implement_result.stdout
    implement_payload = json.loads(implement_result.stdout)
    assert implement_payload["reason_code"] == "feature_archived_from_current_delivery"
    assert (Path(__file__).resolve().parents[1] / "skills" / "beacon" / "beacon-archive" / "SKILL.md").exists()
