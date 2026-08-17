"""v1.1.0 rolling baseline workflow contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    (root / "docs" / "beacon" / "v1.1.0" / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.1.0" / "prd").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.1.0" / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)

    (root / "docs" / "beacon" / "v1.1.0" / "user-story" / "feature.md").write_text("# US\n", encoding="utf-8")
    (root / "docs" / "beacon" / "v1.1.0" / "prd" / "feature.md").write_text("# PRD\n", encoding="utf-8")
    (root / "docs" / "beacon" / "v1.1.0" / "qa" / "test-cases" / "feature.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "layer": "unit",
                        "evidence_path": ".beacon/evidence/auto-test/{run_id}/unit/result.json",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _parse_run_id(stdout: str) -> str:
    for line in stdout.splitlines():
        if line.startswith("Run ID: "):
            return line.split("Run ID: ", 1)[1].strip()
    return ""


def test_baseline_snapshot_should_persist_per_iteration(tmp_path: Path):
    _seed_docs(tmp_path)

    start = _invoke([
        "workflow",
        "start",
        "Debug Loop",
        "--project",
        str(tmp_path),
        "--version",
        "v1.1.0",
    ])
    assert start.exit_code == 0
    run_id = _parse_run_id(start.stdout)
    assert run_id

    baseline_root = tmp_path / ".beacon" / "state" / "baselines" / "v1.1.0"
    latest_1 = json.loads((baseline_root / "latest.json").read_text(encoding="utf-8"))
    first_baseline_id = str(latest_1.get("baseline_id", ""))
    assert first_baseline_id
    assert first_baseline_id.startswith(f"bl-{run_id}-")

    cont = _invoke([
        "workflow",
        "continue",
        "--project",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--run-id",
        run_id,
        "--confirm-execute",
        "--confirm-execute-second",
    ])
    assert cont.exit_code == 0

    snapshots = sorted(p for p in baseline_root.glob("*.json") if p.name != "latest.json")
    assert len(snapshots) >= 2

    latest_2 = json.loads((baseline_root / "latest.json").read_text(encoding="utf-8"))
    assert latest_2.get("baseline_id") != first_baseline_id
    assert latest_2.get("revision_of") == first_baseline_id


def test_baseline_snapshot_should_include_required_fields(tmp_path: Path):
    _seed_docs(tmp_path)

    start = _invoke([
        "workflow",
        "start",
        "Debug Loop",
        "--project",
        str(tmp_path),
        "--version",
        "v1.1.0",
    ])
    assert start.exit_code == 0
    run_id = _parse_run_id(start.stdout)
    assert run_id

    latest_path = tmp_path / ".beacon" / "state" / "baselines" / "v1.1.0" / "latest.json"
    latest = json.loads(latest_path.read_text(encoding="utf-8"))

    assert latest.get("baseline_id", "").startswith(f"bl-{run_id}-")
    assert int(latest.get("baseline_seq", 0)) >= 1
    assert latest.get("workflow_status") == "planned"
    assert isinstance(latest.get("open_questions"), list)
    assert isinstance(latest.get("delta_summary"), dict)
    assert isinstance(latest.get("risk_flags"), list)

    spec_fp = latest.get("spec_fingerprint", {})
    assert spec_fp.get("user_story")
    assert spec_fp.get("prd")
    assert spec_fp.get("test_case")
    assert spec_fp.get("fingerprint_hash")
