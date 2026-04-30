from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.3.10"
FEATURE = "Requirement Package Gate Feature"
SLUG = "requirement-package-gate-feature"


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
    base = root / "docs" / "beacon" / VERSION
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "source-architecture").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (base / "execution" / "project-skill-qa-evolution-blueprint.md").write_text("# Project Skill QA Blueprint\n", encoding="utf-8")
    (base / "source-architecture" / "index.md").write_text("# Source Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text(
        "# PRD\n\n## Functional Requirements\n\n### FR-001 Primary flow\n- keep requirement package aligned\n",
        encoding="utf-8",
    )
    (base / "user-story" / f"{SLUG}.md").write_text(
        (
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | Core | Keep requirement package aligned |\n"
        ),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text(
        "# Test Cases\n\n## TC-001 Primary flow\n- verify requirement package alignment\n",
        encoding="utf-8",
    )


def _freeze(root: Path) -> None:
    result = _invoke(["freeze", FEATURE, "--project-root", str(root), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout


def _mutate_docs_after_freeze(root: Path) -> None:
    story_path = root / "docs" / "beacon" / VERSION / "user-story" / f"{SLUG}.md"
    story_path.write_text(
        (
            "# User Story\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | Core | Keep requirement package aligned |\n"
            "| AC-002 | Drift | Add a new doc-only requirement after freeze |\n"
        ),
        encoding="utf-8",
    )


def test_v13010_implement_should_block_when_requirement_package_drifts_after_freeze(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    _mutate_docs_after_freeze(tmp_path)

    result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "requirement_package_contract_blocked"
    assert payload["requirement_package_gate"]["status"] == "blocked"
    assert "baseline_hash_mismatch" in payload["requirement_package_gate"]["failure_categories"]


def test_v13010_qa_should_block_when_requirement_package_drifts_after_freeze(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    _mutate_docs_after_freeze(tmp_path)

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert "requirement_package_contract_blocked" in payload["reason_codes"]
    assert payload["requirement_package_gate"]["status"] == "blocked"
    assert "baseline_hash_mismatch" in payload["requirement_package_gate"]["failure_categories"]


def test_v13010_release_should_block_when_requirement_package_drifts_after_freeze(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    _mutate_docs_after_freeze(tmp_path)

    result = _invoke(
        [
            "release",
            "check",
            VERSION,
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "requirement_package_contract_blocked"
    assert payload["requirement_package_gate"]["status"] == "blocked"
    assert "baseline_hash_mismatch" in payload["requirement_package_gate"]["failure_categories"]


def test_v13010_help_should_route_doc_drift_to_beacon_change(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    _mutate_docs_after_freeze(tmp_path)

    result = _invoke(
        [
            "help",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["requirement_package_gate"]["status"] == "blocked"
    assert "requirement_package_contract_blocked" in payload["blocking_reasons"]
    assert "baseline_hash_mismatch" in payload["requirement_package_gate"]["failure_categories"]
    assert payload["next_step"]["action"] == "beacon-change"
    assert payload["next_step"]["command"] == "beacon-change"


def test_v13010_help_should_route_missing_machine_artifact_to_sync_materials(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    machine_story = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json"
    assert machine_story.exists()
    machine_story.unlink()

    result = _invoke(
        [
            "help",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["requirement_package_gate"]["status"] == "blocked"
    assert "missing_machine_user_story" in payload["requirement_package_gate"]["failure_categories"]
    assert payload["next_step"]["action"] == "doctor-sync-materials"
    assert "beacon doctor sync-materials" in payload["next_step"]["command"]
    assert f"--feature {FEATURE}" in payload["next_step"]["command"]


def test_v13010_status_board_should_surface_requirement_package_failure_categories(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    _mutate_docs_after_freeze(tmp_path)

    result = _invoke(
        [
            "status",
            "show-status",
            "--board",
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
        ]
    )
    assert result.exit_code == 0, result.stdout
    assert "- source_of_truth.requirement_package_gate: blocked" in result.stdout
    assert "- source_of_truth.requirement_package_failures: baseline_hash_mismatch" in result.stdout
    assert "- source_of_truth.requirement_package_next: beacon-change" in result.stdout
