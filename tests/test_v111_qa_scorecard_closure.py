from __future__ import annotations

from pathlib import Path

from beacon.commands.auto_test import _collect_required_file_issues
from beacon.utils.qa_feature import build_feature_qa_precision_artifacts


def test_feature_qa_precision_should_infer_required_families_from_source_tc_results(tmp_path: Path):
    plan = {
        "version": "v1.1.11",
        "required_scenario_families": ["happy", "negative"],
        "targeted_source_tc_ids": ["TC-003"],
        "story_scenarios": {
            "stories": [
                {
                    "ac_id": "AC-003",
                    "required_families": ["happy", "negative"],
                    "scenarios": [
                        {"source_tc_id": "TC-003", "scenario_family": "happy"},
                        {"source_tc_id": "TC-003", "scenario_family": "negative"},
                    ],
                }
            ]
        },
    }
    per_item_results = [
        {
            "ac_id": "AC-003",
            "tc_id": "TC-003",
            "source_tc_id": "TC-003",
            "scenario_id": "",
            "scenario_family": "",
            "status": "passed",
            "qa_type": "unit",
            "browser_required": False,
            "replay_required": False,
            "replay_ref": "",
            "browser_evidence_pack_ref": "",
            "evidence_ref": ["evidence.json"],
        }
    ]

    _, ac_closure, feature_scorecard, _, _ = build_feature_qa_precision_artifacts(
        tmp_path,
        feature="qa-family-feature",
        run_id="run-qa-family",
        plan=plan,
        per_item_results=per_item_results,
        qa_status={"quality_issues": []},
        exhaustiveness={
            "status": "passed",
            "scenario_count": 1,
            "missing_axes": [],
            "missing_replay_scenarios": [],
            "missing_browser_evidence_scenarios": [],
        },
    )

    report = ac_closure["reports"][0]
    assert report["closure_status"] == "accepted"
    assert report["passed_scenario_families"] == ["happy", "negative"]
    assert feature_scorecard["coverage_current"]["covered_scenario_families"] == ["happy", "negative"]
    assert feature_scorecard["continue_decision"] == "ready_for_release"
    assert feature_scorecard["release_ready"] is True


def test_collect_required_file_issues_should_ignore_non_test_runner_layers(tmp_path: Path):
    layer_results = [
        {
            "layer": "functional",
            "status": "passed",
            "assertion_count": 0,
            "junit_path": "",
        },
        {
            "layer": "unit",
            "status": "passed",
            "assertion_count": 0,
            "junit_path": "",
        },
    ]

    issues = _collect_required_file_issues(
        project_root=tmp_path,
        layer_results=layer_results,
        require_junit=True,
        require_assertion_count=True,
    )

    reason_codes = [item["reason_code"] for item in issues]
    assert reason_codes == ["assertion_count_zero_pass", "junit_missing_or_invalid"]
    assert all(item["layer"] == "unit" for item in issues)


def test_feature_qa_precision_should_continue_for_pending_targeted_cases_without_requesting_test_case_create(tmp_path: Path):
    plan = {
        "version": "v1.1.11",
        "required_scenario_families": [],
        "targeted_source_tc_ids": ["TC-DB001-01", "TC-DB001-08"],
        "story_scenarios": {"stories": []},
    }

    _, _, feature_scorecard, _, _ = build_feature_qa_precision_artifacts(
        tmp_path,
        feature="qa-pending-manual-feature",
        run_id="run-qa-pending-manual",
        plan=plan,
        per_item_results=[],
        qa_status={"quality_issues": []},
        exhaustiveness={
            "status": "passed",
            "scenario_count": 2,
            "missing_axes": [],
            "missing_replay_scenarios": [],
            "missing_browser_evidence_scenarios": [],
        },
    )

    assert feature_scorecard["continue_decision"] == "continue"
    assert feature_scorecard["test_case_backfill_required"] is False
    assert feature_scorecard["coverage_current"]["missing_test_case_ids"] == ["TC-DB001-01", "TC-DB001-08"]
    assert feature_scorecard["repair_handoff"]["action"] == "qa-repair"
    assert "test-case create" not in feature_scorecard["repair_handoff"]["command"]
