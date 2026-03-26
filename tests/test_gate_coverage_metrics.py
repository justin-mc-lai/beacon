"""Coverage metrics gate contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.commands.gate import GateMode, check_coverage_metrics


def test_gate_should_block_when_story_ac_tc_coverage_is_incomplete(tmp_path: Path, monkeypatch):
    version = "v1.0.1"
    monkeypatch.setenv("BEACON_VERSION", version)
    story_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    matrix_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    story_dir.mkdir(parents=True, exist_ok=True)
    matrix_dir.mkdir(parents=True, exist_ok=True)
    (story_dir / "feature-a.md").write_text("# story\n", encoding="utf-8")
    (matrix_dir / "feature-a.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"ac_id": "AC-001", "tc_id": "TC-001", "layer": "unit", "evidence_path": ".beacon/evidence/miss.json"}
                ]
            }
        ),
        encoding="utf-8",
    )

    issues = check_coverage_metrics(tmp_path, GateMode.STRICT, "release")
    assert issues
    assert issues[0]["reason_code"] == "coverage_incomplete"
    assert issues[0]["blocked"] is True


def test_gate_should_pass_coverage_check_when_story_ac_tc_all_fully_covered(tmp_path: Path, monkeypatch):
    version = "v1.0.1"
    monkeypatch.setenv("BEACON_VERSION", version)
    story_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    matrix_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    evidence_path = tmp_path / ".beacon" / "evidence" / "test-results" / "feature-a" / "TC-001.json"
    impl_path = tmp_path / ".beacon" / "state" / "implementation-feature-a.json"
    story_dir.mkdir(parents=True, exist_ok=True)
    matrix_dir.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    impl_path.parent.mkdir(parents=True, exist_ok=True)

    (story_dir / "feature-a.md").write_text("# story\n", encoding="utf-8")
    impl_path.write_text(json.dumps({"status": "completed"}), encoding="utf-8")
    evidence_path.write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (matrix_dir / "feature-a.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "layer": "unit",
                        "evidence_path": str(evidence_path.relative_to(tmp_path)),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    issues = check_coverage_metrics(tmp_path, GateMode.STRICT, "release")
    assert issues == []
