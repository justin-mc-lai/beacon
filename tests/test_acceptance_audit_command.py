from __future__ import annotations

import json
import sys
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.acceptance_audit import parse_pytest_summary
from beacon.utils.artifact_paths import execution_file_output


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_acceptance_inputs(root: Path) -> None:
    qa_dir = root / "docs" / "beacon" / "v1.1.1" / "qa" / "test-cases"
    qa_dir.mkdir(parents=True, exist_ok=True)
    (qa_dir / "feature.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "entries": [
                    {"ac_id": "AC-001", "tc_id": "TC-001"},
                    {"ac_id": "AC-002", "tc_id": "TC-002"},
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    legacy_dir = root / "docs" / "beacon" / "v1.0.0" / "qa" / "test-cases"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    (legacy_dir / "beacon-core.md").write_text("# legacy\n", encoding="utf-8")

    beacon_dir = root / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "version": "v1.1.1",
                "run_id": "run-acc-001",
                "qa9": {"summary": {"cases_total": 2, "passed": 2}},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps(
            {
                "status": "Pass",
                "version": "v1.1.1",
                "run_id": "run-acc-001",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (beacon_dir / "coverage-summary.json").write_text(
        json.dumps(
            {
                "story_coverage": 1.0,
                "ac_coverage": 1.0,
                "tc_coverage": 1.0,
                "full_coverage": True,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def test_parse_pytest_summary_should_extract_passed_counts():
    payload = parse_pytest_summary("348 passed in 48.80s")
    assert payload["status"] == "pass"
    assert payload["passed"] == 348
    assert payload["failed"] == 0
    assert payload["total"] == 348


def test_report_acceptance_audit_should_write_generated_artifacts(tmp_path: Path):
    _seed_acceptance_inputs(tmp_path)
    regression_command = f"{sys.executable} -c 'print(\"5 passed in 0.12s\")'"

    result = _invoke(
        [
            "report",
            "latest",
            "acceptance-audit",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.1",
            "--feature",
            "feature",
            "--run-regression",
            "--regression-command",
            regression_command,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["regression"]["passed"] == 5
    assert payload["release_evidence_run_id"] == "run-acc-001"
    assert payload["executable_specs_total"] == 1
    assert payload["executable_entries_total"] == 2
    assert payload["legacy_manual_specs"] == ["docs/beacon/v1.0.0/qa/test-cases/beacon-core.md"]

    beacon_md = tmp_path / "docs" / "beacon" / "v1.1.1" / "execution" / "acceptance-regression-audit.md"
    beacon_json = execution_file_output(tmp_path, "v1.1.1", "acceptance-regression-audit.json")
    manifest = json.loads((tmp_path / ".beacon" / "evidence-manifest.json").read_text(encoding="utf-8"))
    assert beacon_md.exists()
    assert beacon_json.exists()
    assert "5 passed in 0.12s" in beacon_md.read_text(encoding="utf-8")
    manifest_paths = {str(item.get("path")) for item in manifest.get("entries", []) if isinstance(item, dict)}
    assert "docs/beacon/v1.1.1/execution/acceptance-regression-audit.md" in manifest_paths
    assert "docs/beacon/v1.1.1/.machine/execution/acceptance-regression-audit.json" in manifest_paths
    assert "docs/product/v1.1.1/execution/acceptance-regression-audit.md" not in manifest_paths
