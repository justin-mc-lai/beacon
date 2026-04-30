"""Coverage metrics gate contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.commands.gate import GateMode, check_coverage_metrics
from beacon.utils.coverage import write_coverage_summary


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


def test_gate_should_pass_coverage_check_with_projected_release_summary_in_fresh_worktree(tmp_path: Path, monkeypatch):
    version = "v1.3.4"
    monkeypatch.setenv("BEACON_VERSION", version)
    beacon_dir = tmp_path / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "coverage-summary.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-123",
                "version": version,
                "coverage_rate": 1.0,
                "full_coverage": True,
                "details": {
                    "version": version,
                    "feature": "",
                    "planned_story": 3,
                    "implemented_story": 3,
                    "story_coverage": 1.0,
                    "total_ac": 11,
                    "tested_ac": 11,
                    "ac_coverage": 1.0,
                    "total_tc": 18,
                    "executed_tc": 18,
                    "tc_coverage": 1.0,
                    "full_coverage": True,
                    "matrix_errors": [],
                },
            }
        ),
        encoding="utf-8",
    )

    issues = check_coverage_metrics(tmp_path, GateMode.STRICT, "release")
    assert issues == []


def test_gate_should_prefer_feature_qa_scorecard_over_stale_projected_coverage_summary(tmp_path: Path, monkeypatch):
    version = "v1.3.6"
    monkeypatch.setenv("BEACON_VERSION", version)
    story_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    impl_path = tmp_path / ".beacon" / "state" / "implementation-feature-a.json"
    qa_status_path = tmp_path / ".beacon" / "qa" / "status.json"
    scorecard_path = tmp_path / ".beacon" / "qa" / "features" / "feature-a" / "scorecard.json"
    coverage_path = tmp_path / ".beacon" / "coverage-summary.json"

    story_dir.mkdir(parents=True, exist_ok=True)
    impl_path.parent.mkdir(parents=True, exist_ok=True)
    qa_status_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)

    (story_dir / "feature-a.md").write_text("# story\n", encoding="utf-8")
    impl_path.write_text(json.dumps({"status": "completed"}), encoding="utf-8")
    qa_status_path.write_text(
        json.dumps(
            {
                "version": version,
                "feature": "feature-a",
                "status": "passed",
                "evidence_done": True,
            }
        ),
        encoding="utf-8",
    )
    scorecard_path.write_text(
        json.dumps(
            {
                "feature": "feature-a",
                "feature_slug": "feature-a",
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "unresolved_closure_outcomes": [],
                "ac_total": 1,
                "ac_accepted": 1,
                "scenario_total": 1,
                "scenario_passed": 1,
                "coverage_current": {
                    "required_scenarios": 1,
                    "executed_scenarios": 1,
                    "coverage_rate": 1.0,
                },
            }
        ),
        encoding="utf-8",
    )
    coverage_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-stale",
                "version": version,
                "coverage_rate": 0.0,
                "full_coverage": False,
                "details": {
                    "version": version,
                    "feature": "",
                    "planned_story": 1,
                    "implemented_story": 1,
                    "story_coverage": 1.0,
                    "total_ac": 1,
                    "tested_ac": 0,
                    "ac_coverage": 0.0,
                    "total_tc": 5,
                    "executed_tc": 0,
                    "tc_coverage": 0.0,
                    "full_coverage": False,
                    "matrix_errors": [],
                },
            }
        ),
        encoding="utf-8",
    )

    issues = check_coverage_metrics(tmp_path, GateMode.STRICT, "release")
    assert issues == []


def test_gate_should_expand_run_id_placeholders_when_computing_coverage(tmp_path: Path, monkeypatch):
    version = "v1.3.4"
    monkeypatch.setenv("BEACON_VERSION", version)
    story_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    matrix_dir = tmp_path / "docs" / "beacon" / version / "qa" / "test-cases"
    evidence_path = tmp_path / ".beacon" / "evidence" / "auto-test" / "run-xyz" / "unit" / "result.json"
    impl_path = tmp_path / ".beacon" / "state" / "implementation-feature-a.json"
    story_dir.mkdir(parents=True, exist_ok=True)
    matrix_dir.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    impl_path.parent.mkdir(parents=True, exist_ok=True)

    (story_dir / "feature-a.md").write_text("# story\n", encoding="utf-8")
    impl_path.write_text(json.dumps({"status": "completed"}), encoding="utf-8")
    evidence_path.write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": "run-xyz",
                "execution": {"run_id": "run-xyz", "layers": [{"layer": "unit", "status": "passed"}]},
            }
        ),
        encoding="utf-8",
    )
    (matrix_dir / "feature-a.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "layer": "unit",
                        "evidence_path": ".beacon/evidence/auto-test/{run_id}/unit/result.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    issues = check_coverage_metrics(tmp_path, GateMode.STRICT, "release")
    assert issues == []


def test_gate_should_prefer_qa9_matrix_when_feature_aware_qa_writes_back_evidence(tmp_path: Path, monkeypatch):
    version = "v1.3.6"
    monkeypatch.setenv("BEACON_VERSION", version)
    story_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    machine_qa_dir = tmp_path / "docs" / "beacon" / version / ".machine" / "qa"
    evidence_path = tmp_path / ".beacon" / "evidence" / "auto-test" / "run-xyz" / "qa9-tc" / "TC-001" / "result.json"
    impl_path = tmp_path / ".beacon" / "state" / "implementation-feature-a.json"
    story_dir.mkdir(parents=True, exist_ok=True)
    machine_qa_dir.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    impl_path.parent.mkdir(parents=True, exist_ok=True)

    (story_dir / "feature-a.md").write_text("# story\n", encoding="utf-8")
    impl_path.write_text(json.dumps({"status": "completed"}), encoding="utf-8")
    evidence_path.write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": "run-xyz",
                "execution": {"run_id": "run-xyz", "layers": [{"layer": "functional", "status": "passed"}]},
            }
        ),
        encoding="utf-8",
    )
    (machine_qa_dir / "feature-a.qa9-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "layer": "functional",
                        "evidence_path": str(evidence_path.relative_to(tmp_path)),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    issues = check_coverage_metrics(tmp_path, GateMode.STRICT, "release")
    assert issues == []


def test_write_coverage_summary_should_recompute_from_live_qa9_evidence(tmp_path: Path, monkeypatch):
    version = "v1.3.6"
    monkeypatch.setenv("BEACON_VERSION", version)
    story_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    machine_qa_dir = tmp_path / "docs" / "beacon" / version / ".machine" / "qa"
    evidence_path = tmp_path / ".beacon" / "evidence" / "auto-test" / "run-xyz" / "qa9-tc" / "TC-001" / "result.json"
    impl_path = tmp_path / ".beacon" / "state" / "implementation-feature-a.json"
    story_dir.mkdir(parents=True, exist_ok=True)
    machine_qa_dir.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    impl_path.parent.mkdir(parents=True, exist_ok=True)

    (story_dir / "feature-a.md").write_text("# story\n", encoding="utf-8")
    impl_path.write_text(json.dumps({"status": "completed"}), encoding="utf-8")
    evidence_path.write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps({"version": version, "run_id": "run-xyz", "execution": {"run_id": "run-xyz"}}),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "coverage-summary.json").write_text(
        json.dumps({"version": version, "coverage_rate": 0.0, "full_coverage": False, "details": {"version": version}}),
        encoding="utf-8",
    )
    (machine_qa_dir / "feature-a.qa9-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "layer": "functional",
                        "evidence_path": str(evidence_path.relative_to(tmp_path)),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    summary_path = write_coverage_summary(tmp_path, version=version)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["coverage_rate"] == 1.0
    assert payload["full_coverage"] is True
    assert payload["details"]["executed_tc"] == 1


def test_gate_should_prefer_release_ready_feature_scorecard_aggregate_for_version_coverage(tmp_path: Path, monkeypatch):
    version = "v1.3.9"
    monkeypatch.setenv("BEACON_VERSION", version)
    story_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    qa_root = tmp_path / ".beacon" / "qa" / "features"
    impl_root = tmp_path / ".beacon" / "state"
    story_dir.mkdir(parents=True, exist_ok=True)
    qa_root.mkdir(parents=True, exist_ok=True)
    impl_root.mkdir(parents=True, exist_ok=True)

    for slug, ac_total, scenario_total in (
        ("feature-a", 2, 3),
        ("feature-b", 4, 5),
    ):
        (story_dir / f"{slug}.md").write_text("# story\n", encoding="utf-8")
        (impl_root / f"implementation-{slug}.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
        feature_dir = qa_root / slug
        feature_dir.mkdir(parents=True, exist_ok=True)
        (feature_dir / "scorecard.json").write_text(
            json.dumps(
                {
                    "feature": slug,
                    "feature_slug": slug,
                    "release_ready": True,
                    "continue_decision": "ready_for_release",
                    "unresolved_closure_outcomes": [],
                    "ac_total": ac_total,
                    "ac_accepted": ac_total,
                    "scenario_total": scenario_total,
                    "scenario_passed": scenario_total,
                    "coverage_current": {
                        "required_scenarios": scenario_total,
                        "executed_scenarios": scenario_total,
                        "coverage_rate": 1.0,
                    },
                }
            ),
            encoding="utf-8",
        )

    issues = check_coverage_metrics(tmp_path, GateMode.STRICT, "release")
    assert issues == []
