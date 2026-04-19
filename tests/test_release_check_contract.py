from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_release_artifacts(root: Path, *, version: str, coverage_version: str) -> None:
    beacon_dir = root / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    docs_root = root / "docs" / "beacon" / version
    machine_change = docs_root / ".machine" / "change"
    release_dir = docs_root / "change"
    machine_change.mkdir(parents=True, exist_ok=True)
    release_dir.mkdir(parents=True, exist_ok=True)

    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "version": version, "run_id": "run-123"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-123"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": "run-123",
                "entries": [
                    {"path": ".beacon/auto-test-status.json"},
                    {"path": ".beacon/gate-report.json"},
                    {"path": ".beacon/coverage-summary.json"},
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (beacon_dir / "coverage-summary.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-123",
                "version": coverage_version,
                "coverage_rate": 1.0,
                "full_coverage": True,
                "details": {
                    "version": coverage_version,
                    "feature": "",
                    "planned_story": 1,
                    "implemented_story": 1,
                    "story_coverage": 1.0,
                    "total_ac": 1,
                    "tested_ac": 1,
                    "ac_coverage": 1.0,
                    "total_tc": 1,
                    "executed_tc": 1,
                    "tc_coverage": 1.0,
                    "full_coverage": True,
                    "matrix_errors": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (machine_change / f"{version}.json").write_text(
        json.dumps(
            {
                "version": version,
                "current_feature": "feature-a",
                "features": [{"feature": "feature-a"}],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (release_dir / f"{version}.md").write_text("# release\n", encoding="utf-8")


def test_release_check_should_fail_when_coverage_summary_version_drifts(tmp_path: Path):
    version = "v1.3.4"
    _seed_release_artifacts(tmp_path, version=version, coverage_version="v1.1.10")

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])
    assert result.exit_code == 1
    assert "coverage summary version matches release version" in result.stdout
    assert "artifact_version=v1.1.10" in result.stdout


def test_release_check_should_pass_when_coverage_summary_matches_release(tmp_path: Path):
    version = "v1.3.4"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    assert "Release conditions met" in result.stdout
