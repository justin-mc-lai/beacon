"""v1.1.0 gate spec-consistency contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.v110_baseline import generate_spec_fingerprint, record_baseline_snapshot

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


def test_gate_should_block_on_fingerprint_mismatch(tmp_path: Path):
    _seed_docs(tmp_path)
    fp = generate_spec_fingerprint(tmp_path, run_id="run-doc-fp-001", version="v1.1.0")
    expected_hash = str(fp.get("fingerprint_hash", ""))
    assert expected_hash

    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "execution": {
                    "run_id": "run-auto-001",
                    "layers": [],
                    "spec_fingerprint": {"fingerprint_hash": "mismatch-hash"},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = _invoke([
        "gate",
        "check",
        "release",
        "--strict",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--json",
    ])
    assert result.exit_code == 2
    payload = json.loads(result.stdout)

    reason_codes = [
        str(item.get("reason_code", ""))
        for item in payload.get("issues", [])
        if isinstance(item, dict)
    ]
    assert "spec_impl_drift_detected" in reason_codes
    verdict = payload.get("doc_impl_verdict", {})
    assert verdict.get("status") == "blocked"
    assert "spec_impl_drift_detected" in verdict.get("reason_codes", [])


def test_gate_should_emit_doc_impl_verdict_and_reason_codes(tmp_path: Path):
    _seed_docs(tmp_path)
    fp = generate_spec_fingerprint(tmp_path, run_id="run-doc-fp-002", version="v1.1.0")
    expected_hash = str(fp.get("fingerprint_hash", ""))
    assert expected_hash

    record_baseline_snapshot(
        tmp_path,
        run_id="run-baseline-001",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="running",
    )

    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "failed",
                "execution": {
                    "run_id": "run-auto-002",
                    "layers": [],
                    "spec_fingerprint": {"fingerprint_hash": expected_hash},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = _invoke([
        "gate",
        "check",
        "release",
        "--strict",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--json",
    ])
    # may still block for other checks; we only assert consistency verdict contract.
    assert result.exit_code in {0, 2}
    payload = json.loads(result.stdout)
    verdict = payload.get("doc_impl_verdict", {})
    assert verdict.get("enabled") is True
    assert verdict.get("expected_spec_fingerprint") == expected_hash
    assert verdict.get("actual_spec_fingerprint") == expected_hash
    assert verdict.get("status") in {"pass", "warn"}


def test_gate_should_prefer_gate_report_run_id_for_spec_consistency(tmp_path: Path):
    _seed_docs(tmp_path)
    old_fp = generate_spec_fingerprint(tmp_path, run_id="run-old-001", version="v1.1.0")
    old_hash = str(old_fp.get("fingerprint_hash", ""))
    record_baseline_snapshot(
        tmp_path,
        run_id="run-old-001",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="completed",
    )

    story_file = tmp_path / "docs" / "beacon" / "v1.1.0" / "qa" / "test-cases" / "feature.ac-test-matrix.json"
    payload = json.loads(story_file.read_text(encoding="utf-8"))
    payload["entries"].append(
        {
            "ac_id": "AC-002",
            "tc_id": "TC-002",
            "layer": "unit",
            "evidence_path": ".beacon/evidence/auto-test/{run_id}/unit/result.json",
        }
    )
    story_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    new_fp = generate_spec_fingerprint(tmp_path, run_id="run-new-001", version="v1.1.0")
    new_hash = str(new_fp.get("fingerprint_hash", ""))
    record_baseline_snapshot(
        tmp_path,
        run_id="run-new-001",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="completed",
    )

    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "run_id": "run-new-001"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "run_id": "run-new-001",
                "execution": {
                    "run_id": "run-new-001",
                    "layers": [],
                    "spec_fingerprint": {"fingerprint_hash": new_hash},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    terminal = tmp_path / "docs" / "beacon" / "v1.1.0" / ".machine" / "execution"
    terminal.mkdir(parents=True, exist_ok=True)
    (terminal / "terminal.json").write_text(
        json.dumps({"run_id": "run-old-001", "status": "Pass"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    result = _invoke([
        "gate",
        "check",
        "release",
        "--strict",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--json",
    ])
    assert result.exit_code in {0, 2}
    verdict = json.loads(result.stdout).get("doc_impl_verdict", {})
    assert verdict.get("baseline_id") == "bl-run-new-001-001"
    assert verdict.get("expected_spec_fingerprint") == new_hash
    assert verdict.get("actual_spec_fingerprint") == new_hash


def test_gate_strict_should_block_when_baseline_missing(tmp_path: Path):
    _seed_docs(tmp_path)
    fp = generate_spec_fingerprint(tmp_path, run_id="run-doc-fp-003", version="v1.1.0")
    expected_hash = str(fp.get("fingerprint_hash", ""))
    assert expected_hash

    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "execution": {
                    "run_id": "run-auto-003",
                    "layers": [],
                    "spec_fingerprint": {"fingerprint_hash": expected_hash},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = _invoke([
        "gate",
        "check",
        "release",
        "--strict",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--json",
    ])
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    issues = [item for item in payload.get("issues", []) if isinstance(item, dict)]
    missing_issue = next((item for item in issues if item.get("reason_code") == "baseline_snapshot_missing"), None)
    assert missing_issue is not None
    assert bool(missing_issue.get("blocked")) is True
