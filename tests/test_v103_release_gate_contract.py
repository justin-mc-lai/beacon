"""v1.0.3 release/gate contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _extract_json(stdout: str) -> dict:
    start = stdout.find("{")
    assert start >= 0, stdout
    return json.loads(stdout[start:])


def test_gate_dry_run_should_never_block_exit_code(tmp_path: Path):
    result = _invoke(
        ["gate", "check", "release", "--mode", "dry-run", "--json", "--project-root", str(tmp_path)]
    )
    assert result.exit_code == 0
    payload = _extract_json(result.stdout)
    assert payload["status"] == "Pass"
    assert payload["dry_run"] is True
    assert payload["blocked_count"] >= 1


def test_release_check_should_require_real_artifacts(tmp_path: Path):
    fail = _invoke(["release", "check", "v1.2.3", "--project", str(tmp_path)])
    assert fail.exit_code == 1

    beacon_dir = tmp_path / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    run_id = "run-20260305T000000000000"
    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "run_id": run_id,
                "version": "v1.2.3",
                "execution": {"run_id": run_id, "version": "v1.2.3"},
                "updated_at": "2026-03-05T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps(
            {
                "stage": "release",
                "mode": "strict",
                "status": "Pass",
                "issues": [],
                "run_id": run_id,
                "version": "v1.2.3",
                "coverage": {"full_coverage": True},
                "updated_at": "2026-03-05T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "version": "v1.2.3",
                "entries": [{"path": ".beacon/auto-test-status.json", "sha256": "x"}],
            }
        ),
        encoding="utf-8",
    )
    passed = _invoke(["release", "check", "v1.2.3", "--project", str(tmp_path)])
    assert passed.exit_code == 0
