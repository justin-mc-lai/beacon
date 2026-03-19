from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_formal_package(root: Path, version: str = "v1.1.3") -> None:
    base = root / "docs" / "beacon" / version
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (base / "prd" / "feature.md").write_text("# PRD\n", encoding="utf-8")
    (base / "user-story" / "feature.md").write_text("# User Story\n", encoding="utf-8")
    (base / "qa" / "test-cases" / "feature.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / "feature.ac-test-matrix.json").write_text('{"entries":[]}', encoding="utf-8")
    (base / "qa" / "test-cases" / "feature.qa9-matrix.json").write_text('{"entries":[]}', encoding="utf-8")
    (base / "release" / f"{version}.md").write_text("# Release\n", encoding="utf-8")
    state = root / ".beacon" / "runs" / "run-1"
    state.mkdir(parents=True, exist_ok=True)
    (state / "state.json").write_text(
        json.dumps({"run_id": "run-1", "workflow": "workflow", "version": version, "status": "completed"}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_status_should_surface_beacon_source_of_truth(tmp_path: Path):
    _seed_formal_package(tmp_path)
    result = _invoke(["status", "--project-root", str(tmp_path), "--version", "v1.1.3"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    source = payload.get("source_of_truth", {})
    assert source.get("root") == "docs/beacon/v1.1.3"
    assert source.get("runtime_state_root") == ".beacon"


def test_report_and_resume_should_surface_beacon_source_of_truth(tmp_path: Path):
    _seed_formal_package(tmp_path)
    report = _invoke(["report", "--machine", "--project-root", str(tmp_path), "--version", "v1.1.3", "latest"])
    assert report.exit_code == 0
    report_payload = json.loads(report.stdout)
    assert report_payload.get("source_of_truth", {}).get("root") == "docs/beacon/v1.1.3"

    resume = _invoke(["resume", "run-1", "--project-root", str(tmp_path)])
    assert resume.exit_code == 0
    resume_payload = json.loads(resume.stdout)
    assert resume_payload.get("source_of_truth", {}).get("root") == "docs/beacon/v1.1.3"
